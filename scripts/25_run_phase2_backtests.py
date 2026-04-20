"""
Phase 2 intraday robustness backtests.

Batch: H15, H24, H44, H48, H53, H73, H94, H97, H100
Walk-forward: train=2024, val=2025, holdout=2026-Q1

Output:
  experiments/phase2_results/H{N}.json   — per hypothesis
  experiments/phase2_results/batch_summary.json
  vault/Phase2/H{N}.md
  vault/Phase2/_batch_summary.md

Usage:
  python scripts/25_run_phase2_backtests.py
  python scripts/25_run_phase2_backtests.py --hypotheses H15,H44
  python scripts/25_run_phase2_backtests.py --hypotheses H100 --force
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr, wilcoxon

try:
    import statsmodels.api as sm  # type: ignore
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
DAILY_SERIES = BASE / "data" / "processed" / "daily_series.parquet"
IVX_FILE = BASE / "data" / "raw" / "qqq_ivx.parquet"
RESULTS_DIR = BASE / "experiments" / "phase2_results"
VAULT_DIR = BASE / "vault" / "Phase2"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

# ── Walk-forward windows ───────────────────────────────────────────────────────

TRAIN_START = "2024-01-01"
TRAIN_END = "2024-12-31"
VAL_START = "2025-01-01"
VAL_END = "2025-12-31"
HOLDOUT_START = "2026-01-01"
HOLDOUT_END = "2026-03-31"
FULL_START = "2024-01-01"
FULL_END = "2026-03-31"

_ET = "America/New_York"

# ── Data loading ──────────────────────────────────────────────────────────────

def load_all_1m() -> pd.DataFrame:
    """Concat all 1m monthly parquets into one tz-aware DataFrame."""
    files = sorted(DATABENTO_DIR.glob("qqq_1m_*.parquet"))
    if not files:
        raise FileNotFoundError(f"No 1m parquets in {DATABENTO_DIR}")
    parts = [pd.read_parquet(f) for f in files]
    df = pd.concat(parts).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def load_all_5m() -> pd.DataFrame:
    files = sorted(DATABENTO_DIR.glob("qqq_5m_*.parquet"))
    if not files:
        raise FileNotFoundError(f"No 5m parquets in {DATABENTO_DIR}")
    parts = [pd.read_parquet(f) for f in files]
    df = pd.concat(parts).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def load_daily() -> pd.DataFrame:
    df = pd.read_parquet(DAILY_SERIES)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


def load_ivx() -> pd.DataFrame:
    df = pd.read_parquet(IVX_FILE)[["date", "7d IV Mean", "30d IV Call", "30d IV Put"]]
    df = df.rename(columns={
        "7d IV Mean": "iv_7d",
        "30d IV Call": "iv_call_30d",
        "30d IV Put": "iv_put_30d",
    })
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


# ── Intraday feature builder ───────────────────────────────────────────────────

def _rv_annualized(closes: pd.Series, n_bars_per_day: int = 390) -> float:
    """Annualized realized vol from a sequence of 1m close prices (within-session only)."""
    if len(closes) < 2:
        return np.nan
    log_rets = np.log(closes.values[1:] / closes.values[:-1])
    return float(np.sqrt(n_bars_per_day * 252 * np.mean(log_rets ** 2)))


def build_daily_intraday_features(bars_1m: pd.DataFrame) -> pd.DataFrame:
    """
    Build one row per trading day with intraday range and RV features.

    Columns returned (date as index):
      first_open      — 9:30 bar open
      last_close      — 15:59 bar close
      gap_pct_1m      — |first_open / prev_day_last_close - 1| (set at next-day row)
      range_30m       — (max_high - min_low) / last_close for 9:30-09:59
      range_60m       — 9:30-10:29
      range_120m      — 9:30-11:29
      range_150m      — 9:30-12:29
      range_afternoon — 12:30-15:59
      range_session   — full session
      fh_rv           — first-hour (9:30-10:29) annualized RV from 1m closes
      late_rv         — last-30-min (15:30-15:59) annualized RV
      fd_rv           — full-day annualized RV
    """
    rows = []
    dates = sorted(set(bars_1m.index.date))

    for d in dates:
        mask = bars_1m.index.date == d
        day = bars_1m.loc[mask]
        if day.empty:
            continue

        # Full session
        sess_high = day["high"].max()
        sess_low = day["low"].min()
        last_close = day["close"].iloc[-1]
        first_open = day["open"].iloc[0]

        def range_window(start_time: str, end_time: str) -> float:
            sub = day.between_time(start_time, end_time)
            if sub.empty:
                return np.nan
            return float((sub["high"].max() - sub["low"].min()) / last_close)

        # RV helpers
        fh = day.between_time("09:30", "10:29")
        late = day.between_time("15:30", "15:59")

        rows.append({
            "date": pd.Timestamp(d),
            "first_open": float(first_open),
            "last_close": float(last_close),
            "range_30m": range_window("09:30", "09:59"),
            "range_60m": range_window("09:30", "10:29"),
            "range_120m": range_window("09:30", "11:29"),
            "range_150m": range_window("09:30", "12:29"),
            "range_afternoon": range_window("12:30", "15:59"),
            "range_session": float((sess_high - sess_low) / last_close),
            "fh_rv": _rv_annualized(fh["close"]),
            "late_rv": _rv_annualized(late["close"]),
            "fd_rv": _rv_annualized(day["close"]),
        })

    feat = pd.DataFrame(rows).set_index("date")

    # gap_pct_1m: |this day's first_open / prev day's last_close - 1|
    feat["gap_pct_1m"] = (
        feat["first_open"] / feat["last_close"].shift(1) - 1
    ).abs()

    return feat


# ── Statistical utilities ──────────────────────────────────────────────────────

def cliff_delta(g1: np.ndarray, g2: np.ndarray) -> float:
    """Cliff's delta effect size."""
    g1, g2 = np.asarray(g1, float), np.asarray(g2, float)
    n1, n2 = len(g1), len(g2)
    if n1 == 0 or n2 == 0:
        return np.nan
    dom = int((g1[:, None] > g2[None, :]).sum()) - int((g1[:, None] < g2[None, :]).sum())
    return dom / (n1 * n2)


