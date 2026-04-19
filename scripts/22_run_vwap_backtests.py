#!/usr/bin/env python3
"""
Phase 22: VWAP-based intraday backtests (H78, H79).

H78 — Confirmed VWAP reclaim (9:45-10:25 window) → next 30-min continuation
H79 — VWAP breakout + high relative volume → rest-of-day return, bucket-stratified

Design notes:
- Bar label = bar START time (Databento/pandas resample default: label='left').
  Bar "09:30" closes at 09:34:59. Entry is always at open[T+1] (next bar), never close[T].
- Volume profile uses rolling expanding mean of prior sessions only (leak-safe).
- H79 uses two time-of-day buckets to control for time-left confound.

Usage:
    python scripts/22_run_vwap_backtests.py
    python scripts/22_run_vwap_backtests.py --hypotheses H78
    python scripts/22_run_vwap_backtests.py --force
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
from app.services.databento_price_client import DatabentoPriceClient

PROCESSED_DIR = BASE / "data" / "processed"
EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE = EXPERIMENTS_DIR / "backtest_results.json"
DAILY_SERIES = PROCESSED_DIR / "daily_series.parquet"

TEST_START = "2024-01-01"
TEST_END   = "2026-04-05"
TICKER     = "QQQ"


# ── Utilities ─────────────────────────────────────────────────────────────────

def _sanitise_for_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitise_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitise_for_json(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def _load_existing_results() -> dict[str, dict]:
    if RESULTS_FILE.exists():
        return {r["hypothesis_number"]: r for r in json.loads(RESULTS_FILE.read_text())}
    return {}


def _save_results(results_map: dict[str, dict]) -> None:
    records = _sanitise_for_json(list(results_map.values()))
    RESULTS_FILE.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} results → {RESULTS_FILE}")


def _cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return float("nan")
    wins = sum(1 for x in a for y in b if x > y)
    ties = sum(1 for x in a for y in b if x == y)
    return (wins - (n1 * n2 - wins - ties)) / (n1 * n2)


# ── Intraday data loaders ──────────────────────────────────────────────────────

def _load_all_intraday() -> pd.DataFrame:
    """Load all 5-min bars 2024-01 – 2026-03 via DatabentoPriceClient."""
    print("Loading 5-min bars from Databento cache...")
    client = DatabentoPriceClient(force=False)
    frames = []
    for year in [2024, 2025, 2026]:
        for month in range(1, 13):
            ym = f"{year}{month:02d}"
            if ym > "202603":
                break
            try:
                df = client.get_month_bars(TICKER, ym, interval="5min")
            except Exception as e:
                print(f"  [warn] {ym}: {e}")
                continue
            if df is not None and len(df) > 0:
                frames.append(df)
                print(f"  {ym}: {len(df)} bars")
    if not frames:
        raise SystemExit("No intraday bars loaded. Check Databento cache.")
    all_bars = pd.concat(frames).sort_index()
    # Filter to test window — handle both tz-naive and tz-aware
    if all_bars.index.tzinfo is None:
        start = pd.Timestamp(TEST_START)
        end = pd.Timestamp(TEST_END + " 23:59")
    else:
        import pytz
        tz = all_bars.index.tzinfo
        start = pd.Timestamp(TEST_START, tz=tz)
        end = pd.Timestamp(TEST_END + " 23:59", tz=tz)
    all_bars = all_bars[(all_bars.index >= start) & (all_bars.index <= end)]
    print(f"Loaded {len(all_bars)} 5-min bars across {len(set(all_bars.index.date))} sessions")
    return all_bars


def _verify_timestamp_convention(all_bars: pd.DataFrame) -> None:
    """Assert bar-start convention. Raises SystemExit if data disagrees."""
    first_date = all_bars.index.date[0]
    sample_day = all_bars[all_bars.index.date == first_date]
    times = sample_day.index.strftime("%H:%M").tolist()
    if len(times) < 2 or times[0] != "09:30" or times[1] != "09:35":
        raise SystemExit(
            f"Unexpected bar times: {times[:3]}. Expected 09:30, 09:35, 09:40. "
            "Check Databento resample convention — bar-start assumed."
        )
    print(f"[verify] Timestamp convention OK — bar-start confirmed: {times[:3]}")


def _compute_daily_vwap(day_bars: pd.DataFrame) -> np.ndarray:
    """Cumulative VWAP from session open. Returns numpy array same length as day_bars."""
    typical = (day_bars["high"].values + day_bars["low"].values + day_bars["close"].values) / 3
    vol = day_bars["volume"].values.astype(float)
    cum_tp_vol = np.cumsum(typical * vol)
    cum_vol = np.cumsum(vol)
    # Guard against zero cumulative volume (shouldn't happen but be safe)
    with np.errstate(divide="ignore", invalid="ignore"):
        vwap = np.where(cum_vol > 0, cum_tp_vol / cum_vol, np.nan)
    return vwap


def _build_rolling_vol_profile(
    all_bars: pd.DataFrame, min_prior_sessions: int = 5
) -> tuple[dict, int]:
    """
    Returns (dict[date → pd.Series(HH:MM → cumulative_vol_fraction)], n_fallback).
    Profile for date D uses only sessions prior to D (leak-safe, Version B).
    Full-sample fallback is used for the first min_prior_sessions dates.
    """
    print("Building leak-safe rolling volume profile...")
    dates = sorted(set(all_bars.index.date))

    # Compute per-session cumulative fraction series
    session_fracs: dict = {}
    for d in dates:
        day = all_bars[all_bars.index.date == d]
        total = float(day["volume"].sum())
        if total == 0:
            continue
        cum_frac = day["volume"].cumsum() / total
        cum_frac.index = day.index.strftime("%H:%M")
        session_fracs[d] = cum_frac

    # Full-sample fallback (mildly in-sample, used only for first few sessions)
    full_sample: pd.Series = pd.concat(list(session_fracs.values()), axis=1).mean(axis=1)

    # Expanding mean: profile[d] = mean of sessions strictly before d
    rolling_profiles: dict = {}
    running_frames: list = []
    for d in dates:
        if len(running_frames) >= min_prior_sessions:
            rolling_profiles[d] = pd.concat(running_frames, axis=1).mean(axis=1)
        else:
            rolling_profiles[d] = None  # will use full-sample fallback
        if d in session_fracs:
            running_frames.append(session_fracs[d])

    n_fallback = sum(1 for v in rolling_profiles.values() if v is None)
    for d in dates:
        if rolling_profiles.get(d) is None:
            rolling_profiles[d] = full_sample

    print(
        f"  Volume profile: {len(rolling_profiles)} session profiles built, "
        f"{n_fallback} using full-sample fallback"
    )
    return rolling_profiles, n_fallback


# ── H78 runner ────────────────────────────────────────────────────────────────

def run_h78(all_bars: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    H78: Confirmed VWAP reclaim in 9:45–10:25 window.
    Signal bar T: close[T]>VWAP[T], close[T-1]<=VWAP[T-1], close[T-2]<=VWAP[T-2].
    Entry: open[T+1]. Exit: close[T+6]. Outcome: return > 0 (continuation).
    """
    raw_sessions = len(set(all_bars.index.date))
    records: list[dict] = []
    n_raw_crosses = 0
    skipped_no_exit = 0

    for d, day_bars in all_bars.groupby(all_bars.index.date):
        if len(day_bars) < 10:
            continue
        day_bars = day_bars.reset_index(drop=False)
        vwap = _compute_daily_vwap(day_bars)
        closes = day_bars["close"].values
        opens_ = day_bars["open"].values
        times = pd.DatetimeIndex(day_bars.iloc[:, 0]).strftime("%H:%M").tolist()

        found_raw_cross = False

        for i in range(2, len(day_bars)):
            bar_time = times[i]
            if bar_time < "09:45":
                continue
            if bar_time > "10:25":
                break

            # Raw first cross (no quality filter)
            if closes[i] > vwap[i] and closes[i - 1] <= vwap[i - 1]:
                if not found_raw_cross:
                    n_raw_crosses += 1
                    found_raw_cross = True

                # Quality filter: 2 prior bars confirmed below VWAP
                if closes[i - 2] <= vwap[i - 2]:
                    entry_idx = i + 1   # T+1
                    exit_idx  = i + 6   # T+6
                    if exit_idx >= len(day_bars):
                        skipped_no_exit += 1
                        break
                    entry_open = float(opens_[entry_idx])
                    exit_close = float(closes[exit_idx])
                    ret = math.log(exit_close / entry_open)
                    # Post-signal hold diagnostics (strictly diagnostic, not used for verdict)
                    held_2 = (
                        (closes[i + 1] > vwap[i + 1] and closes[i + 2] > vwap[i + 2])
                        if i + 2 < len(day_bars) else None
                    )
                    held_5 = (
                        all(closes[i + k] > vwap[i + k] for k in range(1, 6)
                            if i + k < len(day_bars))
                        if i + 5 < len(day_bars) else None
                    )
                    records.append({
                        "date": str(d),
                        "bar_time": bar_time,
                        "ret": ret,
                        "continuation": ret > 0,
                        "held_2": held_2,
                        "held_5": held_5,
                    })
                    break  # one signal per day

    n_confirmed = len(records)
    n_total_sessions = raw_sessions

    if n_confirmed < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H78", ticker=TICKER,
            period_start=TEST_START, period_end=TEST_END,
            raw_rows=n_total_sessions, rows_after_validation=n_total_sessions,
            rows_excluded=0,
            exclusion_reason="5-min bar sessions; signals require 2-bar quality filter",
            n_observations=n_total_sessions, n_signals=n_confirmed,
            metric_name="pct_continuation", metric_value=float("nan"),
            support_threshold=0.55, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(
                f"n_confirmed_reclaims={n_confirmed} < 30 (raw first-crosses={n_raw_crosses}). "
                f"Skipped {skipped_no_exit} days with insufficient bars after signal."
            ),
            data_notes="directly_tested",
        )

    wins = sum(1 for r in records if r["continuation"])
    pct_cont = wins / n_confirmed
    p_binom = float(stats.binomtest(wins, n_confirmed, 0.5, alternative="greater").pvalue)
    mean_ret = float(np.mean([r["ret"] for r in records]))
    filter_pct = 1 - (n_confirmed / n_raw_crosses) if n_raw_crosses > 0 else float("nan")
    pct_days = n_confirmed / n_total_sessions
    pct_held_2 = float(np.mean([r["held_2"] for r in records if r["held_2"] is not None]))
    pct_held_5 = float(np.mean([r["held_5"] for r in records if r["held_5"] is not None]))

    extra_caveat = ""
    if pct_held_2 < 0.50:
        extra_caveat = (
            f" NOTE: pct_held_2bars={pct_held_2:.3f} < 0.50 — confirmed reclaims failed "
            f"to hold above VWAP for 2 bars in majority of cases. Signal quality is low."
        )

    if pct_cont > 0.55 and p_binom < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"pct_continuation={pct_cont:.3f} ({wins}/{n_confirmed}) > 0.55, "
            f"p_binomial={p_binom:.4f} < 0.10. mean_return_30min={mean_ret:.5f}. "
            f"n_raw_crosses={n_raw_crosses}, filter removed {filter_pct:.1%}."
            + extra_caveat
        )
    elif pct_cont <= 0.50 or p_binom > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"pct_continuation={pct_cont:.3f} ({wins}/{n_confirmed}), "
            f"p_binomial={p_binom:.4f}. No reliable 30-min continuation after VWAP reclaim."
            + extra_caveat
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"pct_continuation={pct_cont:.3f} ({wins}/{n_confirmed}), "
            f"p_binomial={p_binom:.4f}. Direction present but not significant."
            + extra_caveat
        )

    print(f"  H78: pct_cont={pct_cont:.3f} ({wins}/{n_confirmed}), p_binom={p_binom:.4f}, "
          f"raw_crosses={n_raw_crosses}, filter_removed={filter_pct:.1%}")
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H78", ticker=TICKER,
        period_start=TEST_START, period_end=TEST_END,
        raw_rows=n_total_sessions, rows_after_validation=n_total_sessions,
        rows_excluded=0,
        exclusion_reason="5-min bar sessions; 2-bar quality filter + 09:45-10:25 window",
        n_observations=n_total_sessions, n_signals=n_confirmed,
        metric_name="pct_continuation", metric_value=round(pct_cont, 4),
        support_threshold=0.55, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_confirmed_reclaims": n_confirmed,
            "n_raw_first_crosses": n_raw_crosses,
            "n_wins": wins,
            "filter_reduction_pct": round(filter_pct, 4) if not math.isnan(filter_pct) else None,
            "pct_days_with_reclaim": round(pct_days, 4),
            "mean_return_30min_reclaim": round(mean_ret, 6),
            "p_binomial": round(p_binom, 4),
            "pct_held_2bars": round(pct_held_2, 4),
            "pct_held_5bars": round(pct_held_5, 4),
        },
    )


