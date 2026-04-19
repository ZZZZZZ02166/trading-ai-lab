#!/usr/bin/env python3
"""
Phase 15: Run daily-frequency backtests (H1–H12).

Pilot: run H9 only to validate the pipeline.
After pilot passes, run all of H1–H12.

Each hypothesis is defined as a BacktestSpec dict and processed by a
dedicated test function. Results are appended to experiments/backtest_results.json.

Usage:
    python scripts/15_run_daily_backtests.py                  # all daily
    python scripts/15_run_daily_backtests.py --hypotheses H9  # pilot
    python scripts/15_run_daily_backtests.py --force          # overwrite existing results
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import numpy as np
import pandas as pd
from scipy import stats  # type: ignore

from app.models.backtest_result import BacktestResult, BacktestVerdict, TradeRecord
from app.services.data_validator import validate_dataframe

PROCESSED_DIR = BASE / "data" / "processed"
EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE = EXPERIMENTS_DIR / "backtest_results.json"

DAILY_SERIES = PROCESSED_DIR / "daily_series.parquet"
IVX_FILE = BASE / "data" / "raw" / "qqq_ivx.parquet"

# Frozen test window — all daily backtests run against this exact range.
TEST_WINDOW_START = "2024-01-01"
TEST_WINDOW_END   = "2026-04-05"
TICKER = "QQQ"


def _sanitise_for_json(obj):
    """Recursively replace NaN/Inf floats with None for standards-compliant JSON."""
    if isinstance(obj, dict):
        return {k: _sanitise_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitise_for_json(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def _validate_daily_series(df: pd.DataFrame) -> None:
    """
    Pre-run data quality gate. Raises SystemExit on any failure so no
    hypothesis silently runs on bad data.
    """
    if "date" not in df.columns:
        raise SystemExit("[validate] daily_series has no 'date' column — re-run 14c.")
    dupes = df["date"].duplicated().sum()
    if dupes > 0:
        raise SystemExit(f"[validate] {dupes} duplicate dates in daily_series — re-run 14a/14c --force.")
    dates = pd.to_datetime(df["date"])
    if not dates.is_monotonic_increasing:
        raise SystemExit("[validate] dates not monotonically increasing — re-run 14c --force.")
    for col in ["close", "open", "high", "low"]:
        if col in df.columns:
            bad = (df[col].dropna() <= 0).sum()
            if bad > 0:
                raise SystemExit(f"[validate] {bad} non-positive values in '{col}' — data corrupt.")
    for col in [c for c in df.columns if c.startswith("hv_") or c.startswith("iv_")]:
        val = df[col].dropna()
        if len(val) > 0 and (val > 5.0).any():
            raise SystemExit(
                f"[validate] '{col}' has values > 5.0 — check if stored as decimal (not percent)."
            )
    if len(df) < 20:
        raise SystemExit(f"[validate] only {len(df)} rows — too few for any meaningful test.")
    print(
        f"[validate] OK — {len(df)} rows | {str(df['date'].min())[:10]} → {str(df['date'].max())[:10]}"
    )


def _load_daily() -> pd.DataFrame:
    if not DAILY_SERIES.exists():
        raise SystemExit(
            "daily_series.parquet not found. Run scripts/14c_build_processed_series.py first."
        )
    df = pd.read_parquet(DAILY_SERIES)
    date_col = [c for c in df.columns if "date" in c.lower()]
    if date_col:
        df["date"] = pd.to_datetime(df[date_col[0]])
    df = df.sort_values("date").reset_index(drop=True)
    # Lock to frozen test window
    df = df[(df["date"] >= TEST_WINDOW_START) & (df["date"] <= TEST_WINDOW_END)].reset_index(drop=True)
    return df


def _load_existing_results() -> dict[str, dict]:
    """Load existing results keyed by hypothesis_number."""
    if RESULTS_FILE.exists():
        records = json.loads(RESULTS_FILE.read_text())
        return {r["hypothesis_number"]: r for r in records}
    return {}


def _save_results(results_map: dict[str, dict]) -> None:
    records = _sanitise_for_json(list(results_map.values()))
    RESULTS_FILE.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} results → {RESULTS_FILE}")


# ── H9: Yang-Zhang Outperforms Close-to-Close ────────────────────────────────────

def run_h9(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Yang-Zhang HV estimator has lower RMSE vs. forward realised vol
    than close-to-close HV.

    Ticker: QQQ. Window: TEST_WINDOW_START → TEST_WINDOW_END.
    Signal: always-on (all dates with valid HV data)
    Outcome: RMSE ratio (YZ RMSE / CC RMSE)
    Support: ratio < 0.99, p < 0.05
    test_type: directly_tested
    """
    required = ["hv_20_cc", "hv_20_yz", "fwd_rv_20"]
    raw = len(df)
    excl_reason = "20-day lookback warmup (hv_20_cc/hv_20_yz); 20-day forward window (fwd_rv_20)"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H9",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing required columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="rmse_ratio_yz_vs_cc",
            metric_value=float("nan"),
            support_threshold=0.99, reject_threshold=1.01,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    valid = df[["date"] + required].dropna()
    excluded = raw - len(valid)
    if len(valid) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H9",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(valid), n_signals=0,
            metric_name="rmse_ratio_yz_vs_cc",
            metric_value=float("nan"),
            support_threshold=0.99, reject_threshold=1.01,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations ({len(valid)} < 60)",
            data_notes="directly_tested",
        )

    rmse_cc = float(np.sqrt(((valid["hv_20_cc"] - valid["fwd_rv_20"]) ** 2).mean()))
    rmse_yz = float(np.sqrt(((valid["hv_20_yz"] - valid["fwd_rv_20"]) ** 2).mean()))
    ratio = rmse_yz / rmse_cc if rmse_cc > 0 else float("nan")
    improvement_pct = (1 - ratio) * 100 if not np.isnan(ratio) else float("nan")

    # Paired t-test on squared errors
    err_cc = (valid["hv_20_cc"] - valid["fwd_rv_20"]) ** 2
    err_yz = (valid["hv_20_yz"] - valid["fwd_rv_20"]) ** 2
    t_stat, p_value = stats.ttest_rel(err_yz, err_cc)

    if ratio < 0.99 and p_value < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"YZ RMSE={rmse_yz:.4f} < CC RMSE={rmse_cc:.4f} "
            f"(ratio={ratio:.4f}, {improvement_pct:.1f}% better, p={p_value:.4f})"
        )
    elif ratio > 1.01:
        verdict = BacktestVerdict.REJECTED
        reason = f"YZ RMSE={rmse_yz:.4f} >= CC RMSE={rmse_cc:.4f} (ratio={ratio:.4f})"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"RMSE ratio={ratio:.4f} (p={p_value:.4f}) — direction present but not significant or near 1.0"

    print(
        f"  H9: RMSE_CC={rmse_cc:.4f}, RMSE_YZ={rmse_yz:.4f}, "
        f"ratio={ratio:.4f}, p={p_value:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H9",
        ticker=TICKER,
        period_start=TEST_WINDOW_START,
        period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(valid),
        n_signals=len(valid),  # H9 is always-on; every valid row is a signal
        metric_name="rmse_ratio_yz_vs_cc",
        metric_value=round(ratio, 6),
        support_threshold=0.99,
        reject_threshold=1.01,
        verdict=verdict,
        verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "rmse_cc": round(rmse_cc, 6),
            "rmse_yz": round(rmse_yz, 6),
            "improvement_pct": round(improvement_pct, 2),
            "t_stat": round(t_stat, 4),
            "p_value": round(p_value, 4),
        },
    )


# ── H1: Short Straddle Edge — IV vs HV Variance Premium ──────────────────────────

def run_h1(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When QQQ 30d IVX > 20d CC-HV by 2+ vol pts, the variance premium
    (IV - forward realized vol) is significantly positive, supporting a systematic
    short-vol edge.

    Ticker: QQQ. Window: TEST_WINDOW_START → TEST_WINDOW_END.
    Signal: iv_30d - hv_20_cc > 0.02 (IV > HV by ≥ 2 percentage points)
    Outcome: iv_30d - fwd_rv_20 (variance premium; positive = seller profits)
    Support: mean VP on signal days ≥ 1.0 vol pt AND p < 0.05
    test_type: proxy_tested — IVX used as IV proxy; no actual straddle fills or strikes.
    """
    required = ["iv_30d", "hv_20_cc", "fwd_rv_20"]
    raw = len(df)
    excl_reason = "20-day lookback warmup (hv_20_cc); 20-day forward window (fwd_rv_20)"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H1",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing required columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="mean_variance_premium_signal_days_vpts",
            metric_value=float("nan"),
            support_threshold=1.0, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    valid = df[["date"] + required].dropna()
    excluded = raw - len(valid)
    if len(valid) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H1",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(valid), n_signals=0,
            metric_name="mean_variance_premium_signal_days_vpts",
            metric_value=float("nan"),
            support_threshold=1.0, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations ({len(valid)} < 60)",
            data_notes="proxy_tested",
        )

    IV_HV_THRESHOLD = 0.02  # 2 percentage points in decimal
    signal_mask = (valid["iv_30d"] - valid["hv_20_cc"]) > IV_HV_THRESHOLD
    n_signals = int(signal_mask.sum())

    if n_signals < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H1",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(valid), n_signals=n_signals,
            metric_name="mean_variance_premium_signal_days_vpts",
            metric_value=float("nan"),
            support_threshold=1.0, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few signal days ({n_signals} < 10) where IV > HV + 2pts",
            data_notes="proxy_tested",
        )

    variance_premium = valid["iv_30d"] - valid["fwd_rv_20"]
    vp_signal    = variance_premium[signal_mask]
    vp_no_signal = variance_premium[~signal_mask]

    mean_vp_signal    = float(vp_signal.mean()) * 100
    mean_vp_no_signal = float(vp_no_signal.mean()) * 100 if len(vp_no_signal) > 0 else float("nan")

    t_stat, p_value = stats.ttest_1samp(vp_signal, popmean=0)

    if mean_vp_signal >= 1.0 and p_value < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Mean variance premium on IV>HV+2pt days: {mean_vp_signal:.2f} vol pts "
            f"(vs {mean_vp_no_signal:.2f} on non-signal days), p={p_value:.4f}"
        )
    elif mean_vp_signal <= 0.0:
        verdict = BacktestVerdict.REJECTED
        reason = f"No variance premium on signal days: {mean_vp_signal:.2f} vol pts (≤ 0)"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Variance premium present ({mean_vp_signal:.2f} vol pts) but "
            f"threshold not met (need ≥ 1.0 AND p < 0.05). p={p_value:.4f}"
        )

    print(
        f"  H1: signal_days={n_signals}/{len(valid)}, "
        f"vp_signal={mean_vp_signal:.2f} vpts, vp_all={float(variance_premium.mean())*100:.2f} vpts, "
        f"p={p_value:.4f} → {verdict.value}"
    )

    trade_records = [
        TradeRecord(
            date=str(row["date"])[:10],
            signal=round(float(row["iv_30d"] - row["hv_20_cc"]) * 100, 3),
            outcome=round(float(row["iv_30d"] - row["fwd_rv_20"]) * 100, 3),
            notes=f"iv={row['iv_30d']:.4f} hv={row['hv_20_cc']:.4f} fwd_rv={row['fwd_rv_20']:.4f}",
        )
        for _, row in valid[signal_mask].iterrows()
    ]

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H1",
        ticker=TICKER,
        period_start=TEST_WINDOW_START,
        period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(valid),
        n_signals=n_signals,
        metric_name="mean_variance_premium_signal_days_vpts",
        metric_value=round(mean_vp_signal, 4),
        support_threshold=1.0, reject_threshold=0.0,
        verdict=verdict,
        verdict_reason=reason,
        data_notes="proxy_tested",
        trades=trade_records,
        extra_metrics={
            "mean_vp_signal_days_vpts": round(mean_vp_signal, 4),
            "mean_vp_non_signal_days_vpts": round(mean_vp_no_signal, 4) if not np.isnan(mean_vp_no_signal) else None,
            "n_signal_days": n_signals,
            "n_non_signal_days": int((~signal_mask).sum()),
            "iv_hv_threshold_vpts": 2.0,
            "t_stat": round(t_stat, 4),
            "p_value": round(p_value, 4),
        },
    )


# ── H4: GARCH Timing Outperforms Rolling HV for Straddle Entry ───────────────────

def run_h4(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When GARCH(1,1) forecasts vol below current 30d IVX, the subsequent
    variance premium is higher than when using rolling HV as the timing signal.

    Ticker: QQQ. Window: TEST_WINDOW_START → TEST_WINDOW_END.
    GARCH signal: garch_vol < iv_30d (GARCH says IV is inflated → sell)
    HV baseline: hv_20_cc < iv_30d (naive HV-based sell signal)
    Outcome: iv_30d - fwd_rv_20 (variance premium per signal day)
    Primary metric: GARCH mean VP minus HV baseline mean VP (vol pts)
    Support: GARCH VP ≥ HV VP + 0.5 vol pts AND GARCH VP mean t-test p < 0.05
    test_type: proxy_tested — IVX and GARCH used as proxies; no actual fills.
    """
    required = ["iv_30d", "hv_20_cc", "garch_vol", "fwd_rv_20"]
    raw = len(df)
    excl_reason = "20-day lookback warmup (hv_20_cc); 20-day forward window (fwd_rv_20); GARCH burn-in (garch_vol)"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H4",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing required columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="garch_vp_minus_hv_vp_vpts",
            metric_value=float("nan"),
            support_threshold=0.5, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    valid = df[["date"] + required].dropna()
    excluded = raw - len(valid)
    if len(valid) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H4",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(valid), n_signals=0,
            metric_name="garch_vp_minus_hv_vp_vpts",
            metric_value=float("nan"),
            support_threshold=0.5, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations ({len(valid)} < 60)",
            data_notes="proxy_tested",
        )

    garch_signal = valid["garch_vol"] < valid["iv_30d"]
    hv_signal    = valid["hv_20_cc"]  < valid["iv_30d"]
    n_garch = int(garch_signal.sum())
    n_hv    = int(hv_signal.sum())

    if n_garch < 10 or n_hv < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H4",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(valid), n_signals=n_garch,
            metric_name="garch_vp_minus_hv_vp_vpts",
            metric_value=float("nan"),
            support_threshold=0.5, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few signal days: GARCH={n_garch}, HV={n_hv} (need ≥ 10 each)",
            data_notes="proxy_tested",
        )

    vp = valid["iv_30d"] - valid["fwd_rv_20"]
    vp_garch = vp[garch_signal]
    vp_hv    = vp[hv_signal]

    mean_vp_garch = float(vp_garch.mean()) * 100
    mean_vp_hv    = float(vp_hv.mean())    * 100
    metric        = mean_vp_garch - mean_vp_hv

    # t-test: GARCH signal days variance premium > 0
    t_garch, p_garch = stats.ttest_1samp(vp_garch, popmean=0)
    # Welch t-test: GARCH vs HV signal days
    t_diff, p_diff = stats.ttest_ind(vp_garch, vp_hv, equal_var=False)

    if metric >= 0.5 and mean_vp_garch > 0 and p_garch < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"GARCH-timed VP={mean_vp_garch:.2f} vpts vs HV-timed VP={mean_vp_hv:.2f} vpts "
            f"(edge={metric:.2f} vpts, p_garch={p_garch:.4f})"
        )
    elif metric < 0.0:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"GARCH timing adds no edge: GARCH VP={mean_vp_garch:.2f} vpts, "
            f"HV VP={mean_vp_hv:.2f} vpts (GARCH underperforms)"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"GARCH VP={mean_vp_garch:.2f} vpts vs HV VP={mean_vp_hv:.2f} vpts "
            f"(edge={metric:.2f} vpts) but threshold not met (need ≥ 0.5 AND p < 0.05). "
            f"p_garch={p_garch:.4f}"
        )

    print(
        f"  H4: GARCH_signal={n_garch}d VP={mean_vp_garch:.2f}vpts, "
        f"HV_signal={n_hv}d VP={mean_vp_hv:.2f}vpts, edge={metric:.2f}vpts, "
        f"p_garch={p_garch:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H4",
        ticker=TICKER,
        period_start=TEST_WINDOW_START,
        period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(valid),
        n_signals=n_garch,
        metric_name="garch_vp_minus_hv_vp_vpts",
        metric_value=round(metric, 4),
        support_threshold=0.5,
        reject_threshold=0.0,
        verdict=verdict,
        verdict_reason=reason,
        data_notes="proxy_tested",
        extra_metrics={
            "mean_vp_garch_signal_vpts": round(mean_vp_garch, 4),
            "mean_vp_hv_signal_vpts": round(mean_vp_hv, 4),
            "garch_edge_vpts": round(metric, 4),
            "n_garch_signal_days": n_garch,
            "n_hv_signal_days": n_hv,
            "t_garch_vs_zero": round(t_garch, 4),
            "p_garch_vs_zero": round(p_garch, 4),
            "t_garch_vs_hv": round(t_diff, 4),
            "p_garch_vs_hv": round(p_diff, 4),
        },
    )


