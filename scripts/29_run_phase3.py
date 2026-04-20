"""
Phase 3 — Options Signal Trading Utility Test

Tests whether options/volatility signals add practical value within a
2–2.5 hour morning trading horizon.

Hypotheses: H15, H24, H44, H48, H53, H70, H76, H94, H97, H99, H100
Walk-forward: train=2024, val=2025, holdout=2026-Q1

Output:
  experiments/phase3_results/phase3_H{NN}.json  (per hypothesis)
  experiments/phase3_results/phase3_redundancy_audit.json
  experiments/phase3_results/phase3_summary.json
  Appends ## Phase 3 section to vault/Backtests/h{N}-*.md

Usage:
  python scripts/29_run_phase3.py
  python scripts/29_run_phase3.py --hypotheses H44,H94
  python scripts/29_run_phase3.py --force
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

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE            = Path(__file__).resolve().parent.parent
DATABENTO_DIR   = BASE / "data" / "raw" / "databento"
DAILY_SERIES    = BASE / "data" / "processed" / "daily_series.parquet"
IVX_PATH        = BASE / "data" / "raw" / "qqq_ivx.parquet"
RESULTS_DIR     = BASE / "experiments" / "phase3_results"
VAULT_BACKTESTS = BASE / "vault" / "Backtests"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Walk-forward splits ────────────────────────────────────────────────────────
TRAIN_START, TRAIN_END = "2024-01-01", "2024-12-31"
VAL_START,   VAL_END   = "2025-01-01", "2025-12-31"
HOLD_START,  HOLD_END  = "2026-01-01", "2026-03-31"
FULL_START,  FULL_END  = "2024-01-01", "2026-03-31"
_ET = "America/New_York"

# Window end times (30 min = 30 bars from 09:30, etc.)
# Labeled by last bar's start time (inclusive).
_WINDOW_ENDS = {
    "w30":  "09:59",   # 30 min
    "w60":  "10:29",   # 60 min — initial balance
    "w120": "11:29",   # 120 min
    "w150": "11:59",   # 150 min — max horizon
    "w210": "12:59",   # 210 min — reference only (timing gate)
}

MIN_GAP = 0.002  # 0.2% minimum overnight gap to count as a gap day

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
    df["spread_pct"] = (df["ask"] - df["bid"]) / df["close"]
    return df


def load_ivx() -> pd.DataFrame:
    df = pd.read_parquet(IVX_PATH)
    df = df.iloc[::-1].reset_index(drop=True)          # reverse: oldest first
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    df["ivx_7d"]          = df["7d IV Mean"]
    df["ivx_30d"]         = df["30d IV Mean"]
    df["ivx_spread_7_30"] = df["ivx_7d"] - df["ivx_30d"]
    df["ivx_bkwd"]        = (df["ivx_7d"] > df["ivx_30d"]).astype(float)
    return df[["ivx_7d", "ivx_30d", "ivx_spread_7_30", "ivx_bkwd"]]


# ── Window table ───────────────────────────────────────────────────────────────

def build_window_table(bars_1m: pd.DataFrame) -> pd.DataFrame:
    """Per-date session window metrics from 1m Databento bars."""
    bars_et = bars_1m.tz_convert(_ET) if bars_1m.index.tzinfo else bars_1m
    rows = []
    days = sorted(set(bars_et.index.date))
    last_close: dict = {}          # date → float

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
            "overnight_gap_dir": int(np.sign(overnight_gap)) if np.isfinite(overnight_gap) else 0,
            "gap_magnitude": abs(overnight_gap) if np.isfinite(overnight_gap) else np.nan,
        }

        # Rolling windows from open
        for wname, wend in _WINDOW_ENDS.items():
            sub = day.between_time("09:30", wend)
            if len(sub) < 3:
                row[f"{wname}_range"] = np.nan
                row[f"{wname}_return"] = np.nan
                row[f"{wname}_high"] = np.nan
                row[f"{wname}_low"] = np.nan
            else:
                wh = float(sub["high"].max())
                wl = float(sub["low"].min())
                wc = float(sub["close"].iloc[-1])
                row[f"{wname}_range"] = (wh - wl) / open_0930
                row[f"{wname}_return"] = (wc - open_0930) / open_0930
                row[f"{wname}_high"] = wh
                row[f"{wname}_low"] = wl

        # Gap fill flags (only for meaningful gaps)
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

        # Afternoon window: core 10:30–11:59 (primary for H15/H48) and extended 10:30–12:59
        aw_sub = day.between_time("10:30", "11:59")
        if len(aw_sub) >= 5:
            aw_o = float(aw_sub["open"].iloc[0])
            row["aw_range"]  = (float(aw_sub["high"].max()) - float(aw_sub["low"].min())) / aw_o
            row["aw_return"] = (float(aw_sub["close"].iloc[-1]) - aw_o) / aw_o
        else:
            row["aw_range"] = row["aw_return"] = np.nan

        aw_ext = day.between_time("10:30", "12:59")
        if len(aw_ext) >= 5:
            aw_ext_o = float(aw_ext["open"].iloc[0])
            row["aw_ext_range"] = (float(aw_ext["high"].max()) - float(aw_ext["low"].min())) / aw_ext_o
        else:
            row["aw_ext_range"] = np.nan

        # fh_rv: first-hour (09:30–10:29) annualized realized vol
        fh_bars = day.between_time("09:30", "10:29")
        if len(fh_bars) >= 10:
            fh_rets = np.log(fh_bars["close"] / fh_bars["close"].shift(1)).dropna().values
            n_fh = len(fh_rets)
            row["fh_rv"] = float(np.sqrt(np.sum(fh_rets**2) * (390 / n_fh) * 252)) if n_fh >= 5 else np.nan
        else:
            row["fh_rv"] = np.nan

        # late_rv: 15:30–15:59 annualized realized vol (signal for H24)
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

    # Rolling 252d medians → expansion flags
    for wname in _WINDOW_ENDS:
        col = f"{wname}_range"
        med = wt[col].rolling(252, min_periods=60).median()
        wt[f"{wname}_expansion"] = (wt[col] > med).astype(float)
    for col in ["aw_range", "aw_ext_range"]:
        med = wt[col].rolling(252, min_periods=60).median()
        wt[f"{col}_expansion"] = (wt[col] > med).astype(float)

    wt["range_left_pct"] = (wt["w150_range"] - wt["w60_range"]) / wt["w150_range"].replace(0, np.nan)
    return wt


# ── Signal construction ────────────────────────────────────────────────────────

def build_signal_df(wt: pd.DataFrame, daily: pd.DataFrame, ivx: pd.DataFrame) -> pd.DataFrame:
    """Merge window outcomes with premarket signals (prior EOD = shift(1))."""

    # Premarket signals from prior-day EOD daily_series
    eod_cols = ["iv_30d", "iv_60d", "hv_20_cc", "daily_range", "spread_pct"]
    sig_eod = daily[eod_cols].shift(1)
    sig_eod.columns = ["sig_" + c for c in eod_cols]

    # IVX: prior EOD (already date-indexed, shift by trading day)
    sig_ivx = ivx.shift(1)

    df = wt.join(sig_eod, how="inner").join(sig_ivx, how="left")

    # ── H44: iv term structure slope ──────────────────────────────────────────
    df["iv_spread_30_60"] = df["sig_iv_30d"] - df["sig_iv_60d"]
    df["h44_bkwd"] = (df["sig_iv_30d"] > df["sig_iv_60d"]).astype(float)

    # ── H94: IVX 7d vs 30d ───────────────────────────────────────────────────
    # ivx_spread_7_30 and ivx_bkwd already in sig_ivx (shifted)

    # ── H97: 5-day IV velocity ────────────────────────────────────────────────
    iv_vel = daily["iv_30d"].pct_change(5).shift(1)
    df["iv_velocity_5d"] = iv_vel.reindex(df.index)
    df["h97_rising"] = (df["iv_velocity_5d"] > 0).astype(float)

    # ── H70: rolling 252d rank of prior-day session range ────────────────────
    # Computed globally on date-sorted series; first 252 rows NaN (burn-in).
    prior_range = daily["daily_range"].shift(1)
    range_rank = prior_range.rolling(252, min_periods=252).rank(pct=True)
    df["range_pct_rank"] = range_rank.reindex(df.index)

    # ── H99: rolling 60d spread rank ─────────────────────────────────────────
    spread_rank = daily["spread_pct"].rolling(60, min_periods=20).rank(pct=True).shift(1)
    df["spread_pct_rank"] = spread_rank.reindex(df.index)
    df["h99_high_spread"] = (df["spread_pct_rank"] > 0.75).astype(float)

    # ── H53: IV rising + RV flat ──────────────────────────────────────────────
    iv_rising_5 = (daily["iv_30d"] > daily["iv_30d"].shift(5)).astype(float).shift(1)
    rv_flat = (daily["hv_20_cc"] < daily["iv_30d"] * 0.8).astype(float).shift(1)
    df["h53_signal"] = ((iv_rising_5 == 1) & (rv_flat == 1)).astype(float).reindex(df.index)

    # ── H24: prior-day late_rv ────────────────────────────────────────────────
    df["late_rv_prior"] = df["late_rv"].shift(1)
    late_med = df["late_rv"].rolling(252, min_periods=60).median().shift(1)
    df["h24_late_rv_high"] = (df["late_rv_prior"] > late_med).astype(float)

    # ── H48: fh_rv vs rolling 252d median ────────────────────────────────────
    fh_med = wt["fh_rv"].rolling(252, min_periods=60).median()
    df["fh_rv_med"] = fh_med
    df["h48_above_med"] = (df["fh_rv"] > df["fh_rv_med"]).astype(float)

    # H15 signal is fh_rv (continuous) — already in wt
    # H76 signal: h44_bkwd × gap_dir — computed in run_h76
    # H100 signal: gap_magnitude — already in wt

    return df


# ── Statistical utilities ──────────────────────────────────────────────────────

def cliff_delta(g1: np.ndarray, g2: np.ndarray) -> float:
    g1, g2 = np.asarray(g1, float), np.asarray(g2, float)
    if len(g1) == 0 or len(g2) == 0:
        return np.nan
    dom = int((g1[:, None] > g2[None, :]).sum()) - int((g1[:, None] < g2[None, :]).sum())
    return dom / (len(g1) * len(g2))


def mw_test(g1: np.ndarray, g2: np.ndarray, alternative: str = "two-sided") -> dict:
    g1 = np.asarray(g1, float)[np.isfinite(np.asarray(g1, float))]
    g2 = np.asarray(g2, float)[np.isfinite(np.asarray(g2, float))]
    if len(g1) < 5 or len(g2) < 5:
        return {"n_a": int(len(g1)), "n_b": int(len(g2)), "stat": None, "p": None,
                "cliff_d": None, "median_a": None, "median_b": None, "diff": None}
    stat, p = mannwhitneyu(g1, g2, alternative=alternative)
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
    return {"rho": float(rho), "p_nw": float(p_nw), "n": int(n)}


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> dict:
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[mask], y[mask], z[mask]
    n = len(x)
    if n < 20:
        rho, p = spearmanr(x, y)
        return {"partial_rho": float(rho), "partial_p": float(p), "n": n, "method": "fallback"}
    if not HAS_SM:
        rho, p = spearmanr(x, y)
        return {"partial_rho": float(rho), "partial_p": float(p), "n": n, "method": "fallback"}
    rx = scipy_rankdata(x) / n
    ry = scipy_rankdata(y) / n
    rz = scipy_rankdata(z) / n
    Z = sm.add_constant(rz)
    resid_x = sm.OLS(rx, Z).fit().resid
    resid_y = sm.OLS(ry, Z).fit().resid
    rho, p = spearmanr(resid_x, resid_y)
    return {"partial_rho": float(rho), "partial_p": float(p), "n": n, "method": "residual_ols"}


def fisher_2x2(pos_a: int, neg_a: int, pos_b: int, neg_b: int) -> dict:
    table = [[pos_a, neg_a], [pos_b, neg_b]]
    _, p2 = fisher_exact(table)
    _, pg = fisher_exact(table, alternative="greater")
    _, pl = fisher_exact(table, alternative="less")
    return {
        "table": table,
        "p_two_sided": float(p2),
        "p_greater": float(pg),
        "p_less": float(pl),
        "rate_a": round(pos_a / max(pos_a + neg_a, 1), 4),
        "rate_b": round(pos_b / max(pos_b + neg_b, 1), 4),
        "n_total": pos_a + neg_a + pos_b + neg_b,
    }


def split_by_period(df: pd.DataFrame) -> dict:
    return {
        "full":    df.loc[FULL_START:FULL_END],
        "train":   df.loc[TRAIN_START:TRAIN_END],
        "val":     df.loc[VAL_START:VAL_END],
        "holdout": df.loc[HOLD_START:HOLD_END],
    }


def wf_spearman(df: pd.DataFrame, x: str, y: str, maxlags: int = 5) -> dict:
    splits = split_by_period(df)
    results = {}
    signs = []
    for name, sub in splits.items():
        sub_c = sub[[x, y]].dropna()
        r = nw_spearman(sub_c[x].values, sub_c[y].values, maxlags)
        results[name] = r
        if name != "full" and r["rho"] is not None:
            signs.append(np.sign(r["rho"]))
    n_pos = sum(s > 0 for s in signs)
    return {"splits": results, "consistency": "consistent" if n_pos == 3 else ("mixed" if n_pos == 2 else "inconsistent"), "n_positive_splits": int(n_pos)}


def wf_mw(df: pd.DataFrame, mask_col: str, outcome: str, alternative: str = "two-sided") -> dict:
    splits = split_by_period(df)
    results = {}
    signs = []
    for name, sub in splits.items():
        sub_c = sub[[mask_col, outcome]].dropna()
        ga = sub_c.loc[sub_c[mask_col].astype(bool), outcome].values
        gb = sub_c.loc[~sub_c[mask_col].astype(bool), outcome].values
        r = mw_test(ga, gb, alternative)
        results[name] = r
        if name != "full" and r["diff"] is not None:
            signs.append(np.sign(r["diff"]))
    n_pos = sum(s > 0 for s in signs)
    return {"splits": results, "consistency": "consistent" if n_pos == 3 else ("mixed" if n_pos == 2 else "inconsistent"), "n_positive_splits": int(n_pos)}


def compute_window_rhos(df: pd.DataFrame, signal_col: str) -> dict:
    """Spearman rho of signal vs each window range."""
    result = {}
    sig = df[signal_col].values
    for wname in _WINDOW_ENDS:
        r = nw_spearman(sig, df[f"{wname}_range"].values)
        result[wname] = {"rho": r["rho"], "p_nw": r["p_nw"], "n": r["n"]}
    return result


def timing_gate(window_rhos: dict) -> tuple[str, bool]:
    """
    Returns (peak_window, early_enough).
    early_enough = peak at w150 or before AND w150 effect >= 50% of w210 effect.
    """
    effs = {k: abs(v["rho"] or 0) for k, v in window_rhos.items() if v.get("rho") is not None}
    if not effs:
        return "unknown", True
    peak = max(effs, key=effs.get)
    in_horizon = peak in ["w30", "w60", "w120", "w150"]
    w150 = effs.get("w150", 0)
    w210 = effs.get("w210", 0)
    w150_ok = (w210 == 0) or (w150 >= 0.5 * w210)
    return peak, in_horizon and w150_ok


def assign_verdict(stat_ok: bool, sign_ok: bool, n_ok: bool,
                   early_ok: bool, non_redundant: bool = True) -> str:
    if not n_ok:
        return "insufficient_data"
    if not stat_ok or not sign_ok:
        return "rejected"
    if not early_ok:
        return "too_late_for_style"
    if non_redundant:
        return "supported_trading_useful"
    return "redundant"


def _save(result: dict, stem: str) -> None:
    p = RESULTS_DIR / f"{stem}.json"
    with open(p, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"    → saved {p.name}")


# ── Per-hypothesis runners ─────────────────────────────────────────────────────

def run_h44(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H44.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H44: running...")
    sub = df.dropna(subset=["iv_spread_30_60", "w150_range"]).copy()
    n = len(sub)

    wr = compute_window_rhos(sub, "iv_spread_30_60")
    peak_w, early_ok = timing_gate(wr)
    sp_full = nw_spearman(sub["iv_spread_30_60"].values, sub["w150_range"].values)
    wf_sp = wf_spearman(sub, "iv_spread_30_60", "w150_range")
    wf_binary = wf_mw(sub.dropna(subset=["h44_bkwd"]), "h44_bkwd", "w150_range")

    rho = wf_sp["splits"]["full"].get("rho") or 0
    p = wf_sp["splits"]["full"].get("p_nw") or 1
    train_rho = wf_sp["splits"]["train"].get("rho") or 0
    val_rho   = wf_sp["splits"]["val"].get("rho") or 0
    stat_ok = abs(rho) > 0.10 and p < 0.10
    sign_ok = (train_rho * val_rho) > 0
    verdict = assign_verdict(stat_ok, sign_ok, n >= 120, early_ok)

    result = {
        "hypothesis_number": "H44",
        "signal_strength_tier": "core-strong",
        "tier_rationale": "Phase 2 Cliff's d=0.551; robust across train/val/holdout",
        "role": "premarket_framing",
        "signal_availability": "pre_open",
        "signal": "iv_30d - iv_60d (continuous); binary iv_30d > iv_60d",
        "primary_outcome": "w150_range",
        "outcome_type": "expansion_compression",
        "n_total": n,
        "primary_spearman": sp_full,
        "walk_forward_spearman": wf_sp,
        "walk_forward_mw_binary": wf_binary,
        "window_rhos": wr,
        "peak_window": peak_w,
        "early_enough_for_style": early_ok,
        "phase3_verdict": verdict,
        "verdict_reason": f"rho={rho:.3f}, p_nw={p:.4f}, peak={peak_w}, sign_ok={sign_ok}",
    }
    _save(result, "phase3_H44")
    return result


def run_h94(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H94.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H94: running...")
    sub = df.dropna(subset=["ivx_spread_7_30", "w150_range"]).copy()
    n = len(sub)

    wr = compute_window_rhos(sub, "ivx_spread_7_30")
    peak_w, early_ok = timing_gate(wr)
    sp_full = nw_spearman(sub["ivx_spread_7_30"].values, sub["w150_range"].values)
    wf_sp = wf_spearman(sub, "ivx_spread_7_30", "w150_range")
    wf_binary = wf_mw(sub.dropna(subset=["ivx_bkwd"]), "ivx_bkwd", "w150_range")

    rho = wf_sp["splits"]["full"].get("rho") or 0
    p   = wf_sp["splits"]["full"].get("p_nw") or 1
    tr  = wf_sp["splits"]["train"].get("rho") or 0
    vr  = wf_sp["splits"]["val"].get("rho") or 0
    stat_ok = abs(rho) > 0.10 and p < 0.10
    sign_ok = (tr * vr) > 0
    verdict = assign_verdict(stat_ok, sign_ok, n >= 120, early_ok)

    result = {
        "hypothesis_number": "H94",
        "signal_strength_tier": "core-fragile",
        "tier_rationale": "Phase 2 holdout weakens; correlated with H44",
        "role": "premarket_framing",
        "signal_availability": "pre_open",
        "signal": "IVX_7d - IVX_30d (continuous); binary IVX_7d > IVX_30d",
        "primary_outcome": "w150_range",
        "outcome_type": "expansion_compression",
        "n_total": n,
        "primary_spearman": sp_full,
        "walk_forward_spearman": wf_sp,
        "walk_forward_mw_binary": wf_binary,
        "window_rhos": wr,
        "peak_window": peak_w,
        "early_enough_for_style": early_ok,
        "phase3_verdict": verdict,
        "verdict_reason": f"rho={rho:.3f}, p_nw={p:.4f}, peak={peak_w}, sign_ok={sign_ok}",
    }
    _save(result, "phase3_H94")
    return result


def run_h97(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H97.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H97: running...")
    sub = df.dropna(subset=["iv_velocity_5d", "w150_range"]).copy()
    n = len(sub)

    wr = compute_window_rhos(sub, "iv_velocity_5d")
    peak_w, early_ok = timing_gate(wr)
    sp_full = nw_spearman(sub["iv_velocity_5d"].values, sub["w150_range"].values)
    wf_sp = wf_spearman(sub, "iv_velocity_5d", "w150_range")
    wf_binary = wf_mw(sub.dropna(subset=["h97_rising"]), "h97_rising", "w150_range")

    rho = wf_sp["splits"]["full"].get("rho") or 0
    p   = wf_sp["splits"]["full"].get("p_nw") or 1
    tr  = wf_sp["splits"]["train"].get("rho") or 0
    vr  = wf_sp["splits"]["val"].get("rho") or 0
    stat_ok = abs(rho) > 0.10 and p < 0.10
    sign_ok = (tr * vr) > 0
    verdict = assign_verdict(stat_ok, sign_ok, n >= 120, early_ok)

    result = {
        "hypothesis_number": "H97",
        "signal_strength_tier": "core-fragile",
        "tier_rationale": "Phase 2 holdout n=14; statistically underpowered in holdout",
        "role": "premarket_framing",
        "signal_availability": "pre_open",
        "signal": "iv_30d.pct_change(5) prior day (continuous); binary > 0",
        "primary_outcome": "w150_range",
        "outcome_type": "expansion_compression",
        "n_total": n,
        "primary_spearman": sp_full,
        "walk_forward_spearman": wf_sp,
        "walk_forward_mw_binary": wf_binary,
        "window_rhos": wr,
        "peak_window": peak_w,
        "early_enough_for_style": early_ok,
        "phase3_verdict": verdict,
        "verdict_reason": f"rho={rho:.3f}, p_nw={p:.4f}, peak={peak_w}, sign_ok={sign_ok}",
    }
    _save(result, "phase3_H97")
    return result


def run_h70(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H70.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H70: running...")
    # Burn-in: range_pct_rank requires 252 prior rows → NaN for 2024 train period
    sub = df.dropna(subset=["range_pct_rank", "w150_range"]).copy()
    n = len(sub)
    n_train = len(sub.loc[TRAIN_START:TRAIN_END])

    wr = compute_window_rhos(sub, "range_pct_rank")
    peak_w, early_ok = timing_gate(wr)
    sp_full = nw_spearman(sub["range_pct_rank"].values, sub["w150_range"].values)
    wf_sp = wf_spearman(sub, "range_pct_rank", "w150_range")

    rho = wf_sp["splits"]["full"].get("rho") or 0
    p   = wf_sp["splits"]["full"].get("p_nw") or 1
    # For H70, train is NaN (burn-in). Use val/holdout for sign consistency.
    vr  = wf_sp["splits"]["val"].get("rho") or 0
    hr  = wf_sp["splits"]["holdout"].get("rho") or 0
    sign_ok = (vr * hr) > 0 if (vr != 0 and hr != 0) else None   # None = cannot assess
    stat_ok = abs(rho) > 0.10 and p < 0.10

    burn_in_note = (
        "252-day rolling window consumes all 2024 training data. "
        f"n_train={n_train} (all NaN due to burn-in). "
        "Phase 3 conclusions are out-of-sample only (val + holdout). "
        "No in-sample reference period. Treat with additional caution."
    )

    # sign consistency: val vs holdout (no train)
    sign_ok_flag = bool(sign_ok) if sign_ok is not None else (vr > 0)

    verdict = assign_verdict(stat_ok, sign_ok_flag, n >= 80, early_ok)

    result = {
        "hypothesis_number": "H70",
        "signal_strength_tier": "core-fragile/no-train",
        "tier_rationale": "252-day burn-in leaves NO train split. Val+holdout only.",
        "role": "premarket_framing",
        "signal_availability": "pre_open",
        "signal": "prior_day_range.rolling(252, min_periods=252).rank(pct=True). Global computation, no split leakage.",
        "primary_outcome": "w150_range",
        "outcome_type": "day_quality_framing",
        "n_total": n,
        "n_train_after_burnin": n_train,
        "burn_in_warning": burn_in_note,
        "primary_spearman": sp_full,
        "walk_forward_spearman": wf_sp,
        "walk_forward_note": "Train split = NaN by design (burn-in). Sign consistency assessed from val+holdout only.",
        "window_rhos": wr,
        "peak_window": peak_w,
        "early_enough_for_style": early_ok,
        "phase3_verdict": verdict,
        "verdict_reason": f"rho={rho:.3f}, p_nw={p:.4f}, peak={peak_w}, val_rho={vr:.3f}, holdout_rho={hr:.3f}",
    }
    _save(result, "phase3_H70")
    return result


def run_h99(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H99.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H99: running...")
    sub = df.dropna(subset=["spread_pct_rank", "w150_range"]).copy()
    n = len(sub)

    wr = compute_window_rhos(sub, "spread_pct_rank")
    peak_w, early_ok = timing_gate(wr)
    sp_full = nw_spearman(sub["spread_pct_rank"].values, sub["w150_range"].values)
    wf_sp = wf_spearman(sub, "spread_pct_rank", "w150_range")

    # Caution flag: high spread days (> 75th pctile)
    caution_days = int((sub["spread_pct_rank"] > 0.75).sum())
    caution_pct = round(caution_days / max(n, 1), 3)

    # Direction test — SECONDARY, only if range effect is first established
    sp_direction = nw_spearman(sub["spread_pct_rank"].values, sub["w150_return"].values)

    rho = wf_sp["splits"]["full"].get("rho") or 0
    p   = wf_sp["splits"]["full"].get("p_nw") or 1
    tr  = wf_sp["splits"]["train"].get("rho") or 0
    vr  = wf_sp["splits"]["val"].get("rho") or 0
    stat_ok = abs(rho) > 0.10 and p < 0.10
    sign_ok = (tr * vr) > 0
    verdict = assign_verdict(stat_ok, sign_ok, n >= 120, early_ok)

    result = {
        "hypothesis_number": "H99",
        "signal_strength_tier": "core-fragile",
        "tier_rationale": "Phase 2 rho=0.304; caution overlay interpretation, not directional",
        "role": "premarket_framing_caution_overlay",
        "signal_availability": "pre_open",
        "signal": "rolling 60d rank of (ask-bid)/close (continuous [0,1])",
        "primary_outcome": "w150_range",
        "outcome_type": "liquidity_premium_caution",
        "h99_interpretation_note": (
            "Primary interpretation: CAUTION OVERLAY. "
            "High spread_pct_rank (>0.75) flags liquidity-constrained days. "
            "Directional interpretation (w150_return) is SECONDARY and only reported if "
            "range effect is clearly established first. Do not default to direction framing."
        ),
        "n_total": n,
        "n_caution_days": caution_days,
        "caution_days_pct": caution_pct,
        "primary_spearman_range": sp_full,
        "secondary_spearman_direction": sp_direction,
        "walk_forward_spearman": wf_sp,
        "window_rhos": wr,
        "peak_window": peak_w,
        "early_enough_for_style": early_ok,
        "phase3_verdict": verdict,
        "verdict_reason": f"rho_range={rho:.3f}, p_nw={p:.4f}, peak={peak_w}, sign_ok={sign_ok}",
    }
    _save(result, "phase3_H99")
    return result


def run_h24(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H24.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H24: running...")

    # Filter: only gap days; gap is already known at open
    gap_df = df[df["gap_magnitude"].fillna(0) >= MIN_GAP].copy()
    sub = gap_df.dropna(subset=["late_rv_prior", "gap_fill_30"]).copy()
    n = len(sub)

    # Primary: Fisher's exact — late_rv_high (binary) × gap_fill_30 (binary)
    late_high = sub["h24_late_rv_high"] == 1
    filled_30 = sub["gap_fill_30"] == 1

    a = int((late_high & filled_30).sum())
    b = int((late_high & ~filled_30).sum())
    c = int((~late_high & filled_30).sum())
    d = int((~late_high & ~filled_30).sum())
    fisher_result = fisher_2x2(a, b, c, d) if (a + b >= 5 and c + d >= 5) else {"note": "insufficient n"}

    # gap_fill_60
    sub60 = gap_df.dropna(subset=["late_rv_prior", "gap_fill_60"]).copy()
    late_high_60 = sub60["h24_late_rv_high"] == 1
    filled_60 = sub60["gap_fill_60"] == 1
    a2 = int((late_high_60 & filled_60).sum())
    b2 = int((late_high_60 & ~filled_60).sum())
    c2 = int((~late_high_60 & filled_60).sum())
    d2 = int((~late_high_60 & ~filled_60).sum())
    fisher_60 = fisher_2x2(a2, b2, c2, d2) if (a2 + b2 >= 5 and c2 + d2 >= 5) else {"note": "insufficient n"}

    # Secondary: continuous late_rv_prior vs w30/w60 range and return
    sp_w30r = nw_spearman(sub["late_rv_prior"].values, sub["w30_range"].dropna().reindex(sub.index).values)
    sp_w60r = nw_spearman(sub["late_rv_prior"].values, sub["w60_range"].dropna().reindex(sub.index).values)
    sp_w30ret = nw_spearman(sub["late_rv_prior"].values, sub["w30_return"].dropna().reindex(sub.index).values)
    sp_w60ret = nw_spearman(sub["late_rv_prior"].values, sub["w60_return"].dropna().reindex(sub.index).values)

    # Overnight gap magnitude note (demoted from primary)
    sp_gap = nw_spearman(
        df.dropna(subset=["late_rv_prior", "overnight_gap"])["late_rv_prior"].values,
        df.dropna(subset=["late_rv_prior", "overnight_gap"])["overnight_gap"].abs().values
    )

    # Verdict via Fisher p (primary) and spearman on secondary
    primary_p = fisher_result.get("p_two_sided", 1.0) if isinstance(fisher_result, dict) else 1.0
    stat_ok = primary_p < 0.10
    # For sign consistency: use w30_return direction consistency across splits
    wf_w30ret = wf_spearman(sub.dropna(subset=["late_rv_prior", "w30_return"]), "late_rv_prior", "w30_return")
    tr = wf_w30ret["splits"]["train"].get("rho") or 0
    vr = wf_w30ret["splits"]["val"].get("rho") or 0
    sign_ok = (tr * vr) > 0

    verdict = assign_verdict(stat_ok, sign_ok, n >= 80, True)

    result = {
        "hypothesis_number": "H24",
        "signal_strength_tier": "core-fragile",
        "tier_rationale": "Phase 2 holdout rho=0.148, p=0.30; weakens in 2026 Q1",
        "role": "premarket_framing_post_gap_context",
        "signal_availability": "pre_open_prior_close",
        "signal": "late_rv = annualized realized vol 15:30-15:59 (prior day); binary: > rolling 252d median",
        "primary_outcome": "gap_fill_30 / gap_fill_60 (binary fill within 30/60 min after open)",
        "outcome_type": "fill_continuation",
        "phase3_note": (
            "Gap is known at 9:31. Phase 3 tests whether prior-day late_rv helps interpret "
            "what happens AFTER the gap is known: fill vs extend in the first 30-60 min. "
            "Overnight gap magnitude retained only as secondary reference."
        ),
        "n_gap_days_with_signal": n,
        "fisher_late_rv_high_vs_gap_fill_30": fisher_result,
        "fisher_late_rv_high_vs_gap_fill_60": fisher_60,
        "secondary_spearman_w30_range": sp_w30r,
        "secondary_spearman_w60_range": sp_w60r,
        "secondary_spearman_w30_return": sp_w30ret,
        "secondary_spearman_w60_return": sp_w60ret,
        "walk_forward_spearman_w30_return": wf_w30ret,
        "secondary_reference_gap_magnitude": sp_gap,
        "phase3_verdict": verdict,
        "verdict_reason": f"fisher_p30={primary_p:.4f}, w30_return_sign_ok={sign_ok}, n={n}",
    }
    _save(result, "phase3_H24")
    return result


def run_h53(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H53.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H53: running...")
    sub = df.dropna(subset=["h53_signal", "w150_range", "w150_expansion"]).copy()
    n_signal = int(sub["h53_signal"].sum())
    n_no_signal = int((sub["h53_signal"] == 0).sum())

    wf_binary = wf_mw(sub, "h53_signal", "w150_range")
    sp_expansion = nw_spearman(sub["h53_signal"].values, sub["w150_expansion"].values)

    cd_full = cliff_delta(
        sub.loc[sub["h53_signal"] == 1, "w150_range"].values,
        sub.loc[sub["h53_signal"] == 0, "w150_range"].values,
    )

    tr_d = wf_binary["splits"]["train"].get("cliff_d") or 0
    vr_d = wf_binary["splits"]["val"].get("cliff_d") or 0
    stat_ok = abs(cd_full) > 0.10 and (wf_binary["splits"]["full"].get("p") or 1) < 0.10
    sign_ok = (tr_d * vr_d) > 0
    verdict = assign_verdict(stat_ok, sign_ok, n_signal >= 30 and n_no_signal >= 30, True)

    result = {
        "hypothesis_number": "H53",
        "signal_strength_tier": "exploratory",
        "tier_rationale": "Phase 2 p=0.155; likely to remain inconclusive",
        "role": "premarket_framing",
        "signal_availability": "pre_open",
        "signal": "(iv_30d > iv_30d.shift(5)) AND (hv_20_cc < iv_30d * 0.8) — prior day binary",
        "primary_outcome": "w150_expansion",
        "outcome_type": "day_quality_framing",
        "n_signal_days": n_signal,
        "n_no_signal_days": n_no_signal,
        "cliff_d_full": float(cd_full),
        "walk_forward_mw": wf_binary,
        "spearman_vs_expansion": sp_expansion,
        "phase3_verdict": verdict,
        "verdict_reason": f"cliff_d={cd_full:.3f}, p={wf_binary['splits']['full'].get('p'):.4f}, sign_ok={sign_ok}",
    }
    _save(result, "phase3_H53")
    return result


def run_h76(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H76.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H76: running...")

    # Gap days only
    gap_df = df[df["gap_magnitude"].fillna(0) >= MIN_GAP].copy()
    gap_df = gap_df.dropna(subset=["gap_fill_30", "h44_bkwd", "overnight_gap_dir", "gap_magnitude"])
    n = len(gap_df)

    if n < 30:
        result = {"hypothesis_number": "H76", "phase3_verdict": "insufficient_data",
                  "verdict_reason": f"only {n} gap days"}
        _save(result, "phase3_H76")
        return result

    bkwd = gap_df["h44_bkwd"] == 1
    gap_up = gap_df["overnight_gap_dir"] == 1

    # ── Primary: Fisher's exact (2×2 bkwd × gap_fill_30) ─────────────────────
    a = int((bkwd & (gap_df["gap_fill_30"] == 1)).sum())
    b = int((bkwd & (gap_df["gap_fill_30"] == 0)).sum())
    c = int((~bkwd & (gap_df["gap_fill_30"] == 1)).sum())
    d = int((~bkwd & (gap_df["gap_fill_30"] == 0)).sum())
    fisher_bkwd_fill = fisher_2x2(a, b, c, d)

    # ── 4-cell grid: bkwd × gap_dir → fill rate ───────────────────────────────
    grid = {}
    for b_flag, b_label in [(True, "bkwd"), (False, "contango")]:
        for g_flag, g_label in [(True, "gap_up"), (False, "gap_down")]:
            mask = (bkwd == b_flag) & (gap_up == g_flag)
            sub_g = gap_df.loc[mask, "gap_fill_30"]
            grid[f"{b_label}_{g_label}"] = {
                "n": int(mask.sum()),
                "fill_rate_30": round(float(sub_g.mean()), 4) if len(sub_g) >= 5 else None,
            }

    # ── Logistic regression: fill ~ bkwd + gap_up + bkwd×gap_up + gap_magnitude ─
    logit_result: dict = {"note": "statsmodels not available"}
    if HAS_SM and n >= 30:
        gap_df["gap_up_bin"] = gap_up.astype(float)
        gap_df["bkwd_x_gapup"] = gap_df["h44_bkwd"] * gap_df["gap_up_bin"]
        X = sm.add_constant(gap_df[["h44_bkwd", "gap_up_bin", "bkwd_x_gapup", "gap_magnitude"]])
        try:
            logit = sm.Logit(gap_df["gap_fill_30"], X).fit(disp=0)
            logit_result = {
                "n": n,
                "bkwd_coef": float(logit.params["h44_bkwd"]),
                "bkwd_p": float(logit.pvalues["h44_bkwd"]),
                "gap_up_coef": float(logit.params["gap_up_bin"]),
                "gap_up_p": float(logit.pvalues["gap_up_bin"]),
                "bkwd_x_gapup_coef": float(logit.params["bkwd_x_gapup"]),
                "bkwd_x_gapup_p": float(logit.pvalues["bkwd_x_gapup"]),
                "gap_magnitude_coef": float(logit.params["gap_magnitude"]),
                "gap_magnitude_p": float(logit.pvalues["gap_magnitude"]),
                "pseudo_r2": float(logit.prsquared),
                "note": "gap_magnitude included as control to isolate bkwd x gap_dir from gap-size confound",
            }
        except Exception as e:
            logit_result = {"error": str(e)}

    # ── Secondary: Cliff's d on continuous outcomes ───────────────────────────
    bkwd_vals = gap_df.loc[bkwd, "w60_range"].dropna().values
    cont_vals  = gap_df.loc[~bkwd, "w60_range"].dropna().values
    cd_w60 = float(cliff_delta(bkwd_vals, cont_vals))
    bkwd_120 = gap_df.loc[bkwd, "w120_range"].dropna().values
    cont_120  = gap_df.loc[~bkwd, "w120_range"].dropna().values
    cd_w120 = float(cliff_delta(bkwd_120, cont_120))

    # Verdict via Fisher p (primary)
    primary_p = fisher_bkwd_fill.get("p_two_sided", 1.0)
    stat_ok = primary_p < 0.10
    verdict = assign_verdict(stat_ok, True, n >= 60, True)

    result = {
        "hypothesis_number": "H76",
        "signal_strength_tier": "exploratory",
        "tier_rationale": "Phase 2 fill_diff negligible; first_2h_range Cliff's d=0.44 survived",
        "role": "hybrid_preopen_plus_gap",
        "signal_availability": "9:31_ET",
        "signal": "bkwd_binary (iv_30d > iv_60d, prior day) × overnight_gap_dir",
        "primary_outcome": "gap_fill_30 (binary)",
        "outcome_type": "fill_continuation",
        "n_gap_days": n,
        "fisher_bkwd_vs_gap_fill_30": fisher_bkwd_fill,
        "grid_4cell_bkwd_x_gapdir": grid,
        "logistic_regression": logit_result,
        "secondary_cliff_d_w60_range": {"cliff_d": cd_w60, "n_bkwd": len(bkwd_vals), "n_cont": len(cont_vals)},
        "secondary_cliff_d_w120_range": {"cliff_d": cd_w120},
        "phase3_verdict": verdict,
        "verdict_reason": f"fisher_p_two_sided={primary_p:.4f}, logit_bkwd_p={logit_result.get('bkwd_p', 'na')}, n={n}",
    }
    _save(result, "phase3_H76")
    return result


def run_h100(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H100.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H100: running...")
    gap_df = df[df["gap_magnitude"].fillna(0) >= MIN_GAP].copy()
    sub = gap_df.dropna(subset=["gap_magnitude", "gap_fill_30"]).copy()
    n = len(sub)

    # Fisher: high gap (> median) vs low gap
    gap_med = sub["gap_magnitude"].median()
    big_gap = sub["gap_magnitude"] > gap_med
    filled = sub["gap_fill_30"] == 1
    a = int((big_gap & filled).sum())
    b = int((big_gap & ~filled).sum())
    c = int((~big_gap & filled).sum())
    d = int((~big_gap & ~filled).sum())
    fisher_result = fisher_2x2(a, b, c, d)

    sp_w30r = nw_spearman(sub["gap_magnitude"].values, sub["w30_range"].dropna().reindex(sub.index).values)
    sp_w120r = nw_spearman(sub["gap_magnitude"].values, sub["w120_range"].dropna().reindex(sub.index).values)

    primary_p = fisher_result.get("p_two_sided", 1.0)
    stat_ok = primary_p < 0.10
    verdict = assign_verdict(stat_ok, True, n >= 60, True)

    result = {
        "hypothesis_number": "H100",
        "signal_strength_tier": "exploratory",
        "tier_rationale": "Phase 2 barely above threshold; expect weak result",
        "role": "intraday_early_gap_at_open",
        "signal_availability": "9:31_ET",
        "signal": "|open_0930 - prev_close| / prev_close (gap magnitude)",
        "primary_outcome": "gap_fill_30 (binary)",
        "outcome_type": "fill_continuation",
        "n_gap_days": n,
        "gap_magnitude_median": float(gap_med),
        "fisher_big_vs_small_gap_vs_fill_30": fisher_result,
        "secondary_spearman_w30_range": sp_w30r,
        "secondary_spearman_w120_range": sp_w120r,
        "phase3_verdict": verdict,
        "verdict_reason": f"fisher_p_two_sided={primary_p:.4f}, n={n}",
    }
    _save(result, "phase3_H100")
    return result


def run_h15(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H15.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H15: running...")
    sub = df.dropna(subset=["fh_rv", "aw_range"]).copy()
    n = len(sub)

    # Primary: Spearman fh_rv → aw_range (10:30-11:59, core 1.5h)
    sp_full = nw_spearman(sub["fh_rv"].values, sub["aw_range"].values)
    wf_sp = wf_spearman(sub, "fh_rv", "aw_range")

    # Extended window (secondary reference)
    sp_ext = nw_spearman(sub["fh_rv"].values, sub["aw_ext_range"].dropna().reindex(sub.index).values)

    # range_left_pct
    sp_rleft = nw_spearman(sub["fh_rv"].values, sub["range_left_pct"].dropna().reindex(sub.index).values)

    rho = wf_sp["splits"]["full"].get("rho") or 0
    p   = wf_sp["splits"]["full"].get("p_nw") or 1
    tr  = wf_sp["splits"]["train"].get("rho") or 0
    vr  = wf_sp["splits"]["val"].get("rho") or 0
    stat_ok = abs(rho) > 0.10 and p < 0.10
    sign_ok = (tr * vr) > 0
    # H15/H48 are intraday confirmation — timing gate not applicable (signal at 10:30, outcome starts 10:30)
    verdict = assign_verdict(stat_ok, sign_ok, n >= 120, True)

    result = {
        "hypothesis_number": "H15",
        "signal_strength_tier": "core-strong",
        "tier_rationale": "Phase 2 rho=0.618 all-dates, rho=0.508 high-cov; consistent splits",
        "role": "intraday_confirmation",
        "signal_availability": "10:30_ET",
        "signal": "fh_rv = annualized realized vol from 1m bars 09:30-10:29 (60 bars)",
        "primary_outcome": "aw_range (10:30-11:59, core 1.5h)",
        "secondary_outcome": "aw_ext_range (10:30-12:59, extended 2.5h — reference only)",
        "outcome_type": "range_left_move_done",
        "n_total": n,
        "primary_spearman_aw_core": sp_full,
        "walk_forward_spearman_aw_core": wf_sp,
        "secondary_spearman_aw_extended": sp_ext,
        "secondary_spearman_range_left_pct": sp_rleft,
        "phase3_verdict": verdict,
        "verdict_reason": f"rho_aw_core={rho:.3f}, p_nw={p:.4f}, sign_ok={sign_ok}",
    }
    _save(result, "phase3_H15")
    return result


def run_h48(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_H48.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  H48: running...")
    sub = df.dropna(subset=["h48_above_med", "aw_range"]).copy()
    n = len(sub)

    # Primary: MW + Cliff's d — high fh_rv vs low fh_rv → aw_range
    wf_binary = wf_mw(sub, "h48_above_med", "aw_range")
    cd_full = cliff_delta(
        sub.loc[sub["h48_above_med"] == 1, "aw_range"].values,
        sub.loc[sub["h48_above_med"] == 0, "aw_range"].values,
    )

    # Extended (secondary reference)
    sub_ext = sub.dropna(subset=["aw_ext_range"]).copy()
    cd_ext = cliff_delta(
        sub_ext.loc[sub_ext["h48_above_med"] == 1, "aw_ext_range"].values,
        sub_ext.loc[sub_ext["h48_above_med"] == 0, "aw_ext_range"].values,
    )

    # range_left_pct
    sub_rl = sub.dropna(subset=["range_left_pct"]).copy()
    cd_rleft = cliff_delta(
        sub_rl.loc[sub_rl["h48_above_med"] == 1, "range_left_pct"].values,
        sub_rl.loc[sub_rl["h48_above_med"] == 0, "range_left_pct"].values,
    )

    tr_d = wf_binary["splits"]["train"].get("cliff_d") or 0
    vr_d = wf_binary["splits"]["val"].get("cliff_d") or 0
    p_full = wf_binary["splits"]["full"].get("p") or 1
    stat_ok = abs(cd_full) > 0.10 and p_full < 0.10
    sign_ok = (tr_d * vr_d) > 0
    verdict = assign_verdict(stat_ok, sign_ok, n >= 120, True)

    result = {
        "hypothesis_number": "H48",
        "signal_strength_tier": "core-strong",
        "tier_rationale": "Phase 2 Cliff's d=0.536; direct afternoon range test",
        "role": "intraday_confirmation",
        "signal_availability": "10:30_ET",
        "signal": "fh_rv > rolling 252d median of fh_rv (binary)",
        "primary_outcome": "aw_range (10:30-11:59, core 1.5h)",
        "secondary_outcome": "aw_ext_range (10:30-12:59, extended — reference only), range_left_pct",
        "outcome_type": "range_left_move_done",
        "n_total": n,
        "cliff_d_full_aw_core": float(cd_full),
        "walk_forward_mw_aw_core": wf_binary,
        "secondary_cliff_d_aw_ext": float(cd_ext),
        "secondary_cliff_d_range_left_pct": float(cd_rleft),
        "phase3_verdict": verdict,
        "verdict_reason": f"cliff_d_aw_core={cd_full:.3f}, p={p_full:.4f}, sign_ok={sign_ok}",
    }
    _save(result, "phase3_H48")
    return result


# ── Redundancy audit ───────────────────────────────────────────────────────────

def run_redundancy_audit(df: pd.DataFrame, force: bool = False) -> dict:
    out = RESULTS_DIR / "phase3_redundancy_audit.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    print("  Redundancy audit: running...")

    sigs = {
        "H44_iv_spread_30_60": "iv_spread_30_60",
        "H94_ivx_spread_7_30": "ivx_spread_7_30",
        "H97_iv_velocity_5d":  "iv_velocity_5d",
        "H70_range_pct_rank":  "range_pct_rank",
        "H99_spread_pct_rank": "spread_pct_rank",
    }
    outcome = "w150_range"
    sig_cols = list(sigs.values())
    sub = df.dropna(subset=sig_cols + [outcome])
    n = len(sub)

    # Pairwise Spearman between signals
    pair_matrix: dict = {}
    for na, ca in sigs.items():
        pair_matrix[na] = {}
        for nb, cb in sigs.items():
            r = nw_spearman(sub[ca].values, sub[cb].values)
            pair_matrix[na][nb] = round(r["rho"] or 0, 3)

    # Partial Spearman: each signal vs outcome, controlling for most correlated other
    partial_results: dict = {}
    for name, col in sigs.items():
        # Find strongest correlated other signal
        others = [(nm, cm) for nm, cm in sigs.items() if nm != name]
        best_nm, best_cm = max(others, key=lambda x: abs(pair_matrix[name].get(x[0], 0)))
        ps = partial_spearman(sub[col].values, sub[outcome].values, sub[best_cm].values)
        redundant = (
            abs(ps.get("partial_rho") or 0) < 0.07
            and abs(pair_matrix[name].get(best_nm, 0)) > 0.50
        )
        partial_results[name] = {
            "partial_spearman_vs_w150_range": ps,
            "strongest_correlated_signal": best_nm,
            "signal_signal_rho": round(pair_matrix[name].get(best_nm, 0), 3),
            "flagged_redundant": redundant,
        }

    result = {
        "run_date": date.today().isoformat(),
        "n_observations": n,
        "signals_tested": list(sigs.keys()),
        "pairwise_signal_correlation_matrix": pair_matrix,
        "partial_spearman_vs_w150_range": partial_results,
        "interpretation": (
            "flagged_redundant=True: |partial_rho| < 0.07 AND strongest signal-signal rho > 0.50. "
            "Composite signal (Phase 3B) should only include non-redundant survivors."
        ),
    }
    _save(result, "phase3_redundancy_audit")
    return result


# ── Vault append ───────────────────────────────────────────────────────────────

_VERDICT_LABEL = {
    "supported_trading_useful": "✅ SUPPORTED — Trading Useful",
    "supported_forecasting_only": "⚠️ SUPPORTED — Forecasting Only",
    "inconclusive": "⚠️ INCONCLUSIVE",
    "insufficient_data": "⛔ INSUFFICIENT DATA",
    "redundant": "🔁 REDUNDANT",
    "too_late_for_style": "⏰ TOO LATE FOR STYLE",
    "rejected": "❌ REJECTED",
}


def append_vault_note(r: dict) -> None:
    hnum = r["hypothesis_number"].upper()
    # Find matching file: vault/Backtests/h{N}-*.md (case insensitive)
    num = hnum.replace("H", "").lower()
    matches = list(VAULT_BACKTESTS.glob(f"h{num}-*.md")) + list(VAULT_BACKTESTS.glob(f"H{num}-*.md"))
    if not matches:
        print(f"    ! No vault file found for {hnum} in {VAULT_BACKTESTS}")
        return
    vault_file = matches[0]

    existing = vault_file.read_text()
    if "## Phase 3" in existing:
        print(f"    (Phase 3 section already present in {vault_file.name})")
        return

    verdict = r.get("phase3_verdict", "unknown")
    verdict_label = _VERDICT_LABEL.get(verdict, verdict.upper())
    tier = r.get("signal_strength_tier", "?")
    role = r.get("role", "?")
    signal = r.get("signal", "?")
    primary_out = r.get("primary_outcome", "?")
    reason = r.get("verdict_reason", "?")
    n = r.get("n_total") or r.get("n_gap_days") or r.get("n_gap_days_with_signal") or "?"

    lines = [
        "",
        "---",
        "",
        "## Phase 3 — Trading Utility Test",
        "",
        f"**Verdict:** {verdict_label}",
        f"**Signal Strength Tier:** {tier}",
        f"**Role:** {role}",
        f"**Signal:** {signal}",
        f"**Primary Outcome:** {primary_out}",
        f"**n:** {n}",
        f"**Verdict Reason:** {reason}",
        "",
    ]

    # Walk-forward table (if present)
    wf = r.get("walk_forward_spearman") or r.get("walk_forward_mw_binary") or r.get("walk_forward_spearman_aw_core") or r.get("walk_forward_mw_aw_core")
    if wf and "splits" in wf:
        sp_or_mw = "rho" in (list(wf["splits"].values()) or [{}])[0]
        if sp_or_mw:
            lines += ["| Split | rho | p_nw | n |", "|---|---|---|---|"]
            for split, s in wf["splits"].items():
                rho = s.get("rho"); p = s.get("p_nw"); nn = s.get("n")
                lines.append(f"| {split} | {f'{rho:.3f}' if rho is not None else 'n/a'} | {f'{p:.4f}' if p is not None else 'n/a'} | {nn} |")
        else:
            lines += ["| Split | Cliff's d | p | n_a | n_b |", "|---|---|---|---|---|"]
            for split, s in wf["splits"].items():
                cd = s.get("cliff_d"); p = s.get("p"); na = s.get("n_a"); nb = s.get("n_b")
                lines.append(f"| {split} | {f'{cd:.3f}' if cd is not None else 'n/a'} | {f'{p:.4f}' if p is not None else 'n/a'} | {na} | {nb} |")
        lines.append(f"**Consistency:** {wf.get('consistency', '?')} ({wf.get('n_positive_splits', '?')}/3)")
        lines.append("")

    # Window rhos (if present)
    wr = r.get("window_rhos")
    if wr:
        lines += ["**Effect by window (rho vs signal):**", ""]
        lines += ["| Window | rho | p_nw |", "|---|---|---|"]
        for wname, s in wr.items():
            rho = s.get("rho"); p = s.get("p_nw")
            lines.append(f"| {wname} | {f'{rho:.3f}' if rho is not None else 'n/a'} | {f'{p:.4f}' if p is not None else 'n/a'} |")
        peak = r.get("peak_window"); early = r.get("early_enough_for_style")
        lines.append(f"**Peak window:** {peak} | **Early enough for style:** {early}")
        lines.append("")

    if r.get("burn_in_warning"):
        lines += [f"> ⚠️ **Burn-in warning:** {r['burn_in_warning']}", ""]

    if r.get("h99_interpretation_note"):
        lines += [f"> ℹ️ {r['h99_interpretation_note']}", ""]

    if r.get("phase3_note"):
        lines += [f"> ℹ️ {r['phase3_note']}", ""]

    vault_file.write_text(existing + "\n".join(lines))
    print(f"    → appended Phase 3 to {vault_file.name}")


# ── Summary export ─────────────────────────────────────────────────────────────

def export_summary(results: list[dict], redundancy: dict) -> None:
    summary = {
        "run_date": date.today().isoformat(),
        "hypotheses": {},
    }
    for r in results:
        hnum = r["hypothesis_number"]
        summary["hypotheses"][hnum] = {
            "signal_strength_tier": r.get("signal_strength_tier"),
            "role": r.get("role"),
            "primary_outcome": r.get("primary_outcome"),
            "phase3_verdict": r.get("phase3_verdict"),
            "verdict_reason": r.get("verdict_reason"),
        }

    summary["redundancy_flags"] = {
        nm: info.get("flagged_redundant")
        for nm, info in (redundancy.get("partial_spearman_vs_w150_range") or {}).items()
    }

    n_useful = sum(1 for r in results if r.get("phase3_verdict") == "supported_trading_useful")
    n_late   = sum(1 for r in results if r.get("phase3_verdict") == "too_late_for_style")
    n_inconc = sum(1 for r in results if r.get("phase3_verdict") == "inconclusive")
    n_reject = sum(1 for r in results if r.get("phase3_verdict") == "rejected")
    n_insuf  = sum(1 for r in results if r.get("phase3_verdict") == "insufficient_data")

    summary["counts"] = {
        "supported_trading_useful": n_useful,
        "too_late_for_style": n_late,
        "inconclusive": n_inconc,
        "rejected": n_reject,
        "insufficient_data": n_insuf,
    }

    with open(RESULTS_DIR / "phase3_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  → {RESULTS_DIR / 'phase3_summary.json'}")


# ── Main ───────────────────────────────────────────────────────────────────────

ALL = ["H15", "H24", "H44", "H48", "H53", "H70", "H76", "H94", "H97", "H99", "H100"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default=",".join(ALL))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    targets = [h.strip().upper() for h in args.hypotheses.split(",")]
    print(f"\nPhase 3 Trading Utility Test: {targets}\n")

    print("Loading 1m bars...")
    bars_1m = load_all_1m()
    print(f"  {len(bars_1m):,} bars ({bars_1m.index[0].date()} → {bars_1m.index[-1].date()})")

    print("Building window table...")
    wt = build_window_table(bars_1m)
    print(f"  {len(wt)} trading days")

    print("Loading daily_series and IVX...")
    daily = load_daily()
    ivx   = load_ivx()

    print("Building signal df...")
    df = build_signal_df(wt, daily, ivx)
    print(f"  {len(df)} rows after merge")

    runner_map = {
        "H15":  lambda f: run_h15(df, f),
        "H24":  lambda f: run_h24(df, f),
        "H44":  lambda f: run_h44(df, f),
        "H48":  lambda f: run_h48(df, f),
        "H53":  lambda f: run_h53(df, f),
        "H70":  lambda f: run_h70(df, f),
        "H76":  lambda f: run_h76(df, f),
        "H94":  lambda f: run_h94(df, f),
        "H97":  lambda f: run_h97(df, f),
        "H99":  lambda f: run_h99(df, f),
        "H100": lambda f: run_h100(df, f),
    }

    results = []
    for hnum in targets:
        if hnum not in runner_map:
            print(f"  {hnum}: unknown, skipping")
            continue
        print(f"\n  Running {hnum}...")
        r = runner_map[hnum](args.force)
        results.append(r)
        print(f"  {hnum}: {r.get('phase3_verdict', '?').upper()} — {str(r.get('verdict_reason', ''))[:80]}")
        append_vault_note(r)

    # Redundancy audit (only if premarket signals present in targets)
    premarket = {"H44", "H94", "H97", "H70", "H99"}
    if premarket.intersection(targets):
        print("\n  Running redundancy audit...")
        redundancy = run_redundancy_audit(df, args.force)
    else:
        redundancy = {}

    export_summary(results, redundancy)
    print("\nDone.")


if __name__ == "__main__":
    main()