# ── H79 runner ────────────────────────────────────────────────────────────────

def run_h79(
    all_bars: pd.DataFrame,
    vol_profiles: dict,
    n_fallback: int,
    hyp: dict,
) -> BacktestResult:
    """
    H79: Confirmed VWAP breakout (9:45-12:55 window) + relative volume vs rest-of-day return.
    Entry: open[T+1]. Exit: close[15:55 bar].
    Bucket-stratified: early (09:45-10:25) vs late (10:30-12:55).
    Relative volume uses rolling leak-safe time-of-day profile.

    NOTE: Daily volume baseline is computed from the same Databento intraday bars to
    avoid data-source mismatch (daily_series.parquet total volume is ~23x larger,
    as it aggregates all exchanges vs. Databento EQUS.MINI).
    """
    raw_sessions = len(set(all_bars.index.date))

    # 20-day rolling mean of daily volume — computed from Databento bars (same source)
    daily_intraday_vol = (
        all_bars.groupby(all_bars.index.date)["volume"]
        .sum()
        .sort_index()
    )
    daily_intraday_vol_df = pd.DataFrame({"date": daily_intraday_vol.index,
                                           "total_vol": daily_intraday_vol.values})
    daily_intraday_vol_df["vol_20ma"] = daily_intraday_vol_df["total_vol"].rolling(20).mean()
    vol_lookup: dict = dict(zip(daily_intraday_vol_df["date"],
                                daily_intraday_vol_df["vol_20ma"]))

    records: list[dict] = []
    n_skipped_no_profile = 0
    n_skipped_no_vol = 0
    n_skipped_no_bars = 0

    for d, day_bars in all_bars.groupby(all_bars.index.date):
        if len(day_bars) < 5:
            continue

        profile = vol_profiles.get(d)
        if profile is None:
            n_skipped_no_profile += 1
            continue

        daily_vol_20ma = vol_lookup.get(d)
        if daily_vol_20ma is None or (isinstance(daily_vol_20ma, float) and math.isnan(daily_vol_20ma)) or daily_vol_20ma == 0:
            n_skipped_no_vol += 1
            continue

        day_bars = day_bars.reset_index(drop=False)
        vwap = _compute_daily_vwap(day_bars)
        closes = day_bars["close"].values
        opens_ = day_bars["open"].values
        volumes = day_bars["volume"].values.astype(float)
        times = pd.DatetimeIndex(day_bars.iloc[:, 0]).strftime("%H:%M").tolist()

        for i in range(2, len(day_bars)):
            bar_time = times[i]
            if bar_time < "09:45":
                continue
            if bar_time > "12:55":
                break

            # Confirmed quality-filtered VWAP cross
            if (closes[i] > vwap[i]
                    and closes[i - 1] <= vwap[i - 1]
                    and closes[i - 2] <= vwap[i - 2]):

                entry_idx = i + 1
                if entry_idx >= len(day_bars):
                    n_skipped_no_bars += 1
                    break

                # Relative volume
                cum_vol_at_i = float(volumes[:i + 1].sum())
                expected_frac = float(profile.get(bar_time, 0.0))
                if expected_frac <= 0:
                    break  # sparse profile slot — skip day
                expected_cum_vol = float(daily_vol_20ma) * expected_frac
                rel_vol = cum_vol_at_i / expected_cum_vol

                # Rest-of-day return: entry open to last bar close
                entry_open = float(opens_[entry_idx])
                exit_close = float(closes[-1])
                if entry_open <= 0 or exit_close <= 0:
                    break
                rod_return = math.log(exit_close / entry_open)

                bucket = "early" if bar_time <= "10:25" else "late"
                records.append({
                    "date": str(d),
                    "bar_time": bar_time,
                    "rel_vol": rel_vol,
                    "rod_return": rod_return,
                    "bucket": bucket,
                })
                break  # one signal per day

    # Split into high / low groups
    high_all  = [r for r in records if r["rel_vol"] >= 1.2]
    low_all   = [r for r in records if r["rel_vol"] <= 0.8]
    mid_count = sum(1 for r in records if 0.8 < r["rel_vol"] < 1.2)

    n_high = len(high_all)
    n_low  = len(low_all)

    if n_high < 20 or n_low < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H79", ticker=TICKER,
            period_start=TEST_START, period_end=TEST_END,
            raw_rows=raw_sessions, rows_after_validation=raw_sessions,
            rows_excluded=0,
            exclusion_reason="5-min bar sessions; relative volume split + bucket stratification",
            n_observations=raw_sessions, n_signals=len(records),
            metric_name="mean_rod_return_high_minus_low_overall", metric_value=float("nan"),
            support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(
                f"n_high_vol={n_high}, n_low_vol={n_low} — one or both < 20. "
                f"Total breakout signals={len(records)}, middle-band excluded={mid_count}. "
                f"Skipped: no_profile={n_skipped_no_profile}, no_vol={n_skipped_no_vol}."
            ),
            data_notes="directly_tested",
        )

    # Overall comparison
    high_rod = np.array([r["rod_return"] for r in high_all])
    low_rod  = np.array([r["rod_return"] for r in low_all])
    diff_overall = float(np.mean(high_rod) - np.mean(low_rod))
    _, p_overall = stats.mannwhitneyu(high_rod, low_rod, alternative="greater")
    p_overall = float(p_overall)
    cd_overall = _cliffs_delta(high_rod, low_rod)

    # Bucket-level comparisons
    bucket_stats: dict = {}
    for bucket in ("early", "late"):
        h_b = np.array([r["rod_return"] for r in high_all if r["bucket"] == bucket])
        l_b = np.array([r["rod_return"] for r in low_all  if r["bucket"] == bucket])
        if len(h_b) >= 5 and len(l_b) >= 5:
            diff_b = float(np.mean(h_b) - np.mean(l_b))
            _, p_b = stats.mannwhitneyu(h_b, l_b, alternative="greater")
            bucket_stats[bucket] = {
                "n_high": len(h_b), "n_low": len(l_b),
                "mean_high": round(float(np.mean(h_b)), 6),
                "mean_low": round(float(np.mean(l_b)), 6),
                "diff": round(diff_b, 6),
                "p_mw": round(float(p_b), 4),
            }
        else:
            bucket_stats[bucket] = {"n_high": len(h_b), "n_low": len(l_b), "insufficient": True}

    # Determine if at least one bucket confirms the direction (p < 0.20)
    bucket_confirms = any(
        (not v.get("insufficient", False)) and v.get("p_mw", 1.0) < 0.20
        for v in bucket_stats.values()
    )
    pct_middle = mid_count / len(records) if records else float("nan")
    median_rel_vol = float(np.median([r["rel_vol"] for r in records]))

    if diff_overall > 0.001 and p_overall < 0.10 and bucket_confirms:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Overall diff={diff_overall:.5f} (high mean={np.mean(high_rod):.5f}, "
            f"low mean={np.mean(low_rod):.5f}), p_mw_overall={p_overall:.4f}, "
            f"Cliff's d={cd_overall:.3f}. Effect confirmed in at least one bucket (p<0.20). "
            f"n_high={n_high}, n_low={n_low}. Middle-band excluded={mid_count} ({pct_middle:.1%}). "
            f"Vol profile: rolling_expanding, fallback_sessions={n_fallback}."
        )
    elif diff_overall > 0.001 and p_overall < 0.10:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Overall diff={diff_overall:.5f}, p_mw={p_overall:.4f} — significant overall "
            f"but no individual bucket confirmed (p<0.20). Time-left confound not fully "
            f"controlled. n_high={n_high}, n_low={n_low}."
        )
    elif diff_overall <= 0 or p_overall > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"diff_overall={diff_overall:.5f}, p_mw_overall={p_overall:.4f}. "
            f"High-vol breakouts do not outperform low-vol. "
            f"n_high={n_high}, n_low={n_low}, median_rel_vol={median_rel_vol:.3f}."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"diff_overall={diff_overall:.5f}, p_mw_overall={p_overall:.4f}. Inconclusive. "
            f"n_high={n_high}, n_low={n_low}."
        )

    print(
        f"  H79: diff={diff_overall:.5f}, n_high={n_high}, n_low={n_low}, "
        f"p_overall={p_overall:.4f}, buckets={bucket_stats}"
    )
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H79", ticker=TICKER,
        period_start=TEST_START, period_end=TEST_END,
        raw_rows=raw_sessions, rows_after_validation=raw_sessions,
        rows_excluded=0,
        exclusion_reason="5-min bar sessions; rel-vol split (>=1.2 vs <=0.8) + bucket stratification",
        n_observations=raw_sessions, n_signals=len(records),
        metric_name="mean_rod_return_high_minus_low_overall", metric_value=round(diff_overall, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "n_high_vol_total": n_high,
            "n_low_vol_total": n_low,
            "n_breakout_signals_total": len(records),
            "n_middle_band_excluded": mid_count,
            "pct_middle_band": round(pct_middle, 4) if not math.isnan(pct_middle) else None,
            "mean_rod_high_overall": round(float(np.mean(high_rod)), 6),
            "mean_rod_low_overall": round(float(np.mean(low_rod)), 6),
            "diff_overall": round(diff_overall, 6),
            "p_mannwhitney_overall": round(p_overall, 4),
            "cliffs_delta_overall": round(cd_overall, 4),
            "median_rel_vol_at_breakout": round(median_rel_vol, 4),
            "n_high_vol_early": bucket_stats.get("early", {}).get("n_high"),
            "n_low_vol_early": bucket_stats.get("early", {}).get("n_low"),
            "mean_rod_high_early": bucket_stats.get("early", {}).get("mean_high"),
            "mean_rod_low_early": bucket_stats.get("early", {}).get("mean_low"),
            "p_mannwhitney_early": bucket_stats.get("early", {}).get("p_mw"),
            "n_high_vol_late": bucket_stats.get("late", {}).get("n_high"),
            "n_low_vol_late": bucket_stats.get("late", {}).get("n_low"),
            "mean_rod_high_late": bucket_stats.get("late", {}).get("mean_high"),
            "mean_rod_low_late": bucket_stats.get("late", {}).get("mean_low"),
            "p_mannwhitney_late": bucket_stats.get("late", {}).get("p_mw"),
            "vol_profile_version": "rolling_expanding",
            "n_fallback_sessions": n_fallback,
        },
    )