# ── Shared helpers ────────────────────────────────────────────────────────────────

def _cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Cliff's delta (rank-biserial) for x vs y. Positive = x tends > y."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return float("nan")
    U, _ = stats.mannwhitneyu(x, y, alternative="two-sided")
    return float(2 * U / (n1 * n2) - 1)


# ── H42: IVX Percentile Regime Predicts Intraday Amplitude ───────────────────────

def run_h42(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Sessions in the 20th–70th percentile of rolling 30-day iv_30d produce
    higher intraday amplitude (daily H-L / IVX-implied expected move) than outer-tail
    sessions (below 20th or above 70th percentile).

    Signal: all days with valid iv_30d + OHLC after 30-day warmup
    Metric: median_amplitude_mid - median_amplitude_outer
    Support: diff > 0.05, p_mannwhitney < 0.10, |cliffs_delta| >= 0.10
    data_notes: directly_tested, data_fidelity: exact_underlying
    """
    required = ["iv_30d", "open", "high", "low", "close"]
    raw = len(df)
    excl_reason = "30-day rolling percentile warmup; missing OHLC or iv_30d"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H42", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="median_amplitude_diff_mid_vs_outer",
            metric_value=float("nan"), support_threshold=0.05, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[required + ["date"]].copy()
    work["iv_pct"] = work["iv_30d"].rolling(30, min_periods=15).rank(pct=True)
    work = work.dropna()
    excluded = raw - len(work)

    if len(work) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H42", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_amplitude_diff_mid_vs_outer",
            metric_value=float("nan"), support_threshold=0.05, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations: {len(work)}",
            data_notes="directly_tested",
        )

    # Expected move in price units; amplitude = realized range / expected 1-SD move
    work["expected_move"] = (work["iv_30d"] / np.sqrt(252)) * work["close"]
    work["amplitude"] = (work["high"] - work["low"]) / work["expected_move"]

    # Primary split: mid 20–70th vs outer tails
    mid = work["amplitude"][(work["iv_pct"] >= 0.20) & (work["iv_pct"] <= 0.70)].dropna().values
    outer = work["amplitude"][(work["iv_pct"] < 0.20) | (work["iv_pct"] > 0.70)].dropna().values

    if len(mid) < 10 or len(outer) < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H42", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=len(mid),
            metric_name="median_amplitude_diff_mid_vs_outer",
            metric_value=float("nan"), support_threshold=0.05, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few in mid ({len(mid)}) or outer ({len(outer)}) bucket",
            data_notes="directly_tested",
        )

    median_mid = float(np.median(mid))
    median_outer = float(np.median(outer))
    diff = median_mid - median_outer
    U_stat, p_mw = stats.mannwhitneyu(mid, outer, alternative="greater")
    cd = _cliffs_delta(mid, outer)

    # Sensitivity: Cliff's delta for nearby bucket choices
    sensitivity = {}
    for lo, hi in [(0.20, 0.70), (0.25, 0.75), (0.30, 0.70), (0.20, 0.80)]:
        m = work["amplitude"][(work["iv_pct"] >= lo) & (work["iv_pct"] <= hi)].dropna().values
        o = work["amplitude"][(work["iv_pct"] < lo) | (work["iv_pct"] > hi)].dropna().values
        key = f"sensitivity_{int(lo*100)}_{int(hi*100)}"
        if len(m) >= 5 and len(o) >= 5:
            sensitivity[key] = round(_cliffs_delta(m, o), 4)
        else:
            sensitivity[key] = None

    if diff > 0.05 and p_mw < 0.10 and abs(cd) >= 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Mid-regime amplitude higher: median_mid={median_mid:.3f} vs "
            f"median_outer={median_outer:.3f} (diff={diff:.3f}, p={p_mw:.4f}, "
            f"Cliff's d={cd:.3f})"
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No amplitude advantage in mid-regime: median_mid={median_mid:.3f} vs "
            f"median_outer={median_outer:.3f} (diff={diff:.3f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.3f}) but not significant or effect small "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(f"  H42: n_mid={len(mid)}, n_outer={len(outer)}, diff={diff:.4f}, "
          f"p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H42", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=len(mid),
        metric_name="median_amplitude_diff_mid_vs_outer",
        metric_value=round(diff, 6),
        support_threshold=0.05, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="regime_comparison",
        extra_metrics={
            "n_mid": len(mid), "n_outer": len(outer),
            "median_mid": round(median_mid, 4),
            "median_outer": round(median_outer, 4),
            "cliffs_delta": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "u_stat": round(float(U_stat), 2),
            **sensitivity,
        },
    )


# ── H43: Overnight Gap Budget Consumption Reduces Intraday Range ─────────────────

def run_h43(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Sessions where overnight gap consumes a larger fraction of IVX-implied
    daily expected move show smaller intraday H-L range. Tested across three buckets
    (small/mid/large gap) to verify monotonicity, not just binary contrast.

    Signal: all days with valid OHLC + iv_30d after 1-day lag
    Metric: median_range_small - median_range_large
    Support: diff > 0, p_mannwhitney < 0.10, is_monotonic = True
    data_notes: directly_tested, data_fidelity: exact_underlying
    """
    required = ["open", "high", "low", "close", "iv_30d"]
    raw = len(df)
    excl_reason = "1-day lag for prev_close; missing OHLC or iv_30d"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H43", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="median_range_diff_small_vs_large_gap",
            metric_value=float("nan"), support_threshold=0.0, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[required + ["date"]].copy()
    work["prev_close"] = work["close"].shift(1)
    work["overnight_gap"] = (work["open"] - work["prev_close"]).abs()
    # Expected move based on prior-close price and prior iv_30d (both known pre-open)
    work["prev_iv30d"] = work["iv_30d"].shift(1)
    work["expected_move_prev"] = (work["prev_iv30d"] / np.sqrt(252)) * work["prev_close"]
    work["gap_fraction"] = work["overnight_gap"] / work["expected_move_prev"]
    work["intraday_range"] = (work["high"] - work["low"]) / work["open"]
    work = work.dropna()
    work = work[work["expected_move_prev"] > 0]  # guard against zero IV
    excluded = raw - len(work)

    if len(work) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H43", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_range_diff_small_vs_large_gap",
            metric_value=float("nan"), support_threshold=0.0, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations: {len(work)}",
            data_notes="directly_tested",
        )

    small = work["intraday_range"][work["gap_fraction"] < 0.20].values
    mid_g = work["intraday_range"][(work["gap_fraction"] >= 0.20) & (work["gap_fraction"] <= 0.40)].values
    large = work["intraday_range"][work["gap_fraction"] > 0.40].values

    if len(small) < 5 or len(large) < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H43", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_range_diff_small_vs_large_gap",
            metric_value=float("nan"), support_threshold=0.0, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few in small ({len(small)}) or large ({len(large)}) bucket",
            data_notes="directly_tested",
        )

    med_small = float(np.median(small))
    med_mid_g = float(np.median(mid_g)) if len(mid_g) > 0 else float("nan")
    med_large = float(np.median(large))
    diff = med_small - med_large
    is_monotonic = (not np.isnan(med_mid_g)) and (med_small > med_mid_g > med_large)

    U_stat, p_mw = stats.mannwhitneyu(small, large, alternative="greater")
    cd = _cliffs_delta(small, large)

    # Kruskal-Wallis across all three buckets
    kw_groups = [g for g in [small, mid_g, large] if len(g) >= 3]
    kw_stat, kw_p = stats.kruskal(*kw_groups) if len(kw_groups) >= 2 else (float("nan"), float("nan"))

    if diff > 0 and p_mw < 0.10 and is_monotonic:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Monotonic: small_gap range={med_small:.4f} > mid={med_mid_g:.4f} > "
            f"large={med_large:.4f} (diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No gap-budget effect: small_gap range={med_small:.4f} vs "
            f"large_gap={med_large:.4f} (diff={diff:.4f}, p={p_mw:.4f})"
        )
    else:
        reason_parts = [
            f"diff={diff:.4f} (p={p_mw:.4f}, Cliff's d={cd:.3f})"
        ]
        if not is_monotonic:
            reason_parts.append("not monotonic across three buckets")
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Direction present but criteria not fully met: {'; '.join(reason_parts)}"

    print(f"  H43: n_small={len(small)}, n_mid={len(mid_g)}, n_large={len(large)}, "
          f"diff={diff:.4f}, p={p_mw:.4f}, monotonic={is_monotonic} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H43", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=len(small) + len(large),
        metric_name="median_range_diff_small_vs_large_gap",
        metric_value=round(diff, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="regime_comparison",
        extra_metrics={
            "n_small": len(small), "n_mid": len(mid_g), "n_large": len(large),
            "median_range_small": round(med_small, 4),
            "median_range_mid": round(med_mid_g, 4) if not np.isnan(med_mid_g) else None,
            "median_range_large": round(med_large, 4),
            "cliffs_delta_small_vs_large": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "is_monotonic": is_monotonic,
            "kruskal_stat": round(float(kw_stat), 4) if not np.isnan(kw_stat) else None,
            "kruskal_p": round(float(kw_p), 4) if not np.isnan(kw_p) else None,
            "pct_small_gap_days": round(len(small) / len(work), 3),
            "pct_large_gap_days": round(len(large) / len(work), 3),
        },
    )


# ── H44: IV Term Structure Inversion Predicts Elevated Next-Day Range ─────────────

def run_h44(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Days where QQQ 30d IV > 60d IV (backwardation / term structure inversion)
    predict higher intraday H-L range in the following session vs. contango (normal) days.

    Note: iv_30d and iv_60d are constant-maturity interpolated IVX values (proxy),
    not exact contract IV. Evidence strength is lower than a direct-contract test.

    Signal: backwardation day (iv_30d > iv_60d)
    Outcome: next session's (high - low) / open
    Support: diff > 0.001, p_mannwhitney < 0.10, |cliffs_delta| >= 0.10
    data_notes: proxy_tested, data_fidelity: constant_maturity_iv
    """
    required = ["iv_30d", "iv_60d", "open", "high", "low"]
    raw = len(df)
    excl_reason = "1-day forward shift for next-session range; missing iv_30d/iv_60d or OHLC"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H44", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="median_next_range_diff_backwardation_vs_contango",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[required + ["date"]].copy()
    work["term_slope"] = work["iv_30d"] - work["iv_60d"]
    work["backwardation"] = work["term_slope"] > 0
    work["next_range"] = (work["high"].shift(-1) - work["low"].shift(-1)) / work["open"].shift(-1)
    # Drop last row (no next-day data) and any rows with NaN
    work = work.iloc[:-1].copy()
    work = work.dropna(subset=["term_slope", "next_range"])
    excluded = raw - len(work)

    if len(work) < 40:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H44", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_next_range_diff_backwardation_vs_contango",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations: {len(work)}",
            data_notes="proxy_tested",
        )

    back_vals = work["next_range"][work["backwardation"]].values
    cont_vals = work["next_range"][~work["backwardation"]].values

    if len(back_vals) < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H44", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=int(work["backwardation"].sum()),
            metric_name="median_next_range_diff_backwardation_vs_contango",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few backwardation days ({len(back_vals)}) to test",
            data_notes="proxy_tested",
        )

    med_back = float(np.median(back_vals))
    med_cont = float(np.median(cont_vals))
    diff = med_back - med_cont
    pct_back = float(work["backwardation"].mean())

    U_stat, p_mw = stats.mannwhitneyu(back_vals, cont_vals, alternative="greater")
    cd = _cliffs_delta(back_vals, cont_vals)

    if diff > 0.001 and p_mw < 0.10 and abs(cd) >= 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Backwardation days have higher next-session range: "
            f"median_back={med_back:.4f} vs median_cont={med_cont:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No range elevation after term-structure inversion: "
            f"median_back={med_back:.4f} vs median_cont={med_cont:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.4f}) but not significant or effect small "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(f"  H44: n_back={len(back_vals)} ({pct_back:.1%}), n_cont={len(cont_vals)}, "
          f"diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H44", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=int(work["backwardation"].sum()),
        metric_name="median_next_range_diff_backwardation_vs_contango",
        metric_value=round(diff, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        data_fidelity="constant_maturity_iv",
        metric_family="regime_comparison",
        extra_metrics={
            "n_backwardation": len(back_vals),
            "n_contango": len(cont_vals),
            "median_range_backwardation": round(med_back, 4),
            "median_range_contango": round(med_cont, 4),
            "cliffs_delta": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "u_stat": round(float(U_stat), 2),
            "pct_backwardation_days": round(pct_back, 3),
        },
    )


# ── H53: Passarelli Pattern 4 — IV Rising / Realized Vol Flat → Range Expansion ──

def run_h53(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: 5-day IV rising while 5-day realized vol flat/falling (Pattern 4)
    predicts above-median next-session intraday range.

    Signal: delta_iv > 0.005 AND delta_rv < 0.005 over trailing 5 days.
    Control: delta_iv < 0 AND delta_rv < 0.005 (both flat/falling — no urgency).
    Outcome: next-session (high - low) / close
    Support: median diff > 0.002, p_mw < 0.10, |cliffs_delta| >= 0.10
    data_notes: directly_tested, data_fidelity: constant_maturity_iv
    """
    required = ["iv_30d", "log_return", "high", "low", "close"]
    raw = len(df)
    excl_reason = "5-day rolling warmup for IV/HV change; 1-day forward shift for next-session range"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H53", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="median_range_diff_pattern4_vs_control",
            metric_value=float("nan"), support_threshold=0.002, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[required + ["date"]].copy()
    rv_5d = work["log_return"].rolling(5).std() * np.sqrt(252)
    work["delta_iv"] = work["iv_30d"] - work["iv_30d"].shift(5)
    work["delta_rv"] = rv_5d - rv_5d.shift(5)
    work["next_range"] = (work["high"].shift(-1) - work["low"].shift(-1)) / work["close"]

    work = work.iloc[:-1].copy()  # drop last row (no next-day data)
    work = work.dropna(subset=["delta_iv", "delta_rv", "next_range", "close"])
    work = work[work["close"] > 0]
    excluded = raw - len(work)

    if len(work) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H53", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_range_diff_pattern4_vs_control",
            metric_value=float("nan"), support_threshold=0.002, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations: {len(work)}",
            data_notes="directly_tested",
        )

    pattern4 = (work["delta_iv"] > 0.005) & (work["delta_rv"] < 0.005)
    control   = (work["delta_iv"] < 0.000) & (work["delta_rv"] < 0.005)

    p4_vals   = work["next_range"][pattern4].values
    ctrl_vals = work["next_range"][control].values
    pct_p4 = float(pattern4.mean())

    if len(p4_vals) < 30 or len(ctrl_vals) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H53", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=int(pattern4.sum()),
            metric_name="median_range_diff_pattern4_vs_control",
            metric_value=float("nan"), support_threshold=0.002, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(
                f"Too few observations: pattern4={len(p4_vals)}, control={len(ctrl_vals)}. "
                f"Pattern 4 occurs {pct_p4:.1%} of days — need >= 30 per group."
            ),
            data_notes="directly_tested",
        )

    med_p4   = float(np.median(p4_vals))
    med_ctrl = float(np.median(ctrl_vals))
    diff = med_p4 - med_ctrl
    U_stat, p_mw = stats.mannwhitneyu(p4_vals, ctrl_vals, alternative="greater")
    cd = _cliffs_delta(p4_vals, ctrl_vals)

    if diff > 0.002 and p_mw < 0.10 and abs(cd) >= 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Pattern 4 sessions show higher next-day range: "
            f"median_p4={med_p4:.4f} vs median_ctrl={med_ctrl:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"Pattern 4 shows no range expansion: "
            f"median_p4={med_p4:.4f} vs median_ctrl={med_ctrl:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.4f}) but not significant or effect small "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(
        f"  H53: n_p4={len(p4_vals)} ({pct_p4:.1%}), n_ctrl={len(ctrl_vals)}, "
        f"diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H53", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=int(pattern4.sum()),
        metric_name="median_range_diff_pattern4_vs_control",
        metric_value=round(diff, 6),
        support_threshold=0.002, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="constant_maturity_iv",
        metric_family="regime_comparison",
        extra_metrics={
            "n_pattern4": len(p4_vals),
            "n_control": len(ctrl_vals),
            "median_range_pattern4": round(med_p4, 4),
            "median_range_control": round(med_ctrl, 4),
            "cliffs_delta": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "u_stat": round(float(U_stat), 2),
            "pct_pattern4_days": round(pct_p4, 3),
        },
    )


