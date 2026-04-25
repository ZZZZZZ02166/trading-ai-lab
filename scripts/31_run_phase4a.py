"""
Phase 4A — New Intraday Factor Tests (EOD + 1m data)

Tests 6 new intraday factor hypotheses derived from options/vol research:

  H-NEW-1 (B1): Opening Range Efficiency → Afternoon Range
  H-NEW-2 (B2): RV Surprise Ratio → Range Persistence
  H-NEW-3 (B3): Term Structure Velocity → Expansion
  H-NEW-4 (B4): Prior-Close Vol → Opening Range (NOT gap fill)
  H-NEW-5 (B5): fh_rv × Gap Magnitude → Afternoon Range (4-cell)
  H-NEW-6 (B6): High-Range Streak → Next-Day Expansion

Data: daily_series.parquet + Databento 1m bars
Walk-forward: train=2024, val=2025, holdout=2026-Q1

Output:
  experiments/phase3_results/phase4a_H-NEW-{N}.json
  experiments/phase3_results/phase4a_summary.json
  vault/Phase4/  (created but main vault note written after both scripts run)

Usage:
  python scripts/31_run_phase4a.py
"""

from __future__ import annotations

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

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE          = Path(__file__).resolve().parent.parent
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
DAILY_SERIES  = BASE / "data" / "processed" / "daily_series.parquet"
IVX_PATH      = BASE / "data" / "raw" / "qqq_ivx.parquet"
RESULTS_DIR   = BASE / "experiments" / "phase3_results"
VAULT_P4      = BASE / "vault" / "Phase4"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
VAULT_P4.mkdir(parents=True, exist_ok=True)

# ── Walk-forward splits ────────────────────────────────────────────────────────
TRAIN_START, TRAIN_END = "2024-01-01", "2024-12-31"
VAL_START,   VAL_END   = "2025-01-01", "2025-12-31"
HOLD_START,  HOLD_END  = "2026-01-01", "2026-03-31"
FULL_START,  FULL_END  = "2024-01-01", "2026-03-31"
_ET = "America/New_York"

_WINDOW_ENDS = {
    "w30":  "09:59",
    "w60":  "10:29",
    "w120": "11:29",
    "w150": "11:59",
    "w210": "12:59",
}

MIN_GAP = 0.002  # 0.2% minimum gap


# ── Data loading ───────────────────────────────────────────────────────────────

