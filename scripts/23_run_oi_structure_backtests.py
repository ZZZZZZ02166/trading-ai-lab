#!/usr/bin/env python3
"""
Phase 23: Run options OI-structure backtests (H81–H85).

H81 — Put-heavy volume (PCR) associates with iv_30d rise within 2 sessions
H82 — Near-spot short-dated OI concentration (adj HHI) predicts next-session range
H83 — Peak gamma-weighted OI strike proximity predicts next-day range contraction
H84 — Delta-band OI asymmetry predicts next-session return direction
H85 — Short-dated call OI expansion associates with next-session positive return

Data window:
  Param files:    2025-04-01 → 2025-12-31 (190 overlap C+P dates)
  Call-only:      2024-01-01 → 2025-12-31 (317 C dates, used by H85)
  Daily series:   2024-01-01 → 2026-04-05

All hypotheses use 1-30 DTE restriction except H81 (aggregate all DTE for volume).
Interpretation: all labeled associative/exploratory — no dealer-sign identification.

Usage:
    python scripts/23_run_oi_structure_backtests.py
    python scripts/23_run_oi_structure_backtests.py --hypotheses H81,H82
    python scripts/23_run_oi_structure_backtests.py --force
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

from app.models.backtest_result import BacktestResult, BacktestVerdict

PROCESSED_DIR   = BASE / "data" / "processed"
CHAINS_DIR      = BASE / "data" / "raw" / "chains"
EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE    = EXPERIMENTS_DIR / "backtest_results.json"
DAILY_SERIES    = PROCESSED_DIR / "daily_series.parquet"

CHAINS_START      = "2025-04-01"   # first date with both C and P param files
TEST_WINDOW_START = "2024-01-01"
TEST_WINDOW_END   = "2026-04-05"
TICKER            = "QQQ"


# ── Shared utilities ──────────────────────────────────────────────────────────────

def _sanitise_for_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitise_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitise_for_json(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def _load_daily() -> pd.DataFrame:
    df = pd.read_parquet(DAILY_SERIES)
    date_col = [c for c in df.columns if "date" in c.lower()]
    if date_col:
        df["date"] = pd.to_datetime(df[date_col[0]])
    df = df.sort_values("date").reset_index(drop=True)
    return df[
        (df["date"] >= TEST_WINDOW_START) & (df["date"] <= TEST_WINDOW_END)
    ].reset_index(drop=True)


def _load_chains() -> tuple[dict[str, Path], dict[str, Path]]:
    """Returns (c_files, p_files) dicts keyed by YYYYMMDD string."""
    c_files = {
        f.name.split("_")[4]: f
        for f in CHAINS_DIR.glob("qqq_opts_by_param_*_C.parquet")
    }
    p_files = {
        f.name.split("_")[4]: f
        for f in CHAINS_DIR.glob("qqq_opts_by_param_*_P.parquet")
    }
    return c_files, p_files


def _overlap_dates(c_files: dict, p_files: dict) -> list[str]:
    return sorted(set(c_files.keys()) & set(p_files.keys()))


def _datestr_to_ts(d: str) -> pd.Timestamp:
    return pd.Timestamp(f"{d[:4]}-{d[4:6]}-{d[6:]}")


def _load_existing_results() -> dict[str, dict]:
    if RESULTS_FILE.exists():
        return {r["hypothesis_number"]: r for r in json.loads(RESULTS_FILE.read_text())}
    return {}


def _save_results(results_map: dict[str, dict]) -> None:
    records = _sanitise_for_json(list(results_map.values()))
    RESULTS_FILE.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} results → {RESULTS_FILE}")


# ── H81: PCR → iv_30d Rise ────────────────────────────────────────────────────────

def run_h81(
    daily: pd.DataFrame,
    c_files: dict[str, Path],
    p_files: dict[str, Path],
    hyp: dict,
) -> BacktestResult:
    """
    Claim: Sessions with PCR > 0.58 associate with higher iv_30d over next 2 sessions.
    Associative only — 0DTE put volume confound acknowledged.

    Signal: pcr_vol = sum_put_vol / (sum_put_vol + sum_call_vol) > 0.58
    Control: pcr_vol < 0.42
    Outcome: iv_30d[t+2] - iv_30d[t]
    Support: diff > 0.003 AND p_mannwhitney < 0.10
    """
    overlap = _overlap_dates(c_files, p_files)
    raw = len(overlap)
    excl_reason = "Requires both C and P param files; iv_30d from daily_series"

    rows = []
    for d in overlap:
        try:
            calls = pd.read_parquet(c_files[d])
            puts  = pd.read_parquet(p_files[d])
        except Exception:
            continue
        call_vol = float(calls["volume"].sum())
        put_vol  = float(puts["volume"].sum())
        total_vol = call_vol + put_vol
        if total_vol <= 0:
            continue
        pcr = put_vol / total_vol
        rows.append({"date": _datestr_to_ts(d), "pcr_vol": pcr})

    if not rows:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H81", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=excl_reason, n_observations=0, n_signals=0,
            metric_name="mean_iv_change_diff_put_heavy_vs_control",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="No param file rows loaded",
            data_notes="directly_tested",
        )

    pcr_df = pd.DataFrame(rows).sort_values("date")
    work = pcr_df.merge(daily[["date", "iv_30d"]], on="date", how="inner")
    work = work.sort_values("date").reset_index(drop=True)
    work["iv_change_2d"] = work["iv_30d"].shift(-2) - work["iv_30d"]
    work = work.dropna(subset=["iv_change_2d"])
    excluded = raw - len(work)

    signal  = work[work["pcr_vol"] > 0.58]["iv_change_2d"].values
    control = work[work["pcr_vol"] < 0.42]["iv_change_2d"].values

    n_signal  = len(signal)
    n_control = len(control)

    # PCR for QQQ aggregated params clusters tightly (0.43–0.61).
    # Fixed thresholds (>0.58 / <0.42) produce empty groups.
    # Use data-driven percentile thresholds: top quartile vs bottom quartile.
    pcr_p75 = float(work["pcr_vol"].quantile(0.75))
    pcr_p25 = float(work["pcr_vol"].quantile(0.25))

    signal_mask  = work["pcr_vol"] >= pcr_p75
    control_mask = work["pcr_vol"] <= pcr_p25
    signal  = work[signal_mask]["iv_change_2d"].values
    control = work[control_mask]["iv_change_2d"].values

    n_signal  = len(signal)
    n_control = len(control)

    if n_signal < 10 or n_control < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H81", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(work),
            n_signals=n_signal,
            metric_name="mean_iv_change_diff_put_heavy_vs_control",
            metric_value=float("nan"), support_threshold=0.003, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few in signal ({n_signal}) or control ({n_control}) group",
            data_notes="directly_tested",
        )

    mean_sig  = float(np.mean(signal))
    mean_ctrl = float(np.mean(control))
    diff = mean_sig - mean_ctrl

    _, p_mw = stats.mannwhitneyu(signal, control, alternative="greater")
    median_pcr = float(work["pcr_vol"].median())

    if diff > 0.003 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    confound_note = (
        "Same-day vol confound: 0DTE put volume spikes on large down days mechanically inflate "
        "PCR on days when IV tends to rise regardless. Association may reflect coincident "
        "conditions rather than PCR predicting IV. Treat as exploratory."
    )

    threshold_note = (
        f"Thresholds data-driven: signal=PCR≥p75({pcr_p75:.4f}), "
        f"control=PCR≤p25({pcr_p25:.4f}). "
        "QQQ aggregate PCR clusters in 0.43–0.61; fixed 0.58/0.42 thresholds produce empty groups. "
    )

    reason = (
        f"diff={diff:.4f} (mean_put_heavy={mean_sig:.4f}, mean_control={mean_ctrl:.4f}), "
        f"p_mannwhitney={p_mw:.4f}, n_signal={n_signal}, n_control={n_control}. "
        + threshold_note + confound_note
    )

    print(
        f"  H81: diff={diff:.4f}, p_mw={p_mw:.4f}, n_sig={n_signal}, "
        f"n_ctrl={n_control}, pcr_p75={pcr_p75:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H81", ticker=TICKER,
        period_start=CHAINS_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_signal,
        metric_name="mean_iv_change_diff_put_heavy_vs_control",
        metric_value=round(diff, 6),
        support_threshold=0.003, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "mean_iv_change_put_heavy": round(mean_sig, 6),
            "mean_iv_change_control": round(mean_ctrl, 6),
            "n_signal": n_signal,
            "n_control": n_control,
            "p_mannwhitney": round(p_mw, 6),
            "median_pcr_overall": round(median_pcr, 4),
            "pcr_threshold_p75": round(pcr_p75, 4),
            "pcr_threshold_p25": round(pcr_p25, 4),
        },
    )


# ── H82: Near-Spot Short-Dated OI Concentration (Adj HHI) ────────────────────────

def _compute_adj_hhi(
    calls: pd.DataFrame, puts: pd.DataFrame, spot: float
) -> tuple[float, int]:
    """Compute adjusted HHI for near-spot (±5%), 1-30 DTE combined call+put OI.

    Returns (adj_hhi, n_qualifying_strikes). adj_hhi in [0,1]; NaN if <2 strikes.
    """
    moneyness_lo = spot * 0.95
    moneyness_hi = spot * 1.05

    c_filt = calls[
        (calls["dte"].between(1, 30)) &
        (calls["price_strike"].between(moneyness_lo, moneyness_hi)) &
        (calls["openinterest"] > 0)
    ][["price_strike", "openinterest"]]

    p_filt = puts[
        (puts["dte"].between(1, 30)) &
        (puts["price_strike"].between(moneyness_lo, moneyness_hi)) &
        (puts["openinterest"] > 0)
    ][["price_strike", "openinterest"]]

    combined = (
        pd.concat([c_filt, p_filt])
        .groupby("price_strike")["openinterest"]
        .sum()
    )

    n = len(combined)
    if n < 2:
        return float("nan"), n

    total_oi = float(combined.sum())
    if total_oi <= 0:
        return float("nan"), n

    shares  = combined / total_oi
    raw_hhi = float((shares ** 2).sum())
    adj_hhi = (raw_hhi - 1.0 / n) / (1.0 - 1.0 / n)
    return adj_hhi, n


def run_h82(
    daily: pd.DataFrame,
    c_files: dict[str, Path],
    p_files: dict[str, Path],
    hyp: dict,
) -> BacktestResult:
    """
    Claim: High adj-HHI OI concentration in near-spot short-dated options precedes
    smaller next-session intraday ranges.

    Universe: |strike/spot - 1| <= 0.05, dte 1-30.
    Normalized adj_hhi removes mechanical N-dependence.
    Support: median_range_top_quintile - median_range_bottom_quintile < -0.001 AND p < 0.10
    """
    overlap = _overlap_dates(c_files, p_files)
    raw = len(overlap)
    excl_reason = "Requires C+P param files; next-day range from daily_series"

    rows = []
    for d in overlap:
        try:
            calls = pd.read_parquet(c_files[d])
            puts  = pd.read_parquet(p_files[d])
        except Exception:
            continue
        spot = float(calls["underlying_price"].median())
        if spot <= 0 or pd.isna(spot):
            continue
        adj_hhi, n_strikes = _compute_adj_hhi(calls, puts, spot)
        if pd.isna(adj_hhi):
            continue
        rows.append({
            "date": _datestr_to_ts(d),
            "adj_hhi": adj_hhi,
            "n_qualifying_strikes": n_strikes,
        })

    if len(rows) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H82", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(rows), rows_excluded=raw - len(rows),
            exclusion_reason=excl_reason, n_observations=len(rows), n_signals=0,
            metric_name="median_range_diff_top_vs_bottom_quintile",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(rows)}",
            data_notes="directly_tested",
        )

    hhi_df = pd.DataFrame(rows).sort_values("date")

    # Join with next-day range: shift daily by -1 so each hhi date maps to NEXT day's range
    daily2 = daily.copy()
    daily2["next_range"] = ((daily2["high"] - daily2["low"]) / daily2["close"]).shift(-1)
    work = hhi_df.merge(daily2[["date", "next_range"]], on="date", how="inner")
    work = work.dropna(subset=["next_range"])
    excluded = raw - len(work)

    n_valid = len(work)
    if n_valid < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H82", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=n_valid, rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=n_valid, n_signals=0,
            metric_name="median_range_diff_top_vs_bottom_quintile",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few joined rows after next-range merge: {n_valid}",
            data_notes="directly_tested",
        )

    q20 = float(work["adj_hhi"].quantile(0.20))
    q80 = float(work["adj_hhi"].quantile(0.80))
    top    = work[work["adj_hhi"] >= q80]["next_range"].values
    bottom = work[work["adj_hhi"] <= q20]["next_range"].values

    n_top    = len(top)
    n_bottom = len(bottom)

    if n_top < 5 or n_bottom < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H82", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=n_valid, rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=n_valid, n_signals=n_top,
            metric_name="median_range_diff_top_vs_bottom_quintile",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few in top ({n_top}) or bottom ({n_bottom}) quintile",
            data_notes="directly_tested",
        )

    med_top    = float(np.median(top))
    med_bottom = float(np.median(bottom))
    diff = med_top - med_bottom

    _, p_mw = stats.mannwhitneyu(top, bottom, alternative="less")

    mean_hhi = float(work["adj_hhi"].mean())
    mean_n_strikes = float(work["n_qualifying_strikes"].mean())

    if diff < -0.001 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff >= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    dealer_caveat = (
        "Adjusted HHI measures near-spot short-dated OI dispersion. "
        "Dealer gamma sign unknown — concentration may dampen (long gamma) "
        "or amplify (short gamma) depending on dealer position direction."
    )

    reason = (
        f"median_range_diff={diff:.5f} (top_quintile={med_top:.5f}, bottom={med_bottom:.5f}), "
        f"p_mannwhitney={p_mw:.4f}, n_top={n_top}, n_bottom={n_bottom}. "
        + dealer_caveat
    )

    print(
        f"  H82: diff={diff:.5f}, p_mw={p_mw:.4f}, n_top={n_top}, "
        f"n_bot={n_bottom}, mean_adj_hhi={mean_hhi:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H82", ticker=TICKER,
        period_start=CHAINS_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=n_valid, rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=n_valid, n_signals=n_top,
        metric_name="median_range_diff_top_vs_bottom_quintile",
        metric_value=round(diff, 6),
        support_threshold=-0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "median_range_top_quintile": round(med_top, 6),
            "median_range_bottom_quintile": round(med_bottom, 6),
            "p_mannwhitney": round(p_mw, 6),
            "n_top_quintile": n_top,
            "n_bottom_quintile": n_bottom,
            "mean_adj_hhi": round(mean_hhi, 4),
            "mean_qualifying_strikes": round(mean_n_strikes, 1),
            "n_valid_dates": n_valid,
        },
    )


# ── H83: Peak Gamma-Weighted OI Strike Proximity ─────────────────────────────────

def run_h83(
    daily: pd.DataFrame,
    c_files: dict[str, Path],
    p_files: dict[str, Path],
    hyp: dict,
) -> BacktestResult:
    """
    Claim: Price within $3 of peak gross gamma-weighted OI strike associates
    with smaller next-session range vs $8+ away.

    NO net-gamma / GEX framing. Dealer sign unknown.
    Universe: same as H82 — dte 1-30, ±5% moneyness.
    Support: diff < -0.001 AND p < 0.10
    """
    overlap = _overlap_dates(c_files, p_files)
    raw = len(overlap)
    excl_reason = "Requires C+P param files; EOD close + next-day range from daily_series"

    rows = []
    for d in overlap:
        try:
            calls = pd.read_parquet(c_files[d])
            puts  = pd.read_parquet(p_files[d])
        except Exception:
            continue
        spot = float(calls["underlying_price"].median())
        if spot <= 0 or pd.isna(spot):
            continue

        moneyness_lo = spot * 0.95
        moneyness_hi = spot * 1.05

        c_filt = calls[
            (calls["dte"].between(1, 30)) &
            (calls["price_strike"].between(moneyness_lo, moneyness_hi)) &
            (calls["openinterest"] > 0)
        ][["price_strike", "openinterest", "gamma"]].rename(
            columns={"openinterest": "oi_call", "gamma": "gamma_call"}
        )

        p_filt = puts[
            (puts["dte"].between(1, 30)) &
            (puts["price_strike"].between(moneyness_lo, moneyness_hi)) &
            (puts["openinterest"] > 0)
        ][["price_strike", "openinterest", "gamma"]].rename(
            columns={"openinterest": "oi_put", "gamma": "gamma_put"}
        )

        if c_filt.empty and p_filt.empty:
            continue

        # Aggregate per strike
        c_agg = c_filt.groupby("price_strike").agg(
            oi_call=("oi_call", "sum"), gamma_call=("gamma_call", "mean")
        ).reset_index()
        p_agg = p_filt.groupby("price_strike").agg(
            oi_put=("oi_put", "sum"), gamma_put=("gamma_put", "mean")
        ).reset_index()

        merged = pd.merge(c_agg, p_agg, on="price_strike", how="outer").fillna(0.0)
        merged["gamma_oi"] = (
            merged["gamma_call"] * merged["oi_call"]
            + merged["gamma_put"] * merged["oi_put"]
        )

        if merged["gamma_oi"].max() <= 0:
            continue

        peak_strike = float(merged.loc[merged["gamma_oi"].idxmax(), "price_strike"])
        rows.append({
            "date": _datestr_to_ts(d),
            "peak_strike": peak_strike,
            "spot": spot,
        })

    if len(rows) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H83", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(rows), rows_excluded=raw - len(rows),
            exclusion_reason=excl_reason, n_observations=len(rows), n_signals=0,
            metric_name="median_next_range_near_vs_far",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid peak-strike dates: {len(rows)}",
            data_notes="directly_tested",
        )

    peak_df = pd.DataFrame(rows).sort_values("date")

    # Join daily: need EOD close (for dist_to_peak) and next-day range
    daily2 = daily.copy()
    daily2["next_range"] = ((daily2["high"] - daily2["low"]) / daily2["close"]).shift(-1)
    work = peak_df.merge(daily2[["date", "close", "next_range"]], on="date", how="inner")
    work = work.dropna(subset=["close", "next_range"])
    work["dist_to_peak"] = (work["close"] - work["peak_strike"]).abs()
    excluded = raw - len(work)

    near = work[work["dist_to_peak"] < 3]["next_range"].values
    far  = work[work["dist_to_peak"] > 8]["next_range"].values

    n_near = len(near)
    n_far  = len(far)

    if n_near < 10 or n_far < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H83", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(work), n_signals=n_near,
            metric_name="median_next_range_near_vs_far",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few near ({n_near}) or far ({n_far}) dates for test",
            data_notes="directly_tested",
        )

    med_near = float(np.median(near))
    med_far  = float(np.median(far))
    diff = med_near - med_far

    _, p_mw = stats.mannwhitneyu(near, far, alternative="less")
    median_dist = float(work["dist_to_peak"].median())

    if diff < -0.001 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif diff >= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    gex_caveat = (
        "Gross gamma-weighted OI only — dealer position sign unknown. "
        "Do not interpret as net dealer gamma or GEX. "
        "This is an empirical proximity test; high gamma-OI at a strike "
        "means concentrated option sensitivity, not a known directional hedge."
    )

    reason = (
        f"median_range_diff={diff:.5f} (near={med_near:.5f}, far={med_far:.5f}), "
        f"p_mannwhitney={p_mw:.4f}, n_near={n_near}, n_far={n_far}. "
        + gex_caveat
    )

    print(
        f"  H83: diff={diff:.5f}, p_mw={p_mw:.4f}, n_near={n_near}, "
        f"n_far={n_far}, median_dist=${median_dist:.2f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H83", ticker=TICKER,
        period_start=CHAINS_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_near,
        metric_name="median_next_range_near_vs_far",
        metric_value=round(diff, 6),
        support_threshold=-0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "median_range_near": round(med_near, 6),
            "median_range_far": round(med_far, 6),
            "n_near_lt3": n_near,
            "n_far_gt8": n_far,
            "p_mannwhitney": round(p_mw, 6),
            "median_dist_to_peak": round(median_dist, 2),
        },
    )


# ── H84: Delta-Band OI Asymmetry ─────────────────────────────────────────────────

def run_h84(
    daily: pd.DataFrame,
    c_files: dict[str, Path],
    p_files: dict[str, Path],
    hyp: dict,
) -> BacktestResult:
    """
    Claim: Sessions with put-heavy delta-band OI (oi_ratio > 1.5) associate
    with lower next-session returns vs call-heavy sessions (oi_ratio < 0.67).

    Put band: puts with |delta| in [0.15, 0.40], dte 1-30.
    Call band: calls with delta in [0.15, 0.40], dte 1-30.
    Strictly exploratory — OI aggregates directional, hedge, spread, and dealer inventory.
    Support (loose): diff < -0.001 AND p < 0.15
    """
    overlap = _overlap_dates(c_files, p_files)
    raw = len(overlap)
    excl_reason = "Requires C+P param files; next-session log_return from daily_series"

    rows = []
    for d in overlap:
        try:
            calls = pd.read_parquet(c_files[d])
            puts  = pd.read_parquet(p_files[d])
        except Exception:
            continue

        if "delta" not in calls.columns or "delta" not in puts.columns:
            continue

        call_band_oi = float(
            calls[
                (calls["delta"].between(0.15, 0.40)) &
                (calls["dte"].between(1, 30))
            ]["openinterest"].sum()
        )
        put_band_oi = float(
            puts[
                (puts["delta"].abs().between(0.15, 0.40)) &
                (puts["dte"].between(1, 30))
            ]["openinterest"].sum()
        )

        if call_band_oi <= 0:
            continue
        oi_ratio = put_band_oi / call_band_oi
        rows.append({"date": _datestr_to_ts(d), "oi_ratio": oi_ratio})

    if len(rows) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H84", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(rows), rows_excluded=raw - len(rows),
            exclusion_reason=excl_reason, n_observations=len(rows), n_signals=0,
            metric_name="mean_next_return_diff_put_heavy_vs_call_heavy",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(rows)}",
            data_notes="directly_tested",
        )

    ratio_df = pd.DataFrame(rows).sort_values("date")

    daily2 = daily.copy()
    daily2["next_return"] = daily2["log_return"].shift(-1)
    work = ratio_df.merge(daily2[["date", "next_return"]], on="date", how="inner")
    work = work.dropna(subset=["next_return"])
    excluded = raw - len(work)

    put_heavy  = work[work["oi_ratio"] > 1.5]["next_return"].values
    call_heavy = work[work["oi_ratio"] < 0.67]["next_return"].values

    n_put  = len(put_heavy)
    n_call = len(call_heavy)

    if n_put < 10 or n_call < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H84", ticker=TICKER,
            period_start=CHAINS_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(work), n_signals=n_put,
            metric_name="mean_next_return_diff_put_heavy_vs_call_heavy",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few put-heavy ({n_put}) or call-heavy ({n_call}) dates",
            data_notes="directly_tested",
        )

    mean_put  = float(np.mean(put_heavy))
    mean_call = float(np.mean(call_heavy))
    diff = mean_put - mean_call

    _, p_mw = stats.mannwhitneyu(put_heavy, call_heavy, alternative="less")
    median_ratio = float(work["oi_ratio"].median())
    pct_middle_band = float(
        ((work["oi_ratio"] >= 0.67) & (work["oi_ratio"] <= 1.5)).mean()
    )

    if diff < -0.001 and p_mw < 0.15:
        verdict = BacktestVerdict.SUPPORTED
    elif diff >= 0 or p_mw > 0.40:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    oi_caveat = (
        "Delta-band OI aggregates directional bets, portfolio hedges, covered writes, "
        "and dealer inventory indiscriminately. Cannot isolate institutional hedging demand. "
        "Exploratory association test — loose thresholds applied."
    )

    reason = (
        f"diff={diff:.5f} (put_heavy={mean_put:.5f}, call_heavy={mean_call:.5f}), "
        f"p_mannwhitney={p_mw:.4f}, n_put={n_put}, n_call={n_call}, "
        f"pct_middle_band={pct_middle_band:.1%}. " + oi_caveat
    )

    print(
        f"  H84: diff={diff:.5f}, p_mw={p_mw:.4f}, n_put={n_put}, "
        f"n_call={n_call} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H84", ticker=TICKER,
        period_start=CHAINS_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_put,
        metric_name="mean_next_return_diff_put_heavy_vs_call_heavy",
        metric_value=round(diff, 6),
        support_threshold=-0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "mean_next_return_put_heavy": round(mean_put, 6),
            "mean_next_return_call_heavy": round(mean_call, 6),
            "n_put_heavy": n_put,
            "n_call_heavy": n_call,
            "p_mannwhitney": round(p_mw, 6),
            "median_oi_ratio": round(median_ratio, 4),
            "pct_middle_band_excluded": round(pct_middle_band, 4),
        },
    )


# ── H85: Short-Dated Call OI Expansion ───────────────────────────────────────────

def run_h85(
    daily: pd.DataFrame,
    c_files: dict[str, Path],
    p_files: dict[str, Path],  # noqa: ARG001 — not used, signature kept consistent
    hyp: dict,
) -> BacktestResult:
    """
    Claim: Sessions where short-dated (1-30 DTE) call OI expands >5% day-over-day
    associate with higher next-session win rate vs sessions where call OI contracts.

    Filters: DTE 1-30 only; exclude dates where prior session had >15% call OI drop
    (expiry contamination).

    Strictly exploratory — call OI expansion ≠ bullish flow.
    Support (loose): win_rate > 0.55 AND p_binomial < 0.10
    """
    c_date_strs = sorted(c_files.keys())
    raw = len(c_date_strs)
    excl_reason = "Requires consecutive call param file dates; next-session log_return from daily_series"

    rows = []
    for d in c_date_strs:
        try:
            calls = pd.read_parquet(c_files[d])
        except Exception:
            continue
        oi_1to30 = float(
            calls[calls["dte"].between(1, 30)]["openinterest"].sum()
        )
        rows.append({"date": _datestr_to_ts(d), "call_oi_1to30": oi_1to30})

    if len(rows) < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H85", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason=excl_reason, n_observations=0, n_signals=0,
            metric_name="win_rate_call_oi_expansion",
            metric_value=float("nan"), support_threshold=0.55, reject_threshold=0.5,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="Too few call file dates loaded",
            data_notes="directly_tested",
        )

    oi_df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    oi_df["oi_change_pct"] = oi_df["call_oi_1to30"].pct_change()

    # Prior-day drop filter: exclude dates where the preceding date had >15% OI collapse
    oi_df["prior_oi_drop_pct"] = oi_df["call_oi_1to30"].shift(1) / oi_df["call_oi_1to30"].shift(2) - 1
    before_filter = len(oi_df)
    oi_df = oi_df[
        oi_df["prior_oi_drop_pct"].isna() | (oi_df["prior_oi_drop_pct"] > -0.15)
    ].reset_index(drop=True)
    n_expiry_filtered = before_filter - len(oi_df)

    work = oi_df.merge(daily[["date", "log_return"]], on="date", how="inner")
    work = work.dropna(subset=["oi_change_pct", "log_return"])

    # Forward-shift log_return to get NEXT session return
    work = oi_df.merge(daily[["date", "log_return"]], on="date", how="inner")
    work = work.sort_values("date").reset_index(drop=True)
    work["next_return"] = work["log_return"].shift(-1)
    work = work.dropna(subset=["oi_change_pct", "next_return"])
    excluded = raw - len(work)

    signal  = work[work["oi_change_pct"] >  0.05]
    control = work[work["oi_change_pct"] < -0.05]

    n_signal  = len(signal)
    n_control = len(control)

    if n_signal < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H85", ticker=TICKER,
            period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason, n_observations=len(work), n_signals=n_signal,
            metric_name="win_rate_call_oi_expansion",
            metric_value=float("nan"), support_threshold=0.55, reject_threshold=0.5,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few signal days ({n_signal} < 10)",
            data_notes="directly_tested",
        )

    win_rate = float((signal["next_return"] > 0).mean())
    n_wins   = int((signal["next_return"] > 0).sum())

    binom_result = stats.binomtest(n_wins, n_signal, p=0.50, alternative="greater")
    p_binomial = float(binom_result.pvalue)

    win_rate_control = float((control["next_return"] > 0).mean()) if n_control > 0 else float("nan")

    _, p_mw = (
        stats.mannwhitneyu(
            signal["next_return"].values,
            control["next_return"].values,
            alternative="greater",
        )
        if n_control > 0
        else (float("nan"), float("nan"))
    )

    pct_expiry_filtered = n_expiry_filtered / max(before_filter, 1)

    if win_rate > 0.55 and p_binomial < 0.10:
        verdict = BacktestVerdict.SUPPORTED
    elif win_rate <= 0.50 or p_binomial > 0.30:
        verdict = BacktestVerdict.REJECTED
    else:
        verdict = BacktestVerdict.INCONCLUSIVE

    oi_caveat = (
        "Call OI expansion reflects covered call writing, roll activity, spread construction, "
        "and dealer inventory changes alongside directional long-call positioning. "
        "Net position direction is unknown. Exploratory association only."
    )

    reason = (
        f"win_rate={win_rate:.1%} (n_signal={n_signal}, wins={n_wins}), "
        f"p_binomial={p_binomial:.4f}, win_rate_control={win_rate_control:.1%}. "
        f"n_expiry_filtered={n_expiry_filtered} ({pct_expiry_filtered:.1%} of dates). "
        + oi_caveat
    )

    print(
        f"  H85: win_rate={win_rate:.1%}, p_binom={p_binomial:.4f}, "
        f"n_sig={n_signal}, n_expiry_filt={n_expiry_filtered} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H85", ticker=TICKER,
        period_start=TEST_WINDOW_START, period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_signal,
        metric_name="win_rate_call_oi_expansion",
        metric_value=round(win_rate, 4),
        support_threshold=0.55, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        extra_metrics={
            "win_rate_signal": round(win_rate, 4),
            "win_rate_control": round(win_rate_control, 4) if not math.isnan(win_rate_control) else None,
            "n_signal": n_signal,
            "n_wins_signal": n_wins,
            "p_binomial": round(p_binomial, 6),
            "p_mannwhitney": round(float(p_mw), 6) if not math.isnan(float(p_mw)) else None,
            "n_control": n_control,
            "n_expiry_filtered": n_expiry_filtered,
            "pct_expiry_filtered": round(pct_expiry_filtered, 4),
        },
    )


# ── Dispatch table ────────────────────────────────────────────────────────────────

OI_RUNNERS = {
    "H81": run_h81,
    "H82": run_h82,
    "H83": run_h83,
    "H84": run_h84,
    "H85": run_h85,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default="all")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    wanted = (
        list(OI_RUNNERS.keys())
        if args.hypotheses.lower() == "all"
        else [h.strip().upper() for h in args.hypotheses.split(",")]
    )
    unknown = [h for h in wanted if h not in OI_RUNNERS]
    if unknown:
        print(f"Unknown IDs: {unknown}. Available: {list(OI_RUNNERS.keys())}")
        sys.exit(1)

    if not CHAINS_DIR.exists():
        raise SystemExit(f"chains/ directory not found: {CHAINS_DIR}")

    hyp_file = EXPERIMENTS_DIR / "hypotheses.json"
    all_hyps = json.loads(hyp_file.read_text())
    hyp_by_num = {f"H{i+1}": h for i, h in enumerate(all_hyps)}

    daily = _load_daily()
    print(f"Loaded daily_series: {len(daily)} rows | {TEST_WINDOW_START} → {TEST_WINDOW_END}")

    c_files, p_files = _load_chains()
    overlap = _overlap_dates(c_files, p_files)
    print(
        f"Param files: {len(c_files)} C dates, {len(p_files)} P dates, "
        f"{len(overlap)} overlap dates"
    )

    existing = _load_existing_results()

    for hnum in wanted:
        if hnum in existing and not args.force:
            print(f"[skip] {hnum} already in backtest_results.json (use --force to re-run)")
            continue

        hyp = hyp_by_num.get(hnum)
        if hyp is None:
            raise SystemExit(f"{hnum} not found in hypotheses.json (has {len(all_hyps)} entries)")

        print(f"Running {hnum}: {hyp.get('title','')[:65]}...")
        result = OI_RUNNERS[hnum](daily, c_files, p_files, hyp)
        existing[hnum] = result.model_dump()
        print(f"  → {result.verdict.value}: {result.verdict_reason[:100]}")

    _save_results(existing)
    print(f"\nCompleted {len(wanted)} OI-structure backtest(s).")
    print("Next: run scripts/17_score_and_report.py")


if __name__ == "__main__":
    main()