# ── H55: Vanna Near Expiry — Thursday Downs → Stronger Next-Session IV Rebound ──

def run_h55(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Down sessions on Thursdays (day before weekly expiry) show larger
    next-session iv_30d rebounds than comparable down sessions on other days.

    Signal: Thursday AND log_return < -0.005
    Control: non-Thursday AND log_return < -0.005
    Outcome: next-session iv_30d change (iv_30d.shift(-1) - iv_30d)
    Support: mean diff > 0.003, p_mw < 0.15
    data_notes: proxy_tested, data_fidelity: constant_maturity_iv
    """
    required = ["iv_30d", "log_return", "date"]
    raw = len(df)
    excl_reason = "1-day forward shift for next-session IV; requires date column for day-of-week"
    missing = [c for c in ["iv_30d", "log_return"] if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H55", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="mean_iv_rebound_diff_thursday_vs_other_down",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[["iv_30d", "log_return", "date"]].copy()
    work["date"] = pd.to_datetime(work["date"])
    work["is_thursday"] = work["date"].dt.dayofweek == 3
    work["next_iv_change"] = work["iv_30d"].shift(-1) - work["iv_30d"]
    work = work.iloc[:-1].copy()  # drop last row (no next-day data)
    work = work.dropna(subset=["iv_30d", "log_return", "next_iv_change"])
    excluded = raw - len(work)

    if len(work) < 40:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H55", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="mean_iv_rebound_diff_thursday_vs_other_down",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations: {len(work)}",
            data_notes="proxy_tested",
        )

    down = work["log_return"] < -0.005
    thu_down = work["is_thursday"] & down
    other_down = ~work["is_thursday"] & down

    thu_vals   = work["next_iv_change"][thu_down].values
    other_vals = work["next_iv_change"][other_down].values

    if len(thu_vals) < 10 or len(other_vals) < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H55", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=int(thu_down.sum()),
            metric_name="mean_iv_rebound_diff_thursday_vs_other_down",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(
                f"Too few down sessions: thursday_down={len(thu_vals)}, "
                f"other_down={len(other_vals)}. Need >= 10 each."
            ),
            data_notes="proxy_tested",
        )

    mean_thu   = float(np.mean(thu_vals))
    mean_other = float(np.mean(other_vals))
    diff = mean_thu - mean_other
    U_stat, p_mw = stats.mannwhitneyu(thu_vals, other_vals, alternative="greater")
    cd = _cliffs_delta(thu_vals, other_vals)

    if diff > 0.003 and p_mw < 0.15:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Thursday down sessions show stronger IV rebound: "
            f"mean_thu={mean_thu:.4f} vs mean_other={mean_other:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )
    elif diff <= 0 or p_mw > 0.35:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No vanna-expiry IV rebound: mean_thu={mean_thu:.4f} vs "
            f"mean_other={mean_other:.4f} (diff={diff:.4f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.4f}) but not significant "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(
        f"  H55: n_thu_down={len(thu_vals)}, n_other_down={len(other_vals)}, "
        f"diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H55", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=int(thu_down.sum()),
        metric_name="mean_iv_rebound_diff_thursday_vs_other_down",
        metric_value=round(diff, 6),
        support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        data_fidelity="constant_maturity_iv",
        metric_family="iv_level_change",
        extra_metrics={
            "n_thursday_down": len(thu_vals),
            "n_other_down": len(other_vals),
            "mean_iv_rebound_thursday": round(mean_thu, 4),
            "mean_iv_rebound_other": round(mean_other, 4),
            "cliffs_delta": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "u_stat": round(float(U_stat), 2),
        },
    )


# ── H57: Continuous Term Structure Slope → Calendar Spread Efficiency ─────────────

def run_h57(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Days in the top quintile of iv_60d - iv_30d slope (steep contango)
    show greater 5-day slope convergence than bottom-quintile days (flat/backwardation),
    consistent with calendar spread P&L being favorable in steep contango.

    Signal: slope in top quintile (>= 80th pct) or bottom quintile (<= 20th pct)
    Outcome: slope_convergence = slope - slope.shift(-5)  (positive = moved toward flat)
    Support: median diff > 0.001, p_mw < 0.10
    data_notes: proxy_tested, data_fidelity: constant_maturity_iv
    """
    required = ["iv_30d", "iv_60d"]
    raw = len(df)
    excl_reason = "5-day forward shift for slope convergence; requires both iv_30d and iv_60d"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H57", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="median_slope_convergence_diff_top_vs_bottom_quintile",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[required + ["date"]].copy()
    work["slope"] = work["iv_60d"] - work["iv_30d"]
    work["slope_5d_later"] = work["slope"].shift(-5)
    work["convergence"] = work["slope"] - work["slope_5d_later"]
    work = work.dropna(subset=["slope", "convergence"])
    excluded = raw - len(work)

    if len(work) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H57", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_slope_convergence_diff_top_vs_bottom_quintile",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations: {len(work)}",
            data_notes="proxy_tested",
        )

    q20 = float(work["slope"].quantile(0.20))
    q80 = float(work["slope"].quantile(0.80))

    top    = work["convergence"][work["slope"] >= q80].values
    bottom = work["convergence"][work["slope"] <= q20].values

    if len(top) < 10 or len(bottom) < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H57", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=len(top),
            metric_name="median_slope_convergence_diff_top_vs_bottom_quintile",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few in top ({len(top)}) or bottom ({len(bottom)}) quintile",
            data_notes="proxy_tested",
        )

    med_top    = float(np.median(top))
    med_bottom = float(np.median(bottom))
    diff = med_top - med_bottom
    U_stat, p_mw = stats.mannwhitneyu(top, bottom, alternative="greater")
    cd = _cliffs_delta(top, bottom)

    if diff > 0.001 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Steep contango shows more slope convergence: "
            f"median_top={med_top:.4f} vs median_bottom={med_bottom:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f}). "
            f"Note: convergence is a proxy for calendar spread P&L; actual P&L requires options pricing."
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No contango advantage: median_top={med_top:.4f} vs "
            f"median_bottom={med_bottom:.4f} (diff={diff:.4f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.4f}) but not significant "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(
        f"  H57: n_top={len(top)}, n_bottom={len(bottom)}, q20={q20:.4f}, q80={q80:.4f}, "
        f"diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H57", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=len(top),
        metric_name="median_slope_convergence_diff_top_vs_bottom_quintile",
        metric_value=round(diff, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        data_fidelity="constant_maturity_iv",
        metric_family="regime_comparison",
        extra_metrics={
            "n_top_quintile": len(top),
            "n_bottom_quintile": len(bottom),
            "median_convergence_top": round(med_top, 4),
            "median_convergence_bottom": round(med_bottom, 4),
            "cliffs_delta": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "u_stat": round(float(U_stat), 2),
            "slope_q20": round(q20, 4),
            "slope_q80": round(q80, 4),
        },
    )


# ── H59: Thursday Term Structure → Monday IV Direction (Expiry Roll Effect) ───────

def run_h59(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Thursday iv_60d - iv_30d slope sign predicts Monday iv_30d change direction
    with > 60% win rate, consistent with weekly expiry roll compression artifact.

    Signal: all Thursdays with valid slope data
    Outcome: following Monday iv_30d - Thursday iv_30d (positive = IV rose over weekend)
    Metric: win_rate = fraction where Thursday slope sign matches Monday IV change direction
    Support: win_rate > 0.60, p_binomial < 0.10
    data_notes: directly_tested, data_fidelity: constant_maturity_iv
    """
    required = ["iv_30d", "iv_60d", "date"]
    raw = len(df)
    excl_reason = "Requires matching Thursday-to-Monday pairs; day-of-week filtering"
    missing = [c for c in ["iv_30d", "iv_60d"] if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H59", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="thursday_slope_predicts_monday_iv_win_rate",
            metric_value=float("nan"), support_threshold=0.60, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[["iv_30d", "iv_60d", "date"]].copy()
    work["date"] = pd.to_datetime(work["date"])
    work["slope"] = work["iv_60d"] - work["iv_30d"]
    work["dow"] = work["date"].dt.dayofweek  # Monday=0, Thursday=3
    work = work.dropna(subset=["iv_30d", "iv_60d", "slope"]).reset_index(drop=True)
    excluded = raw - len(work)

    thursdays = work[work["dow"] == 3].copy()
    mondays = work[work["dow"] == 0].copy()

    if len(thursdays) < 20 or len(mondays) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H59", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=len(thursdays),
            metric_name="thursday_slope_predicts_monday_iv_win_rate",
            metric_value=float("nan"), support_threshold=0.60, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few Thursdays ({len(thursdays)}) or Mondays ({len(mondays)})",
            data_notes="directly_tested",
        )

    # Match each Thursday to the nearest following Monday
    pairs = []
    mon_dates = mondays["date"].sort_values().values
    for _, thu_row in thursdays.iterrows():
        thu_date = thu_row["date"]
        future_mons = mon_dates[mon_dates > thu_date]
        if len(future_mons) == 0:
            continue
        next_mon = future_mons[0]
        mon_row = mondays[mondays["date"] == next_mon]
        if len(mon_row) == 0:
            continue
        mon_iv = float(mon_row["iv_30d"].iloc[0])
        thu_iv = float(thu_row["iv_30d"])
        thu_slope = float(thu_row["slope"])
        mon_iv_change = mon_iv - thu_iv
        slope_positive = thu_slope > 0
        iv_rose = mon_iv_change > 0
        win = (slope_positive == iv_rose)
        pairs.append({
            "thu_date": thu_date,
            "thu_slope": thu_slope,
            "mon_iv_change": mon_iv_change,
            "win": win,
            "slope_positive": slope_positive,
        })

    if len(pairs) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H59", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=len(pairs),
            metric_name="thursday_slope_predicts_monday_iv_win_rate",
            metric_value=float("nan"), support_threshold=0.60, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few matched Thursday-Monday pairs: {len(pairs)} (need >= 20)",
            data_notes="directly_tested",
        )

    pairs_df = pd.DataFrame(pairs)
    n_pairs = len(pairs_df)
    n_wins = int(pairs_df["win"].sum())
    win_rate = float(pairs_df["win"].mean())

    # Binomial test: is win_rate > 0.50?
    binom_result = stats.binomtest(n_wins, n_pairs, p=0.50, alternative="greater")
    p_binomial = float(binom_result.pvalue)

    # Group means for extra context
    steep_contango = pairs_df["slope_positive"]
    mean_mon_change_contango = float(pairs_df["mon_iv_change"][steep_contango].mean()) if steep_contango.sum() > 0 else float("nan")
    mean_mon_change_back = float(pairs_df["mon_iv_change"][~steep_contango].mean()) if (~steep_contango).sum() > 0 else float("nan")

    if win_rate > 0.60 and p_binomial < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Thursday slope correctly predicts Monday IV direction {win_rate:.1%} of weeks "
            f"(n={n_pairs}, wins={n_wins}, p_binomial={p_binomial:.4f}) — "
            f"consistent with weekly expiry roll compression."
        )
    elif win_rate <= 0.50 or p_binomial > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"Thursday slope does not predict Monday IV direction: "
            f"win_rate={win_rate:.1%} (n={n_pairs}, p_binomial={p_binomial:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Win rate={win_rate:.1%} (p_binomial={p_binomial:.4f}) — "
            f"above 50% but not significant at alpha=0.10"
        )

    print(
        f"  H59: n_pairs={n_pairs}, wins={n_wins}, win_rate={win_rate:.1%}, "
        f"p_binomial={p_binomial:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H59", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_pairs,
        metric_name="thursday_slope_predicts_monday_iv_win_rate",
        metric_value=round(win_rate, 4),
        support_threshold=0.60, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="constant_maturity_iv",
        metric_family="intraday_pattern",
        extra_metrics={
            "n_weeks": n_pairs,
            "n_wins": n_wins,
            "win_rate": round(win_rate, 4),
            "p_binomial": round(p_binomial, 4),
            "mean_monday_change_contango": round(mean_mon_change_contango, 4) if not np.isnan(mean_mon_change_contango) else None,
            "mean_monday_change_backwardation": round(mean_mon_change_back, 4) if not np.isnan(mean_mon_change_back) else None,
        },
    )


# ── H60: Pattern 4 Episode Clustering (≥ 3 Consecutive Days) ─────────────────────

def run_h60(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Pattern 4 signals (IV rising 5-day while realized vol flat) cluster into
    episodes lasting >= 3 consecutive sessions in the majority of occurrences.

    Signal: same pattern4_mask as H53 — delta_iv > 0.005 AND delta_rv < 0.005
    Metric: pct_runs_ge_3 = fraction of consecutive-True runs with length >= 3
    Support: pct_runs_ge_3 > 0.50 AND n_runs >= 10
    Reject: pct_runs_ge_3 <= 0.30
    data_notes: directly_tested, data_fidelity: constant_maturity_iv
    Note: meaningfully interpreted only if H53 is supported.
    """
    required = ["iv_30d", "log_return"]
    raw = len(df)
    excl_reason = "5-day rolling warmup for IV/HV change"
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H60", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="pct_pattern4_runs_ge_3_days",
            metric_value=float("nan"), support_threshold=0.50, reject_threshold=0.30,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    work = df[required].copy()
    rv_5d = work["log_return"].rolling(5).std() * np.sqrt(252)
    delta_iv = work["iv_30d"] - work["iv_30d"].shift(5)
    delta_rv = rv_5d - rv_5d.shift(5)
    work["delta_iv"] = delta_iv
    work["delta_rv"] = delta_rv
    work = work.dropna()
    excluded = raw - len(work)

    pattern4 = ((work["delta_iv"] > 0.005) & (work["delta_rv"] < 0.005)).values

    if len(work) < 40:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H60", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=int(pattern4.sum()),
            metric_name="pct_pattern4_runs_ge_3_days",
            metric_value=float("nan"), support_threshold=0.50, reject_threshold=0.30,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations: {len(work)}",
            data_notes="directly_tested",
        )

    # Compute run lengths of consecutive True blocks
    run_lengths = []
    in_run = False
    current_run = 0
    for val in pattern4:
        if val:
            current_run += 1
            in_run = True
        else:
            if in_run:
                run_lengths.append(current_run)
            current_run = 0
            in_run = False
    if in_run and current_run > 0:
        run_lengths.append(current_run)

    n_runs = len(run_lengths)

    if n_runs < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H60", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=int(pattern4.sum()),
            metric_name="pct_pattern4_runs_ge_3_days",
            metric_value=float("nan"), support_threshold=0.50, reject_threshold=0.30,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(
                f"Only {n_runs} Pattern 4 episodes found (need >= 5). "
                f"Pattern 4 occurs on {pattern4.mean():.1%} of days."
            ),
            data_notes="directly_tested",
        )

    pct_ge_3 = float(sum(1 for r in run_lengths if r >= 3) / n_runs)
    median_run = float(np.median(run_lengths))
    mean_run = float(np.mean(run_lengths))
    max_run = int(max(run_lengths))

    if pct_ge_3 > 0.50 and n_runs >= 10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Pattern 4 episodes cluster: {pct_ge_3:.1%} of {n_runs} episodes last >= 3 days "
            f"(median run={median_run:.1f}, max={max_run}). "
            f"Note: interpret meaningfully only if H53 is supported."
        )
    elif pct_ge_3 <= 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"Pattern 4 does not cluster: only {pct_ge_3:.1%} of {n_runs} episodes last >= 3 days "
            f"(median run={median_run:.1f}). Signal resolves quickly."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Mixed clustering: {pct_ge_3:.1%} of {n_runs} episodes >= 3 days "
            f"(median run={median_run:.1f}) — between 30% and 50% threshold."
        )

    print(
        f"  H60: n_runs={n_runs}, pct_ge_3={pct_ge_3:.1%}, "
        f"median_run={median_run:.1f}, max_run={max_run} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H60", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=int(pattern4.sum()),
        metric_name="pct_pattern4_runs_ge_3_days",
        metric_value=round(pct_ge_3, 4),
        support_threshold=0.50, reject_threshold=0.30,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="constant_maturity_iv",
        metric_family="persistence",
        extra_metrics={
            "n_runs": n_runs,
            "pct_runs_ge_3": round(pct_ge_3, 4),
            "median_run_length": round(median_run, 2),
            "mean_run_length": round(mean_run, 2),
            "max_run_length": max_run,
            "pct_pattern4_days": round(float(pattern4.mean()), 3),
        },
    )