def load_all_1m() -> pd.DataFrame:
    files = sorted(DATABENTO_DIR.glob("qqq_1m_*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files]).sort_index()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(_ET)
    return df


def load_daily() -> pd.DataFrame:
    df = pd.read_parquet(DAILY_SERIES)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    df["daily_range"] = (df["high"] - df["low"]) / df["close"]
    df["spread_pct"]  = (df["ask"] - df["bid"]) / df["close"]
    return df


# ── Window table (mirrors 29_run_phase3.py) ────────────────────────────────────

def build_window_table(bars_1m: pd.DataFrame) -> pd.DataFrame:
    bars_et = bars_1m.tz_convert(_ET) if bars_1m.index.tzinfo else bars_1m
    rows = []
    days = sorted(set(bars_et.index.date))
    last_close: dict = {}

    for i, d in enumerate(days):
        day = bars_et[bars_et.index.date == d]
        if day.empty:
            continue
        prev_close = last_close.get(days[i - 1]) if i > 0 else np.nan
        last_close[d] = float(day["close"].iloc[-1])

        first_bar = day.between_time("09:30", "09:30")
        if first_bar.empty:
            continue
        open_0930 = float(first_bar["open"].iloc[0])
        if prev_close is None or not np.isfinite(prev_close):
            overnight_gap = np.nan
        else:
            overnight_gap = (open_0930 - prev_close) / prev_close

        row: dict = {
            "date": pd.Timestamp(d),
            "open_0930": open_0930,
            "prev_close": prev_close if (prev_close is not None and np.isfinite(prev_close)) else np.nan,
            "overnight_gap": overnight_gap,
            "gap_magnitude": abs(overnight_gap) if np.isfinite(overnight_gap) else np.nan,
        }

        for wname, wend in _WINDOW_ENDS.items():
            sub = day.between_time("09:30", wend)
            if len(sub) < 3:
                row[f"{wname}_range"] = np.nan
                row[f"{wname}_high"]  = np.nan
                row[f"{wname}_low"]   = np.nan
            else:
                wh = float(sub["high"].max())
                wl = float(sub["low"].min())
                wc = float(sub["close"].iloc[-1])
                row[f"{wname}_range"]  = (wh - wl) / open_0930
                row[f"{wname}_return"] = (wc - open_0930) / open_0930
                row[f"{wname}_high"]   = wh
                row[f"{wname}_low"]    = wl

        # Gap fill (for B5 context)
        if np.isfinite(overnight_gap) and abs(overnight_gap) >= MIN_GAP and np.isfinite(prev_close):
            for wname in ["w30", "w60"]:
                wh = row.get(f"{wname}_high", np.nan)
                wl = row.get(f"{wname}_low", np.nan)
                if not np.isfinite(wh) or not np.isfinite(wl):
                    row[f"gap_fill_{wname[1:]}"] = np.nan
                elif overnight_gap > 0:
                    row[f"gap_fill_{wname[1:]}"] = int(wl <= prev_close)
                else:
                    row[f"gap_fill_{wname[1:]}"] = int(wh >= prev_close)
        else:
            row["gap_fill_30"] = np.nan
            row["gap_fill_60"] = np.nan

        # Afternoon window 10:30–11:59 (primary for H-NEW-1/2/5)
        aw_sub = day.between_time("10:30", "11:59")
        if len(aw_sub) >= 5:
            aw_o = float(aw_sub["open"].iloc[0])
            row["aw_range"]  = (float(aw_sub["high"].max()) - float(aw_sub["low"].min())) / aw_o
            row["aw_return"] = (float(aw_sub["close"].iloc[-1]) - aw_o) / aw_o
        else:
            row["aw_range"] = row["aw_return"] = np.nan

        # fh_rv: first-hour (09:30–10:29) annualized realized vol
        fh_bars = day.between_time("09:30", "10:29")
        if len(fh_bars) >= 10:
            fh_rets = np.log(fh_bars["close"] / fh_bars["close"].shift(1)).dropna().values
            n_fh = len(fh_rets)
            row["fh_rv"] = float(np.sqrt(np.sum(fh_rets**2) * (390 / n_fh) * 252)) if n_fh >= 5 else np.nan
        else:
            row["fh_rv"] = np.nan

        # late_rv: 15:30–15:59 annualized realized vol
        late_bars = day.between_time("15:30", "15:59")
        if len(late_bars) >= 5:
            late_rets = np.log(late_bars["close"] / late_bars["close"].shift(1)).dropna().values
            n_late = len(late_rets)
            row["late_rv"] = float(np.sqrt(np.sum(late_rets**2) * (390 / n_late) * 252)) if n_late >= 3 else np.nan
        else:
            row["late_rv"] = np.nan

        rows.append(row)

    wt = pd.DataFrame(rows).set_index("date").sort_index()
    wt.index = pd.to_datetime(wt.index)

    # Rolling 252d medians
    for wname in _WINDOW_ENDS:
        col = f"{wname}_range"
        med = wt[col].rolling(252, min_periods=60).median()
        wt[f"{wname}_expansion"] = (wt[col] > med).astype(float)
        wt[f"{wname}_med"] = med  # store for efficiency ratio

    return wt


def build_signal_df(wt: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    # Prior-day EOD signals
    eod_cols = ["iv_30d", "iv_60d", "daily_range", "spread_pct"]
    sig_eod = daily[eod_cols].shift(1)
    sig_eod.columns = ["sig_" + c for c in eod_cols]
    df = wt.join(sig_eod, how="inner")

    # H44-style iv spread (prior day)
    df["iv_spread_30_60"] = df["sig_iv_30d"] - df["sig_iv_60d"]

    # B3: Term structure velocity = day-over-day change in iv_spread_30_60
    daily_spread = daily["iv_30d"] - daily["iv_60d"]
    df["ts_velocity"] = daily_spread.shift(1).diff().reindex(df.index)

    # B4: Prior-close vol (late_rv shifted) → today's opening range/fh_rv
    df["late_rv_prior"] = wt["late_rv"].shift(1).reindex(df.index)

    # H97-style iv velocity (5d, already tested; include for redundancy check vs B3)
    iv_vel = daily["iv_30d"].pct_change(5).shift(1)
    df["iv_velocity_5d"] = iv_vel.reindex(df.index)

    # Rolling 252d range rank (H70 style, for B6 base)
    prior_range = daily["daily_range"].shift(1)
    range_rank = prior_range.rolling(252, min_periods=252).rank(pct=True)
    df["range_pct_rank"] = range_rank.reindex(df.index)

    # H48-style: fh_rv above 252d rolling median
    fh_med = wt["fh_rv"].rolling(252, min_periods=60).median()
    df["fh_rv_med"] = fh_med
    df["h48_above_med"] = (df["fh_rv"] > fh_med).astype(float)

    # B1: Opening range efficiency = w30_range / rolling_252d_median(w30_range)
    df["w30_range_efficiency"] = df["w30_range"] / df["w30_med"].replace(0, np.nan)

    # B2: RV surprise ratio = w30_range / expected 30-min range from prior-day IV
    # Expected 30-min range = iv_30d_prior / sqrt(252 * 13)  [13 = 390min/30min]
    expected_30m = df["sig_iv_30d"] / np.sqrt(252 * 13)
    df["rv_surprise_ratio"] = df["w30_range"] / expected_30m.replace(0, np.nan)

    # B5: fh_rv binary and gap binary (already have gap_magnitude and h48_above_med)
    gap_med = df["gap_magnitude"].median()
    df["large_gap"] = (df["gap_magnitude"] > gap_med).astype(float)

    # B6: streak of consecutive above-median w150_range days
    expansion_series = df["w150_expansion"].fillna(0).astype(bool)
    streaks = []
    current = 0
    for val in expansion_series:
        current = current + 1 if val else 0
        streaks.append(current)
    df["range_streak"] = streaks

    return df


# ── Statistical utilities ──────────────────────────────────────────────────────

def cliff_delta(g1: np.ndarray, g2: np.ndarray) -> float:
    g1, g2 = np.asarray(g1, float), np.asarray(g2, float)
    if len(g1) == 0 or len(g2) == 0:
        return np.nan
    dom = int((g1[:, None] > g2[None, :]).sum()) - int((g1[:, None] < g2[None, :]).sum())
    return dom / (len(g1) * len(g2))


def mw_test(g1: np.ndarray, g2: np.ndarray) -> dict:
    g1 = np.asarray(g1, float)[np.isfinite(np.asarray(g1, float))]
    g2 = np.asarray(g2, float)[np.isfinite(np.asarray(g2, float))]
    if len(g1) < 5 or len(g2) < 5:
        return {"n_a": int(len(g1)), "n_b": int(len(g2)), "stat": None, "p": None,
                "cliff_d": None, "median_a": None, "median_b": None, "diff": None}
    stat, p = mannwhitneyu(g1, g2, alternative="two-sided")
    return {"n_a": int(len(g1)), "n_b": int(len(g2)), "stat": float(stat), "p": float(p),
            "cliff_d": float(cliff_delta(g1, g2)),
            "median_a": float(np.median(g1)), "median_b": float(np.median(g2)),
            "diff": float(np.median(g1) - np.median(g2))}


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
        X2 = sm.add_constant(rx)
        p_nw = float(sm.OLS(ry, X2).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags}).pvalues[1])
    else:
        p_nw = float(p_scipy)
    return {"rho": round(float(rho), 4), "p_nw": float(p_nw), "n": int(n)}


def split_by_period(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "full":    df.loc[FULL_START:FULL_END],
        "train":   df.loc[TRAIN_START:TRAIN_END],
        "val":     df.loc[VAL_START:VAL_END],
        "holdout": df.loc[HOLD_START:HOLD_END],
    }


def wf_spearman(df: pd.DataFrame, x: str, y: str) -> dict:
    splits = split_by_period(df)
    results = {}
    signs = []
    for name, sub in splits.items():
        sub_c = sub[[x, y]].dropna()
        r = nw_spearman(sub_c[x].values, sub_c[y].values)
        results[name] = r
        if name != "full" and r["rho"] is not None:
            signs.append(np.sign(r["rho"]))
    n_pos = sum(s > 0 for s in signs)
    consistency = "consistent" if n_pos == 3 else ("mixed" if n_pos == 2 else "inconsistent")
    return {"splits": results, "consistency": consistency, "n_positive_splits": int(n_pos)}


def timing_gate(df: pd.DataFrame, signal_col: str) -> tuple[dict, str, bool]:
    """Compute window rhos and check if peak effect is within w150."""
    sig = df[signal_col].values
    window_rhos = {}
    for wname in _WINDOW_ENDS:
        sub = df.dropna(subset=[signal_col, f"{wname}_range"])
        r = nw_spearman(sub[signal_col].values, sub[f"{wname}_range"].values)
        window_rhos[wname] = r
    eff = {w: abs(r["rho"] or 0) for w, r in window_rhos.items()}
    peak = max(eff, key=eff.get)
    eff_w150 = eff.get("w150", 0)
    eff_w210 = eff.get("w210", 1e-9)
    early_enough = peak in ["w30", "w60", "w120", "w150"] and eff_w150 >= 0.5 * eff_w210
    return window_rhos, peak, early_enough


def assign_verdict(stat_ok: bool, sign_ok: bool, n_ok: bool, early_ok: bool) -> str:
    if not n_ok:       return "insufficient_data"
    if not stat_ok or not sign_ok: return "rejected"
    if not early_ok:   return "too_late_for_style"
    return "supported_trading_useful"


def save_json(data: dict, filename: str) -> Path:
    out = RESULTS_DIR / filename
    with open(out, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return out


# ── H-NEW-1 (B1): Opening Range Efficiency → Afternoon Range ──────────────────

def run_h_new_1(df: pd.DataFrame) -> dict:
    """
    Signal: w30_range_efficiency = w30_range / rolling_252d_median(w30_range)
    Low efficiency (vol hasn't arrived) → more range left in afternoon.
    Primary outcome: aw_range (10:30–11:59).
    Note: signal at 10:00; outcome AFTER signal (no lookahead).
    """
    # Invert: low efficiency → high remaining range → test (1 - efficiency) vs aw_range
    # Or equivalently test efficiency with expected NEGATIVE rho vs aw_range
    sub = df.dropna(subset=["w30_range_efficiency", "aw_range"]).copy()
    n = len(sub)

    full_sp = nw_spearman(sub["w30_range_efficiency"].values, sub["aw_range"].values)
    # Expected sign: NEGATIVE (low efficiency → more range). Check sign.
    wf = wf_spearman(sub, "w30_range_efficiency", "aw_range")

    # MW: low efficiency (below median) vs high efficiency
    eff_med = sub["w30_range_efficiency"].median()
    low_eff = sub[sub["w30_range_efficiency"] <= eff_med]["aw_range"].values
    high_eff = sub[sub["w30_range_efficiency"] > eff_med]["aw_range"].values
    mw = mw_test(low_eff, high_eff)  # expect low_eff (low efficiency → more range) to have higher aw_range

    # Stat check: negative rho = low efficiency → more range (what we want)
    stat_ok = (full_sp["rho"] or 0) < -0.05 and (full_sp["p_nw"] or 1) < 0.10
    sign_ok = all((wf["splits"][s]["rho"] or 0) < 0
                  for s in ["train", "val", "holdout"] if wf["splits"][s]["rho"] is not None)
    n_ok = n >= 80
    # B1 signal at 10:00 — no timing gate across morning windows (outcome is after-signal aw_range)
    verdict = assign_verdict(stat_ok, sign_ok, n_ok, early_ok=True)

    result = {
        "hypothesis": "H-NEW-1",
        "label": "Opening Range Efficiency → Afternoon Range",
        "signal": "w30_range / rolling_252d_median(w30_range) — efficiency ratio at 10:00",
        "outcome": "aw_range (10:30–11:59)",
        "role": "BOTH (early warning partial at 9:45; confirmation at 10:00)",
        "n_total": int(n),
        "primary_spearman_aw_range": full_sp,
        "expected_sign": "negative (low efficiency → more remaining range)",
        "walk_forward_spearman": wf,
        "mw_low_vs_high_efficiency": mw,
        "mw_note": "median(aw_range) for low-efficiency days vs high-efficiency days",
        "phase4a_verdict": verdict,
        "verdict_note": "Negative rho = low efficiency → more afternoon range. Positive = opposite."
    }
    return result


# ── H-NEW-2 (B2): RV Surprise Ratio → Range Persistence ──────────────────────

def run_h_new_2(df: pd.DataFrame) -> dict:
    """
    Signal: w30_range / (iv_30d_prior / sqrt(252*13)) — how much did realized exceed expected?
    High ratio → IV underpriced → more range coming.
    Primary: aw_range. Secondary: w150_range.
    Signal available at 10:00 (after first 30 min).
    """
    sub = df.dropna(subset=["rv_surprise_ratio", "aw_range", "w150_range"]).copy()
    n = len(sub)

    sp_aw   = nw_spearman(sub["rv_surprise_ratio"].values, sub["aw_range"].values)
    sp_w150 = nw_spearman(sub["rv_surprise_ratio"].values, sub["w150_range"].values)
    wf_aw   = wf_spearman(sub, "rv_surprise_ratio", "aw_range")

    # MW: high surprise (>1.5×) vs low surprise (<0.75×)
    high_surp = sub[sub["rv_surprise_ratio"] >= 1.5]["aw_range"].values
    low_surp  = sub[sub["rv_surprise_ratio"] <= 0.75]["aw_range"].values
    mw_thresh = mw_test(high_surp, low_surp)

    stat_ok = (sp_aw["rho"] or 0) > 0.08 and (sp_aw["p_nw"] or 1) < 0.10
    sign_ok = all((wf_aw["splits"][s]["rho"] or 0) > 0
                  for s in ["train", "val", "holdout"] if wf_aw["splits"][s]["rho"] is not None)
    n_ok    = n >= 80
    verdict = assign_verdict(stat_ok, sign_ok, n_ok, early_ok=True)

    result = {
        "hypothesis": "H-NEW-2",
        "label": "RV Surprise Ratio → Range Persistence",
        "signal": "w30_range / (iv_30d_prior / sqrt(252*13)). Ratio > 1 = realized > expected.",
        "outcome": "aw_range (primary, 10:30–11:59); w150_range (secondary)",
        "role": "BOTH (9:31 early read; confirmed at 10:00)",
        "n_total": int(n),
        "primary_spearman_aw_range": sp_aw,
        "secondary_spearman_w150_range": sp_w150,
        "walk_forward_spearman_aw": wf_aw,
        "mw_high_vs_low_surprise": mw_thresh,
        "n_high_surprise": int(len(high_surp)),
        "n_low_surprise": int(len(low_surp)),
        "signal_stats": {
            "median": round(float(sub["rv_surprise_ratio"].median()), 3),
            "p25":    round(float(sub["rv_surprise_ratio"].quantile(0.25)), 3),
            "p75":    round(float(sub["rv_surprise_ratio"].quantile(0.75)), 3),
        },
        "phase4a_verdict": verdict,
    }
    return result


# ── H-NEW-3 (B3): Term Structure Velocity → Expansion ────────────────────────

def run_h_new_3(df: pd.DataFrame) -> dict:
    """
    Signal: day-over-day change in (iv_30d - iv_60d). Pre-open signal.
    Positive velocity (flip to backwardation) = regime transition → expansion.
    Primary: w150_range. Timing gate applied.
    """
    sub = df.dropna(subset=["ts_velocity", "w150_range"]).copy()
    n = len(sub)

    sp_full = nw_spearman(sub["ts_velocity"].values, sub["w150_range"].values)
    wf      = wf_spearman(sub, "ts_velocity", "w150_range")
    window_rhos, peak, early_enough = timing_gate(sub, "ts_velocity")

    stat_ok = abs(sp_full["rho"] or 0) > 0.08 and (sp_full["p_nw"] or 1) < 0.10
    sign_ok = all((wf["splits"][s]["rho"] or 0) > 0
                  for s in ["train", "val", "holdout"] if wf["splits"][s]["rho"] is not None)
    n_ok    = n >= 100
    verdict = assign_verdict(stat_ok, sign_ok, n_ok, early_enough)

    # MW: flip day (ts_velocity > 0) vs non-flip (ts_velocity <= 0)
    flip_days    = sub[sub["ts_velocity"] > 0]["w150_range"].values
    no_flip_days = sub[sub["ts_velocity"] <= 0]["w150_range"].values
    mw_flip = mw_test(flip_days, no_flip_days)

    result = {
        "hypothesis": "H-NEW-3",
        "label": "Term Structure Velocity → Range Expansion",
        "signal": "Δ(iv_30d - iv_60d) day-over-day. Pre-open.",
        "outcome": "w150_range (09:30–11:59)",
        "role": "EARLY WARNING (pre-open)",
        "n_total": int(n),
        "primary_spearman_w150": sp_full,
        "walk_forward_spearman": wf,
        "window_rhos": window_rhos,
        "peak_window": peak,
        "early_enough_for_style": early_enough,
        "mw_flip_vs_no_flip": mw_flip,
        "n_flip_days": int((sub["ts_velocity"] > 0).sum()),
        "n_no_flip_days": int((sub["ts_velocity"] <= 0).sum()),
        "phase4a_verdict": verdict,
    }
    return result


# ── H-NEW-4 (B4): Prior-Close Vol → Opening Range ────────────────────────────

def run_h_new_4(df: pd.DataFrame) -> dict:
    """
    Signal: late_rv from 15:30–15:59 prior day.
    Does yesterday's close vol predict today's opening range / first-hour RV?
    DIFFERENT from H24 (which tested gap fill — rejected).
    Primary: w30_range AND fh_rv.
    """
    sub_w30 = df.dropna(subset=["late_rv_prior", "w30_range"]).copy()
    sub_fh  = df.dropna(subset=["late_rv_prior", "fh_rv"]).copy()

    sp_w30 = nw_spearman(sub_w30["late_rv_prior"].values, sub_w30["w30_range"].values)
    sp_fh  = nw_spearman(sub_fh["late_rv_prior"].values,  sub_fh["fh_rv"].values)

    wf_w30 = wf_spearman(sub_w30, "late_rv_prior", "w30_range")
    wf_fh  = wf_spearman(sub_fh,  "late_rv_prior", "fh_rv")

    window_rhos, peak, early_enough = timing_gate(df.dropna(subset=["late_rv_prior"]), "late_rv_prior")

    # MW: high prior-close vol vs low prior-close vol → w30_range
    late_med = sub_w30["late_rv_prior"].median()
    high_late = sub_w30[sub_w30["late_rv_prior"] > late_med]["w30_range"].values
    low_late  = sub_w30[sub_w30["late_rv_prior"] <= late_med]["w30_range"].values
    mw = mw_test(high_late, low_late)

    stat_ok = (sp_w30["rho"] or 0) > 0.08 and (sp_w30["p_nw"] or 1) < 0.10
    sign_ok = all((wf_w30["splits"][s]["rho"] or 0) > 0
                  for s in ["train", "val", "holdout"] if wf_w30["splits"][s]["rho"] is not None)
    n_ok    = len(sub_w30) >= 80
    verdict = assign_verdict(stat_ok, sign_ok, n_ok, early_enough)

    result = {
        "hypothesis": "H-NEW-4",
        "label": "Prior-Close Realized Vol → Opening Range (NOT gap fill)",
        "signal": "late_rv (15:30–15:59 prior day). Distinct from H24 which tested gap fill.",
        "outcome_primary":   "w30_range (9:30–9:59 opening range)",
        "outcome_secondary": "fh_rv (9:30–10:29 first-hour RV)",
        "role": "EARLY WARNING (pre-open, prior-session data)",
        "n_w30": int(len(sub_w30)),
        "n_fh":  int(len(sub_fh)),
        "spearman_vs_w30_range": sp_w30,
        "spearman_vs_fh_rv": sp_fh,
        "walk_forward_spearman_w30": wf_w30,
        "walk_forward_spearman_fh": wf_fh,
        "window_rhos_vs_session_ranges": window_rhos,
        "peak_window": peak,
        "early_enough_for_style": early_enough,
        "mw_high_vs_low_prior_close_vol": mw,
        "phase4a_verdict": verdict,
        "h24_distinction": "H24 tested late_rv → gap_fill_30/60 (Fisher, rejected p=0.278/0.910). This tests late_rv → w30_range and fh_rv (opening activity, not fill direction).",
    }
    return result


# ── H-NEW-5 (B5): fh_rv × Gap Magnitude → Afternoon Range (4-cell) ──────────

def run_h_new_5(df: pd.DataFrame) -> dict:
    """
    4-cell conditional: {high fh_rv, low fh_rv} × {large gap, small gap} → aw_range.
    Confirmation signal at 10:30.
    """
    sub = df.dropna(subset=["fh_rv", "gap_magnitude", "aw_range"]).copy()

    fh_med  = sub["fh_rv"].median()
    gap_med = sub["gap_magnitude"].median()
    sub["fh_high"]   = sub["fh_rv"] > fh_med
    sub["gap_large"] = sub["gap_magnitude"] > gap_med

    cells = {}
    for fh_label, fh_mask in [("high_fh_rv", True), ("low_fh_rv", False)]:
        for gap_label, gap_mask in [("large_gap", True), ("small_gap", False)]:
            mask = (sub["fh_high"] == fh_mask) & (sub["gap_large"] == gap_mask)
            cell_sub = sub[mask]["aw_range"]
            cells[f"{fh_label}__{gap_label}"] = {
                "n": int(mask.sum()),
                "median_aw_range": round(float(cell_sub.median()), 6) if len(cell_sub) > 0 else None,
                "mean_aw_range":   round(float(cell_sub.mean()),   6) if len(cell_sub) > 0 else None,
            }

    # Cliff's d: maximum cell vs minimum cell
    max_cell_key = max(cells, key=lambda k: cells[k]["median_aw_range"] or 0)
    min_cell_key = min(cells, key=lambda k: cells[k]["median_aw_range"] or float("inf"))
    sub_max = sub[(sub["fh_high"] == (max_cell_key.startswith("high"))) &
                  (sub["gap_large"] == ("large" in max_cell_key))]["aw_range"].values
    sub_min = sub[(sub["fh_high"] == (min_cell_key.startswith("high"))) &
                  (sub["gap_large"] == ("large" in min_cell_key))]["aw_range"].values
    mw_top_vs_bottom = mw_test(sub_max, sub_min)

    # Are max and min cells as expected? max should be high_fh_rv__large_gap
    expected_max = "high_fh_rv__large_gap"
    expected_min = "low_fh_rv__small_gap"
    pattern_as_expected = max_cell_key == expected_max and min_cell_key == expected_min

    result = {
        "hypothesis": "H-NEW-5",
        "label": "fh_rv × Gap Magnitude → Afternoon Range (4-cell)",
        "signal": "4-cell: {high/low fh_rv} × {large/small gap}. At 10:30.",
        "outcome": "aw_range (10:30–11:59)",
        "role": "CONFIRMATION at 10:30",
        "n_total": int(len(sub)),
        "fh_rv_median_threshold": round(float(fh_med), 6),
        "gap_magnitude_median_threshold": round(float(gap_med), 6),
        "four_cell_table": cells,
        "mw_max_cell_vs_min_cell": mw_top_vs_bottom,
        "peak_cell": max_cell_key,
        "trough_cell": min_cell_key,
        "pattern_matches_hypothesis": pattern_as_expected,
        "expected_pattern": f"max={expected_max}, min={expected_min}",
        "phase4a_verdict": "supported_trading_useful" if (
            pattern_as_expected and
            (mw_top_vs_bottom["p"] or 1) < 0.10 and
            abs(mw_top_vs_bottom["cliff_d"] or 0) > 0.10
        ) else "inconclusive",
    }
    return result


# ── H-NEW-6 (B6): High-Range Streak → Next-Day Expansion ─────────────────────

def run_h_new_6(df: pd.DataFrame) -> dict:
    """
    Signal: consecutive days with w150_range > 252d rolling median (streak count).
    Streak ≥ 3 = vol clustering regime.
    Test redundancy with H70 (range_pct_rank).
    """
    sub = df.dropna(subset=["range_streak", "w150_range"]).copy()
    n = len(sub)

    sp_full = nw_spearman(sub["range_streak"].values, sub["w150_range"].values)
    wf      = wf_spearman(sub, "range_streak", "w150_range")
    window_rhos, peak, early_enough = timing_gate(sub, "range_streak")

    # MW: streak >= 3 vs streak == 0 (clean dichotomy)
    high_streak = sub[sub["range_streak"] >= 3]["w150_range"].values
    zero_streak = sub[sub["range_streak"] == 0]["w150_range"].values
    mw = mw_test(high_streak, zero_streak)

    # Partial rho vs range_pct_rank (check if streak adds info beyond H70)
    shared = sub.dropna(subset=["range_streak", "range_pct_rank", "w150_range"])
    if len(shared) >= 20 and HAS_SM:
        from scipy.stats import rankdata as rd
        n_sh = len(shared)
        rx_s = rd(shared["range_streak"].values) / n_sh
        ry   = rd(shared["w150_range"].values) / n_sh
        rz   = rd(shared["range_pct_rank"].values) / n_sh
        Z = sm.add_constant(rz)
        resid_x = sm.OLS(rx_s, Z).fit().resid
        resid_y = sm.OLS(ry, Z).fit().resid
        pr, pp = spearmanr(resid_x, resid_y)
        partial_vs_h70 = {"partial_rho": round(float(pr), 4), "partial_p": float(pp), "n": n_sh}
    else:
        partial_vs_h70 = {"partial_rho": None, "partial_p": None, "n": 0}

    stat_ok = abs(sp_full["rho"] or 0) > 0.08 and (sp_full["p_nw"] or 1) < 0.10
    sign_ok = all((wf["splits"][s]["rho"] or 0) > 0
                  for s in ["train", "val", "holdout"] if wf["splits"][s]["rho"] is not None)
    n_ok    = n >= 100
    verdict = assign_verdict(stat_ok, sign_ok, n_ok, early_enough)

    # Override verdict if partial rho is low (redundant with H70)
    if partial_vs_h70["partial_rho"] is not None and abs(partial_vs_h70["partial_rho"]) < 0.07:
        verdict = "redundant"

    result = {
        "hypothesis": "H-NEW-6",
        "label": "High-Range Streak → Next-Day Expansion",
        "signal": "Consecutive days with w150_range > rolling_252d_median. Pre-open.",
        "outcome": "w150_range (next day's session range)",
        "role": "EARLY WARNING / vol regime context (pre-open)",
        "n_total": int(n),
        "primary_spearman_w150": sp_full,
        "walk_forward_spearman": wf,
        "window_rhos": window_rhos,
        "peak_window": peak,
        "early_enough_for_style": early_enough,
        "mw_streak_ge3_vs_zero": mw,
        "n_streak_ge3": int((sub["range_streak"] >= 3).sum()),
        "n_streak_zero": int((sub["range_streak"] == 0).sum()),
        "partial_spearman_controlling_h70": partial_vs_h70,
        "redundancy_note": "Flagged redundant if partial_rho < 0.07 after controlling for H70 range_pct_rank",
        "phase4a_verdict": verdict,
    }
    return result


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Phase 4A — New Intraday Factor Tests (EOD + 1m)\n")

    print("Loading 1m bars...")
    bars = load_all_1m()
    print(f"  {len(bars):,} bars")

    print("Building window table...")
    wt = build_window_table(bars)
    print(f"  {len(wt)} trading days")

    print("Loading daily_series...")
    daily = load_daily()

    print("Building signal df...")
    df = build_signal_df(wt, daily)
    df = df.dropna(subset=["w150_range"])
    print(f"  {len(df)} rows\n")

    runners = [
        ("H-NEW-1", run_h_new_1),
        ("H-NEW-2", run_h_new_2),
        ("H-NEW-3", run_h_new_3),
        ("H-NEW-4", run_h_new_4),
        ("H-NEW-5", run_h_new_5),
        ("H-NEW-6", run_h_new_6),
    ]

    summary = {}
    for label, fn in runners:
        print(f"  Running {label}...")
        result = fn(df)
        verdict = result.get("phase4a_verdict", "?")
        fname = f"phase4a_{label.replace('-', '_')}.json"
        save_json(result, fname)
        print(f"    → {fname} | verdict: {verdict}")
        summary[label] = {
            "label": result.get("label"),
            "role": result.get("role"),
            "phase4a_verdict": verdict,
        }
        # Print key stat
        for key in ["primary_spearman_aw_range", "primary_spearman_w150",
                    "spearman_vs_w30_range", "spearman_vs_fh_rv"]:
            if key in result and result[key] and result[key].get("rho") is not None:
                sp = result[key]
                print(f"    ρ={sp['rho']:.3f}, p={sp['p_nw']:.4f}, n={sp['n']}")
                break

    out = {
        "run_date": str(date.today()),
        "script": "31_run_phase4a.py",
        "hypotheses": summary,
        "counts": {v: sum(1 for x in summary.values() if x["phase4a_verdict"] == v)
                   for v in ["supported_trading_useful", "too_late_for_style",
                              "inconclusive", "rejected", "redundant", "insufficient_data"]},
    }
    save_json(out, "phase4a_summary.json")
    print(f"\n  → phase4a_summary.json")
    print("\nDone.")


if __name__ == "__main__":
    main()