# ── Dispatch ──────────────────────────────────────────────────────────────────

VWAP_RUNNERS = {
    "H78": "h78",
    "H79": "h79",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default="all")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    wanted = (
        list(VWAP_RUNNERS.keys())
        if args.hypotheses.lower() == "all"
        else [h.strip().upper() for h in args.hypotheses.split(",")]
    )
    unknown = [h for h in wanted if h not in VWAP_RUNNERS]
    if unknown:
        print(f"Unknown: {unknown}. Available: {list(VWAP_RUNNERS.keys())}")
        sys.exit(1)

    hyp_file = EXPERIMENTS_DIR / "hypotheses.json"
    all_hyps = json.loads(hyp_file.read_text())
    hyp_by_num = {f"H{i + 1}": h for i, h in enumerate(all_hyps)}

    existing = _load_existing_results()

    # Load intraday bars (shared across runners)
    all_bars = _load_all_intraday()
    _verify_timestamp_convention(all_bars)

    # Build vol profile once (used by H79)
    vol_profiles, n_fallback = _build_rolling_vol_profile(all_bars)

    # Load daily series once (used by H79)
    daily_df = pd.read_parquet(DAILY_SERIES)
    if "date" in daily_df.columns:
        daily_df["date"] = pd.to_datetime(daily_df["date"])

    for hnum in wanted:
        if hnum in existing and not args.force:
            print(f"[skip] {hnum} already in results (use --force to re-run)")
            continue

        hyp = hyp_by_num.get(hnum)
        if hyp is None:
            raise SystemExit(f"{hnum} not found in hypotheses.json.")

        print(f"Running {hnum}: {hyp.get('title', '')[:70]}...")
        if hnum == "H78":
            result = run_h78(all_bars, hyp)
        elif hnum == "H79":
            result = run_h79(all_bars, vol_profiles, n_fallback, hyp)
        else:
            raise SystemExit(f"No runner for {hnum}")

        existing[hnum] = result.model_dump()
        print(f"  → {result.verdict.value}: {result.verdict_reason[:100]}")

    _save_results(existing)
    print(f"\nCompleted {len(wanted)} VWAP backtest(s).")
    print("Next: run scripts/17_score_and_report.py && scripts/18_export_backtest_vault.py")


if __name__ == "__main__":
    main()