# ── H70: 1-Day RV Autocorrelation — Top Quintile Range → Next-Session Range ────────

def run_h70(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H70", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="win_rate_top_quintile", metric_value=float("nan"),
            support_threshold=0.60, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date"] + required].dropna().copy()
    work["daily_range"] = (work["high"] - work["low"]) / work["close"]
    work["next_range"] = work["daily_range"].shift(-1)
    work = work.dropna(subset=["next_range"])

    q80 = work["daily_range"].quantile(0.80)
    median_range = work["daily_range"].median()

    signal = work["daily_range"] >= q80
    n_signal = int(signal.sum())
    if n_signal < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H70", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="1-day forward shift; next_range NaN on last row",
            n_observations=len(work), n_signals=n_signal,
            metric_name="win_rate_top_quintile", metric_value=float("nan"),
            support_threshold=0.60, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_signal={n_signal} < 20", data_notes="directly_tested",
        )

    wins = int((work["next_range"][signal] > median_range).sum())
    win_rate = wins / n_signal
    p_binom = float(stats.binomtest(wins, n_signal, 0.5, alternative="greater").pvalue)

    if win_rate > 0.60 and p_binom < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"win_rate={win_rate:.3f} ({wins}/{n_signal}) > 0.60 threshold, "
            f"p_binomial={p_binom:.4f} < 0.10. Top-quintile range threshold: {q80:.4f}."
        )
    elif win_rate <= 0.50 or p_binom > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"win_rate={win_rate:.3f} ({wins}/{n_signal}), p_binomial={p_binom:.4f}. "
            f"No reliable 1-day range autocorrelation at top-quintile threshold."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"win_rate={win_rate:.3f} ({wins}/{n_signal}), p_binomial={p_binom:.4f}. "
            f"Direction present but below significance threshold."
        )

    print(f"  H70: win_rate={win_rate:.3f}, n_signal={n_signal}, p_binom={p_binom:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H70", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="1-day forward shift; next_range NaN on last row",
        n_observations=len(work), n_signals=n_signal,
        metric_name="win_rate_top_quintile", metric_value=round(win_rate, 4),
        support_threshold=0.60, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "q80_threshold": round(float(q80), 5),
            "median_range": round(float(median_range), 5),
            "n_signal": n_signal,
            "n_wins": wins,
            "p_binomial": round(p_binom, 4),
            "mean_next_range_signal": round(float(work["next_range"][signal].mean()), 5),
            "mean_next_range_rest": round(float(work["next_range"][~signal].mean()), 5),
        },
    )


# ── H71: Opening Gap Fill ─────────────────────────────────────────────────────────

def run_h71(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["open", "close", "log_return"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H71", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="gap_fill_rate", metric_value=float("nan"),
            support_threshold=0.55, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date", "open", "close", "log_return"]].dropna().copy()
    # Reconstruct prev_close from log_return: prev_close = close / exp(log_return)
    work["prev_close"] = work["close"] / np.exp(work["log_return"])
    work["gap_pct"] = (work["open"] - work["prev_close"]) / work["prev_close"]
    work["gap_abs"] = work["gap_pct"].abs()

    gap_days = work[work["gap_abs"] > 0.005].copy()
    n_gap = len(gap_days)

    if n_gap < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H71", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="Rows with NaN in open/close/log_return dropped",
            n_observations=len(work), n_signals=n_gap,
            metric_name="gap_fill_rate", metric_value=float("nan"),
            support_threshold=0.55, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_gap_days={n_gap} < 20", data_notes="directly_tested",
        )

    # Gap fill: close nearer to prev_close than to open
    gap_days["dist_to_prev"] = (gap_days["close"] - gap_days["prev_close"]).abs()
    gap_days["dist_to_open"] = (gap_days["close"] - gap_days["open"]).abs()
    gap_days["filled"] = gap_days["dist_to_prev"] < gap_days["dist_to_open"]

    n_filled = int(gap_days["filled"].sum())
    fill_rate = n_filled / n_gap
    p_binom = float(stats.binomtest(n_filled, n_gap, 0.5, alternative="greater").pvalue)

    # Split by direction
    up_gaps = gap_days[gap_days["gap_pct"] > 0]
    dn_gaps = gap_days[gap_days["gap_pct"] < 0]
    up_fill = float(up_gaps["filled"].mean()) if len(up_gaps) > 0 else float("nan")
    dn_fill = float(dn_gaps["filled"].mean()) if len(dn_gaps) > 0 else float("nan")

    if fill_rate > 0.55 and p_binom < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Gap fill rate={fill_rate:.3f} ({n_filled}/{n_gap}) > 0.55 threshold, "
            f"p_binomial={p_binom:.4f} < 0.10. Up-gap fill: {up_fill:.3f} ({len(up_gaps)} gaps). "
            f"Down-gap fill: {dn_fill:.3f} ({len(dn_gaps)} gaps)."
        )
    elif fill_rate <= 0.50 or p_binom > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"Gap fill rate={fill_rate:.3f} ({n_filled}/{n_gap}), p_binomial={p_binom:.4f}. "
            f"No reliable gap-fill bias for gaps > 0.5%."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Gap fill rate={fill_rate:.3f} ({n_filled}/{n_gap}), p_binomial={p_binom:.4f}. "
            f"Fill bias present but below significance threshold."
        )

    print(f"  H71: fill_rate={fill_rate:.3f}, n_gap={n_gap}, p_binom={p_binom:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H71", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="Rows with NaN in open/close/log_return dropped",
        n_observations=len(work), n_signals=n_gap,
        metric_name="gap_fill_rate", metric_value=round(fill_rate, 4),
        support_threshold=0.55, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_gap_days": n_gap,
            "n_filled": n_filled,
            "p_binomial": round(p_binom, 4),
            "fill_rate_up_gaps": round(up_fill, 4) if not np.isnan(up_fill) else None,
            "fill_rate_down_gaps": round(dn_fill, 4) if not np.isnan(dn_fill) else None,
            "n_up_gaps": len(up_gaps),
            "n_down_gaps": len(dn_gaps),
            "pct_gap_days": round(n_gap / len(work), 3),
        },
    )


# ── H72: Variance Premium Sweet Spot ─────────────────────────────────────────────

def run_h72(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["iv_30d", "fwd_rv_20"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H72", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="mean_vp_sweetspot_minus_overextended", metric_value=float("nan"),
            support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date"] + required].dropna().copy()
    # Rolling 90-day mean/std of iv_30d
    work["iv_mean90"] = work["iv_30d"].rolling(90).mean()
    work["iv_std90"] = work["iv_30d"].rolling(90).std()
    work = work.dropna(subset=["iv_mean90", "iv_std90"])

    work["z_iv"] = (work["iv_30d"] - work["iv_mean90"]) / work["iv_std90"]
    work["vp"] = work["iv_30d"] - work["fwd_rv_20"]
    work = work.dropna(subset=["vp"])

    sweetspot = work[(work["z_iv"] >= 1.0) & (work["z_iv"] <= 1.5)]
    overextended = work[work["z_iv"] > 2.0]
    baseline = work[work["z_iv"] < 0.5]

    n_sweet = len(sweetspot)
    n_over = len(overextended)

    if n_sweet < 10 or n_over < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H72", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="90-day rolling warmup; fwd_rv_20 NaN for last 20 rows",
            n_observations=len(work), n_signals=n_sweet,
            metric_name="mean_vp_sweetspot_minus_overextended", metric_value=float("nan"),
            support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_sweetspot={n_sweet}, n_overextended={n_over} — too few for test",
            data_notes="directly_tested",
        )

    mean_vp_sweet = float(sweetspot["vp"].mean())
    mean_vp_over = float(overextended["vp"].mean())
    mean_vp_base = float(baseline["vp"].mean())
    diff = mean_vp_sweet - mean_vp_over

    _, p_mw = stats.mannwhitneyu(sweetspot["vp"].values, overextended["vp"].values,
                                  alternative="greater")

    if diff > 0.005 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Sweet-spot VP={mean_vp_sweet:.4f} > overextended VP={mean_vp_over:.4f} "
            f"(diff={diff:.4f}), p_mannwhitney={p_mw:.4f}. "
            f"Baseline VP={mean_vp_base:.4f}. n_sweet={n_sweet}, n_over={n_over}."
        )
    elif diff <= 0.0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No sweet-spot advantage: diff={diff:.4f}, p_mannwhitney={p_mw:.4f}. "
            f"VP sweet={mean_vp_sweet:.4f}, VP over={mean_vp_over:.4f}."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"diff={diff:.4f}, p_mannwhitney={p_mw:.4f}. "
            f"VP sweet={mean_vp_sweet:.4f}, VP over={mean_vp_over:.4f}. "
            f"Direction correct but not significant."
        )

    print(f"  H72: diff={diff:.4f}, n_sweet={n_sweet}, n_over={n_over}, p={p_mw:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H72", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="90-day rolling warmup; fwd_rv_20 NaN for last 20 rows",
        n_observations=len(work), n_signals=n_sweet,
        metric_name="mean_vp_sweetspot_minus_overextended", metric_value=round(diff, 5),
        support_threshold=0.005, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_sweetspot": n_sweet,
            "n_overextended": n_over,
            "n_baseline": len(baseline),
            "mean_vp_sweetspot": round(mean_vp_sweet, 5),
            "mean_vp_overextended": round(mean_vp_over, 5),
            "mean_vp_baseline": round(mean_vp_base, 5),
            "p_mannwhitney": round(p_mw, 4),
        },
    )


# ── H73: Compound Signal — Pattern 4 + Backwardation → Range ─────────────────────

def run_h73(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["iv_30d", "iv_60d", "log_return", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H73", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="median_range_both_minus_p4_only", metric_value=float("nan"),
            support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date"] + required].dropna().copy()
    work["daily_range"] = (work["high"] - work["low"]) / work["close"]

    # Pattern 4: 5-day IV rising, 5-day RV flat/falling
    rv_5d = work["log_return"].rolling(5).std() * np.sqrt(252)
    delta_iv = work["iv_30d"] - work["iv_30d"].shift(5)
    delta_rv = rv_5d - rv_5d.shift(5)
    pattern4 = (delta_iv > 0.005) & (delta_rv < 0.005)

    # Backwardation: iv_30d > iv_60d
    backwardation = work["iv_30d"] > work["iv_60d"]

    work["next_range"] = work["daily_range"].shift(-1)
    work = work.dropna(subset=["next_range"])
    pattern4 = pattern4.reindex(work.index)
    backwardation = backwardation.reindex(work.index)

    both = pattern4 & backwardation
    p4_only = pattern4 & ~backwardation
    bk_only = ~pattern4 & backwardation
    neither = ~pattern4 & ~backwardation

    n_both = int(both.sum())
    n_p4 = int(p4_only.sum())

    if n_both < 10 or n_p4 < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H73", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="5-day rolling warmup; 1-day forward shift",
            n_observations=len(work), n_signals=n_both,
            metric_name="median_range_both_minus_p4_only", metric_value=float("nan"),
            support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_both={n_both}, n_p4_only={n_p4} — too few for comparison",
            data_notes="directly_tested",
        )

    both_vals = work["next_range"][both].values
    p4_vals = work["next_range"][p4_only].values
    bk_vals = work["next_range"][bk_only].values
    neither_vals = work["next_range"][neither].values

    med_both = float(np.median(both_vals))
    med_p4 = float(np.median(p4_vals))
    med_bk = float(np.median(bk_vals))
    med_neither = float(np.median(neither_vals))
    diff = med_both - med_p4

    _, p_mw = stats.mannwhitneyu(both_vals, p4_vals, alternative="greater")

    if diff > 0.001 and p_mw < 0.15:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Compound signal range={med_both:.5f} > P4-only range={med_p4:.5f} "
            f"(diff={diff:.5f}), p_mannwhitney={p_mw:.4f}. "
            f"n_both={n_both}, n_p4_only={n_p4}."
        )
    elif diff <= 0.0 or p_mw > 0.35:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No compound signal advantage: diff={diff:.5f}, p_mannwhitney={p_mw:.4f}. "
            f"Both={med_both:.5f}, P4-only={med_p4:.5f}."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"diff={diff:.5f}, p_mannwhitney={p_mw:.4f}. "
            f"Both={med_both:.5f}, P4-only={med_p4:.5f}. Inconclusive."
        )

    print(f"  H73: diff={diff:.5f}, n_both={n_both}, p={p_mw:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H73", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="5-day rolling warmup; 1-day forward shift",
        n_observations=len(work), n_signals=n_both,
        metric_name="median_range_both_minus_p4_only", metric_value=round(diff, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_both": n_both,
            "n_p4_only": n_p4,
            "n_backwardation_only": int(bk_only.sum()),
            "n_neither": int(neither.sum()),
            "median_range_both": round(med_both, 6),
            "median_range_p4_only": round(med_p4, 6),
            "median_range_backwardation_only": round(med_bk, 6),
            "median_range_neither": round(med_neither, 6),
            "p_mannwhitney_both_vs_p4": round(p_mw, 4),
        },
    )


# ── H74: Buy-the-Dip 3-Session Swing ─────────────────────────────────────────────

def run_h74(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["log_return"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H74", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="win_rate_positive_3d", metric_value=float("nan"),
            support_threshold=0.55, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date", "log_return"]].dropna().copy().reset_index(drop=True)
    # Forward 3-session cumulative return
    work["cum3"] = (
        work["log_return"].shift(-1) +
        work["log_return"].shift(-2) +
        work["log_return"].shift(-3)
    )
    # Signal: today's return < -1%
    signal = work["log_return"] < -0.01
    valid = work[signal & work["cum3"].notna()].copy()
    n_signal = len(valid)

    if n_signal < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H74", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="3-day forward cumsum NaN for last 3 rows",
            n_observations=len(work), n_signals=n_signal,
            metric_name="win_rate_positive_3d", metric_value=float("nan"),
            support_threshold=0.55, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_signal={n_signal} < 20", data_notes="directly_tested",
        )

    n_wins = int((valid["cum3"] > 0).sum())
    win_rate = n_wins / n_signal
    mean_3d = float(valid["cum3"].mean())
    median_3d = float(valid["cum3"].median())
    p_binom = float(stats.binomtest(n_wins, n_signal, 0.5, alternative="greater").pvalue)

    if win_rate > 0.55 and p_binom < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"3-day win rate={win_rate:.3f} ({n_wins}/{n_signal}) > 0.55 threshold, "
            f"p_binomial={p_binom:.4f}. mean_3d_return={mean_3d:.4f}, "
            f"median_3d_return={median_3d:.4f}. Signal: log_return < -1% ({n_signal} occurrences)."
        )
    elif win_rate <= 0.50 or p_binom > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"win_rate={win_rate:.3f} ({n_wins}/{n_signal}), p_binomial={p_binom:.4f}. "
            f"mean_3d={mean_3d:.4f}. No reliable buy-the-dip 3-session effect."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"win_rate={win_rate:.3f} ({n_wins}/{n_signal}), p_binomial={p_binom:.4f}. "
            f"mean_3d={mean_3d:.4f}. Direction present but not significant."
        )

    print(f"  H74: win_rate={win_rate:.3f}, n={n_signal}, p_binom={p_binom:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H74", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="3-day forward cumsum NaN for last 3 rows",
        n_observations=len(work), n_signals=n_signal,
        metric_name="win_rate_positive_3d", metric_value=round(win_rate, 4),
        support_threshold=0.55, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_signal_days": n_signal,
            "n_wins": n_wins,
            "p_binomial": round(p_binom, 4),
            "mean_3d_return": round(mean_3d, 5),
            "median_3d_return": round(median_3d, 5),
            "pct_signal_days": round(n_signal / len(work), 3),
        },
    )


# ── H75: Weekend IV Premium — Monday vs Prior Friday ─────────────────────────────