def _circular_block_sample(rng: np.random.Generator, n: int, block: int) -> np.ndarray:
    """Return indices of a circular block bootstrap sample of length n."""
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=n_blocks)
    idx = []
    for s in starts:
        idx.extend([(s + k) % n for k in range(block)])
    return np.array(idx[:n])


def block_bootstrap_median_diff(
    signal: np.ndarray,
    outcome: np.ndarray,
    mask_a: np.ndarray,
    mask_b: np.ndarray,
    n_boot: int = 2000,
    block: int = 5,
    seed: int = 42,
) -> tuple[float, float, tuple[float, float]]:
    """
    Bootstrap p-value and 95% CI for median(outcome[a]) - median(outcome[b]).
    Resamples (signal, outcome) pairs in blocks to respect serial dependence.
    Returns (observed_diff, p_value_greater, (ci_lo, ci_hi))
    """
    rng = np.random.default_rng(seed)
    n = len(outcome)
    observed = float(np.median(outcome[mask_a]) - np.median(outcome[mask_b]))

    diffs = []
    for _ in range(n_boot):
        idx = _circular_block_sample(rng, n, block)
        bo = outcome[idx]
        bma = mask_a[idx]
        bmb = mask_b[idx]
        if bma.sum() > 1 and bmb.sum() > 1:
            diffs.append(float(np.median(bo[bma]) - np.median(bo[bmb])))

    diffs_arr = np.array(diffs)
    p_greater = float((diffs_arr <= 0).mean())  # fraction of bootstraps ≤ 0 when we claim >0
    ci_lo, ci_hi = float(np.percentile(diffs_arr, 2.5)), float(np.percentile(diffs_arr, 97.5))
    return observed, p_greater, (ci_lo, ci_hi)


def newey_west_spearman(x: np.ndarray, y: np.ndarray, max_lag: int = 5) -> dict:
    """Spearman correlation with Newey-West HAC standard errors via ranked OLS."""
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 20:
        return {"rho": np.nan, "p_nw": np.nan, "n": n}

    # Rank transform
    from scipy.stats import rankdata
    rx = rankdata(x) / n
    ry = rankdata(y) / n

    if HAS_STATSMODELS:
        X = sm.add_constant(rx)
        model = sm.OLS(ry, X).fit(cov_type="HAC", cov_kwds={"maxlags": max_lag})
        rho, _ = spearmanr(x, y)
        p_nw = float(model.pvalues[1])
    else:
        rho, p_nw = spearmanr(x, y)

    return {"rho": float(rho), "p_nw": float(p_nw), "n": int(n)}


def mw_test(g1: np.ndarray, g2: np.ndarray, alternative: str = "greater") -> dict:
    """Mann-Whitney U test with effect size."""
    g1, g2 = np.asarray(g1, float), np.asarray(g2, float)
    g1, g2 = g1[np.isfinite(g1)], g2[np.isfinite(g2)]
    if len(g1) < 5 or len(g2) < 5:
        return {"n_a": len(g1), "n_b": len(g2), "stat": np.nan, "p": np.nan, "cliff_d": np.nan,
                "median_a": np.nan, "median_b": np.nan, "diff": np.nan}
    stat, p = mannwhitneyu(g1, g2, alternative=alternative)
    return {
        "n_a": int(len(g1)),
        "n_b": int(len(g2)),
        "stat": float(stat),
        "p": float(p),
        "cliff_d": cliff_delta(g1, g2),
        "median_a": float(np.median(g1)),
        "median_b": float(np.median(g2)),
        "diff": float(np.median(g1) - np.median(g2)),
    }


# ── Walk-forward helper ───────────────────────────────────────────────────────

