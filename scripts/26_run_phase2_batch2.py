"""
Phase 2 intraday robustness backtests — Batch 2.

Hypotheses: H58 (BLOCKED), H70, H76, H96, H99
Walk-forward: train=2024, val=2025, holdout=2026-Q1

Key design choices vs script 25:
  H70 — transition matrix + leak-safe rolling percentile
  H76 — 1m-bar gap fill (touch/cross prior close), 12-column per-gap schema
  H96 — continuous fwd_ratio + mandatory H44 redundancy gate
  H99 — corrected outcome (next_day_range, not hv_20_cc) + contamination table

Output:
  experiments/phase2_results/H{N}_b2.json
  experiments/phase2_results/batch2_summary.json
  vault/Phase2/H{N}_b2.md

Usage:
  python scripts/26_run_phase2_batch2.py
  python scripts/26_run_phase2_batch2.py --hypotheses H76,H70
  python scripts/26_run_phase2_batch2.py --force
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr, fisher_exact
from scipy.stats import rankdata as scipy_rankdata

try:
    import statsmodels.api as sm
    HAS_SM = True
except ImportError:
    HAS_SM = False

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
DAILY_SERIES = BASE / "data" / "processed" / "daily_series.parquet"
RESULTS_DIR = BASE / "experiments" / "phase2_results"
VAULT_DIR = BASE / "vault" / "Phase2"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

# ── Walk-forward windows ───────────────────────────────────────────────────────

TRAIN_START, TRAIN_END = "2024-01-01", "2024-12-31"
VAL_START,   VAL_END   = "2025-01-01", "2025-12-31"
HOLD_START,  HOLD_END  = "2026-01-01", "2026-03-31"
FULL_START,  FULL_END  = "2024-01-01", "2026-03-31"
_ET = "America/New_York"

# ── Data loading ──────────────────────────────────────────────────────────────

def load_all_1m() -> pd.DataFrame:
    files = sorted(DATABENTO_DIR.glob("qqq_1m_*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files]).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def load_daily() -> pd.DataFrame:
    df = pd.read_parquet(DAILY_SERIES)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


# ── Intraday feature builder (range windows, reused from script 25) ────────────

def build_daily_intraday_features(bars_1m: pd.DataFrame) -> pd.DataFrame:
    """Per-day range windows and first/last bar prices from 1m data."""
    rows = []
    for d in sorted(set(bars_1m.index.date)):
        mask = bars_1m.index.date == d
        day = bars_1m.loc[mask]
        if day.empty:
            continue
        last_close = day["close"].iloc[-1]
        first_open = day["open"].iloc[0]
        last_close_ts = day.index[-1]

        def rng(start, end):
            sub = day.between_time(start, end)
            if sub.empty:
                return np.nan
            return float((sub["high"].max() - sub["low"].min()) / last_close)

        rows.append({
            "date": pd.Timestamp(d),
            "first_open": float(first_open),
            "last_close": float(last_close),
            "last_close_ts": last_close_ts,
            "range_30m": rng("09:30", "09:59"),
            "range_60m": rng("09:30", "10:29"),
            "range_120m": rng("09:30", "11:29"),
            "range_session": float((day["high"].max() - day["low"].min()) / last_close),
        })

    feat = pd.DataFrame(rows).set_index("date")
    feat["gap_pct_1m"] = (feat["first_open"] / feat["last_close"].shift(1) - 1)
    return feat


# ── Statistical utilities ──────────────────────────────────────────────────────

def cliff_delta(g1: np.ndarray, g2: np.ndarray) -> float:
    g1, g2 = np.asarray(g1, float), np.asarray(g2, float)
    if len(g1) == 0 or len(g2) == 0:
        return np.nan
    dom = int((g1[:, None] > g2[None, :]).sum()) - int((g1[:, None] < g2[None, :]).sum())
    return dom / (len(g1) * len(g2))


def mw_test(g1: np.ndarray, g2: np.ndarray, alternative: str = "greater") -> dict:
    g1 = np.asarray(g1, float); g1 = g1[np.isfinite(g1)]
    g2 = np.asarray(g2, float); g2 = g2[np.isfinite(g2)]
    if len(g1) < 5 or len(g2) < 5:
        return {"n_a": len(g1), "n_b": len(g2), "stat": None, "p": None,
                "cliff_d": None, "median_a": float(np.median(g1)) if len(g1) else None,
                "median_b": float(np.median(g2)) if len(g2) else None, "diff": None}
    stat, p = mannwhitneyu(g1, g2, alternative=alternative)
    return {
        "n_a": int(len(g1)), "n_b": int(len(g2)),
        "stat": float(stat), "p": float(p),
        "cliff_d": cliff_delta(g1, g2),
        "median_a": float(np.median(g1)), "median_b": float(np.median(g2)),
        "diff": float(np.median(g1) - np.median(g2)),
    }


def nw_spearman(x: np.ndarray, y: np.ndarray, maxlags: int = 5) -> dict:
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 20:
        return {"rho": None, "p_nw": None, "n": n}
    rho, p_scipy = spearmanr(x, y)
    if HAS_SM:
        rx = scipy_rankdata(x) / n
        ry = scipy_rankdata(y) / n
        X = sm.add_constant(rx)
        p_nw = float(sm.OLS(ry, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags}).pvalues[1])
    else:
        p_nw = float(p_scipy)
    return {"rho": float(rho), "p_nw": float(p_nw), "n": int(n)}


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> dict:
    """Partial Spearman of x~y after removing the linear effect of z (rank scale)."""
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[mask], y[mask], z[mask]
    n = len(x)
    if n < 20 or not HAS_SM:
        rho, p = spearmanr(x, y)
        return {"partial_rho": float(rho), "partial_p": float(p), "n": int(n), "method": "full_spearman_fallback"}
    rx = scipy_rankdata(x) / n
    ry = scipy_rankdata(y) / n
    rz = scipy_rankdata(z) / n
    Z = sm.add_constant(rz)
    resid_x = sm.OLS(rx, Z).fit().resid
    resid_y = sm.OLS(ry, Z).fit().resid
    rho, p = spearmanr(resid_x, resid_y)
    return {"partial_rho": float(rho), "partial_p": float(p), "n": int(n), "method": "residual_ols"}


def _cbb_idx(rng: np.random.Generator, n: int, block: int) -> np.ndarray:
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=n_blocks)
    idx = []
    for s in starts:
        idx.extend([(s + k) % n for k in range(block)])
    return np.array(idx[:n])


def block_bootstrap_diff(
    outcome: np.ndarray, mask_a: np.ndarray, mask_b: np.ndarray,
    n_boot: int = 2000, block: int = 5, seed: int = 42,
) -> tuple[float, float, tuple[float, float]]:
    """Bootstrap p-value (greater) and CI for median(a) - median(b)."""
    rng = np.random.default_rng(seed)
    observed = float(np.median(outcome[mask_a]) - np.median(outcome[mask_b]))
    diffs = []
    n = len(outcome)
    for _ in range(n_boot):
        idx = _cbb_idx(rng, n, block)
        bo = outcome[idx]; bma = mask_a[idx]; bmb = mask_b[idx]
        if bma.sum() > 1 and bmb.sum() > 1:
            diffs.append(float(np.median(bo[bma]) - np.median(bo[bmb])))
    d = np.array(diffs)
    p = float((d <= 0).mean())
    ci = (float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)))
    return observed, p, ci


def split_by_period(df: pd.DataFrame) -> dict:
    return {
        "full":    df.loc[FULL_START:FULL_END],
        "train":   df.loc[TRAIN_START:TRAIN_END],
        "val":     df.loc[VAL_START:VAL_END],
        "holdout": df.loc[HOLD_START:HOLD_END],
    }


def walk_forward_spearman(
    df: pd.DataFrame, x_col: str, y_col: str, maxlags: int = 5
) -> dict:
    splits = split_by_period(df)
    results = {}
    signs = []
    for name, sub in splits.items():
        r = nw_spearman(sub[x_col].values, sub[y_col].values, maxlags)
        results[name] = r
        if name != "full" and r["rho"] is not None:
            signs.append(np.sign(r["rho"]))
    n_pos = sum(s > 0 for s in signs)
    consistency = "consistent" if n_pos == 3 else ("mixed" if n_pos == 2 else "inconsistent")
    return {"splits": results, "consistency": consistency, "n_positive_splits": int(n_pos)}


def walk_forward_mw(
    df: pd.DataFrame, mask_col: str, outcome_col: str, alternative: str = "greater"
) -> dict:
    splits = split_by_period(df)
    results = {}
    signs = []
    for name, sub in splits.items():
        sub_c = sub[[mask_col, outcome_col]].dropna()
        ga = sub_c.loc[sub_c[mask_col], outcome_col].values
        gb = sub_c.loc[~sub_c[mask_col], outcome_col].values
        r = mw_test(ga, gb, alternative)
        results[name] = r
        if name != "full" and r["diff"] is not None:
            signs.append(np.sign(r["diff"]))
    n_pos = sum(s > 0 for s in signs)
    consistency = "consistent" if n_pos == 3 else ("mixed" if n_pos == 2 else "inconsistent")
    return {"splits": results, "consistency": consistency, "n_positive_splits": int(n_pos)}


def _save(result: dict, stem: str) -> None:
    p = RESULTS_DIR / f"{stem}.json"
    with open(p, "w") as f:
        json.dump(result, f, indent=2, default=str)


# ── H58 — BLOCKED ─────────────────────────────────────────────────────────────

def run_h58(force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H58_b2.json"
    if out_path.exists() and not force:
        return json.loads(out_path.read_text())

    result = {
        "hypothesis_number": "H58",
        "hypothesis_title": "First-30-Minute Option Volume Direction Predicts Rest-of-Day Price Direction",
        "classification": "blocked_feasibility_first",
        "phase2_verdict": "blocked",
        "phase2_verdict_reason": (
            "data/raw/chains/ contains ~4045 files for ~563 trading days = ~7 contracts/day. "
            "Constructing an honest call/put volume ratio requires the full option chain "
            "(all strikes, all expirations) at 5-min granularity. "
            "No full-chain volume feed has been fetched from iVolatility BackendPlus. "
            "A Databento underlying-bar proxy would test a different hypothesis. "
            "H58 remains blocked until a full intraday chain volume feed is confirmed available."
        ),
        "condition_to_unblock": (
            "Confirm iVolatility BackendPlus provides full intraday QQQ option chain volume "
            "at 5-min bars for all strikes/expirations. If yes, design the data fetch first."
        ),
        "phase1_verdict": "insufficient_data",
        "phase1_n_observations": 0,
    }
    _save(result, "H58_b2")
    return result


# ── H70 — Daily Range Persistence ─────────────────────────────────────────────

def run_h70(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H70_b2.json"
    if out_path.exists() and not force:
        print("  H70: cached"); return json.loads(out_path.read_text())

    print("  H70: running...")

    # --- Signal construction (leak-safe) ---
    df = daily[["high", "low", "close", "iv_30d", "iv_60d", "log_return"]].copy()
    df.index = pd.to_datetime(df.index)

    df["daily_range"] = (df["high"] - df["low"]) / df["close"]

    # prior_range: shift(1) so row t = yesterday's range — fully pre-open
    df["prior_range"] = df["daily_range"].shift(1)

    # Rolling 252-day percentile rank — leak-safe (see design spec proof)
    df["prior_range_pct"] = df["prior_range"].rolling(252, min_periods=60).rank(pct=True)

    # Maturity flag: window has full 252 observations
    df["prior_range_pct_mature"] = df["prior_range"].rolling(252).count() >= 252

    # Quintile (on mature rows only)
    mature_mask = df["prior_range_pct_mature"]
    df["prior_quintile"] = np.nan
    df.loc[mature_mask, "prior_quintile"] = pd.qcut(
        df.loc[mature_mask, "prior_range_pct"], 5, labels=[1, 2, 3, 4, 5]
    ).astype(float)

    # Outcomes
    df["next_day_range"] = df["daily_range"].shift(-1)
    df["next_day_range_pct"] = df["prior_range_pct"].shift(-1)  # reuse rolling rank shifted -1
    df["h44_slope"] = df["iv_30d"] / df["iv_60d"]   # for controls

    # Intraday ranges from feats (next session)
    feats_idx = feats[["range_30m", "range_60m", "range_120m"]].copy()
    feats_idx.index = pd.to_datetime(feats_idx.index)
    df = df.join(feats_idx.shift(-1).rename(columns={
        "range_30m": "next_30m", "range_60m": "next_60m", "range_120m": "next_120m"
    }), how="left")

    # --- Transition matrix (mature rows, full period) ---
    mat_df = df.loc[mature_mask & df["prior_quintile"].notna()].copy()
    mat_df["next_quintile"] = np.nan
    valid_next = mat_df["next_day_range_pct"].notna()
    mat_df.loc[valid_next, "next_quintile"] = pd.qcut(
        mat_df.loc[valid_next, "next_day_range_pct"], 5, labels=[1, 2, 3, 4, 5]
    ).astype(float)
    trans_df = mat_df.dropna(subset=["prior_quintile", "next_quintile"])
    transition_matrix = pd.crosstab(
        trans_df["prior_quintile"].astype(int),
        trans_df["next_quintile"].astype(int),
        normalize="index"
    ).round(3).to_dict()

    # --- Continuous Spearman (prior_range_pct → next_day_range) ---
    wf_spearman = walk_forward_spearman(
        df.loc[mature_mask].dropna(subset=["prior_range_pct", "next_day_range"]),
        "prior_range_pct", "next_day_range"
    )

    # --- Binary MW (Q5 vs rest) ---
    df["is_q5"] = (df["prior_range_pct"] >= 0.80) & mature_mask
    wf_mw = walk_forward_mw(df.dropna(subset=["next_day_range"]), "is_q5", "next_day_range")

    # --- Quintile gradient (median next_day_range by quintile bucket) ---
    quintile_medians = {}
    for q in [1, 2, 3, 4, 5]:
        sub = df.loc[df["prior_quintile"] == q, "next_day_range"].dropna()
        quintile_medians[f"Q{q}"] = {"n": int(len(sub)), "median_next_range": float(np.median(sub)) if len(sub) else None}
    # Monotonicity: is each quintile higher than previous?
    meds = [quintile_medians[f"Q{q}"]["median_next_range"] for q in [1,2,3,4,5] if quintile_medians[f"Q{q}"]["median_next_range"] is not None]
    is_monotonic = all(meds[i] <= meds[i+1] for i in range(len(meds)-1)) if len(meds) == 5 else None

    # --- Controls: partial Spearman after conditioning on iv_30d ---
    ctrl_df = df.loc[mature_mask].dropna(subset=["prior_range_pct", "next_day_range", "iv_30d"])
    partial_vs_iv30 = partial_spearman(
        ctrl_df["prior_range_pct"].values,
        ctrl_df["next_day_range"].values,
        ctrl_df["iv_30d"].values,
    )

    # --- Intraday expression: Spearman prior_range_pct → next_30/60/120m ---
    intraday_spearman = {}
    for col in ["next_30m", "next_60m", "next_120m"]:
        sub = df.loc[mature_mask].dropna(subset=["prior_range_pct", col])
        intraday_spearman[col] = nw_spearman(sub["prior_range_pct"].values, sub[col].values)

    # --- Burn-in note ---
    n_mature = int(mature_mask.sum())
    n_immature = int((~mature_mask & df["prior_range_pct"].notna()).sum())
    n_train_mature = int((mature_mask & (df.index >= TRAIN_START) & (df.index <= TRAIN_END)).sum())

    # --- Verdict ---
    full_sp = wf_spearman["splits"]["full"]
    rho = full_sp.get("rho") or 0
    p_nw = full_sp.get("p_nw") or 1
    n_pos = wf_spearman.get("n_positive_splits", 0)
    if n_mature < 30:
        verdict, reason = "insufficient_data", f"only {n_mature} mature rows"
    elif rho > 0.15 and p_nw < 0.05 and n_pos >= 2 and is_monotonic:
        verdict = "supported"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}, {wf_spearman['consistency']}, monotonic={is_monotonic}"
    elif rho < 0 or p_nw > 0.30:
        verdict = "rejected"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}"
    else:
        verdict = "inconclusive"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}, monotonic={is_monotonic}, {wf_spearman['consistency']}"

    result = {
        "hypothesis_number": "H70",
        "hypothesis_title": "Big-Range Day Tends to Be Followed by Another Big-Range Day",
        "classification": "eod_primary",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "n_mature_rows": n_mature,
        "n_immature_rows": n_immature,
        "n_train_mature": n_train_mature,
        "burn_in_warning": n_train_mature < 50,
        "transition_matrix_row_normalized": transition_matrix,
        "quintile_gradient": quintile_medians,
        "is_monotonic": is_monotonic,
        "continuous_spearman_wf": wf_spearman,
        "binary_mw_q5_vs_rest_wf": wf_mw,
        "partial_spearman_vs_iv30d": partial_vs_iv30,
        "intraday_expression": intraday_spearman,
        "phase1_alignment": "extends",
        "notes": "Signal: prior_range_pct via daily_range.shift(1).rolling(252,min_periods=60).rank(pct=True). Mature flag requires 252 observations.",
    }
    _save(result, "H70_b2")
    return result


# ── H76 — Gap Fill in Backwardation vs Contango ───────────────────────────────

def _build_gap_table(bars_1m: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    """
    Build the 12-column per-gap-day table (gap_abs > 0.5%).
    Uses 1m bars for gap calculation and fill detection.
    """
    feats_rows = []
    days = sorted(set(bars_1m.index.date))

    for i, d in enumerate(days):
        if i == 0:
            continue  # need prior session
        dt = pd.Timestamp(d)
        if dt not in daily.index:
            continue

        prev_d = days[i - 1]
        prev_dt = pd.Timestamp(prev_d)
        if prev_dt not in daily.index:
            continue

        # 1m bars for current and prior session
        day_bars = bars_1m.loc[bars_1m.index.date == d]
        prev_bars = bars_1m.loc[bars_1m.index.date == prev_d]
        if day_bars.empty or prev_bars.empty:
            continue

        # Gap computation from 1m bars
        prev_close_1m = float(prev_bars["close"].iloc[-1])
        curr_first_open = float(day_bars["open"].iloc[0])
        gap_signed = curr_first_open / prev_close_1m - 1
        gap_abs = abs(gap_signed)

        if gap_abs < 0.005:  # not a gap day
            continue

        gap_dir = "up" if gap_signed > 0 else "down"
        if gap_abs < 0.01:
            gap_size_bucket = "small"
        elif gap_abs < 0.02:
            gap_size_bucket = "medium"
        else:
            gap_size_bucket = "large"

        # Signal: prior EOD iv_30d > iv_60d
        prev_row = daily.loc[prev_dt]
        in_backwardation = bool(prev_row["iv_30d"] > prev_row["iv_60d"])
        prior_day_return = float(prev_row["log_return"]) if "log_return" in daily.columns else np.nan
        iv_30d = float(prev_row["iv_30d"])

        # Gap fill detection via 1m bars
        fill_time = None
        if gap_dir == "up":
            # Fill = any bar's low ≤ prev_close
            for ts, bar in day_bars.iterrows():
                if bar["low"] <= prev_close_1m:
                    fill_time = ts
                    break
        else:
            # Fill = any bar's high ≥ prev_close
            for ts, bar in day_bars.iterrows():
                if bar["high"] >= prev_close_1m:
                    fill_time = ts
                    break

        fill_by_1130 = False
        fill_by_close = fill_time is not None
        fill_time_minutes = np.nan
        if fill_time is not None:
            open_ts = day_bars.index[0]
            fill_by_1130 = fill_time.strftime("%H:%M") <= "11:30"
            fill_time_minutes = float((fill_time - open_ts).total_seconds() / 60)

        # First 2h range (09:30–11:29)
        fh2 = day_bars.between_time("09:30", "11:29")
        first_2h_range = float((fh2["high"].max() - fh2["low"].min()) / prev_close_1m) if not fh2.empty else np.nan

        # No-fill continuation: for non-fill days only
        curr_last_close = float(day_bars["close"].iloc[-1])
        no_fill_continuation = np.nan
        if not fill_by_close and gap_abs > 0:
            no_fill_continuation = float(abs(curr_last_close - curr_first_open) / gap_abs)

        feats_rows.append({
            "date": dt,
            "gap_signed": round(gap_signed, 6),
            "gap_abs": round(gap_abs, 6),
            "gap_dir": gap_dir,
            "in_backwardation": in_backwardation,
            "gap_size_bucket": gap_size_bucket,
            "prior_day_return": round(prior_day_return, 6),
            "iv_30d": round(iv_30d, 6),
            "fill_by_1130": fill_by_1130,
            "fill_by_close": fill_by_close,
            "fill_time_minutes": round(fill_time_minutes, 1) if np.isfinite(fill_time_minutes) else None,
            "first_2h_range": round(first_2h_range, 6) if np.isfinite(first_2h_range) else None,
            "no_fill_continuation": round(no_fill_continuation, 4) if np.isfinite(no_fill_continuation) else None,
        })

    return pd.DataFrame(feats_rows).set_index("date")


def run_h76(bars_1m: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H76_b2.json"
    if out_path.exists() and not force:
        print("  H76: cached"); return json.loads(out_path.read_text())

    print("  H76: building gap-day table (scanning 1m bars for fill events)...")
    gap_df = _build_gap_table(bars_1m, daily)
    n_total = len(gap_df)
    print(f"  H76: {n_total} gap days found")

    if n_total < 30:
        result = {
            "hypothesis_number": "H76",
            "phase2_verdict": "insufficient_data",
            "phase2_verdict_reason": f"only {n_total} gap days",
        }
        _save(result, "H76_b2")
        return result

    backw = gap_df["in_backwardation"]
    cont = ~backw

    # --- Primary: fill_by_close rates (replication with corrected definition) ---
    n_backw = int(backw.sum())
    n_cont = int(cont.sum())
    fill_rate_backw = float(gap_df.loc[backw, "fill_by_close"].mean())
    fill_rate_cont = float(gap_df.loc[cont, "fill_by_close"].mean())
    diff_fill = fill_rate_backw - fill_rate_cont

    # Fisher exact test (fill/no-fill × backw/contango)
    a = int(gap_df.loc[backw, "fill_by_close"].sum())
    b = n_backw - a
    c = int(gap_df.loc[cont, "fill_by_close"].sum())
    d = n_cont - c
    _, p_fisher = fisher_exact([[a, b], [c, d]], alternative="greater")

    # Block bootstrap CI on fill rate diff
    outcome_fill = gap_df["fill_by_close"].astype(float).values
    mask_backw = backw.values
    mask_cont = cont.values
    _, p_boot, ci_boot = block_bootstrap_diff(outcome_fill, mask_backw, mask_cont)

    # --- fill_by_1130 ---
    fill1130_backw = float(gap_df.loc[backw, "fill_by_1130"].mean())
    fill1130_cont = float(gap_df.loc[cont, "fill_by_1130"].mean())
    diff_1130 = fill1130_backw - fill1130_cont

    # --- Time-to-fill MW (filled days only) ---
    filled_backw_ttf = gap_df.loc[backw & gap_df["fill_by_close"], "fill_time_minutes"].dropna().values
    filled_cont_ttf = gap_df.loc[cont & gap_df["fill_by_close"], "fill_time_minutes"].dropna().values
    ttf_mw = mw_test(filled_backw_ttf, filled_cont_ttf, alternative="less")  # backw fills faster

    # --- First 2h range ---
    range_mw = mw_test(
        gap_df.loc[backw, "first_2h_range"].dropna().values,
        gap_df.loc[cont, "first_2h_range"].dropna().values,
    )

    # --- Segmentation: direction × backwardation ---
    seg_table = {}
    for g_dir in ["up", "down"]:
        for regime in ["backwardation", "contango"]:
            mask = (gap_df["gap_dir"] == g_dir) & (backw if regime == "backwardation" else cont)
            n = int(mask.sum())
            if n < 5:
                seg_table[f"{g_dir}_{regime}"] = {"n": n, "fill_rate_close": None, "fill_rate_1130": None}
            else:
                seg_table[f"{g_dir}_{regime}"] = {
                    "n": n,
                    "fill_rate_close": float(gap_df.loc[mask, "fill_by_close"].mean()),
                    "fill_rate_1130": float(gap_df.loc[mask, "fill_by_1130"].mean()),
                }

    # Gap size control: does backw add beyond gap size?
    size_table = {}
    for bucket in ["small", "medium", "large"]:
        bm = gap_df["gap_size_bucket"] == bucket
        nb = int((bm & backw).sum()); nc = int((bm & cont).sum())
        if nb < 5 or nc < 5:
            size_table[bucket] = {"n_backw": nb, "n_cont": nc, "fill_diff": None, "note": "n<5 flagged"}
        else:
            size_table[bucket] = {
                "n_backw": nb, "n_cont": nc,
                "fill_rate_backw": float(gap_df.loc[bm & backw, "fill_by_close"].mean()),
                "fill_rate_cont": float(gap_df.loc[bm & cont, "fill_by_close"].mean()),
                "fill_diff": float(gap_df.loc[bm & backw, "fill_by_close"].mean() -
                                   gap_df.loc[bm & cont, "fill_by_close"].mean()),
            }

    # Walk-forward fill rate diff
    wf_fill = {}
    for period_name, (s, e) in [("full",(FULL_START,FULL_END)),("train",(TRAIN_START,TRAIN_END)),("val",(VAL_START,VAL_END)),("holdout",(HOLD_START,HOLD_END))]:
        sub = gap_df.loc[s:e]
        sb = sub["in_backwardation"]
        sc = ~sb
        nb2 = int(sb.sum()); nc2 = int(sc.sum())
        if nb2 < 5 or nc2 < 5:
            wf_fill[period_name] = {"n_backw": nb2, "n_cont": nc2, "fill_diff": None}
        else:
            wf_fill[period_name] = {
                "n_backw": nb2, "n_cont": nc2,
                "fill_rate_backw": float(sub.loc[sb, "fill_by_close"].mean()),
                "fill_rate_cont": float(sub.loc[sc, "fill_by_close"].mean()),
                "fill_diff": float(sub.loc[sb, "fill_by_close"].mean() - sub.loc[sc, "fill_by_close"].mean()),
            }

    signs = [np.sign(wf_fill[p]["fill_diff"]) for p in ["train","val","holdout"] if wf_fill[p]["fill_diff"] is not None]
    n_pos = sum(s > 0 for s in signs)
    wf_consistency = "consistent" if n_pos == 3 else ("mixed" if n_pos == 2 else "inconsistent")

    # Phase 1 comparison (EOD fill proxy was: dist_to_prev < dist_to_open)
    # We report the corrected fill rates for reference
    phase1_comparison = {
        "phase1_fill_rate_backw": 0.404,
        "phase1_fill_rate_cont": 0.272,
        "phase1_diff": 0.132,
        "phase2_fill_rate_backw": round(fill_rate_backw, 4),
        "phase2_fill_rate_cont": round(fill_rate_cont, 4),
        "phase2_diff": round(diff_fill, 4),
        "definition_change": "Phase 1 used dist_to_prev < dist_to_open (EOD proxy). Phase 2 uses 1m touch/cross of prior session close.",
    }

    # Verdict
    if diff_fill > 0.08 and p_boot < 0.10 and n_pos >= 2:
        verdict = "supported"
        reason = f"fill_diff={diff_fill:.3f} > 0.08, p_boot={p_boot:.4f}, {wf_consistency}"
    elif diff_fill <= 0:
        verdict = "rejected"
        reason = f"fill_diff={diff_fill:.3f} ≤ 0 (corrected definition reversed Phase 1 result)"
    else:
        verdict = "inconclusive"
        reason = f"fill_diff={diff_fill:.3f}, p_boot={p_boot:.4f}, p_fisher={p_fisher:.4f}, {wf_consistency}"

    result = {
        "hypothesis_number": "H76",
        "hypothesis_title": "Gap Days in Backwardation Fill More Frequently Than in Contango",
        "classification": "hybrid",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "n_total_gap_days": n_total,
        "n_backwardation": n_backw,
        "n_contango": n_cont,
        "fill_by_close": {
            "fill_rate_backw": round(fill_rate_backw, 4),
            "fill_rate_cont": round(fill_rate_cont, 4),
            "diff": round(diff_fill, 4),
            "p_fisher": round(p_fisher, 4),
            "p_bootstrap": round(p_boot, 4),
            "ci_95_boot": [round(x, 4) for x in ci_boot],
        },
        "fill_by_1130": {
            "fill_rate_backw": round(fill1130_backw, 4),
            "fill_rate_cont": round(fill1130_cont, 4),
            "diff": round(diff_1130, 4),
        },
        "time_to_fill_mw": ttf_mw,
        "first_2h_range_mw": range_mw,
        "segmentation_direction_x_regime": seg_table,
        "gap_size_control": size_table,
        "walk_forward_fill_diff": wf_fill,
        "walk_forward_consistency": wf_consistency,
        "n_positive_splits": int(n_pos),
        "phase1_vs_phase2_comparison": phase1_comparison,
        "phase1_alignment": "confirmed" if verdict == "supported" else ("weakened" if diff_fill > 0 else "contradicted"),
        "notes": "Fill defined as: for gap-up, any 1m bar low ≤ prev_session_last_1m_close; for gap-down, any high ≥ prev_close.",
    }
    _save(result, "H76_b2")
    return result


# ── H96 — Forward Vol Inversion → Multi-Session Range ─────────────────────────

def run_h96(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H96_b2.json"
    if out_path.exists() and not force:
        print("  H96: cached"); return json.loads(out_path.read_text())

    print("  H96: running...")

    df = daily[["high", "low", "close", "iv_30d", "iv_60d"]].copy()
    df.index = pd.to_datetime(df.index)
    df["daily_range"] = (df["high"] - df["low"]) / df["close"]

    # Forward vol signal
    df["fwd_vol"] = np.sqrt(np.maximum(
        (df["iv_60d"]**2 * 60 - df["iv_30d"]**2 * 30) / 30, 1e-8
    ))
    df["fwd_ratio"] = df["fwd_vol"] / df["iv_30d"]
    df["fwd_inverted"] = df["fwd_ratio"] < 1.0

    # H44 slope (for redundancy test)
    df["h44_slope"] = df["iv_30d"] / df["iv_60d"]
    df["in_backwardation"] = df["iv_30d"] > df["iv_60d"]

    # Outcomes — verified forward alignment:
    # range_5d_fwd[t] = mean(range[t+1..t+5]) via rolling(5).mean().shift(-5) ✓
    df["range_5d_fwd"] = df["daily_range"].rolling(5).mean().shift(-5)
    df["next_1d_range"] = df["daily_range"].shift(-1)
    df["next_2d_range"] = df["daily_range"].rolling(2).mean().shift(-2)

    # Intraday: first 120m from feats (next session)
    feats_idx = feats[["range_120m"]].copy()
    feats_idx.index = pd.to_datetime(feats_idx.index)
    df = df.join(feats_idx.shift(-1).rename(columns={"range_120m": "next_120m"}), how="left")

    # Direction agreement: H96 vs H44
    agree = (df["fwd_inverted"] == df["in_backwardation"])
    agreement_rate = float(agree.mean())

    # --- Continuous Spearman on primary outcome (5d forward range) ---
    wf_5d = walk_forward_spearman(
        df.dropna(subset=["fwd_ratio", "range_5d_fwd"]), "fwd_ratio", "range_5d_fwd"
    )
    wf_1d = walk_forward_spearman(
        df.dropna(subset=["fwd_ratio", "next_1d_range"]), "fwd_ratio", "next_1d_range"
    )

    # --- Binary MW (replication) ---
    df["mask_inv"] = df["fwd_inverted"]
    wf_bin = walk_forward_mw(df.dropna(subset=["range_5d_fwd"]), "mask_inv", "range_5d_fwd")

    # --- Quintile gradient ---
    valid = df["fwd_ratio"].notna() & df["range_5d_fwd"].notna()
    df.loc[valid, "fwd_quintile"] = pd.qcut(
        df.loc[valid, "fwd_ratio"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop"
    ).astype(float)
    quintile_medians = {}
    for q in [1, 2, 3, 4, 5]:
        sub = df.loc[df.get("fwd_quintile", pd.Series()) == q, "range_5d_fwd"].dropna()
        quintile_medians[f"Q{q}"] = {"n": int(len(sub)), "median_5d_range": float(np.median(sub)) if len(sub) else None}

    # --- MANDATORY H44 REDUNDANCY TEST ---
    ctrl = df.dropna(subset=["fwd_ratio", "range_5d_fwd", "h44_slope"])

    # Test 1: Partial Spearman (H96 | H44)
    partial_vs_h44 = partial_spearman(
        ctrl["fwd_ratio"].values,
        ctrl["range_5d_fwd"].values,
        ctrl["h44_slope"].values,
    )

    # Test 2: Nested OLS/HAC
    nested_result = {"model_A": None, "model_B": None, "h96_beta_p": None}
    if HAS_SM and len(ctrl) >= 30:
        y = ctrl["range_5d_fwd"].values
        x_h44 = ctrl["h44_slope"].values
        x_h96 = ctrl["fwd_ratio"].values
        X_A = sm.add_constant(x_h44)
        X_B = sm.add_constant(np.column_stack([x_h44, x_h96]))
        try:
            m_A = sm.OLS(y, X_A).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
            m_B = sm.OLS(y, X_B).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
            nested_result = {
                "model_A_r2": float(m_A.rsquared),
                "model_B_r2": float(m_B.rsquared),
                "h96_beta": float(m_B.params[-1]),
                "h96_beta_tstat": float(m_B.tvalues[-1]),
                "h96_beta_p": float(m_B.pvalues[-1]),
                "h44_beta_in_B": float(m_B.params[1]),
            }
        except Exception as e:
            nested_result = {"error": str(e)}

    # Test 3: Direction agreement
    redundancy_conclusion = "unknown"
    p_partial = partial_vs_h44.get("partial_p") or 1.0
    partial_rho = abs(partial_vs_h44.get("partial_rho") or 0)
    h96_beta_p = nested_result.get("h96_beta_p") or 1.0
    if agreement_rate > 0.90:
        redundancy_conclusion = "H96 REDUNDANT with H44: agreement_rate={:.1%} — signals nearly identical in practice".format(agreement_rate)
    elif partial_rho < 0.05 or p_partial > 0.20:
        redundancy_conclusion = "H96 REDUNDANT with H44: partial_rho={:.3f}, p_partial={:.3f} — no incremental contribution".format(
            partial_vs_h44.get("partial_rho") or 0, p_partial)
    elif h96_beta_p > 0.10:
        redundancy_conclusion = "H96 REDUNDANT with H44: H96 beta not significant in nested model (p={:.3f})".format(h96_beta_p)
    else:
        redundancy_conclusion = "H96 DISTINCT from H44: partial_rho={:.3f} (p={:.3f}), H96 beta p={:.3f}, agreement={:.1%}".format(
            partial_vs_h44.get("partial_rho") or 0, p_partial, h96_beta_p, agreement_rate)

    passed_redundancy_gate = "REDUNDANT" not in redundancy_conclusion

    # Verdict
    full_sp = wf_5d["splits"]["full"]
    rho = full_sp.get("rho") or 0
    p_nw = full_sp.get("p_nw") or 1
    n_pos = wf_5d.get("n_positive_splits", 0)

    if not passed_redundancy_gate:
        verdict = "inconclusive"
        reason = f"Redundancy gate failed: {redundancy_conclusion}"
    elif rho < 0 or p_nw > 0.30:
        verdict = "rejected"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}"
    elif rho > 0.10 and p_nw < 0.05 and n_pos >= 2 and passed_redundancy_gate:
        verdict = "supported"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}, {wf_5d['consistency']}, redundancy gate passed"
    else:
        verdict = "inconclusive"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}, {wf_5d['consistency']}"

    result = {
        "hypothesis_number": "H96",
        "hypothesis_title": "Forward Vol Inversion (30→60d) Predicts Larger Multi-Session Range",
        "classification": "eod_primary",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "n_inverted": int(df["fwd_inverted"].sum()),
        "n_normal": int((~df["fwd_inverted"]).sum()),
        "pct_inverted": float(df["fwd_inverted"].mean()),
        "h44_agreement_rate": round(agreement_rate, 4),
        "spearman_5d_wf": wf_5d,
        "spearman_1d_wf": wf_1d,
        "binary_mw_5d_wf": wf_bin,
        "quintile_gradient": quintile_medians,
        "mandatory_h44_redundancy_test": {
            "partial_spearman_h96_given_h44": partial_vs_h44,
            "nested_ols_hac": nested_result,
            "direction_agreement_rate": round(agreement_rate, 4),
            "conclusion": redundancy_conclusion,
            "passed_gate": passed_redundancy_gate,
        },
        "phase1_alignment": "confirmed" if verdict == "supported" else "subsumed_or_inconclusive",
        "notes": "range_5d_fwd verified: rolling(5).mean().shift(-5) = mean(range[t+1..t+5]). H44 redundancy gate mandatory before verdict.",
    }
    _save(result, "H96_b2")
    return result


# ── H99 — EOD Spread → Next-Session Range ─────────────────────────────────────

def run_h99(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H99_b2.json"
    if out_path.exists() and not force:
        print("  H99: cached"); return json.loads(out_path.read_text())

    print("  H99: running...")

    df = daily[["high", "low", "close", "bid", "ask", "hv_20_cc", "iv_30d", "iv_60d"]].copy()
    df.index = pd.to_datetime(df.index)
    df["daily_range"] = (df["high"] - df["low"]) / df["close"]
    df["prior_range"] = df["daily_range"].shift(1)
    df["h44_slope"] = df["iv_30d"] / df["iv_60d"]

    # Signal: 3 spread versions
    df["spread_pct"] = (df["ask"] - df["bid"]) / df["close"]
    df["spread_rank"] = df["spread_pct"].rolling(60, min_periods=20).rank(pct=True)
    df["spread_zscore"] = (
        (df["spread_pct"] - df["spread_pct"].rolling(60, min_periods=20).mean())
        / df["spread_pct"].rolling(60, min_periods=20).std()
    )

    # Primary outcome (FIXED): clean next-day range, no smoothing
    df["next_day_range"] = df["daily_range"].shift(-1)

    # Intraday robustness outcomes from feats (next session)
    feats_idx = feats[["range_30m", "range_60m", "range_120m"]].copy()
    feats_idx.index = pd.to_datetime(feats_idx.index)
    df = df.join(feats_idx.shift(-1).rename(columns={
        "range_30m": "next_30m", "range_60m": "next_60m", "range_120m": "next_120m"
    }), how="left")

    # Reference (contaminated): Phase 1 outcome — NOT used in verdict
    df["phase1_proxy_contaminated"] = df["hv_20_cc"].shift(-1)

    # --- Primary Spearman: spread_rank → next_day_range ---
    wf_rank_next = walk_forward_spearman(
        df.dropna(subset=["spread_rank", "next_day_range"]), "spread_rank", "next_day_range"
    )

    # --- Contamination side-by-side ---
    contamination_table = {
        "phase1_outcome_hv20_shift1": {
            "outcome_description": "hv_20_cc.shift(-1) — 20-day smoothed HV, incorporates returns t-18..t+1 (CONTAMINATED)",
            "spearman": nw_spearman(
                df["spread_rank"].values, df["phase1_proxy_contaminated"].values
            ),
        },
        "phase2_outcome_next_day_range": {
            "outcome_description": "next_day_range = (high-low)/close shift(-1) — clean next-session observation",
            "spearman": wf_rank_next["splits"]["full"],
        },
    }

    # --- Binary MW (top 20% vs bottom 20%) ---
    df["high_spread"] = df["spread_rank"] > 0.80
    df["low_spread"] = df["spread_rank"] < 0.20
    df_binary = df.loc[df["high_spread"] | df["low_spread"]].copy()
    df_binary["mask_a"] = df_binary["high_spread"]
    wf_bin = walk_forward_mw(df_binary.dropna(subset=["next_day_range"]), "mask_a", "next_day_range")

    # --- Intraday expression ---
    intraday_spearman = {}
    for col in ["next_30m", "next_60m", "next_120m"]:
        sub = df.dropna(subset=["spread_rank", col])
        intraday_spearman[col] = nw_spearman(sub["spread_rank"].values, sub[col].values)

    # --- Incremental value: partial Spearman after controls ---
    ctrl = df.dropna(subset=["spread_rank", "next_day_range", "iv_30d", "prior_range"])
    partial_vs_iv30 = partial_spearman(
        ctrl["spread_rank"].values, ctrl["next_day_range"].values, ctrl["iv_30d"].values
    )
    partial_vs_prior_range = partial_spearman(
        ctrl["spread_rank"].values, ctrl["next_day_range"].values, ctrl["prior_range"].values
    )

    # OLS/HAC multivariate
    ols_result = {}
    if HAS_SM and len(ctrl) >= 30:
        y = ctrl["next_day_range"].values
        X = sm.add_constant(ctrl[["spread_rank", "iv_30d", "prior_range"]].values)
        try:
            m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
            ols_result = {
                "r2": float(m.rsquared),
                "spread_rank_beta": float(m.params[1]),
                "spread_rank_p": float(m.pvalues[1]),
                "iv30d_beta": float(m.params[2]),
                "prior_range_beta": float(m.params[3]),
            }
        except Exception as e:
            ols_result = {"error": str(e)}

    # Verdict
    full_sp = wf_rank_next["splits"]["full"]
    rho = full_sp.get("rho") or 0
    p_nw = full_sp.get("p_nw") or 1
    n_pos = wf_rank_next.get("n_positive_splits", 0)
    p_partial_iv = partial_vs_iv30.get("partial_p") or 1.0

    if rho > 0.10 and p_nw < 0.05 and n_pos >= 2 and p_partial_iv < 0.10:
        verdict = "supported"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}, partial_p_vs_iv30={p_partial_iv:.4f}, {wf_rank_next['consistency']}"
    elif rho < 0 or p_nw > 0.30:
        verdict = "rejected"
        reason = (f"rho={rho:.3f} on corrected next_day_range outcome (vs Phase 1 used contaminated hv_20_cc). "
                  f"p_nw={p_nw:.4f}")
    else:
        verdict = "inconclusive"
        reason = f"rho={rho:.3f}, p_nw={p_nw:.4f}, partial_p_vs_iv30={p_partial_iv:.4f}, {wf_rank_next['consistency']}"

    result = {
        "hypothesis_number": "H99",
        "hypothesis_title": "EOD Bid-Ask Spread Percentile → Next-Session Range",
        "classification": "hybrid",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "CONTAMINATION_WARNING": (
            "Phase 1 used hv_20_cc.shift(-1) which incorporates returns from days t-18 to t+1. "
            "Phase 1 SUPPORTED verdict is almost certainly a false positive due to regime smoothing. "
            "Phase 2 uses next_day_range = (high-low)/close shift(-1) as the clean outcome. "
            "A REJECTED verdict here is expected and informative, not a design failure."
        ),
        "contamination_side_by_side": contamination_table,
        "primary_spearman_wf": wf_rank_next,
        "binary_mw_top_vs_bottom_20pct": wf_bin,
        "intraday_expression": intraday_spearman,
        "partial_spearman_vs_iv30d": partial_vs_iv30,
        "partial_spearman_vs_prior_range": partial_vs_prior_range,
        "multivariate_ols_hac": ols_result,
        "phase1_alignment": "corrected" if verdict in ("rejected","inconclusive") else "confirmed",
        "notes": "Primary outcome: next_day_range (clean). hv_5_cc_fwd omitted (shift alignment risk). hv_20_cc stored as phase1_proxy_contaminated reference only.",
    }
    _save(result, "H99_b2")
    return result


# ── Vault markdown export ─────────────────────────────────────────────────────

_BADGE = {
    "supported": "✅ SUPPORTED",
    "rejected": "❌ REJECTED",
    "inconclusive": "⚠️ INCONCLUSIVE",
    "insufficient_data": "⛔ INSUFFICIENT DATA",
    "blocked": "🔒 BLOCKED",
}


def export_vault_note(r: dict) -> None:
    hnum = r["hypothesis_number"]
    title = r["hypothesis_title"]
    verdict = r["phase2_verdict"]
    reason = r.get("phase2_verdict_reason", "")
    cls = r.get("classification", "?")
    p1 = r.get("phase1_alignment", "?")

    lines = [
        f"# {hnum} — Phase 2 Batch 2 Intraday Robustness",
        "",
        f"**Hypothesis:** {title}",
        f"**Classification:** {cls}",
        f"**Phase 2 Verdict:** {_BADGE.get(verdict, verdict.upper())}",
        f"**Reason:** {reason}",
        f"**Phase 1 Alignment:** {p1}",
        "",
    ]

    if "CONTAMINATION_WARNING" in r:
        lines += [f"> ⚠️ **{r['CONTAMINATION_WARNING']}**", ""]

    if "contamination_side_by_side" in r:
        lines += ["## Contamination Side-by-Side (H99)", ""]
        for k, v in r["contamination_side_by_side"].items():
            sp = v.get("spearman", {})
            rho = sp.get("rho"); p = sp.get("p_nw")
            rho_s = f"{rho:.3f}" if rho is not None else "n/a"
            p_s = f"{p:.4f}" if p is not None else "n/a"
            lines.append(f"- **{k}**: {v.get('outcome_description', '')} → rho={rho_s}, p_nw={p_s}")
        lines.append("")

    if "mandatory_h44_redundancy_test" in r:
        rt = r["mandatory_h44_redundancy_test"]
        lines += [
            "## H44 Redundancy Test (H96 — Mandatory Gate)",
            "",
            f"**Conclusion:** {rt.get('conclusion', '?')}",
            f"**Gate passed:** {rt.get('passed_gate', '?')}",
            f"**Direction agreement rate (H96 vs H44):** {rt.get('direction_agreement_rate', '?'):.1%}",
            "",
        ]
        ps = rt.get("partial_spearman_h96_given_h44", {})
        lines.append(f"- Partial Spearman (H96 | H44): rho={ps.get('partial_rho','?')}, p={ps.get('partial_p','?')}")
        nm = rt.get("nested_ols_hac", {})
        if "h96_beta_p" in nm:
            lines.append(f"- Nested OLS HAC: H96 beta p={nm['h96_beta_p']:.4f}, R²_A={nm.get('model_A_r2','?'):.4f} → R²_B={nm.get('model_B_r2','?'):.4f}")
        lines.append("")

    for wf_key in ["spearman_5d_wf", "spearman_1d_wf", "primary_spearman_wf", "continuous_spearman_wf"]:
        if wf_key not in r:
            continue
        wf = r[wf_key]
        lines += [f"## Walk-Forward Spearman ({wf_key})", "", "| Split | rho | p_nw | n |", "|---|---|---|---|"]
        for split, s in wf.get("splits", {}).items():
            rho = s.get("rho"); p = s.get("p_nw"); n = s.get("n")
            lines.append(f"| {split} | {f'{rho:.3f}' if rho is not None else 'n/a'} | {f'{p:.4f}' if p is not None else 'n/a'} | {n} |")
        lines.append(f"**Consistency:** {wf.get('consistency','?')} ({wf.get('n_positive_splits','?')}/3)")
        lines.append("")

    for wf_key in ["binary_mw_q5_vs_rest_wf", "binary_mw_5d_wf", "binary_mw_top_vs_bottom_20pct"]:
        if wf_key not in r:
            continue
        wf = r[wf_key]
        lines += [f"## Walk-Forward MW ({wf_key})", "", "| Split | diff | p | cliff_d | n_a | n_b |", "|---|---|---|---|---|---|"]
        for split, s in wf.get("splits", {}).items():
            diff = s.get("diff"); p = s.get("p"); cd = s.get("cliff_d")
            na = s.get("n_a"); nb = s.get("n_b")
            def _f(v, fmt): return fmt.format(v) if v is not None else "n/a"
            lines.append(f"| {split} | {_f(diff,'{:.4f}')} | {_f(p,'{:.4f}')} | {_f(cd,'{:.3f}')} | {na} | {nb} |")
        lines.append(f"**Consistency:** {wf.get('consistency','?')} ({wf.get('n_positive_splits','?')}/3)")
        lines.append("")

    if "quintile_gradient" in r:
        lines += ["## Quintile Gradient", "", "| Quintile | n | Median Outcome |", "|---|---|---|"]
        for k, v in r["quintile_gradient"].items():
            m = v.get("median_next_range") or v.get("median_5d_range")
            lines.append(f"| {k} | {v['n']} | {f'{m:.4f}' if m is not None else 'n/a'} |")
        lines.append("")

    if "phase1_vs_phase2_comparison" in r:
        cmp = r["phase1_vs_phase2_comparison"]
        lines += [
            "## Phase 1 vs Phase 2 Fill Rate Comparison (H76)",
            "",
            f"| | Backwardation | Contango | Diff |",
            "|---|---|---|---|",
            f"| Phase 1 (EOD proxy) | {cmp['phase1_fill_rate_backw']:.3f} | {cmp['phase1_fill_rate_cont']:.3f} | {cmp['phase1_diff']:.3f} |",
            f"| Phase 2 (1m intraday) | {cmp['phase2_fill_rate_backw']:.3f} | {cmp['phase2_fill_rate_cont']:.3f} | {cmp['phase2_diff']:.3f} |",
            "",
            f"> {cmp['definition_change']}",
            "",
        ]

    out_path = VAULT_DIR / f"{hnum}_b2.md"
    out_path.write_text("\n".join(lines))


def export_batch_summary(results: list[dict]) -> None:
    lines = [
        "# Phase 2 Batch 2 Summary",
        "",
        f"**Run date:** {date.today().isoformat()}",
        f"**Batch:** H58 (blocked), H70, H76, H96, H99",
        "",
        "| H# | Classification | Verdict | Phase 1 Alignment |",
        "|---|---|---|---|",
    ]
    for r in results:
        hnum = r["hypothesis_number"]
        cls = r.get("classification", "?")
        v = _BADGE.get(r["phase2_verdict"], r["phase2_verdict"].upper())
        p1 = r.get("phase1_alignment", "?")
        lines.append(f"| {hnum} | {cls} | {v} | {p1} |")

    summary = {
        "run_date": date.today().isoformat(),
        "batch": ["H58", "H70", "H76", "H96", "H99"],
        "verdicts": {r["hypothesis_number"]: r["phase2_verdict"] for r in results},
        "n_supported": sum(r["phase2_verdict"] == "supported" for r in results),
        "n_rejected": sum(r["phase2_verdict"] == "rejected" for r in results),
        "n_inconclusive": sum(r["phase2_verdict"] == "inconclusive" for r in results),
        "n_blocked": sum(r["phase2_verdict"] == "blocked" for r in results),
    }
    (RESULTS_DIR / "batch2_summary.json").write_text(json.dumps(summary, indent=2))
    (VAULT_DIR / "_batch2_summary.md").write_text("\n".join(lines))


# ── Main ──────────────────────────────────────────────────────────────────────

ALL = ["H58", "H70", "H76", "H96", "H99"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default=",".join(ALL))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    targets = [h.strip().upper() for h in args.hypotheses.split(",")]
    print(f"\nPhase 2 Batch 2: {targets}\n")

    needs_1m = bool(set(targets) & {"H70", "H76", "H99"})
    bars_1m = None
    feats = None

    if needs_1m:
        print("Loading 1m bars...")
        bars_1m = load_all_1m()
        print(f"  {len(bars_1m):,} bars ({bars_1m.index[0].date()} → {bars_1m.index[-1].date()})")
        print("  Building daily intraday features...")
        feats = build_daily_intraday_features(bars_1m)
        feats.index = pd.to_datetime(feats.index)
        print(f"  {len(feats)} trading days")
    elif set(targets) & {"H96"}:
        # H96 needs feats for 120m, build from 1m
        print("Loading 1m bars for H96 intraday expression...")
        bars_1m = load_all_1m()
        feats = build_daily_intraday_features(bars_1m)
        feats.index = pd.to_datetime(feats.index)

    daily = load_daily()

    runner_map = {
        "H58": lambda f: run_h58(f),
        "H70": lambda f: run_h70(feats, daily, f),
        "H76": lambda f: run_h76(bars_1m, daily, f),
        "H96": lambda f: run_h96(feats, daily, f),
        "H99": lambda f: run_h99(feats, daily, f),
    }

    results = []
    for hnum in targets:
        if hnum not in runner_map:
            print(f"  {hnum}: unknown"); continue
        r = runner_map[hnum](args.force)
        results.append(r)
        print(f"  {hnum}: {r['phase2_verdict'].upper()} — {str(r.get('phase2_verdict_reason',''))[:90]}")
        export_vault_note(r)

    if len(results) > 1:
        export_batch_summary(results)
        print(f"\nSummary → {RESULTS_DIR / 'batch2_summary.json'}")

    print("\nDone.")


if __name__ == "__main__":
    main()