def run_h75(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["iv_30d", "date"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H75", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="mean_iv_change_monday", metric_value=float("nan"),
            support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date", "iv_30d"]].dropna().copy()
    work["dow"] = pd.to_datetime(work["date"]).dt.dayofweek  # 0=Mon, 4=Fri

    mondays = work[work["dow"] == 0].copy().reset_index(drop=True)
    fridays = work[work["dow"] == 4].copy().reset_index(drop=True)

    # Match each Monday to the most recent prior Friday
    iv_changes = []
    fri_dates = pd.to_datetime(fridays["date"]).values
    for _, row in mondays.iterrows():
        mon_date = pd.to_datetime(row["date"])
        prior_fris = fri_dates[fri_dates < mon_date]
        if len(prior_fris) == 0:
            continue
        prior_fri = prior_fris[-1]
        fri_row = fridays[pd.to_datetime(fridays["date"]) == prior_fri]
        if len(fri_row) == 0:
            continue
        iv_changes.append(float(row["iv_30d"]) - float(fri_row["iv_30d"].values[0]))

    iv_changes = np.array(iv_changes)
    n_mon = len(iv_changes)

    if n_mon < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H75", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="Requires matched Monday/Friday pairs",
            n_observations=len(work), n_signals=n_mon,
            metric_name="mean_iv_change_monday", metric_value=float("nan"),
            support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_matched_pairs={n_mon} < 20", data_notes="directly_tested",
        )

    mean_change = float(np.mean(iv_changes))
    median_change = float(np.median(iv_changes))
    t_stat, p_ttest = stats.ttest_1samp(iv_changes, 0.0)
    p_one = float(p_ttest / 2) if t_stat > 0 else 1.0  # one-sided p for positive

    pct_higher = float(np.mean(iv_changes > 0))

    if mean_change > 0.003 and p_one < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Mean Monday IV change={mean_change:.5f} > 0 (p_one_sided={p_one:.4f}). "
            f"Weekend premium confirmed: Monday iv_30d exceeds prior-Friday by "
            f"{mean_change:.4f} on average. n_pairs={n_mon}, pct_mondays_higher={pct_higher:.3f}."
        )
    elif mean_change <= 0.0 or p_one > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"mean_change={mean_change:.5f}, p_one_sided={p_one:.4f}. "
            f"No systematic Monday IV premium over prior Friday."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"mean_change={mean_change:.5f}, p_one_sided={p_one:.4f}. "
            f"Some upward bias ({pct_higher:.1%} of Mondays higher) but below threshold."
        )

    print(f"  H75: mean_change={mean_change:.5f}, n_pairs={n_mon}, p_one={p_one:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H75", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="Requires matched Monday/Friday pairs",
        n_observations=len(work), n_signals=n_mon,
        metric_name="mean_iv_change_monday", metric_value=round(mean_change, 6),
        support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_matched_pairs": n_mon,
            "mean_iv_change_monday": round(mean_change, 6),
            "median_iv_change_monday": round(median_change, 6),
            "pct_mondays_higher": round(pct_higher, 4),
            "p_ttest_one_sided": round(p_one, 4),
            "t_statistic": round(float(t_stat), 4),
        },
    )


# ── H76: Gap Days in Backwardation Fill More Than in Contango ─────────────────────

def run_h76(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["open", "close", "log_return", "iv_30d", "iv_60d"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H76", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="gap_fill_rate_backw_minus_contango", metric_value=float("nan"),
            support_threshold=0.08, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date"] + required].dropna().copy()
    work["prev_close"] = work["close"] / np.exp(work["log_return"])
    work["gap_pct"] = (work["open"] - work["prev_close"]) / work["prev_close"]
    work["gap_abs"] = work["gap_pct"].abs()
    gap_days = work[work["gap_abs"] > 0.005].copy()

    if len(gap_days) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H76", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="Gap > 0.5% filter",
            n_observations=len(work), n_signals=len(gap_days),
            metric_name="gap_fill_rate_backw_minus_contango", metric_value=float("nan"),
            support_threshold=0.08, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_gap_days={len(gap_days)} < 20", data_notes="directly_tested",
        )

    gap_days["dist_to_prev"] = (gap_days["close"] - gap_days["prev_close"]).abs()
    gap_days["dist_to_open"] = (gap_days["close"] - gap_days["open"]).abs()
    gap_days["filled"] = gap_days["dist_to_prev"] < gap_days["dist_to_open"]
    gap_days["backwardation"] = gap_days["iv_30d"] > gap_days["iv_60d"]

    backw_gaps = gap_days[gap_days["backwardation"]]
    contango_gaps = gap_days[~gap_days["backwardation"]]

    n_backw = len(backw_gaps)
    n_cont = len(contango_gaps)

    if n_backw < 5 or n_cont < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H76", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="Gap > 0.5% filter + backwardation split",
            n_observations=len(work), n_signals=n_backw,
            metric_name="gap_fill_rate_backw_minus_contango", metric_value=float("nan"),
            support_threshold=0.08, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_backw={n_backw} or n_contango={n_cont} < 5 after split",
            data_notes="directly_tested",
        )

    fill_backw = float(backw_gaps["filled"].mean())
    fill_cont = float(contango_gaps["filled"].mean())
    diff = fill_backw - fill_cont

    # Fisher's exact test
    contingency = [
        [int(backw_gaps["filled"].sum()), n_backw - int(backw_gaps["filled"].sum())],
        [int(contango_gaps["filled"].sum()), n_cont - int(contango_gaps["filled"].sum())],
    ]
    _, p_fisher = stats.fisher_exact(contingency, alternative="greater")

    if diff > 0.08 and p_fisher < 0.15:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Gap fill rate: backwardation={fill_backw:.3f} vs contango={fill_cont:.3f} "
            f"(diff={diff:.3f}), p_fisher={p_fisher:.4f}. "
            f"n_backw={n_backw}, n_contango={n_cont}."
        )
    elif diff <= 0.0 or p_fisher > 0.35:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"diff={diff:.3f}, p_fisher={p_fisher:.4f}. "
            f"Backwardation does not increase gap-fill rate (backw={fill_backw:.3f} vs cont={fill_cont:.3f})."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"diff={diff:.3f}, p_fisher={p_fisher:.4f}. "
            f"backw={fill_backw:.3f} vs cont={fill_cont:.3f}. Inconclusive."
        )

    print(f"  H76: diff={diff:.3f}, n_backw={n_backw}, n_cont={n_cont}, p_fisher={p_fisher:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H76", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="Gap > 0.5% filter + backwardation/contango split",
        n_observations=len(work), n_signals=n_backw,
        metric_name="gap_fill_rate_backw_minus_contango", metric_value=round(diff, 4),
        support_threshold=0.08, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_backwardation_gaps": n_backw,
            "n_contango_gaps": n_cont,
            "fill_rate_backwardation": round(fill_backw, 4),
            "fill_rate_contango": round(fill_cont, 4),
            "p_fisher_exact": round(p_fisher, 4),
            "total_gap_days": len(gap_days),
        },
    )


# ── H77: Low Vol-of-Vol Entry Filter → Larger Variance Premium ───────────────────

def run_h77(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    raw = len(df)
    required = ["iv_30d", "fwd_rv_20"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H77", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="mean_vp_stable_minus_volatile", metric_value=float("nan"),
            support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}", data_notes="insufficient_data",
        )

    work = df[["date"] + required].dropna().copy()
    # 10-day rolling std of iv_30d = vol-of-vol
    work["vol_of_vol"] = work["iv_30d"].rolling(10).std()
    work = work.dropna(subset=["vol_of_vol", "fwd_rv_20"])
    work["vp"] = work["iv_30d"] - work["fwd_rv_20"]

    q33 = work["vol_of_vol"].quantile(0.333)
    q67 = work["vol_of_vol"].quantile(0.667)

    stable = work[work["vol_of_vol"] <= q33]
    volatile = work[work["vol_of_vol"] >= q67]

    n_stable = len(stable)
    n_volatile = len(volatile)

    if n_stable < 20 or n_volatile < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H77", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason="10-day vol-of-vol warmup; fwd_rv_20 NaN for last 20 rows",
            n_observations=len(work), n_signals=n_stable,
            metric_name="mean_vp_stable_minus_volatile", metric_value=float("nan"),
            support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"n_stable={n_stable} or n_volatile={n_volatile} < 20",
            data_notes="directly_tested",
        )

    mean_vp_stable = float(stable["vp"].mean())
    mean_vp_volatile = float(volatile["vp"].mean())
    diff = mean_vp_stable - mean_vp_volatile

    _, p_mw = stats.mannwhitneyu(stable["vp"].values, volatile["vp"].values,
                                  alternative="greater")

    if diff > 0.005 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Stable VP={mean_vp_stable:.4f} > volatile VP={mean_vp_volatile:.4f} "
            f"(diff={diff:.4f}), p_mannwhitney={p_mw:.4f}. "
            f"n_stable={n_stable}, n_volatile={n_volatile}. "
            f"Low vol-of-vol entry filter delivers larger premium."
        )
    elif diff <= 0.0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"diff={diff:.4f}, p_mannwhitney={p_mw:.4f}. "
            f"Stable VP={mean_vp_stable:.4f}, Volatile VP={mean_vp_volatile:.4f}. "
            f"Low vol-of-vol does not predict larger variance premium."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"diff={diff:.4f}, p_mannwhitney={p_mw:.4f}. "
            f"Stable={mean_vp_stable:.4f}, Volatile={mean_vp_volatile:.4f}. Inconclusive."
        )

    print(f"  H77: diff={diff:.4f}, n_stable={n_stable}, n_volatile={n_volatile}, p={p_mw:.4f}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H77", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work),
        rows_excluded=raw - len(work),
        exclusion_reason="10-day vol-of-vol warmup; fwd_rv_20 NaN for last 20 rows",
        n_observations=len(work), n_signals=n_stable,
        metric_name="mean_vp_stable_minus_volatile", metric_value=round(diff, 5),
        support_threshold=0.005, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_stable_vov": n_stable,
            "n_volatile_vov": n_volatile,
            "mean_vp_stable": round(mean_vp_stable, 5),
            "mean_vp_volatile": round(mean_vp_volatile, 5),
            "p_mannwhitney": round(p_mw, 4),
            "q33_vov": round(float(q33), 6),
            "q67_vov": round(float(q67), 6),
        },
    )


# ── H80: 60-Day Variance Premium ──────────────────────────────────────────────────

def run_h80(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: iv_60d exceeds 60-day forward realized vol by positive mean on average.

    Ticker: QQQ. Window: TEST_WINDOW_START → TEST_WINDOW_END.
    Signal: always-on (every date with valid iv_60d and 60 future log returns)
    Outcome: iv_60d - fwd_rv_60 (positive = IV exceeded subsequent RV)
    Support: mean_vp_60d > 0.010 (1 vol point)
    test_type: proxy_tested — iv_60d is constant-maturity IVX surface interpolation

    CAVEAT: fwd_rv_60 windows overlap by ~59/60 days. t-test p-value is approximate
    (effective N ≈ 8 non-overlapping blocks). Mean sign and magnitude are primary evidence.
    """
    raw = len(df)
    excl_reason = "60-day forward window: requires 60 future log returns (last 60 rows excluded)"

    required = ["iv_60d", "log_return"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H80",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing required columns: {missing}",
            n_observations=0, n_signals=0,
            metric_name="mean_vp_60d",
            metric_value=float("nan"),
            support_threshold=0.010, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing columns: {missing}",
            data_notes="insufficient_data",
        )

    df2 = df.copy()
    df2["fwd_rv_60"] = df2["log_return"].shift(-1).rolling(60).std() * np.sqrt(252)
    df2["vp_60d"] = df2["iv_60d"] - df2["fwd_rv_60"]
    valid = df2.dropna(subset=["iv_60d", "fwd_rv_60"]).reset_index(drop=True)
    excluded = raw - len(valid)

    if len(valid) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H80",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(valid), n_signals=0,
            metric_name="mean_vp_60d",
            metric_value=float("nan"),
            support_threshold=0.010, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid observations ({len(valid)} < 30)",
            data_notes="proxy_tested",
        )

    mean_vp = float(valid["vp_60d"].mean())
    median_vp = float(valid["vp_60d"].median())
    pct_positive = float((valid["vp_60d"] > 0).mean())
    effective_n = max(1, len(valid) // 60)

    t_stat, p_ttest = stats.ttest_1samp(valid["vp_60d"].dropna(), 0.0)

    # Pull comparison mean_vp_20d from H1 result if available
    comparison_vp_20d: float | None = None
    if RESULTS_FILE.exists():
        try:
            h1 = next(
                (r for r in json.loads(RESULTS_FILE.read_text())
                 if r.get("hypothesis_number") == "H1"),
                None,
            )
            if h1:
                comparison_vp_20d = h1.get("metric_value")
        except Exception:
            pass

    overlap_caveat = (
        f"Forward realized vol windows overlap by ~59/60 days. "
        f"t-test p={p_ttest:.4f} treats {len(valid)} obs as independent — "
        f"effective N ≈ {effective_n} non-overlapping blocks. "
        f"Mean sign and magnitude are primary evidence."
    )

    if mean_vp > 0.010:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"mean_vp_60d={mean_vp:.4f} > 0.010 threshold. "
            f"pct_positive={pct_positive:.1%}, median={median_vp:.4f}. "
            + overlap_caveat
        )
    elif mean_vp <= 0.0:
        verdict = BacktestVerdict.REJECTED
        reason = f"mean_vp_60d={mean_vp:.4f} ≤ 0 — premium absent or negative. " + overlap_caveat
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"mean_vp_60d={mean_vp:.4f} positive but below 1 vol point threshold. "
            + overlap_caveat
        )

    print(
        f"  H80: mean_vp_60d={mean_vp:.4f}, pct_positive={pct_positive:.1%}, "
        f"p_approx={p_ttest:.4f} (N={len(valid)}, eff_N≈{effective_n}) → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H80",
        ticker=TICKER,
        period_start=TEST_WINDOW_START,
        period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(valid),
        n_signals=len(valid),
        metric_name="mean_vp_60d",
        metric_value=round(mean_vp, 6),
        support_threshold=0.010,
        reject_threshold=0.0,
        verdict=verdict,
        verdict_reason=reason,
        data_notes="proxy_tested",
        extra_metrics={
            "pct_days_positive_vp": round(pct_positive, 4),
            "median_vp_60d": round(median_vp, 6),
            "p_ttest_vs_zero_approx": round(float(p_ttest), 6),
            "t_stat_approx": round(float(t_stat), 4),
            "effective_n_approx": effective_n,
            "comparison_mean_vp_20d": (
                round(float(comparison_vp_20d), 6) if comparison_vp_20d is not None else None
            ),
        },
    )


# ── H86: Daily Leverage Effect ───────────────────────────────────────────────────

def run_h86(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: After negative return days (< -0.5%), forward 5-day RV is significantly
    higher than after positive return days (> +0.5%).

    Mechanism: leverage effect — price declines raise equity risk asymmetrically.
    Signal: log_return < -0.005 | Control: log_return > +0.005
    Outcome: fwd_hv_5 = std(log_return[t+1:t+6]) * sqrt(252)
    Support: diff > 0.003 AND p < 0.05
    """
    raw = len(df)
    excl_reason = "5-day forward window (last 5 rows excluded); 0.5% return threshold filters neutral days"

    if "log_return" not in df.columns:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H86", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="Missing log_return", n_observations=0, n_signals=0,
            metric_name="mean_fwd_hv5_diff_down_vs_up",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="Missing log_return column",
            data_notes="directly_tested",
        )

    df2 = df.copy()
    df2["fwd_hv_5"] = df2["log_return"].shift(-1).rolling(5).std() * np.sqrt(252)
    valid = df2.dropna(subset=["log_return", "fwd_hv_5"])
    excluded = raw - len(valid)

    negative = valid[valid["log_return"] < -0.005]
    positive = valid[valid["log_return"] >  0.005]

    n_neg = len(negative)
    n_pos = len(positive)

    if n_neg < 20 or n_pos < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H86", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(valid), n_signals=n_neg,
            metric_name="mean_fwd_hv5_diff_down_vs_up",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few negative ({n_neg}) or positive ({n_pos}) days",
            data_notes="directly_tested",
        )

    mean_neg = float(negative["fwd_hv_5"].mean())
    mean_pos = float(positive["fwd_hv_5"].mean())
    diff = mean_neg - mean_pos

    _, p_mw = stats.mannwhitneyu(
        negative["fwd_hv_5"].values, positive["fwd_hv_5"].values, alternative="greater"
    )

    # Confound check: are negative days larger in abs magnitude?
    med_abs_neg = float(negative["log_return"].abs().median())
    med_abs_pos = float(positive["log_return"].abs().median())

    if diff > 0.003 and p_mw < 0.05:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.20:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    magnitude_note = (
        f"Median abs|return|: down={med_abs_neg:.4f}, up={med_abs_pos:.4f}. "
        + ("Note: down days have larger magnitude — vol spike may partly reflect return size, not pure asymmetry."
           if med_abs_neg > med_abs_pos * 1.2 else "Magnitudes comparable — asymmetry likely structural.")
    )

    reason = (
        f"diff={diff:.4f} (mean_fwd_hv5_down={mean_neg:.4f}, up={mean_pos:.4f}), "
        f"p_mannwhitney={p_mw:.4f}, n_neg={n_neg}, n_pos={n_pos}. " + magnitude_note
    )

    print(
        f"  H86: diff={diff:.4f}, p_mw={p_mw:.4f}, n_neg={n_neg}, "
        f"n_pos={n_pos} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H86", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(valid), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(valid), n_signals=n_neg,
        metric_name="mean_fwd_hv5_diff_down_vs_up",
        metric_value=round(diff, 6),
        support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "mean_fwd_hv5_down_days": round(mean_neg, 4),
            "mean_fwd_hv5_up_days": round(mean_pos, 4),
            "n_negative_days": n_neg,
            "n_positive_days": n_pos,
            "p_mannwhitney": round(p_mw, 6),
            "median_abs_return_down": round(med_abs_neg, 5),
            "median_abs_return_up": round(med_abs_pos, 5),
        },
    )


