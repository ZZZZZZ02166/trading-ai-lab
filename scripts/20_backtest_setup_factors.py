#!/usr/bin/env python3
"""
Phase 20: Options-side factor backtests (H48–H51).

Tests options-side market properties directly on all available days.
No entry signal assumed — hypotheses are tested unconditionally.

Hypotheses:
  H48 — First-hour RV predicts total session range
  H49 — IV level predicts realized/implied ratio
  H50 — ATM put-call IV spread predicts next-session return
  H51 — Prior-day put/call volume ratio predicts next-session range

Window: 2024-01-01 → 2026-04-01
Data  : daily_series.parquet, qqq_ivx.parquet, data/raw/chains/,
        Databento 5-min bars (H48 only, cached to fh_rv_cache.parquet)

Usage:
    python scripts/20_backtest_setup_factors.py
    python scripts/20_backtest_setup_factors.py --hypotheses H48,H49
    python scripts/20_backtest_setup_factors.py --force
    python scripts/20_backtest_setup_factors.py --rebuild-cache --force
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import numpy as np
import pandas as pd
from scipy import stats

from app.models.backtest_result import BacktestResult, BacktestVerdict
from app.services.databento_price_client import DatabentoPriceClient

PROCESSED_DIR   = BASE / "data" / "processed"
EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE    = EXPERIMENTS_DIR / "backtest_results.json"
DAILY_SERIES    = PROCESSED_DIR / "daily_series.parquet"
RAW_IVOL        = BASE / "data" / "raw" / "qqq_ivx.parquet"
CHAINS_DIR      = BASE / "data" / "raw" / "chains"
FH_RV_CACHE     = EXPERIMENTS_DIR / "fh_rv_cache.parquet"

WINDOW_START = "2024-01-01"
WINDOW_END   = "2026-04-01"
TICKER       = "QQQ"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _san(obj):
    if isinstance(obj, dict):
        return {k: _san(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_san(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def _cliffs_delta(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) == 0 or len(y) == 0:
        return float("nan")
    U, _ = stats.mannwhitneyu(x, y, alternative="two-sided")
    return float(2 * U / (len(x) * len(y)) - 1)


# ── First-hour RV cache (H48) ─────────────────────────────────────────────────

def _build_fh_rv_series() -> pd.DataFrame:
    """Compute first-hour (09:30–10:29) 5-min RV for all trading days. Cached."""
    if FH_RV_CACHE.exists():
        df = pd.read_parquet(FH_RV_CACHE)
        print(f"[cache] {len(df)} first-hour RV observations loaded")
        return df

    db = DatabentoPriceClient()
    trading_days = pd.bdate_range(start=WINDOW_START, end=WINDOW_END)
    rows = []
    print(f"[H48] Computing first-hour RV for {len(trading_days)} trading days...")
    for day in trading_days:
        try:
            bars = db.get_bars(TICKER, day.strftime("%Y-%m-%d"), interval="5min")
        except Exception:
            continue
        if bars is None or bars.empty:
            continue
        fh = bars.between_time("09:30", "10:29")
        if len(fh) < 8:
            continue
        rv = float(fh["close"].pct_change().dropna().std())
        if np.isfinite(rv) and rv > 0:
            rows.append({"date": day.date(), "fh_rv": rv})

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df.to_parquet(FH_RV_CACHE, index=False)
    print(f"[cache] {len(df)} observations cached → {FH_RV_CACHE.name}")
    return df


# ── Put/call ratio series (H51) ───────────────────────────────────────────────

_CHAIN_PAT = re.compile(
    r"intraday_QQQ___\d{6}([CP])\d+_(\d{8})_MINUTE_5\.parquet$"
)


def _build_pcr_series() -> pd.DataFrame:
    """
    Compute daily total put and call volume from data/raw/chains/ files.
    optionVolume is cumulative intraday — last bar value = full-day volume.
    Returns DataFrame: date, put_vol, call_vol, pcr.
    """
    if not CHAINS_DIR.exists():
        return pd.DataFrame(columns=["date", "put_vol", "call_vol", "pcr"])

    day_put: dict = {}
    day_call: dict = {}

    for f in CHAINS_DIR.glob("*.parquet"):
        m = _CHAIN_PAT.match(f.name)
        if not m:
            continue
        opt_type = m.group(1)
        date_str = m.group(2)
        try:
            dt = pd.Timestamp(date_str).date()
        except Exception:
            continue
        try:
            df = pd.read_parquet(f, columns=["optionVolume"])
            vol_series = df["optionVolume"].dropna()
            if vol_series.empty:
                continue
            day_vol = float(vol_series.iloc[-1])
        except Exception:
            continue
        if opt_type == "P":
            day_put[dt] = day_put.get(dt, 0.0) + day_vol
        else:
            day_call[dt] = day_call.get(dt, 0.0) + day_vol

    all_dates = sorted(set(day_put) | set(day_call))
    if not all_dates:
        return pd.DataFrame(columns=["date", "put_vol", "call_vol", "pcr"])

    rows = []
    for dt in all_dates:
        pv = day_put.get(dt, 0.0)
        cv = day_call.get(dt, 0.0)
        pcr = pv / cv if cv > 0 else float("nan")
        rows.append({"date": dt, "put_vol": pv, "call_vol": cv, "pcr": pcr})

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


# ── Hypothesis runners ────────────────────────────────────────────────────────

def run_h48(hyp: dict, daily: pd.DataFrame) -> BacktestResult:
    """H48: First-hour RV predicts total session range."""
    fh_df = _build_fh_rv_series()
    raw = len(fh_df)

    if raw < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H48", ticker=TICKER,
            period_start=WINDOW_START, period_end=WINDOW_END,
            raw_rows=raw, rows_after_validation=raw, rows_excluded=0,
            exclusion_reason="insufficient Databento data",
            n_observations=raw, n_signals=0,
            metric_name="spearman_r_fh_rv_vs_session_range",
            metric_value=float("nan"), support_threshold=0.15, reject_threshold=0.05,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few days with first-hour RV: {raw}",
            data_notes="insufficient_data",
        )

    daily_c = daily.copy()
    daily_c["date_d"] = pd.to_datetime(daily_c["date"]).dt.date
    daily_c["session_range"] = (daily_c["high"] - daily_c["low"]) / daily_c["open"]

    fh_df = fh_df.copy()
    fh_df["date_d"] = fh_df["date"]
    merged = daily_c.merge(fh_df[["date_d", "fh_rv"]], on="date_d", how="inner")
    valid = merged.dropna(subset=["session_range", "fh_rv"])
    n = len(valid)

    r, p_r = stats.spearmanr(valid["fh_rv"], valid["session_range"])

    q33, q66 = np.percentile(valid["fh_rv"], [33, 66])
    low_rv  = valid[valid["fh_rv"] <= q33]
    mid_rv  = valid[(valid["fh_rv"] > q33) & (valid["fh_rv"] <= q66)]
    high_rv = valid[valid["fh_rv"] > q66]

    med_low  = float(np.median(low_rv["session_range"]))
    med_mid  = float(np.median(mid_rv["session_range"]))
    med_high = float(np.median(high_rv["session_range"]))
    med_diff = med_high - med_low
    is_monotonic = med_high > med_mid > med_low

    _, p_mw = stats.mannwhitneyu(high_rv["session_range"].values, low_rv["session_range"].values,
                                  alternative="greater")
    cd = _cliffs_delta(high_rv["session_range"].values, low_rv["session_range"].values)

    if abs(r) >= 0.15 and p_r < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason  = (f"First-hour RV predicts session range: r={r:.3f}, p={p_r:.4f}, "
                   f"med_diff={med_diff:.4f}, Cliff's d={cd:.3f}")
    elif abs(r) < 0.05 or p_r > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason  = f"No correlation between first-hour RV and session range: r={r:.3f}, p={p_r:.4f}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason  = f"Weak correlation: r={r:.3f}, p={p_r:.4f}, Cliff's d={cd:.3f}"

    print(f"  H48: n={n}, r={r:.3f}, p={p_r:.4f}, med_diff={med_diff:.4f}, "
          f"monotonic={is_monotonic} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H48", ticker=TICKER,
        period_start=WINDOW_START, period_end=WINDOW_END,
        raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
        exclusion_reason="missing session_range or fh_rv",
        n_observations=n, n_signals=len(high_rv),
        metric_name="spearman_r_fh_rv_vs_session_range",
        metric_value=round(float(r), 4), support_threshold=0.15, reject_threshold=0.05,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested", data_fidelity="exact_underlying",
        metric_family="correlation",
        extra_metrics={
            "spearman_r":            round(float(r), 4),
            "p_spearman":            round(float(p_r), 4),
            "n_low_rv":              len(low_rv),
            "n_mid_rv":              len(mid_rv),
            "n_high_rv":             len(high_rv),
            "median_range_low_rv":   round(med_low, 5),
            "median_range_mid_rv":   round(med_mid, 5),
            "median_range_high_rv":  round(med_high, 5),
            "median_diff_high_vs_low": round(med_diff, 5),
            "cliffs_delta":          round(cd, 4) if np.isfinite(cd) else None,
            "p_mannwhitney":         round(float(p_mw), 4),
            "is_monotonic":          is_monotonic,
        },
    )


def run_h49(hyp: dict, daily: pd.DataFrame) -> BacktestResult:
    """H49: IV level predicts realized/implied ratio (does market over/under-move vs IV?)."""
    df = daily.copy()
    df = df.dropna(subset=["iv_30d", "high", "low", "open"])
    df = df[(df["iv_30d"] > 0) & (df["open"] > 0)]
    raw = len(df)

    df["implied_1d_pct"] = df["iv_30d"] / np.sqrt(252)
    df["session_range_pct"] = (df["high"] - df["low"]) / df["open"]
    df["rv_iv_ratio"] = df["session_range_pct"] / df["implied_1d_pct"]
    df["iv_pct"] = df["iv_30d"].rolling(60, min_periods=20).rank(pct=True)

    valid = df.dropna(subset=["rv_iv_ratio", "iv_pct"])
    n = len(valid)

    if n < 50:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H49", ticker=TICKER,
            period_start=WINDOW_START, period_end=WINDOW_END,
            raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
            exclusion_reason="missing iv_30d or insufficient rolling history",
            n_observations=n, n_signals=0,
            metric_name="spearman_r_iv_vs_rv_iv_ratio",
            metric_value=float("nan"), support_threshold=0.10, reject_threshold=0.05,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Insufficient data: {n} rows",
            data_notes="proxy_tested",
        )

    r, p_r = stats.spearmanr(valid["iv_30d"], valid["rv_iv_ratio"])

    low_iv  = valid[valid["iv_pct"] < 0.33]
    mid_iv  = valid[valid["iv_pct"].between(0.33, 0.67)]
    high_iv = valid[valid["iv_pct"] > 0.67]

    med_low  = float(np.median(low_iv["rv_iv_ratio"]))
    med_mid  = float(np.median(mid_iv["rv_iv_ratio"]))
    med_high = float(np.median(high_iv["rv_iv_ratio"]))
    med_diff = med_high - med_low

    if len(low_iv) >= 5 and len(high_iv) >= 5:
        _, p_mw = stats.mannwhitneyu(high_iv["rv_iv_ratio"].values, low_iv["rv_iv_ratio"].values,
                                      alternative="two-sided")
        cd = _cliffs_delta(high_iv["rv_iv_ratio"].values, low_iv["rv_iv_ratio"].values)
    else:
        p_mw, cd = 1.0, float("nan")

    if abs(r) >= 0.10 and p_r < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason  = (f"IV level predicts realized/implied ratio: r={r:.3f}, p={p_r:.4f}. "
                   f"High-IV median ratio={med_high:.2f} vs low-IV={med_low:.2f}")
    elif abs(r) < 0.05 or p_r > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason  = f"No relationship between IV level and RV/IV ratio: r={r:.3f}, p={p_r:.4f}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason  = f"Weak relationship: r={r:.3f}, p={p_r:.4f}, Cliff's d={cd:.3f}"

    print(f"  H49: n={n}, r={r:.3f}, p={p_r:.4f}, med_diff={med_diff:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H49", ticker=TICKER,
        period_start=WINDOW_START, period_end=WINDOW_END,
        raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
        exclusion_reason="missing iv_30d, OHLC, or insufficient rolling history",
        n_observations=n, n_signals=len(high_iv),
        metric_name="spearman_r_iv_vs_rv_iv_ratio",
        metric_value=round(float(r), 4), support_threshold=0.10, reject_threshold=0.05,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested", data_fidelity="constant_maturity_iv",
        metric_family="correlation",
        extra_metrics={
            "spearman_r":            round(float(r), 4),
            "p_spearman":            round(float(p_r), 4),
            "n_low_iv":              len(low_iv),
            "n_mid_iv":              len(mid_iv),
            "n_high_iv":             len(high_iv),
            "median_ratio_low_iv":   round(med_low, 4),
            "median_ratio_mid_iv":   round(med_mid, 4),
            "median_ratio_high_iv":  round(med_high, 4),
            "median_diff_high_vs_low": round(med_diff, 4),
            "cliffs_delta":          round(cd, 4) if np.isfinite(cd) else None,
            "p_mannwhitney":         round(float(p_mw), 4),
        },
    )


def run_h50(hyp: dict, daily: pd.DataFrame) -> BacktestResult:
    """H50: Elevated ATM put-call IV spread predicts next-session return."""
    if not RAW_IVOL.exists():
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H50", ticker=TICKER,
            period_start=WINDOW_START, period_end=WINDOW_END,
            raw_rows=0, rows_after_validation=0, rows_excluded=0,
            exclusion_reason="raw iVol file not found",
            n_observations=0, n_signals=0,
            metric_name="median_next_return_diff_elevated_vs_normal_skew",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="Raw iVol file not available",
            data_notes="insufficient_data",
        )

    raw_iv = pd.read_parquet(RAW_IVOL)
    raw_iv["date_d"] = pd.to_datetime(raw_iv["date"]).dt.date
    raw_iv = raw_iv.dropna(subset=["30d IV Put", "30d IV Call"])
    raw_iv["put_skew"] = raw_iv["30d IV Put"] - raw_iv["30d IV Call"]
    raw_iv["put_skew_z20"] = (
        (raw_iv["put_skew"] - raw_iv["put_skew"].rolling(20).mean()) /
        raw_iv["put_skew"].rolling(20).std().replace(0, np.nan)
    )

    daily_c = daily.copy()
    daily_c["date_d"] = pd.to_datetime(daily_c["date"]).dt.date
    daily_c["next_return"] = daily_c["log_return"].shift(-1)
    daily_c["next_range"]  = (
        (daily_c["high"].shift(-1) - daily_c["low"].shift(-1)) / daily_c["open"].shift(-1)
    )

    merged = raw_iv[["date_d", "put_skew", "put_skew_z20"]].merge(
        daily_c[["date_d", "next_return", "next_range"]], on="date_d", how="inner"
    )
    valid = merged.dropna(subset=["put_skew_z20", "next_return"])
    raw = len(valid)

    if raw < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H50", ticker=TICKER,
            period_start=WINDOW_START, period_end=WINDOW_END,
            raw_rows=raw, rows_after_validation=raw, rows_excluded=0,
            exclusion_reason="insufficient put-call skew history",
            n_observations=raw, n_signals=0,
            metric_name="median_next_return_diff_elevated_vs_normal_skew",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few observations: {raw}",
            data_notes="proxy_tested",
        )

    elevated = valid[valid["put_skew_z20"] >  0.5]
    normal   = valid[valid["put_skew_z20"] <= 0.5]

    med_elev = float(np.median(elevated["next_return"])) if len(elevated) > 0 else float("nan")
    med_norm = float(np.median(normal["next_return"]))   if len(normal)   > 0 else float("nan")
    diff = med_elev - med_norm

    r, p_r = stats.spearmanr(valid["put_skew_z20"], valid["next_return"])

    if len(elevated) >= 5 and len(normal) >= 5:
        _, p_mw = stats.mannwhitneyu(elevated["next_return"].values, normal["next_return"].values,
                                      alternative="two-sided")
        cd = _cliffs_delta(elevated["next_return"].values, normal["next_return"].values)
    else:
        p_mw, cd = 1.0, float("nan")

    pct_elev = float(len(elevated) / raw) if raw > 0 else float("nan")

    if diff > 0.001 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason  = (f"Elevated put skew → higher next-session return: "
                   f"elev={med_elev:.5f} vs normal={med_norm:.5f} "
                   f"(diff={diff:.5f}, p={p_mw:.4f}, r={r:.3f}). "
                   f"Caveat: ATM put-call spread is a weak skew proxy.")
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason  = (f"No predictive edge from put-call spread: "
                   f"elev={med_elev:.5f} vs normal={med_norm:.5f} "
                   f"(diff={diff:.5f}, p={p_mw:.4f}). "
                   f"Caveat: ATM spread is imprecise skew proxy.")
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason  = (f"Direction present (diff={diff:.5f}) but not significant "
                   f"(p={p_mw:.4f}, r={r:.3f}). "
                   f"Caveat: ATM put-call spread is a weak skew proxy.")

    print(f"  H50: n={raw}, n_elevated={len(elevated)} ({pct_elev:.1%}), "
          f"diff={diff:.5f}, p_mw={p_mw:.4f}, r={r:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H50", ticker=TICKER,
        period_start=WINDOW_START, period_end=WINDOW_END,
        raw_rows=raw, rows_after_validation=raw, rows_excluded=0,
        exclusion_reason="",
        n_observations=raw, n_signals=len(elevated),
        metric_name="median_next_return_diff_elevated_vs_normal_skew",
        metric_value=round(diff, 5) if np.isfinite(diff) else float("nan"),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested", data_fidelity="constant_maturity_iv",
        metric_family="mean_difference",
        extra_metrics={
            "n_elevated":             len(elevated),
            "n_normal":               len(normal),
            "median_return_elevated": round(med_elev, 5) if np.isfinite(med_elev) else None,
            "median_return_normal":   round(med_norm, 5) if np.isfinite(med_norm) else None,
            "spearman_r":             round(float(r), 4),
            "p_spearman":             round(float(p_r), 4),
            "cliffs_delta":           round(cd, 4) if np.isfinite(cd) else None,
            "p_mannwhitney":          round(float(p_mw), 4),
            "pct_elevated_days":      round(pct_elev, 3),
            "skew_proxy_caveat":      "ATM 30d put-call spread, not true 25-delta skew",
        },
    )


def run_h51(hyp: dict, daily: pd.DataFrame) -> BacktestResult:
    """H51: Prior-day put/call volume ratio predicts next-session range."""
    pcr_df = _build_pcr_series()
    n_pcr = len(pcr_df)

    if pcr_df.empty or n_pcr < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H51", ticker=TICKER,
            period_start=WINDOW_START, period_end=WINDOW_END,
            raw_rows=0, rows_after_validation=0, rows_excluded=0,
            exclusion_reason="no put/call chain data in chains/",
            n_observations=0, n_signals=0,
            metric_name="median_next_range_diff_high_vs_normal_pcr",
            metric_value=float("nan"), support_threshold=0.002, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="No put/call volume data available in data/raw/chains/",
            data_notes="insufficient_data",
        )

    pcr_df = pcr_df.copy()
    pcr_df["pcr_med20"]   = pcr_df["pcr"].rolling(20, min_periods=5).median()
    pcr_df["pcr_elevated"] = pcr_df["pcr"] > pcr_df["pcr_med20"]
    pcr_df["date_d"] = pcr_df["date"]

    daily_c = daily.copy()
    daily_c["date_d"]     = pd.to_datetime(daily_c["date"]).dt.date
    daily_c["next_range"] = (
        (daily_c["high"].shift(-1) - daily_c["low"].shift(-1)) / daily_c["open"].shift(-1)
    )
    daily_c["next_return"] = daily_c["log_return"].shift(-1)

    merged = pcr_df[["date_d", "pcr", "pcr_med20", "pcr_elevated"]].merge(
        daily_c[["date_d", "next_range", "next_return"]], on="date_d", how="inner"
    )
    valid = merged.dropna(subset=["pcr", "next_range", "pcr_med20"])
    raw = len(valid)

    r, p_r = stats.spearmanr(valid["pcr"], valid["next_range"])

    elevated = valid[valid["pcr_elevated"] == True]
    normal   = valid[valid["pcr_elevated"] != True]

    med_elev = float(np.median(elevated["next_range"])) if len(elevated) > 0 else float("nan")
    med_norm = float(np.median(normal["next_range"]))   if len(normal)   > 0 else float("nan")
    diff = med_elev - med_norm

    if len(elevated) >= 5 and len(normal) >= 5:
        _, p_mw = stats.mannwhitneyu(elevated["next_range"].values, normal["next_range"].values,
                                      alternative="two-sided")
        cd = _cliffs_delta(elevated["next_range"].values, normal["next_range"].values)
    else:
        p_mw, cd = 1.0, float("nan")

    put_window_note = (f"Put chain data covers 2025-04-01–2025-12-31 only "
                       f"({n_pcr} PCR dates).")

    if abs(r) >= 0.10 and p_r < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason  = f"PCR predicts next-session range: r={r:.3f}, p={p_r:.4f}. {put_window_note}"
    elif abs(r) < 0.05 or p_r > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason  = f"No PCR effect on next-session range: r={r:.3f}, p={p_r:.4f}. {put_window_note}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason  = (f"Weak relationship: r={r:.3f}, p={p_r:.4f}, diff={diff:.4f}. "
                   + put_window_note)

    print(f"  H51: n={raw}, r={r:.3f}, p={p_r:.4f}, "
          f"n_elevated={len(elevated)}, diff={diff:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H51", ticker=TICKER,
        period_start="2025-04-01", period_end="2025-12-31",
        raw_rows=n_pcr, rows_after_validation=raw, rows_excluded=n_pcr - raw,
        exclusion_reason="no matching next-session data or missing rolling PCR baseline",
        n_observations=raw, n_signals=len(elevated),
        metric_name="median_next_range_diff_high_vs_normal_pcr",
        metric_value=round(diff, 5) if np.isfinite(diff) else float("nan"),
        support_threshold=0.002, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested", data_fidelity="index_proxy",
        metric_family="mean_difference",
        extra_metrics={
            "spearman_r_pcr_vs_next_range": round(float(r), 4),
            "p_spearman":            round(float(p_r), 4),
            "n_elevated_pcr":        len(elevated),
            "n_normal_pcr":          len(normal),
            "median_range_elevated": round(med_elev, 5) if np.isfinite(med_elev) else None,
            "median_range_normal":   round(med_norm, 5) if np.isfinite(med_norm) else None,
            "median_diff":           round(diff, 5) if np.isfinite(diff) else None,
            "cliffs_delta":          round(cd, 4) if np.isfinite(cd) else None,
            "p_mannwhitney":         round(float(p_mw), 4),
            "n_pcr_dates":           n_pcr,
            "put_data_window":       "2025-04-01 to 2025-12-31",
        },
    )


# ── Dispatch table ────────────────────────────────────────────────────────────

SETUP_RUNNERS = {
    "H48": run_h48,
    "H49": run_h49,
    "H50": run_h50,
    "H51": run_h51,
}


# ── Result persistence ────────────────────────────────────────────────────────

def _load_existing() -> dict[str, dict]:
    if RESULTS_FILE.exists():
        return {r["hypothesis_number"]: r for r in json.loads(RESULTS_FILE.read_text())}
    return {}


def _save_results(results_map: dict[str, dict]) -> None:
    records = _san(list(results_map.values()))
    RESULTS_FILE.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} results → {RESULTS_FILE.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default="all")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--rebuild-cache", action="store_true",
                        help="Delete and rebuild all caches (fh_rv)")
    args = parser.parse_args()

    wanted = (
        list(SETUP_RUNNERS)
        if args.hypotheses.lower() == "all"
        else [h.strip().upper() for h in args.hypotheses.split(",")]
    )
    unknown = [h for h in wanted if h not in SETUP_RUNNERS]
    if unknown:
        print(f"Unknown: {unknown}. Available: {list(SETUP_RUNNERS)}")
        sys.exit(1)

    if args.rebuild_cache and FH_RV_CACHE.exists():
        FH_RV_CACHE.unlink()
        print(f"[rebuild] Deleted {FH_RV_CACHE.name}")

    hyp_file = EXPERIMENTS_DIR / "hypotheses.json"
    all_hyps = json.loads(hyp_file.read_text())
    hyp_by_num = {f"H{i+1}": h for i, h in enumerate(all_hyps)}

    daily = pd.read_parquet(DAILY_SERIES).sort_values("date").reset_index(drop=True)

    existing = _load_existing()

    # Remove stale entry-signal-dependent results
    for stale in ("H45", "H46", "H47"):
        if stale in existing:
            del existing[stale]
            print(f"[cleanup] Removed stale {stale} (required entry signal, not a market hypothesis)")

    for hnum in wanted:
        if hnum in existing and not args.force:
            print(f"[skip] {hnum} already in results (use --force to re-run)")
            continue
        hyp = hyp_by_num.get(hnum)
        if hyp is None:
            print(f"[warn] {hnum} not found in hypotheses.json")
            continue

        print(f"Running {hnum}: {hyp['title'][:65]}...")
        runner = SETUP_RUNNERS[hnum]
        result = runner(hyp, daily)
        existing[hnum] = result.model_dump()
        print(f"  → {result.verdict.value}: {result.verdict_reason[:90]}")

    _save_results(existing)
    print(f"\nCompleted {len(wanted)} runner(s).")
    print("Next: run scripts/17_score_and_report.py")


if __name__ == "__main__":
    main()