def split_by_period(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split DataFrame (date-indexed) into train/val/holdout/full."""
    return {
        "full":    df.loc[FULL_START:FULL_END],
        "train":   df.loc[TRAIN_START:TRAIN_END],
        "val":     df.loc[VAL_START:VAL_END],
        "holdout": df.loc[HOLDOUT_START:HOLDOUT_END],
    }


def walk_forward_mw(
    df: pd.DataFrame,
    group_a_mask_col: str,
    outcome_col: str,
    alternative: str = "greater",
) -> dict:
    """Run MW test on each walk-forward split and assess consistency."""
    splits = split_by_period(df)
    results = {}
    signs = []
    for name, sub in splits.items():
        sub_clean = sub[[group_a_mask_col, outcome_col]].dropna()
        ga = sub_clean.loc[sub_clean[group_a_mask_col], outcome_col].values
        gb = sub_clean.loc[~sub_clean[group_a_mask_col], outcome_col].values
        r = mw_test(ga, gb, alternative)
        results[name] = r
        if name != "full" and not np.isnan(r["diff"]):
            signs.append(np.sign(r["diff"]))

    n_positive = sum(s > 0 for s in signs)
    consistency = "consistent" if n_positive == 3 else ("mixed" if n_positive == 2 else "inconsistent")
    return {"splits": results, "consistency": consistency, "n_positive_splits": int(n_positive)}


def _verdict(full: dict, wf: dict, support_thresh: float, reject_thresh: float,
             p_thresh_support: float = 0.10, p_thresh_reject: float = 0.30,
             min_n: int = 20) -> tuple[str, str]:
    diff = full.get("diff", np.nan)
    p = full.get("p", np.nan)
    n_a = full.get("n_a", 0)
    n_b = full.get("n_b", 0)
    if min(n_a, n_b) < min_n:
        return "insufficient_data", f"n_a={n_a}, n_b={n_b} below minimum {min_n}"
    if np.isnan(diff) or np.isnan(p):
        return "inconclusive", "insufficient valid data"
    if diff > support_thresh and p < p_thresh_support and wf.get("n_positive_splits", 0) >= 2:
        return "supported", f"diff={diff:.4f} > {support_thresh}, p={p:.4f} < {p_thresh_support}, {wf['consistency']}"
    if diff <= reject_thresh or p > p_thresh_reject:
        reason = []
        if diff <= reject_thresh:
            reason.append(f"diff={diff:.4f} ≤ {reject_thresh}")
        if p > p_thresh_reject:
            reason.append(f"p={p:.4f} > {p_thresh_reject}")
        return "rejected", "; ".join(reason)
    return "inconclusive", f"diff={diff:.4f}, p={p:.4f}, {wf.get('consistency','unknown')}"


def _save(result: dict, hnum: str) -> Path:
    p = RESULTS_DIR / f"{hnum}.json"
    with open(p, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return p


# ── H15: First-Hour RV Bias ───────────────────────────────────────────────────

def run_h15(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    """
    Phase 2 test: Does first-hour RV overestimate full-day RV (positive bias)?
    Also: conditional — when fh_rv > iv_30d + 0.02, is fd_rv lower?
    """
    out_path = RESULTS_DIR / "H15.json"
    if out_path.exists() and not force:
        print("  H15: cached")
        return json.loads(out_path.read_text())

    print("  H15: running...")
    df = feats[["fh_rv", "fd_rv"]].join(daily[["iv_30d"]], how="inner").dropna()

    # Bias: mean(fh_rv - fd_rv)
    df["bias"] = df["fh_rv"] - df["fd_rv"]

    def bias_stats(sub: pd.DataFrame) -> dict:
        b = sub["bias"].dropna().values
        if len(b) < 10:
            return {"n": len(b), "mean_bias": np.nan, "pct_positive": np.nan, "p_wilcoxon": np.nan}
        try:
            _, p_w = wilcoxon(b, alternative="greater")
        except Exception:
            p_w = np.nan
        return {
            "n": int(len(b)),
            "mean_bias": float(np.mean(b)),
            "median_bias": float(np.median(b)),
            "pct_positive": float((b > 0).mean()),
            "p_wilcoxon": float(p_w),
        }

    splits = split_by_period(df)
    bias_wf = {name: bias_stats(sub) for name, sub in splits.items()}

    # Conditional: fh_rv exceeds iv_30d by > 2pp
    df["fh_exceeds_iv"] = df["fh_rv"] > (df["iv_30d"] + 0.02)
    # When fh exceeds iv, is fd_rv < fh_rv? Already true if bias > 0, but test magnitude
    cond_sub = df[df["fh_exceeds_iv"]]
    cond_bias = bias_stats(cond_sub) if len(cond_sub) >= 5 else {"n": len(cond_sub)}

    full_bias = bias_wf["full"]
    mean_b = full_bias.get("mean_bias", np.nan)
    pct_pos = full_bias.get("pct_positive", np.nan)
    p_w = full_bias.get("p_wilcoxon", np.nan)

    if full_bias.get("n", 0) < 30:
        verdict, reason = "insufficient_data", "n < 30"
    elif not np.isnan(mean_b) and mean_b > 0.02 and not np.isnan(p_w) and p_w < 0.05:
        verdict = "supported"
        reason = f"mean_bias={mean_b:.4f} > 0.02, p_wilcoxon={p_w:.4f}"
    elif not np.isnan(mean_b) and mean_b < 0:
        verdict = "rejected"
        reason = f"mean_bias={mean_b:.4f} < 0 (wrong direction)"
    else:
        verdict = "inconclusive"
        reason = f"mean_bias={mean_b:.4f}, p_wilcoxon={p_w:.4f}"

    result = {
        "hypothesis_number": "H15",
        "hypothesis_title": "First-Hour Realised Vol Predicts Full-Day Realised Vol With Positive Bias",
        "classification": "intraday_primary",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "bias_walk_forward": bias_wf,
        "conditional_fh_exceeds_iv": cond_bias,
        "phase1_alignment": "extends",
        "notes": "Phase 1 tested vol clustering (supported). Phase 2 tests the bias claim directly from 1m data.",
    }
    _save(result, "H15")
    return result


# ── H24: Late RV → Overnight Gap ─────────────────────────────────────────────

def run_h24(feats: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H24.json"
    if out_path.exists() and not force:
        print("  H24: cached")
        return json.loads(out_path.read_text())

    print("  H24: running...")
    # gap_pct_1m at row t = gap from t-1 last close to t first open
    # So signal is late_rv[t-1], outcome is gap_pct_1m[t]
    df = feats[["late_rv", "gap_pct_1m", "fd_rv"]].copy()
    df["late_rv_lag"] = df["late_rv"]               # late_rv on day t
    df["next_gap"] = df["gap_pct_1m"]               # gap on day t+1 (already shifted in feats)
    # Align: signal = late_rv[t], outcome = gap_pct_1m[t+1]
    df["late_rv_for_next"] = df["late_rv"]
    df["next_gap_out"] = df["gap_pct_1m"].shift(-1)  # shift outcome forward

    # Also compare late_rv vs fd_rv as predictors
    df["fd_rv_for_next"] = df["fd_rv"]

    def spearman_stats(sub: pd.DataFrame, x_col: str, y_col: str) -> dict:
        sub = sub[[x_col, y_col]].dropna()
        if len(sub) < 15:
            return {"n": len(sub), "rho": np.nan, "p_nw": np.nan}
        return newey_west_spearman(sub[x_col].values, sub[y_col].values)

    splits = split_by_period(df)
    late_wf = {name: spearman_stats(sub, "late_rv_for_next", "next_gap_out") for name, sub in splits.items()}
    fd_wf = {name: spearman_stats(sub, "fd_rv_for_next", "next_gap_out") for name, sub in splits.items()}

    full_late = late_wf["full"]
    full_fd = fd_wf["full"]

    rho = full_late.get("rho", np.nan)
    p = full_late.get("p_nw", np.nan)

    if full_late.get("n", 0) < 30:
        verdict, reason = "insufficient_data", "n < 30"
    elif not np.isnan(rho) and rho > 0.10 and not np.isnan(p) and p < 0.10:
        # Check if late_rv outperforms fd_rv
        rho_fd = full_fd.get("rho", 0.0) or 0.0
        verdict = "supported"
        reason = f"rho_late={rho:.3f} > 0.10, p={p:.4f}; rho_fd={rho_fd:.3f}"
    elif not np.isnan(rho) and rho < 0:
        verdict = "rejected"
        reason = f"rho_late={rho:.3f} negative"
    else:
        verdict = "inconclusive"
        reason = f"rho_late={rho:.3f}, p_nw={p:.4f}"

    result = {
        "hypothesis_number": "H24",
        "hypothesis_title": "Late-Session (15:30-16:00) RV Predicts Next-Day Overnight Gap",
        "classification": "intraday_primary",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "late_rv_spearman_wf": late_wf,
        "fd_rv_spearman_wf": fd_wf,
        "phase1_alignment": "extends",
        "notes": "Phase 1 used full-day OHLC range as proxy. Phase 2 uses actual 1m last-30-min RV and 1m gap.",
    }
    _save(result, "H24")
    return result


# ── H44: Term Structure Backwardation → Intraday Range ───────────────────────

def run_h44(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H44.json"
    if out_path.exists() and not force:
        print("  H44: cached")
        return json.loads(out_path.read_text())

    print("  H44: running...")
    eod = daily[["iv_30d", "iv_60d"]].copy()
    eod["in_backwardation"] = eod["iv_30d"] > eod["iv_60d"]

    # Join with NEXT-session intraday features
    # Signal: backwardation on day t → outcome: range on day t+1
    eod["in_backwardation_lag"] = eod["in_backwardation"]  # signal on day t
    next_feats = feats[["range_30m", "range_60m", "range_120m", "range_session"]].copy()
    next_feats.index = pd.to_datetime(next_feats.index)
    eod.index = pd.to_datetime(eod.index)

    df = eod.join(next_feats.shift(-1), how="inner")  # range features shifted backward = next day's ranges

    windows = ["range_30m", "range_60m", "range_120m", "range_session"]
    full_results = {}
    for w in windows:
        tmp = df[["in_backwardation_lag", w]].dropna()
        ga = tmp.loc[tmp["in_backwardation_lag"], w].values
        gb = tmp.loc[~tmp["in_backwardation_lag"], w].values
        full_results[w] = mw_test(ga, gb, alternative="greater")

    # Walk-forward on range_session (primary metric)
    df["mask_a"] = df["in_backwardation_lag"].fillna(False)
    wf = walk_forward_mw(df, "mask_a", "range_session")

    primary = full_results.get("range_session", {})
    verdict, reason = _verdict(
        primary, wf, support_thresh=0.003, reject_thresh=0.0, p_thresh_support=0.10, p_thresh_reject=0.30
    )

    result = {
        "hypothesis_number": "H44",
        "hypothesis_title": "IV Term Structure Backwardation → Next-Session Intraday Range",
        "classification": "hybrid",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "intraday_windows": full_results,
        "walk_forward_range_session": wf,
        "phase1_alignment": "confirmed" if verdict == "supported" else "partial",
        "notes": "Phase 1 used daily_series EOD range. Phase 2 validates against 1m intraday range windows.",
    }
    _save(result, "H44")
    return result


# ── H48: High First-Hour RV → Afternoon Range ────────────────────────────────

def run_h48(feats: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H48.json"
    if out_path.exists() and not force:
        print("  H48: cached")
        return json.loads(out_path.read_text())

    print("  H48: running...")
    df = feats[["fh_rv", "range_afternoon", "range_session"]].dropna()
    fh_median = df["fh_rv"].median()
    df["above_median_fh"] = df["fh_rv"] > fh_median

    wf_aft = walk_forward_mw(df, "above_median_fh", "range_afternoon")
    wf_sess = walk_forward_mw(df, "above_median_fh", "range_session")

    full_aft = wf_aft["splits"]["full"]
    verdict, reason = _verdict(
        full_aft, wf_aft, support_thresh=0.003, reject_thresh=0.0,
        p_thresh_support=0.10, p_thresh_reject=0.30, min_n=20
    )

    result = {
        "hypothesis_number": "H48",
        "hypothesis_title": "High First-Hour RV Predicts Larger Afternoon Session Range",
        "classification": "intraday_primary",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "full_afternoon": full_aft,
        "full_session": wf_sess["splits"]["full"],
        "walk_forward_afternoon": wf_aft,
        "walk_forward_session": wf_sess,
        "fh_rv_median": float(fh_median),
        "phase1_alignment": "extends",
        "notes": "Phase 1 stripped RP-Long conditioning. Phase 2 tests unconditional: high fh_rv → larger afternoon range.",
    }
    _save(result, "H48")
    return result


# ── H53: Pattern 4 (IV↑, RV↓) → Next-Session Range ──────────────────────────

def run_h53(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H53.json"
    if out_path.exists() and not force:
        print("  H53: cached")
        return json.loads(out_path.read_text())

    print("  H53: running...")
    # Pattern 4: iv_30d rising (5-day pct_change > 0) AND hv_20_cc flat/falling (5-day pct_change <= 0)
    eod = daily[["iv_30d", "hv_20_cc"]].copy()
    eod.index = pd.to_datetime(eod.index)
    eod["delta_iv_5d"] = eod["iv_30d"].pct_change(5)
    eod["delta_hv_5d"] = eod["hv_20_cc"].pct_change(5)
    eod["pattern4"] = (eod["delta_iv_5d"] > 0.005) & (eod["delta_hv_5d"] <= 0.005)

    # Join with next-session intraday range
    next_feats = feats[["range_session", "range_60m"]].copy()
    next_feats.index = pd.to_datetime(next_feats.index)
    df = eod.join(next_feats.shift(-1), how="inner")  # next day range

    df["mask_a"] = df["pattern4"].fillna(False)
    wf_sess = walk_forward_mw(df, "mask_a", "range_session")
    wf_60m = walk_forward_mw(df, "mask_a", "range_60m")

    primary = wf_sess["splits"]["full"]
    n_pattern4 = int(df["mask_a"].sum())

    verdict, reason = _verdict(
        primary, wf_sess, support_thresh=0.003, reject_thresh=0.0,
        p_thresh_support=0.10, p_thresh_reject=0.30, min_n=15
    )

    result = {
        "hypothesis_number": "H53",
        "hypothesis_title": "Pattern 4 (IV Rising, RV Flat) → Next-Session Range Expansion",
        "classification": "hybrid",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "n_pattern4_days": n_pattern4,
        "full_session": primary,
        "full_60m": wf_60m["splits"]["full"],
        "walk_forward_session": wf_sess,
        "phase1_alignment": "confirmed" if verdict == "supported" else "partial",
        "notes": "Pattern 4 (Passarelli): iv rising while rv flat signals hidden demand for vol. Phase 2 tests against actual intraday 1m range.",
    }
    _save(result, "H53")
    return result


# ── H73: Compound Signal (Pattern 4 + Backwardation) → Range ─────────────────

def run_h73(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H73.json"
    if out_path.exists() and not force:
        print("  H73: cached")
        return json.loads(out_path.read_text())

    print("  H73: running...")
    eod = daily[["iv_30d", "iv_60d", "hv_20_cc"]].copy()
    eod.index = pd.to_datetime(eod.index)
    eod["delta_iv_5d"] = eod["iv_30d"].pct_change(5)
    eod["delta_hv_5d"] = eod["hv_20_cc"].pct_change(5)
    eod["pattern4"] = (eod["delta_iv_5d"] > 0.005) & (eod["delta_hv_5d"] <= 0.005)
    eod["backwardation"] = eod["iv_30d"] > eod["iv_60d"]
    eod["compound"] = eod["pattern4"] & eod["backwardation"]
    eod["single_only"] = eod["pattern4"] ^ eod["backwardation"]  # XOR: exactly one active

    next_feats = feats[["range_session"]].copy()
    next_feats.index = pd.to_datetime(next_feats.index)
    df = eod.join(next_feats.shift(-1), how="inner")

    g_compound = df.loc[df["compound"].fillna(False), "range_session"].dropna().values
    g_single = df.loc[df["single_only"].fillna(False), "range_session"].dropna().values
    g_neither = df.loc[~df["compound"].fillna(False) & ~df["single_only"].fillna(False), "range_session"].dropna().values

    full_stats = mw_test(g_compound, g_single, alternative="greater")

    # Bootstrap only — n may be small
    n_compound = len(g_compound)
    use_bootstrap = n_compound < 40
    boot_result = None
    if use_bootstrap and n_compound >= 10 and len(g_single) >= 10:
        outcome = df["range_session"].values
        mask_c = df["compound"].fillna(False).values
        mask_s = df["single_only"].fillna(False).values
        obs, p_boot, ci = block_bootstrap_median_diff(
            None, outcome, mask_c, mask_s, n_boot=2000, block=5
        )
        boot_result = {"observed_diff": obs, "p_bootstrap_greater": p_boot, "ci_95": list(ci)}

    if n_compound < 10:
        verdict, reason = "insufficient_data", f"n_compound={n_compound} < 10"
    elif full_stats["diff"] > 0.003 and full_stats["p"] < 0.15:
        verdict = "supported"
        reason = f"diff={full_stats['diff']:.4f}, p={full_stats['p']:.4f}, n_compound={n_compound}"
    elif full_stats["diff"] <= 0:
        verdict = "rejected"
        reason = f"diff={full_stats['diff']:.4f} ≤ 0"
    else:
        verdict = "inconclusive"
        reason = f"diff={full_stats['diff']:.4f}, p={full_stats['p']:.4f}"

    result = {
        "hypothesis_number": "H73",
        "hypothesis_title": "Compound Signal (Pattern 4 AND Backwardation) → Larger Range Than Single Signal",
        "classification": "hybrid",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "n_compound": int(n_compound),
        "n_single_only": int(len(g_single)),
        "n_neither": int(len(g_neither)),
        "compound_vs_single": full_stats,
        "bootstrap_result": boot_result,
        "used_bootstrap_only": bool(use_bootstrap),
        "phase1_alignment": "extends",
        "notes": "n_compound typically small (~20-40). Bootstrap used instead of walk-forward when n < 40.",
    }
    _save(result, "H73")
    return result


# ── H94: 7d/30d Slope → Next-Session Intraday Range ─────────────────────────

def run_h94(feats: pd.DataFrame, daily: pd.DataFrame, ivx: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H94.json"
    if out_path.exists() and not force:
        print("  H94: cached")
        return json.loads(out_path.read_text())

    print("  H94: running...")
    eod = daily[["iv_30d"]].join(ivx[["iv_7d"]], how="inner")
    eod.index = pd.to_datetime(eod.index)
    eod["slope_7_30"] = eod["iv_7d"] / eod["iv_30d"]
    eod["in_backwardation"] = eod["slope_7_30"] > 1.0

    next_feats = feats[["range_session", "range_60m", "range_30m"]].copy()
    next_feats.index = pd.to_datetime(next_feats.index)
    df = eod.join(next_feats.shift(-1), how="inner")

    df["mask_a"] = df["in_backwardation"].fillna(False)

    windows = {}
    for w in ["range_30m", "range_60m", "range_session"]:
        tmp = df[["mask_a", w]].dropna()
        ga = tmp.loc[tmp["mask_a"], w].values
        gb = tmp.loc[~tmp["mask_a"], w].values
        windows[w] = mw_test(ga, gb, alternative="greater")

    wf = walk_forward_mw(df, "mask_a", "range_session")
    primary = windows["range_session"]
    verdict, reason = _verdict(
        primary, wf, support_thresh=0.003, reject_thresh=0.0,
        p_thresh_support=0.10, p_thresh_reject=0.30, min_n=15
    )

    result = {
        "hypothesis_number": "H94",
        "hypothesis_title": "Front-End Term Structure (7d/30d) Backwardation → Next-Session Range",
        "classification": "hybrid",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "intraday_windows": windows,
        "walk_forward_session": wf,
        "median_slope_7_30": float(df["slope_7_30"].median()),
        "pct_backwardation": float(df["in_backwardation"].mean()),
        "phase1_alignment": "confirmed" if verdict == "supported" else "partial",
        "notes": "Phase 1 used EOD daily range. Phase 2 validates 7d/30d slope signal vs 1m intraday range windows.",
    }
    _save(result, "H94")
    return result


# ── H97: IV Velocity → Next-Session Range ────────────────────────────────────

def run_h97(feats: pd.DataFrame, daily: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H97.json"
    if out_path.exists() and not force:
        print("  H97: cached")
        return json.loads(out_path.read_text())

    print("  H97: running...")
    eod = daily[["iv_30d"]].copy()
    eod.index = pd.to_datetime(eod.index)
    eod["iv_vel_5d"] = eod["iv_30d"].pct_change(5)
    eod["rising"] = eod["iv_vel_5d"] > 0.10
    eod["falling"] = eod["iv_vel_5d"] < -0.08

    next_feats = feats[["range_session", "range_60m", "range_30m"]].copy()
    next_feats.index = pd.to_datetime(next_feats.index)
    df = eod.join(next_feats.shift(-1), how="inner")

    # Rising vs falling (the main Phase 1 test)
    rising_mask = df["rising"].fillna(False)
    falling_mask = df["falling"].fillna(False)

    df_rf = df.loc[rising_mask | falling_mask].copy()
    df_rf["mask_a"] = rising_mask.loc[df_rf.index]

    full_rf = {}
    for w in ["range_30m", "range_60m", "range_session"]:
        tmp = df_rf[["mask_a", w]].dropna()
        ga = tmp.loc[tmp["mask_a"], w].values
        gb = tmp.loc[~tmp["mask_a"], w].values
        full_rf[w] = mw_test(ga, gb, alternative="greater")

    # Walk-forward on subset with rising or falling
    wf = walk_forward_mw(df_rf, "mask_a", "range_session")
    primary = full_rf["range_session"]

    n_rising = int(rising_mask.sum())
    n_falling = int(falling_mask.sum())

    if min(n_rising, n_falling) < 15:
        verdict = "insufficient_data"
        reason = f"n_rising={n_rising}, n_falling={n_falling}"
    else:
        verdict, reason = _verdict(
            primary, wf, support_thresh=0.003, reject_thresh=0.0,
            p_thresh_support=0.10, p_thresh_reject=0.30, min_n=15
        )

    result = {
        "hypothesis_number": "H97",
        "hypothesis_title": "IV Velocity (5-Day Pct Change) → Next-Session Range",
        "classification": "hybrid",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "n_rising": n_rising,
        "n_falling": n_falling,
        "intraday_windows": full_rf,
        "walk_forward_session": wf,
        "phase1_alignment": "confirmed" if verdict == "supported" else "partial",
        "notes": "Phase 1 used EOD daily range. Phase 2 validates velocity signal vs 1m intraday range windows.",
    }
    _save(result, "H97")
    return result


# ── H100: Overnight Gap → Same-Session Range (1m precision) ──────────────────

def run_h100(feats: pd.DataFrame, force: bool = False) -> dict:
    out_path = RESULTS_DIR / "H100.json"
    if out_path.exists() and not force:
        print("  H100: cached")
        return json.loads(out_path.read_text())

    print("  H100: running...")
    df = feats[["gap_pct_1m", "range_session", "range_60m", "range_30m"]].dropna()

    large_thresh = 0.005
    small_thresh = 0.001
    df["large_gap"] = df["gap_pct_1m"] > large_thresh
    df["small_gap"] = df["gap_pct_1m"] < small_thresh

    df_gs = df.loc[df["large_gap"] | df["small_gap"]].copy()
    df_gs["mask_a"] = df["large_gap"].loc[df_gs.index]

    full_windows = {}
    for w in ["range_30m", "range_60m", "range_session"]:
        tmp = df_gs[["mask_a", w]].dropna()
        ga = tmp.loc[tmp["mask_a"], w].values
        gb = tmp.loc[~tmp["mask_a"], w].values
        full_windows[w] = mw_test(ga, gb, alternative="greater")

    wf = walk_forward_mw(df_gs, "mask_a", "range_session")
    primary = full_windows["range_session"]

    n_large = int(df["large_gap"].sum())
    n_small = int(df["small_gap"].sum())
    pct_large = float(df["large_gap"].mean())
    median_gap = float(df["gap_pct_1m"].median())

    if n_large < 30:
        verdict = "insufficient_data"
        reason = f"n_large={n_large} < 30"
    else:
        # Phase 2 threshold: diff > 0.004 and p < 0.05 (tighter than Phase 1 EOD test)
        diff = primary.get("diff", np.nan)
        p = primary.get("p", np.nan)
        n_pos = wf.get("n_positive_splits", 0)
        if not np.isnan(diff) and diff > 0.004 and not np.isnan(p) and p < 0.05 and n_pos >= 2:
            verdict = "supported"
            reason = f"diff={diff:.4f} > 0.004, p={p:.4f}, {wf['consistency']}"
        elif not np.isnan(diff) and diff <= 0:
            verdict = "rejected"
            reason = f"diff={diff:.4f} ≤ 0"
        else:
            verdict = "inconclusive"
            reason = f"diff={diff:.4f}, p={p:.4f} — 1m gap precision tested"

    result = {
        "hypothesis_number": "H100",
        "hypothesis_title": "Overnight Gap (1m precision) → Same-Session Intraday Range",
        "classification": "intraday_primary",
        "phase2_verdict": verdict,
        "phase2_verdict_reason": reason,
        "n_large_gap": n_large,
        "n_small_gap": n_small,
        "pct_days_large_gap": round(pct_large, 4),
        "median_gap_pct": round(median_gap, 5),
        "intraday_windows": full_windows,
        "walk_forward_session": wf,
        "phase1_alignment": "extends",
        "notes": "Phase 1 used EOD open/prev_close (inconclusive, diff=0.0039 vs 0.004 threshold). Phase 2 uses 1m first_bar_open vs prev_session last_close for precision.",
    }
    _save(result, "H100")
    return result


# ── Vault markdown export ─────────────────────────────────────────────────────

def _verdict_badge(v: str) -> str:
    mapping = {
        "supported": "✅ SUPPORTED",
        "rejected": "❌ REJECTED",
        "inconclusive": "⚠️ INCONCLUSIVE",
        "insufficient_data": "⛔ INSUFFICIENT DATA",
    }
    return mapping.get(v, v.upper())


def _fmt_mw(r: dict) -> str:
    if not r or np.isnan(r.get("p", np.nan)):
        return "n/a"
    return (
        f"diff={r.get('diff', 0):.4f}, p={r.get('p', 1):.4f}, "
        f"cliff_d={r.get('cliff_d', 0):.3f}, n_a={r.get('n_a')}, n_b={r.get('n_b')}"
    )


def export_vault_note(result: dict) -> None:
    hnum = result["hypothesis_number"]
    title = result["hypothesis_title"]
    verdict = result["phase2_verdict"]
    reason = result["phase2_verdict_reason"]
    classification = result.get("classification", "unknown")
    phase1 = result.get("phase1_alignment", "unknown")
    notes = result.get("notes", "")

    lines = [
        f"# {hnum} — Phase 2 Intraday Robustness",
        "",
        f"**Hypothesis:** {title}",
        f"**Classification:** {classification}",
        f"**Phase 2 Verdict:** {_verdict_badge(verdict)}",
        f"**Reason:** {reason}",
        f"**Phase 1 Alignment:** {phase1}",
        "",
        f"> {notes}",
        "",
        "## Walk-Forward Results",
        "",
    ]

    # Emit any walk-forward splits found at top level
    for key in ["walk_forward_session", "walk_forward_range_session", "walk_forward_afternoon"]:
        if key in result:
            wf = result[key]
            lines.append(f"### {key.replace('_', ' ').title()}")
            for split_name, split_r in wf.get("splits", {}).items():
                lines.append(f"- **{split_name}**: {_fmt_mw(split_r)}")
            lines.append(f"- **Consistency:** {wf.get('consistency', 'n/a')} ({wf.get('n_positive_splits', '?')}/3 splits positive)")
            lines.append("")

    # Intraday windows
    for key in ["intraday_windows", "intraday_profile"]:
        if key in result:
            lines.append("## Intraday Window Breakdown")
            for wname, wr in result[key].items():
                lines.append(f"- **{wname}**: {_fmt_mw(wr)}")
            lines.append("")

    # Bias stats (H15)
    if "bias_walk_forward" in result:
        lines.append("## Bias Walk-Forward (fh_rv − fd_rv)")
        for split_name, br in result["bias_walk_forward"].items():
            lines.append(
                f"- **{split_name}**: mean_bias={br.get('mean_bias', np.nan):.4f}, "
                f"pct_pos={br.get('pct_positive', np.nan):.2%}, p_wilcoxon={br.get('p_wilcoxon', np.nan):.4f}"
            )
        lines.append("")

    # Spearman (H24)
    for key in ["late_rv_spearman_wf", "fd_rv_spearman_wf"]:
        if key in result:
            lines.append(f"## {key.replace('_', ' ').title()}")
            for split_name, sr in result[key].items():
                lines.append(f"- **{split_name}**: rho={sr.get('rho', np.nan):.3f}, p_nw={sr.get('p_nw', np.nan):.4f}, n={sr.get('n')}")
            lines.append("")

    out_path = VAULT_DIR / f"{hnum}.md"
    out_path.write_text("\n".join(lines))


def export_batch_summary(results: list[dict]) -> None:
    lines = [
        "# Phase 2 Batch Summary — Intraday Robustness",
        "",
        f"**Run date:** {date.today().isoformat()}",
        f"**Batch:** H15, H24, H44, H48, H53, H73, H94, H97, H100",
        "",
        "| H# | Title | Class | Verdict | Phase 1 Alignment |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        hnum = r["hypothesis_number"]
        title = r["hypothesis_title"][:55]
        cls = r.get("classification", "?")
        v = _verdict_badge(r["phase2_verdict"])
        p1 = r.get("phase1_alignment", "?")
        lines.append(f"| {hnum} | {title} | {cls} | {v} | {p1} |")

    lines += ["", "## Verdicts by Category", ""]
    by_verdict: dict[str, list[str]] = {}
    for r in results:
        v = r["phase2_verdict"]
        by_verdict.setdefault(v, []).append(r["hypothesis_number"])
    for v, hnums in sorted(by_verdict.items()):
        lines.append(f"- **{v.upper()}:** {', '.join(hnums)}")

    (VAULT_DIR / "_batch_summary.md").write_text("\n".join(lines))

    summary_data = {
        "run_date": date.today().isoformat(),
        "batch": ["H15", "H24", "H44", "H48", "H53", "H73", "H94", "H97", "H100"],
        "verdicts": {r["hypothesis_number"]: r["phase2_verdict"] for r in results},
        "n_supported": sum(r["phase2_verdict"] == "supported" for r in results),
        "n_rejected": sum(r["phase2_verdict"] == "rejected" for r in results),
        "n_inconclusive": sum(r["phase2_verdict"] == "inconclusive" for r in results),
        "n_insufficient": sum(r["phase2_verdict"] == "insufficient_data" for r in results),
    }
    (RESULTS_DIR / "batch_summary.json").write_text(json.dumps(summary_data, indent=2))


# ── Main ──────────────────────────────────────────────────────────────────────

ALL_HYPOTHESES = ["H15", "H24", "H44", "H48", "H53", "H73", "H94", "H97", "H100"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 2 intraday robustness backtests")
    parser.add_argument("--hypotheses", default=",".join(ALL_HYPOTHESES),
                        help="Comma-separated list, e.g. H15,H44")
    parser.add_argument("--force", action="store_true", help="Overwrite existing results")
    args = parser.parse_args()

    targets = [h.strip().upper() for h in args.hypotheses.split(",")]
    print(f"\nPhase 2 backtests: {targets}\n")

    # Load shared data
    print("Loading data...")
    bars_1m = load_all_1m()
    print(f"  1m bars: {len(bars_1m):,} rows ({bars_1m.index[0].date()} → {bars_1m.index[-1].date()})")

    print("  Building daily intraday features...")
    feats = build_daily_intraday_features(bars_1m)
    feats.index = pd.to_datetime(feats.index)
    print(f"  Features: {len(feats)} trading days")

    daily = load_daily()

    needs_ivx = bool(set(targets) & {"H94"})
    ivx = load_ivx() if needs_ivx else None

    results = []

    runner_map = {
        "H15":  lambda force: run_h15(feats, daily, force),
        "H24":  lambda force: run_h24(feats, force),
        "H44":  lambda force: run_h44(feats, daily, force),
        "H48":  lambda force: run_h48(feats, force),
        "H53":  lambda force: run_h53(feats, daily, force),
        "H73":  lambda force: run_h73(feats, daily, force),
        "H94":  lambda force: run_h94(feats, daily, ivx, force),
        "H97":  lambda force: run_h97(feats, daily, force),
        "H100": lambda force: run_h100(feats, force),
    }

    for hnum in targets:
        if hnum not in runner_map:
            print(f"  {hnum}: unknown, skipping")
            continue
        result = runner_map[hnum](args.force)
        results.append(result)
        print(f"  {hnum}: {result['phase2_verdict'].upper()} — {result['phase2_verdict_reason'][:80]}")
        export_vault_note(result)

    if len(targets) == len(ALL_HYPOTHESES) or len(results) > 1:
        export_batch_summary(results)
        print(f"\nSummary → {RESULTS_DIR / 'batch_summary.json'}")
        print(f"Vault   → {VAULT_DIR / '_batch_summary.md'}")

    print("\nDone.")


if __name__ == "__main__":
    main()