# ── H87: Bear Regime Vol Level ────────────────────────────────────────────────────

def run_h87(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Median hv_20_cc when price < 200-day MA is >= 1.5x the median when above.

    Signal: close <= rolling 200-day MA (bear regime)
    Control: close > rolling 200-day MA (bull regime)
    Primary metric: ratio = median_hv20_bear / median_hv20_bull
    Support: ratio > 1.50 AND p_mannwhitney < 0.01
    """
    raw = len(df)
    excl_reason = "200-day MA warmup (first 200 rows) + hv_20_cc NaN rows"

    required = ["close", "hv_20_cc"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H87", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}", n_observations=0, n_signals=0,
            metric_name="ratio_median_hv20_bear_vs_bull",
            metric_value=float("nan"), support_threshold=1.5, reject_threshold=1.2,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing: {missing}",
            data_notes="directly_tested",
        )

    df2 = df.copy()
    df2["ma_200"] = df2["close"].rolling(200).mean()
    df2 = df2.dropna(subset=["ma_200", "hv_20_cc"])
    excluded = raw - len(df2)

    bull = df2[df2["close"] > df2["ma_200"]]["hv_20_cc"]
    bear = df2[df2["close"] <= df2["ma_200"]]["hv_20_cc"]

    n_bull = len(bull)
    n_bear = len(bear)

    if n_bear < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H87", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_bear,
            metric_name="ratio_median_hv20_bear_vs_bull",
            metric_value=float("nan"), support_threshold=1.5, reject_threshold=1.2,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few bear-regime days: {n_bear} (need >= 10). "
                           f"QQQ may have been above 200-day MA for most of test window.",
            data_notes="directly_tested",
        )

    med_bull = float(bull.median())
    med_bear = float(bear.median())
    ratio = med_bear / med_bull if med_bull > 0 else float("nan")

    _, p_mw = stats.mannwhitneyu(bear.values, bull.values, alternative="greater")

    if ratio > 1.50 and p_mw < 0.01:
        verdict = BacktestVerdict.SUPPORTED
    elif ratio < 1.20 or p_mw > 0.10:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"ratio={ratio:.3f} (median_bear={med_bear:.4f}, median_bull={med_bull:.4f}), "
        f"p_mannwhitney={p_mw:.4f}, n_bear={n_bear}, n_bull={n_bull}."
    )

    print(
        f"  H87: ratio={ratio:.3f}, p_mw={p_mw:.4f}, n_bear={n_bear}, "
        f"n_bull={n_bull} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H87", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_bear,
        metric_name="ratio_median_hv20_bear_vs_bull",
        metric_value=round(ratio, 4),
        support_threshold=1.5, reject_threshold=1.2,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "median_hv20_bear": round(med_bear, 4),
            "median_hv20_bull": round(med_bull, 4),
            "mean_hv20_bear": round(float(bear.mean()), 4),
            "mean_hv20_bull": round(float(bull.mean()), 4),
            "n_bear_days": n_bear,
            "n_bull_days": n_bull,
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H88: Inverted Term Structure Predicts iv_30d Decline ─────────────────────────

def run_h88(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When iv_30d > iv_90d * 1.05, iv_30d is lower 20 sessions later
    more than 58% of the time (front-month IV mean-reverts after inversion).

    Signal: iv_30d > iv_90d * 1.05 (5% inversion)
    Outcome: iv_30d[t+20] < iv_30d[t]
    Support: pct_decline > 0.58 AND p_binomial < 0.10
    Distinct from H44 which tests range; this tests IV direction.
    """
    raw = len(df)
    excl_reason = "20-day forward IV window; iv_30d or iv_90d NaN rows"

    required = ["iv_30d", "iv_90d"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H88", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}", n_observations=0, n_signals=0,
            metric_name="pct_iv30d_declines_20d_after_inversion",
            metric_value=float("nan"), support_threshold=0.58, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing: {missing}", data_notes="proxy_tested",
        )

    df2 = df.copy()
    df2["iv30d_fwd_20"] = df2["iv_30d"].shift(-20)
    df2["iv30d_change_20d"] = df2["iv30d_fwd_20"] - df2["iv_30d"]
    df2 = df2.dropna(subset=["iv_30d", "iv_90d", "iv30d_change_20d"])
    excluded = raw - len(df2)

    signal = df2[df2["iv_30d"] > df2["iv_90d"] * 1.05]
    n_signal = len(signal)

    if n_signal < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H88", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_signal,
            metric_name="pct_iv30d_declines_20d_after_inversion",
            metric_value=float("nan"), support_threshold=0.58, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few inversion days: {n_signal} (need >= 20)",
            data_notes="proxy_tested",
        )

    n_decline = int((signal["iv30d_change_20d"] < 0).sum())
    pct_decline = n_decline / n_signal

    binom_result = stats.binomtest(n_decline, n_signal, p=0.50, alternative="greater")
    p_binomial = float(binom_result.pvalue)

    mean_change = float(signal["iv30d_change_20d"].mean())
    pct_inv_days = float(len(signal) / len(df2))
    mean_inv_magnitude = float((df2["iv_30d"] - df2["iv_90d"]).clip(lower=0).mean())

    overlap_note = "Forward 20-day iv_30d windows overlap — p-value approximate (shared ~10 days between consecutive windows)."

    if pct_decline > 0.58 and p_binomial < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif pct_decline < 0.50 or p_binomial > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"pct_iv30d_decline={pct_decline:.1%} ({n_decline}/{n_signal} inversion days), "
        f"p_binomial={p_binomial:.4f}, mean_iv30d_change={mean_change:.4f}. "
        + overlap_note
    )

    print(
        f"  H88: pct_decline={pct_decline:.1%}, p_binom={p_binomial:.4f}, "
        f"n_signal={n_signal} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H88", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_signal,
        metric_name="pct_iv30d_declines_20d_after_inversion",
        metric_value=round(pct_decline, 4),
        support_threshold=0.58, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        extra_metrics={
            "n_inversion_days": n_signal,
            "n_declines": n_decline,
            "p_binomial": round(p_binomial, 6),
            "mean_iv30d_change_20d": round(mean_change, 5),
            "pct_inversion_days_overall": round(pct_inv_days, 4),
        },
    )


# ── H89: Normalized Variance Premium ─────────────────────────────────────────────

def run_h89(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: (iv_30d - fwd_rv_20) / iv_30d averages 0.15–0.35 (the "30% overpayment").

    Support: mean in [0.10, 0.40]
    Reject: mean <= 0 or > 0.50
    Distinct from H1 (premium existence) and H80 (60-day absolute premium).
    """
    raw = len(df)
    excl_reason = "20-day forward window; iv_30d < 0.05 excluded (near-zero IV noise)"

    required = ["iv_30d", "fwd_rv_20"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H89", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing columns: {missing}", n_observations=0, n_signals=0,
            metric_name="mean_normalized_vp",
            metric_value=float("nan"), support_threshold=0.10, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing: {missing}", data_notes="proxy_tested",
        )

    df2 = df.copy()
    df2 = df2.dropna(subset=["iv_30d", "fwd_rv_20"])
    df2 = df2[df2["iv_30d"] > 0.05]  # exclude near-zero IV
    excluded = raw - len(df2)

    df2["norm_vp"] = (df2["iv_30d"] - df2["fwd_rv_20"]) / df2["iv_30d"]

    if len(df2) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H89", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=len(df2),
            metric_name="mean_normalized_vp",
            metric_value=float("nan"), support_threshold=0.10, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid rows: {len(df2)}",
            data_notes="proxy_tested",
        )

    mean_nvp = float(df2["norm_vp"].mean())
    median_nvp = float(df2["norm_vp"].median())
    pct_positive = float((df2["norm_vp"] > 0).mean())
    t_stat, p_ttest = stats.ttest_1samp(df2["norm_vp"].dropna(), 0.0)
    eff_n = max(1, len(df2) // 20)

    if 0.10 <= mean_nvp <= 0.40:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"mean_normalized_vp={mean_nvp:.4f} within [0.10, 0.40] (book claim: ~0.30). "
            f"median={median_nvp:.4f}, pct_positive={pct_positive:.1%}. "
            f"Overlapping 20-day windows; eff_N≈{eff_n}."
        )
    elif mean_nvp <= 0.0 or mean_nvp > 0.50:
        verdict = BacktestVerdict.REJECTED
        reason = f"mean_normalized_vp={mean_nvp:.4f} outside any plausible range."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"mean_normalized_vp={mean_nvp:.4f} positive but outside [0.10, 0.40] range."
        )

    print(f"  H89: mean_norm_vp={mean_nvp:.4f}, pct_pos={pct_positive:.1%} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H89", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=len(df2),
        metric_name="mean_normalized_vp",
        metric_value=round(mean_nvp, 6),
        support_threshold=0.10, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        extra_metrics={
            "median_normalized_vp": round(median_nvp, 6),
            "pct_days_positive": round(pct_positive, 4),
            "p_ttest_approx": round(float(p_ttest), 6),
            "effective_n_approx": eff_n,
            "n_valid": len(df2),
        },
    )


# ── H90: IV Percentile Rank as Variance Premium Filter ───────────────────────────

def run_h90(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: iv_30d above trailing 252-day 75th pct → larger subsequent vp than
    iv_30d in the 25th–75th pct range.

    High percentile = historically expensive IV → stronger mean reversion premium.
    Support: diff > 0.005 AND p_mannwhitney < 0.10
    Distinct from H28 (absolute IV level regime, rejected).
    """
    raw = len(df)
    excl_reason = "252-day rolling quantile warmup + 20-day forward window for fwd_rv_20"

    required = ["iv_30d", "fwd_rv_20"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H90", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="mean_vp_diff_high_vs_mid_percentile",
            metric_value=float("nan"), support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing: {missing}", data_notes="proxy_tested",
        )

    df2 = df.copy()
    df2["iv30d_p75"] = df2["iv_30d"].rolling(252, min_periods=100).quantile(0.75)
    df2["iv30d_p25"] = df2["iv_30d"].rolling(252, min_periods=100).quantile(0.25)
    df2["vp_20d"] = df2["iv_30d"] - df2["fwd_rv_20"]
    df2 = df2.dropna(subset=["iv_30d", "iv30d_p75", "iv30d_p25", "vp_20d"])
    excluded = raw - len(df2)

    high = df2[df2["iv_30d"] > df2["iv30d_p75"]]["vp_20d"]
    mid  = df2[(df2["iv_30d"] >= df2["iv30d_p25"]) &
               (df2["iv_30d"] <= df2["iv30d_p75"])]["vp_20d"]

    n_high = len(high)
    n_mid  = len(mid)

    if n_high < 20 or n_mid < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H90", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_high,
            metric_name="mean_vp_diff_high_vs_mid_percentile",
            metric_value=float("nan"), support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few high ({n_high}) or mid ({n_mid}) percentile days",
            data_notes="proxy_tested",
        )

    mean_high = float(high.mean())
    mean_mid  = float(mid.mean())
    diff = mean_high - mean_mid

    _, p_mw = stats.mannwhitneyu(high.values, mid.values, alternative="greater")

    if diff > 0.005 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff={diff:.5f} (mean_vp_high_pct={mean_high:.5f}, mid_pct={mean_mid:.5f}), "
        f"p_mannwhitney={p_mw:.4f}, n_high={n_high}, n_mid={n_mid}. "
        "Rolling 252-day percentile threshold; 20-day overlapping forward windows."
    )

    print(
        f"  H90: diff={diff:.5f}, p_mw={p_mw:.4f}, n_high={n_high}, "
        f"n_mid={n_mid} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H90", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_high,
        metric_name="mean_vp_diff_high_vs_mid_percentile",
        metric_value=round(diff, 6),
        support_threshold=0.005, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        extra_metrics={
            "mean_vp_high_percentile": round(mean_high, 6),
            "mean_vp_mid_percentile": round(mean_mid, 6),
            "n_high_pct": n_high,
            "n_mid_pct": n_mid,
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H91: Volatility Shock Half-Life ──────────────────────────────────────────────

def run_h91(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: After hv_20_cc spikes above trailing 252-day p80, median days to revert
    to trailing p50 is 10–50 trading days.

    New spike: first bar above p80 after >= 5 consecutive bars below p80.
    Support: median_days_to_revert in [10, 50]
    Insufficient: n_spike_events < 5
    """
    raw = len(df)
    excl_reason = "252-day rolling quantile warmup for p80/p50 thresholds"

    if "hv_20_cc" not in df.columns or df["hv_20_cc"].isna().all():
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H91", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="Missing hv_20_cc", n_observations=0, n_signals=0,
            metric_name="median_days_to_revert_after_spike",
            metric_value=float("nan"), support_threshold=50.0, reject_threshold=60.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="Missing hv_20_cc", data_notes="directly_tested",
        )

    df2 = df.copy()
    df2["hv_p80"] = df2["hv_20_cc"].rolling(252, min_periods=100).quantile(0.80)
    df2["hv_p50"] = df2["hv_20_cc"].rolling(252, min_periods=100).quantile(0.50)
    df2 = df2.dropna(subset=["hv_20_cc", "hv_p80", "hv_p50"]).reset_index(drop=True)
    excluded = raw - len(df2)

    # Identify new spikes: first bar above p80 after >= 5 bars below p80
    spike_events = []
    below_count = 0
    in_spike = False

    for i, row in df2.iterrows():
        above_p80 = row["hv_20_cc"] > row["hv_p80"]
        if not above_p80:
            below_count += 1
            in_spike = False
        else:
            if not in_spike and below_count >= 5:
                spike_events.append(i)
                in_spike = True
            below_count = 0

    if len(spike_events) < 3:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H91", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=len(spike_events),
            metric_name="median_days_to_revert_after_spike",
            metric_value=float("nan"), support_threshold=50.0, reject_threshold=60.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few spike events: {len(spike_events)} (need >= 3)",
            data_notes="directly_tested",
        )

    revert_days = []
    for spike_idx in spike_events:
        p50_at_spike = df2.loc[spike_idx, "hv_p50"]
        for j in range(spike_idx + 1, min(spike_idx + 120, len(df2))):
            if df2.loc[j, "hv_20_cc"] < p50_at_spike:
                revert_days.append(j - spike_idx)
                break
        else:
            revert_days.append(None)  # did not revert within 120 days

    reverted = [d for d in revert_days if d is not None]
    n_reverted = len(reverted)
    n_not_reverted = len(revert_days) - n_reverted
    pct_reverted_30 = sum(1 for d in reverted if d <= 30) / len(spike_events)
    pct_reverted_60 = sum(1 for d in reverted if d <= 60) / len(spike_events)

    if not reverted:
        median_days = float("nan")
    else:
        median_days = float(np.median(reverted))

    if not np.isnan(median_days) and 10 <= median_days <= 50:
        verdict = BacktestVerdict.SUPPORTED
    elif np.isnan(median_days) or (len(reverted) > 0 and median_days > 60):
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"n_spike_events={len(spike_events)}, n_reverted_within_120d={n_reverted}, "
        f"median_days_to_revert={'N/A' if math.isnan(median_days) else f'{median_days:.1f}'}, "
        f"pct_within_30d={pct_reverted_30:.1%}, pct_within_60d={pct_reverted_60:.1%}."
    )

    med_str = f"{median_days:.1f}" if not math.isnan(median_days) else "NaN"
    print(
        f"  H91: n_spikes={len(spike_events)}, median_days={med_str}, "
        f"pct_30d={pct_reverted_30:.1%} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H91", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=len(spike_events),
        metric_name="median_days_to_revert_after_spike",
        metric_value=round(median_days, 1) if not np.isnan(median_days) else float("nan"),
        support_threshold=50.0, reject_threshold=60.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "n_spike_events": len(spike_events),
            "n_reverted_within_120d": n_reverted,
            "n_did_not_revert": n_not_reverted,
            "pct_reverted_within_30d": round(pct_reverted_30, 4),
            "pct_reverted_within_60d": round(pct_reverted_60, 4),
        },
    )


# ── H92: GARCH vs EWMA Forecast Quality ──────────────────────────────────────────

def run_h92(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: garch_vol (one-step GARCH forecast) has lower RMSE vs fwd_rv_20 than
    EWMA(lambda=0.94) computed from log_return.

    Uses existing garch_vol column — no re-fitting required.
    Paired t-test on squared errors.
    Support: ratio < 0.95 AND p < 0.10
    """
    raw = len(df)
    excl_reason = "EWMA warmup (first ~20 rows) + 20-day forward window for fwd_rv_20"

    required = ["log_return", "garch_vol", "fwd_rv_20"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H92", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="rmse_ratio_garch_vs_ewma",
            metric_value=float("nan"), support_threshold=0.95, reject_threshold=1.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing: {missing}", data_notes="directly_tested",
        )

    df2 = df.copy()

    # Compute EWMA(λ=0.94) variance from log_return
    lam = 0.94
    ewma_var = [float("nan")] * len(df2)
    r = df2["log_return"].values
    for i in range(1, len(df2)):
        if np.isnan(r[i-1]):
            ewma_var[i] = ewma_var[i-1] if i > 1 else float("nan")
        elif np.isnan(ewma_var[i-1]):
            ewma_var[i] = r[i-1] ** 2
        else:
            ewma_var[i] = lam * ewma_var[i-1] + (1 - lam) * r[i-1] ** 2
    df2["ewma_vol"] = np.sqrt(pd.array(ewma_var, dtype=float)) * np.sqrt(252)

    df2 = df2.dropna(subset=["garch_vol", "ewma_vol", "fwd_rv_20"])
    excluded = raw - len(df2)

    if len(df2) < 60:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H92", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=0,
            metric_name="rmse_ratio_garch_vs_ewma",
            metric_value=float("nan"), support_threshold=0.95, reject_threshold=1.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid rows: {len(df2)}",
            data_notes="directly_tested",
        )

    err_garch = (df2["garch_vol"] - df2["fwd_rv_20"]) ** 2
    err_ewma  = (df2["ewma_vol"]  - df2["fwd_rv_20"]) ** 2

    rmse_garch = float(np.sqrt(err_garch.mean()))
    rmse_ewma  = float(np.sqrt(err_ewma.mean()))
    ratio = rmse_garch / rmse_ewma if rmse_ewma > 0 else float("nan")

    t_stat, p_paired = stats.ttest_rel(err_garch.values, err_ewma.values)

    if ratio < 0.95 and p_paired < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif ratio > 1.0:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"rmse_ratio={ratio:.4f} (GARCH={rmse_garch:.5f}, EWMA={rmse_ewma:.5f}), "
        f"p_paired_ttest={p_paired:.4f}, n={len(df2)}."
    )

    print(
        f"  H92: rmse_ratio={ratio:.4f}, p_paired={p_paired:.4f}, "
        f"n={len(df2)} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H92", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=len(df2),
        metric_name="rmse_ratio_garch_vs_ewma",
        metric_value=round(ratio, 6),
        support_threshold=0.95, reject_threshold=1.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "rmse_garch": round(rmse_garch, 6),
            "rmse_ewma": round(rmse_ewma, 6),
            "t_stat_paired": round(float(t_stat), 4),
            "p_paired_ttest": round(float(p_paired), 6),
            "n_valid": len(df2),
        },
    )


# ── H93: Variance Premium by Bull/Bear Regime ────────────────────────────────────

def run_h93(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Variance premium (iv_30d - fwd_rv_20) is higher in bull regime
    (price > 200-day MA) than in bear regime.

    Mechanism: bear-regime RV is frequently elevated → premium shrinks or reverses.
    Support: diff > 0.003 AND p < 0.10
    Insufficient: n_bear < 20
    """
    raw = len(df)
    excl_reason = "200-day MA warmup + 20-day forward window for fwd_rv_20"

    required = ["close", "iv_30d", "fwd_rv_20"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H93", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="mean_vp_diff_bull_vs_bear",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing: {missing}", data_notes="proxy_tested",
        )

    df2 = df.copy()
    df2["ma_200"] = df2["close"].rolling(200).mean()
    df2["vp_20d"] = df2["iv_30d"] - df2["fwd_rv_20"]
    df2 = df2.dropna(subset=["ma_200", "vp_20d"])
    excluded = raw - len(df2)

    bull_vp = df2[df2["close"] > df2["ma_200"]]["vp_20d"]
    bear_vp = df2[df2["close"] <= df2["ma_200"]]["vp_20d"]

    n_bull = len(bull_vp)
    n_bear = len(bear_vp)

    if n_bear < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H93", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_bull,
            metric_name="mean_vp_diff_bull_vs_bear",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few bear-regime days: {n_bear}. "
                           "QQQ likely above 200-day MA for most of test window.",
            data_notes="proxy_tested",
        )

    mean_bull = float(bull_vp.mean())
    mean_bear = float(bear_vp.mean())
    diff = mean_bull - mean_bear

    _, p_mw = stats.mannwhitneyu(bull_vp.values, bear_vp.values, alternative="greater")

    if diff > 0.003 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff={diff:.5f} (mean_vp_bull={mean_bull:.5f}, mean_vp_bear={mean_bear:.5f}), "
        f"p_mannwhitney={p_mw:.4f}, n_bull={n_bull}, n_bear={n_bear}."
    )

    print(
        f"  H93: diff={diff:.5f}, p_mw={p_mw:.4f}, n_bull={n_bull}, "
        f"n_bear={n_bear} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H93", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_bull,
        metric_name="mean_vp_diff_bull_vs_bear",
        metric_value=round(diff, 6),
        support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        extra_metrics={
            "mean_vp_bull": round(mean_bull, 6),
            "mean_vp_bear": round(mean_bear, 6),
            "n_bull_days": n_bull,
            "n_bear_days": n_bear,
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── IVX loader (shared by H94, H95) ──────────────────────────────────────────────

def _load_ivx() -> pd.DataFrame:
    """Return date-indexed DataFrame with iv_7d, iv_call_30d, iv_put_30d columns."""
    if not IVX_FILE.exists():
        raise SystemExit(f"qqq_ivx.parquet not found at {IVX_FILE}")
    df = pd.read_parquet(IVX_FILE)[["date", "7d IV Mean", "30d IV Call", "30d IV Put"]]
    df = df.rename(columns={
        "7d IV Mean": "iv_7d",
        "30d IV Call": "iv_call_30d",
        "30d IV Put": "iv_put_30d",
    })
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")


# ── H94: Front-End Term Structure Slope (7d/30d) as Session Quality Filter ───────

def run_h94(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When iv_7d > iv_30d (front-end backwardation), next-session range is
    larger than when the front end is in contango.

    Support: diff > 0.003 AND p < 0.10
    Insufficient: n_backwardation < 20
    """
    raw = len(df)
    excl_reason = "7d IV join + 1-day forward range"

    try:
        ivx = _load_ivx()
    except SystemExit as e:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H94", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="qqq_ivx.parquet not found", n_observations=0, n_signals=0,
            metric_name="median_range_diff_backwardation_vs_contango",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=str(e), data_notes="proxy_tested",
        )

    for col in ["iv_30d", "high", "low", "close"]:
        if col not in df.columns:
            return BacktestResult(
                hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
                hypothesis_number="H94", ticker=TICKER,
                period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
                raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
                exclusion_reason=f"Missing column: {col}", n_observations=0, n_signals=0,
                metric_name="median_range_diff_backwardation_vs_contango",
                metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
                verdict=BacktestVerdict.INSUFFICIENT_DATA,
                verdict_reason=f"Missing: {col}", data_notes="proxy_tested",
            )

    df2 = df.copy()
    df2 = df2.join(ivx[["iv_7d"]], on="date")
    df2["next_range"] = ((df2["high"] - df2["low"]) / df2["close"]).shift(-1)
    df2 = df2.dropna(subset=["iv_7d", "iv_30d", "next_range"])
    excluded = raw - len(df2)

    df2["slope_7_30"] = df2["iv_7d"] / df2["iv_30d"]
    backwardation = df2[df2["slope_7_30"] > 1.0]["next_range"]
    contango = df2[df2["slope_7_30"] <= 1.0]["next_range"]

    n_back = len(backwardation)
    n_cont = len(contango)

    if n_back < 20 or n_cont < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H94", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_back,
            metric_name="median_range_diff_backwardation_vs_contango",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few backwardation days: {n_back}",
            data_notes="proxy_tested",
        )

    diff = float(backwardation.median() - contango.median())
    _, p_mw = stats.mannwhitneyu(backwardation.values, contango.values, alternative="greater")
    mean_slope = float(df2["slope_7_30"].mean())

    if diff > 0.003 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff_median_range={diff:.5f} (backwardation={backwardation.median():.5f}, "
        f"contango={contango.median():.5f}), p_mannwhitney={p_mw:.4f}, "
        f"n_backwardation={n_back}, n_contango={n_cont}, mean_slope_7_30={mean_slope:.4f}."
    )
    print(f"  H94: diff={diff:.5f}, p_mw={p_mw:.4f}, n_back={n_back}, n_cont={n_cont} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H94", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_back,
        metric_name="median_range_diff_backwardation_vs_contango",
        metric_value=round(diff, 6), support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "median_range_backwardation": round(float(backwardation.median()), 6),
            "median_range_contango": round(float(contango.median()), 6),
            "n_backwardation": n_back,
            "n_contango": n_cont,
            "mean_slope_7_30": round(mean_slope, 4),
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H95: ATM Put-Call IV Spread (IVX 30d) as Near-Term Risk Signal ────────────────

def run_h95(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When (iv_put_30d - iv_call_30d) > its 90-day rolling median,
    next-session log_return is lower than when spread is at/below median.

    Support: diff < -0.001 AND p < 0.15
    Insufficient: n < 30
    """
    raw = len(df)
    excl_reason = "ivx join + 90-day rolling median warmup + 1-day forward return"

    try:
        ivx = _load_ivx()
    except SystemExit as e:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H95", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="qqq_ivx.parquet not found", n_observations=0, n_signals=0,
            metric_name="mean_return_diff_high_vs_low_spread",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=str(e), data_notes="proxy_tested",
        )

    if "log_return" not in df.columns:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H95", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="Missing log_return", n_observations=0, n_signals=0,
            metric_name="mean_return_diff_high_vs_low_spread",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="Missing log_return", data_notes="proxy_tested",
        )

    df2 = df.copy()
    df2 = df2.join(ivx[["iv_call_30d", "iv_put_30d"]], on="date")
    df2["pc_iv_spread"] = df2["iv_put_30d"] - df2["iv_call_30d"]
    df2["pc_spread_median"] = df2["pc_iv_spread"].rolling(90, min_periods=30).median()
    df2["next_return"] = df2["log_return"].shift(-1)
    df2 = df2.dropna(subset=["pc_iv_spread", "pc_spread_median", "next_return"])
    excluded = raw - len(df2)

    high_skew = df2[df2["pc_iv_spread"] > df2["pc_spread_median"]]["next_return"]
    low_skew = df2[df2["pc_iv_spread"] <= df2["pc_spread_median"]]["next_return"]

    n_high = len(high_skew)
    n_low = len(low_skew)

    if n_high < 30 or n_low < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H95", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_high,
            metric_name="mean_return_diff_high_vs_low_spread",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few observations: n_high={n_high}, n_low={n_low}",
            data_notes="proxy_tested",
        )

    diff = float(high_skew.mean() - low_skew.mean())
    _, p_mw = stats.mannwhitneyu(high_skew.values, low_skew.values, alternative="less")
    median_spread = float(df2["pc_iv_spread"].median())

    if diff < -0.001 and p_mw < 0.15:
        verdict = BacktestVerdict.SUPPORTED
    elif diff >= 0 or p_mw > 0.35:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff_mean_return={diff:.5f} (high_spread={high_skew.mean():.5f}, "
        f"low_spread={low_skew.mean():.5f}), p_mannwhitney={p_mw:.4f}, "
        f"n_high={n_high}, n_low={n_low}, median_pc_iv_spread={median_spread:.5f}. "
        f"Note: IVX ATM composite IV — not chain-derived skew. Associative finding only."
    )
    print(f"  H95: diff={diff:.5f}, p_mw={p_mw:.4f}, n_high={n_high} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H95", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_high,
        metric_name="mean_return_diff_high_vs_low_spread",
        metric_value=round(diff, 6), support_threshold=-0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "mean_return_high_spread": round(float(high_skew.mean()), 6),
            "mean_return_low_spread": round(float(low_skew.mean()), 6),
            "median_pc_iv_spread": round(median_spread, 6),
            "n_high_spread": n_high,
            "n_low_spread": n_low,
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H96: Bootstrapped Forward Vol Inversion (30→60d) as Near-Term Stress Signal ──

def run_h96(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When bootstrapped fwd_vol_30_60 < iv_30d (inverted short-end forward
    curve), next-5-session median range is larger than when forward curve is normal.

    Forward vol: sqrt(max((iv_60d^2*60 - iv_30d^2*30)/30, epsilon))
    Alignment: range_5d_fwd = range_d.rolling(5).mean().shift(-5)
               -> at row t, reads value from t+5 = mean(range[t+1..t+5])

    Support: diff > 0.003 AND p < 0.10
    Insufficient: n_inverted < 20
    """
    raw = len(df)
    excl_reason = "iv_30d/iv_60d required + 5-day forward range window"

    for col in ["iv_30d", "iv_60d", "high", "low", "close"]:
        if col not in df.columns or df[col].isna().all():
            return BacktestResult(
                hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
                hypothesis_number="H96", ticker=TICKER,
                period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
                raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
                exclusion_reason=f"Missing: {col}", n_observations=0, n_signals=0,
                metric_name="median_range_5d_diff_inverted_vs_normal",
                metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
                verdict=BacktestVerdict.INSUFFICIENT_DATA,
                verdict_reason=f"Missing: {col}", data_notes="proxy_tested",
            )

    df2 = df.copy()
    df2["fwd_vol_30_60"] = np.sqrt(
        np.maximum((df2["iv_60d"] ** 2 * 60 - df2["iv_30d"] ** 2 * 30) / 30, 1e-8)
    )
    df2["fwd_inverted"] = df2["fwd_vol_30_60"] < df2["iv_30d"]
    df2["range_d"] = (df2["high"] - df2["low"]) / df2["close"]
    # At row t: mean(range[t+1], ..., range[t+5]) ✓
    df2["range_5d_fwd"] = df2["range_d"].rolling(5).mean().shift(-5)
    df2 = df2.dropna(subset=["fwd_inverted", "range_5d_fwd"])
    excluded = raw - len(df2)

    inverted = df2[df2["fwd_inverted"]]["range_5d_fwd"]
    normal = df2[~df2["fwd_inverted"]]["range_5d_fwd"]

    n_inv = len(inverted)
    n_norm = len(normal)
    pct_inverted = float(df2["fwd_inverted"].mean())

    if n_inv < 20 or n_norm < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H96", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_inv,
            metric_name="median_range_5d_diff_inverted_vs_normal",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few inverted-curve days: {n_inv}",
            data_notes="proxy_tested",
        )

    diff = float(inverted.median() - normal.median())
    _, p_mw = stats.mannwhitneyu(inverted.values, normal.values, alternative="greater")

    if diff > 0.003 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff_median_range_5d={diff:.5f} (inverted={inverted.median():.5f}, "
        f"normal={normal.median():.5f}), p_mannwhitney={p_mw:.4f}, "
        f"n_inverted={n_inv}, n_normal={n_norm}, pct_inverted={pct_inverted:.3f}."
    )
    print(f"  H96: diff={diff:.5f}, p_mw={p_mw:.4f}, n_inv={n_inv} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H96", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_inv,
        metric_name="median_range_5d_diff_inverted_vs_normal",
        metric_value=round(diff, 6), support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "median_range_5d_inverted": round(float(inverted.median()), 6),
            "median_range_5d_normal": round(float(normal.median()), 6),
            "pct_inverted": round(pct_inverted, 4),
            "n_inverted": n_inv,
            "n_normal": n_norm,
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H97: IV Velocity (5-Day Rate of Change) as Session Range Predictor ───────────

def run_h97(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When iv_30d has risen >10% over prior 5 sessions (rising), next-session
    range is larger than when iv_30d has fallen >8% (falling).

    Support: diff > 0.003 AND p < 0.10
    Insufficient: n_rising < 15 or n_falling < 15
    """
    raw = len(df)
    excl_reason = "5-day IV pct_change warmup + 1-day forward range"

    for col in ["iv_30d", "high", "low", "close"]:
        if col not in df.columns or df[col].isna().all():
            return BacktestResult(
                hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
                hypothesis_number="H97", ticker=TICKER,
                period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
                raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
                exclusion_reason=f"Missing: {col}", n_observations=0, n_signals=0,
                metric_name="median_range_diff_rising_vs_falling_iv",
                metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
                verdict=BacktestVerdict.INSUFFICIENT_DATA,
                verdict_reason=f"Missing: {col}", data_notes="proxy_tested",
            )

    df2 = df.copy()
    df2["iv_vel_5d"] = df2["iv_30d"].pct_change(5)
    df2["next_range"] = ((df2["high"] - df2["low"]) / df2["close"]).shift(-1)
    df2 = df2.dropna(subset=["iv_vel_5d", "next_range"])
    excluded = raw - len(df2)

    rising = df2[df2["iv_vel_5d"] > 0.10]["next_range"]
    falling = df2[df2["iv_vel_5d"] < -0.08]["next_range"]

    n_rising = len(rising)
    n_falling = len(falling)

    if n_rising < 15 or n_falling < 15:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H97", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_rising,
            metric_name="median_range_diff_rising_vs_falling_iv",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few obs: n_rising={n_rising}, n_falling={n_falling}",
            data_notes="proxy_tested",
        )

    diff = float(rising.median() - falling.median())
    _, p_mw = stats.mannwhitneyu(rising.values, falling.values, alternative="greater")
    pct_rising = float((df2["iv_vel_5d"] > 0.10).mean())
    pct_falling = float((df2["iv_vel_5d"] < -0.08).mean())

    if diff > 0.003 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff_median_range={diff:.5f} (rising={rising.median():.5f}, "
        f"falling={falling.median():.5f}), p_mannwhitney={p_mw:.4f}, "
        f"n_rising={n_rising}, n_falling={n_falling}, "
        f"pct_rising={pct_rising:.3f}, pct_falling={pct_falling:.3f}."
    )
    print(f"  H97: diff={diff:.5f}, p_mw={p_mw:.4f}, n_rising={n_rising}, n_falling={n_falling} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H97", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_rising,
        metric_name="median_range_diff_rising_vs_falling_iv",
        metric_value=round(diff, 6), support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "median_range_rising": round(float(rising.median()), 6),
            "median_range_falling": round(float(falling.median()), 6),
            "n_rising": n_rising,
            "n_falling": n_falling,
            "pct_days_rising": round(pct_rising, 4),
            "pct_days_falling": round(pct_falling, 4),
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H98: Variance Premium Conditional on Term Structure Contango ──────────────────

def run_h98(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Variance premium (iv_30d - fwd_rv_20) is larger and more consistently
    positive when term structure is in contango (iv_30d < iv_90d) than when inverted.

    Primary metric: mean_vp_contango - mean_vp_inverted
    Support: diff > 0.005 AND p < 0.10
    """
    raw = len(df)
    excl_reason = "20-day forward window for fwd_rv_20 + iv_30d / iv_90d"

    required = ["iv_30d", "iv_90d", "fwd_rv_20"]
    missing = [c for c in required if c not in df.columns or df[c].isna().all()]
    if missing:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H98", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=f"Missing: {missing}", n_observations=0, n_signals=0,
            metric_name="mean_vp_diff_contango_vs_inverted",
            metric_value=float("nan"), support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Missing: {missing}", data_notes="proxy_tested",
        )

    df2 = df.copy()
    df2["vp_20d"] = df2["iv_30d"] - df2["fwd_rv_20"]
    df2["in_contango"] = df2["iv_30d"] < df2["iv_90d"]
    df2 = df2.dropna(subset=["vp_20d", "iv_30d", "iv_90d"])
    excluded = raw - len(df2)

    contango_vp = df2[df2["in_contango"]]["vp_20d"]
    inverted_vp = df2[~df2["in_contango"]]["vp_20d"]

    n_cont = len(contango_vp)
    n_inv = len(inverted_vp)

    if n_cont < 10 or n_inv < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H98", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_cont,
            metric_name="mean_vp_diff_contango_vs_inverted",
            metric_value=float("nan"), support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few observations: n_cont={n_cont}, n_inv={n_inv}",
            data_notes="proxy_tested",
        )

    mean_cont = float(contango_vp.mean())
    mean_inv = float(inverted_vp.mean())
    diff = mean_cont - mean_inv
    pct_pos_cont = float((contango_vp > 0).mean())
    pct_pos_inv = float((inverted_vp > 0).mean())

    _, p_mw = stats.mannwhitneyu(contango_vp.values, inverted_vp.values, alternative="greater")

    if diff > 0.005 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff_mean_vp={diff:.5f} (contango={mean_cont:.5f}, inverted={mean_inv:.5f}), "
        f"p_mannwhitney={p_mw:.4f}, pct_positive_contango={pct_pos_cont:.3f}, "
        f"pct_positive_inverted={pct_pos_inv:.3f}, n_contango={n_cont}, n_inverted={n_inv}."
    )
    print(f"  H98: diff={diff:.5f}, p_mw={p_mw:.4f}, n_cont={n_cont}, n_inv={n_inv} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H98", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_cont,
        metric_name="mean_vp_diff_contango_vs_inverted",
        metric_value=round(diff, 6), support_threshold=0.005, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "mean_vp_contango": round(mean_cont, 6),
            "mean_vp_inverted": round(mean_inv, 6),
            "pct_positive_contango": round(pct_pos_cont, 4),
            "pct_positive_inverted": round(pct_pos_inv, 4),
            "n_contango": n_cont,
            "n_inverted": n_inv,
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H99: EOD Bid-Ask Spread Percentile as Session Quality Signal ──────────────────

def run_h99(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When EOD relative bid-ask spread is in top 20th percentile (rolling 60d),
    next-session hv_20_cc is higher than when spread is in bottom 20th percentile.

    Note: daily bid/ask is EOD snapshot — regime proxy, not intraday fill estimate.
    Support: diff > 0.005 AND p < 0.10
    Insufficient: n < 20 per group
    """
    raw = len(df)
    excl_reason = "bid/ask spread + 60-day rolling rank warmup + hv_20_cc next-day"

    for col in ["bid", "ask", "close", "hv_20_cc"]:
        if col not in df.columns or df[col].isna().all():
            return BacktestResult(
                hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
                hypothesis_number="H99", ticker=TICKER,
                period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
                raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
                exclusion_reason=f"Missing: {col}", n_observations=0, n_signals=0,
                metric_name="median_hv_diff_high_vs_low_spread",
                metric_value=float("nan"), support_threshold=0.005, reject_threshold=0.0,
                verdict=BacktestVerdict.INSUFFICIENT_DATA,
                verdict_reason=f"Missing: {col}", data_notes="proxy_tested",
            )

    df2 = df.copy()
    df2["spread_pct"] = (df2["ask"] - df2["bid"]) / df2["close"]
    df2["spread_rank"] = df2["spread_pct"].rolling(60, min_periods=20).rank(pct=True)
    df2["next_hv"] = df2["hv_20_cc"].shift(-1)
    df2 = df2.dropna(subset=["spread_rank", "next_hv", "spread_pct"])
    excluded = raw - len(df2)

    high_spread = df2[df2["spread_rank"] > 0.80]["next_hv"]
    low_spread = df2[df2["spread_rank"] < 0.20]["next_hv"]

    n_high = len(high_spread)
    n_low = len(low_spread)

    if n_high < 20 or n_low < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H99", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_high,
            metric_name="median_hv_diff_high_vs_low_spread",
            metric_value=float("nan"), support_threshold=0.005, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few obs: n_high={n_high}, n_low={n_low}",
            data_notes="proxy_tested",
        )

    diff = float(high_spread.median() - low_spread.median())
    _, p_mw = stats.mannwhitneyu(high_spread.values, low_spread.values, alternative="greater")
    median_spread = float(df2["spread_pct"].median())

    if diff > 0.005 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff_median_hv={diff:.5f} (high_spread={high_spread.median():.5f}, "
        f"low_spread={low_spread.median():.5f}), p_mannwhitney={p_mw:.4f}, "
        f"n_high={n_high}, n_low={n_low}, median_spread_pct={median_spread:.5f}. "
        f"Note: EOD bid/ask is regime proxy — not intraday fill estimate."
    )
    print(f"  H99: diff={diff:.5f}, p_mw={p_mw:.4f}, n_high={n_high} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H99", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_high,
        metric_name="median_hv_diff_high_vs_low_spread",
        metric_value=round(diff, 6), support_threshold=0.005, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "median_hv_high_spread": round(float(high_spread.median()), 6),
            "median_hv_low_spread": round(float(low_spread.median()), 6),
            "median_spread_pct": round(median_spread, 6),
            "n_high_spread": n_high,
            "n_low_spread": n_low,
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── H100: Overnight Gap Magnitude as Same-Session Range Predictor ─────────────────

def run_h100(df: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Sessions with large overnight gaps (|open/prev_close - 1| > 0.5%)
    have a higher same-session realized range than sessions with small gaps (<0.1%).

    Practical use: 0DTE entry confirmation — avoid open short-straddle on large-gap days.
    Support: diff > 0.004 AND p < 0.05
    Insufficient: n_large < 30
    """
    raw = len(df)
    excl_reason = "1-day gap requires prev close; same-session high/low/close"

    for col in ["open", "close", "high", "low"]:
        if col not in df.columns or df[col].isna().all():
            return BacktestResult(
                hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
                hypothesis_number="H100", ticker=TICKER,
                period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
                raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
                exclusion_reason=f"Missing: {col}", n_observations=0, n_signals=0,
                metric_name="median_range_diff_large_vs_small_gap",
                metric_value=float("nan"), support_threshold=0.004, reject_threshold=0.0,
                verdict=BacktestVerdict.INSUFFICIENT_DATA,
                verdict_reason=f"Missing: {col}", data_notes="proxy_tested",
            )

    df2 = df.copy()
    df2["gap_pct"] = (df2["open"] / df2["close"].shift(1) - 1).abs()
    df2["same_range"] = (df2["high"] - df2["low"]) / df2["close"]
    df2 = df2.dropna(subset=["gap_pct", "same_range"])
    excluded = raw - len(df2)

    large_gap = df2[df2["gap_pct"] > 0.005]["same_range"]
    small_gap = df2[df2["gap_pct"] < 0.001]["same_range"]

    n_large = len(large_gap)
    n_small = len(small_gap)
    pct_large = float((df2["gap_pct"] > 0.005).mean())
    median_gap = float(df2["gap_pct"].median())

    if n_large < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H100", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(df2), n_signals=n_large,
            metric_name="median_range_diff_large_vs_small_gap",
            metric_value=float("nan"), support_threshold=0.004, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few large-gap days (n={n_large} < 30) at >0.5% threshold. "
                           f"pct_large={pct_large:.3f}, median_gap={median_gap:.5f}.",
            data_notes="proxy_tested",
        )

    diff = float(large_gap.median() - small_gap.median())
    _, p_mw = stats.mannwhitneyu(large_gap.values, small_gap.values, alternative="greater")

    if diff > 0.004 and p_mw < 0.05:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.20:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    reason = (
        f"diff_median_range={diff:.5f} (large_gap={large_gap.median():.5f}, "
        f"small_gap={small_gap.median():.5f}), p_mannwhitney={p_mw:.4f}, "
        f"n_large={n_large}, n_small={n_small}, pct_days_large_gap={pct_large:.3f}, "
        f"median_gap_pct={median_gap:.5f}. "
        f"Practical use: large gap at open → expect expanded intraday range → "
        f"avoid 0DTE short straddle entry at open."
    )
    print(f"  H100: diff={diff:.5f}, p_mw={p_mw:.4f}, n_large={n_large} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H100", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df2), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(df2), n_signals=n_large,
        metric_name="median_range_diff_large_vs_small_gap",
        metric_value=round(diff, 6), support_threshold=0.004, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "median_range_large_gap": round(float(large_gap.median()), 6),
            "median_range_small_gap": round(float(small_gap.median()), 6),
            "n_large_gap": n_large,
            "n_small_gap": n_small,
            "pct_days_large_gap": round(pct_large, 4),
            "median_gap_pct": round(median_gap, 6),
            "p_mannwhitney": round(p_mw, 6),
        },
    )


# ── Dispatch table ────────────────────────────────────────────────────────────────

DAILY_RUNNERS: dict[str, callable] = {
    "H1": run_h1,
    "H4": run_h4,
    "H9": run_h9,
    "H42": run_h42,
    "H43": run_h43,
    "H44": run_h44,
    "H53": run_h53,
    "H55": run_h55,
    "H57": run_h57,
    "H59": run_h59,
    "H60": run_h60,
    "H70": run_h70,
    "H71": run_h71,
    "H72": run_h72,
    "H73": run_h73,
    "H74": run_h74,
    "H75": run_h75,
    "H76": run_h76,
    "H77": run_h77,
    "H80": run_h80,
    "H86": run_h86,
    "H87": run_h87,
    "H88": run_h88,
    "H89": run_h89,
    "H90": run_h90,
    "H91": run_h91,
    "H92": run_h92,
    "H93": run_h93,
    "H94": run_h94,
    "H95": run_h95,
    "H96": run_h96,
    "H97": run_h97,
    "H98": run_h98,
    "H99": run_h99,
    "H100": run_h100,
    # H2, H3, H5–H8, H10–H12: require VIX futures, options chain, or earnings data
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default="all", help="Comma-separated: H9 or all")
    parser.add_argument("--force", action="store_true", help="Overwrite existing results")
    args = parser.parse_args()

    wanted = (
        list(DAILY_RUNNERS.keys())
        if args.hypotheses.lower() == "all"
        else [h.strip().upper() for h in args.hypotheses.split(",")]
    )
    unknown = [h for h in wanted if h not in DAILY_RUNNERS]
    if unknown:
        print(f"Unknown hypothesis IDs: {unknown}. Available: {list(DAILY_RUNNERS.keys())}")
        sys.exit(1)

    # Load hypotheses.json — ordered H1..H26 by list position.
    hyp_file = EXPERIMENTS_DIR / "hypotheses.json"
    if not hyp_file.exists():
        raise SystemExit("experiments/hypotheses.json not found.")
    all_hyps = json.loads(hyp_file.read_text())
    hyp_by_num: dict[str, dict] = {f"H{i+1}": h for i, h in enumerate(all_hyps)}

    df = _load_daily()
    print(f"Loaded daily_series: {len(df)} rows | window: {TEST_WINDOW_START} → {TEST_WINDOW_END}")
    _validate_daily_series(df)

    existing = _load_existing_results()

    for hnum in wanted:
        if hnum in existing and not args.force:
            print(f"[skip] {hnum} already in backtest_results.json (use --force to re-run)")
            continue

        hyp = hyp_by_num.get(hnum)
        if hyp is None:
            raise SystemExit(
                f"{hnum} not found in hypotheses.json — check H-number ordering "
                f"(hypotheses.json has {len(all_hyps)} entries: H1–H{len(all_hyps)})"
            )

        print(f"Running {hnum}: {hyp.get('title', '')[:60]}...")
        runner = DAILY_RUNNERS[hnum]
        result = runner(df, hyp)
        existing[hnum] = result.model_dump()
        print(f"  → {result.verdict.value}: {result.verdict_reason[:80]}")

    _save_results(existing)
    print(f"\nCompleted {len(wanted)} daily backtest(s).")
    print("Next: run scripts/16_run_intraday_backtests.py --hypotheses H13,H16")


if __name__ == "__main__":
    main()
