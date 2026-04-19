#!/usr/bin/env python3
"""
Phase 21: Run put/call wall and open-interest backtests (H61–H65).

Wall definitions:
  Call wall = highest-OI call strike strictly ABOVE underlying (dte 1–30)
  Put wall  = highest-OI put strike strictly BELOW underlying (dte 1–30)

Data window: 2025-04-01 → 2025-12-31 (190 dates with both C and P param files).

H61: Open inside wall range → session containment
H62: Open outside wall range → same-direction continuation
H63: Rising price + rising OI → next-session continuation
H64: Expiry Fridays close nearer max pain than open
H65: Both walls shift up/down overnight → next-session direction

Usage:
    python scripts/21_run_wall_backtests.py
    python scripts/21_run_wall_backtests.py --hypotheses H61,H62
    python scripts/21_run_wall_backtests.py --force
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

CHAINS_START      = "2025-04-01"
CHAINS_END        = "2025-12-31"
TEST_WINDOW_START = "2024-01-01"
TEST_WINDOW_END   = "2026-04-05"
TICKER            = "QQQ"

# DTE window for wall calculation
WALL_DTE_MIN = 1
WALL_DTE_MAX = 30


def _sanitise_for_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitise_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitise_for_json(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def _cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) == 0 or len(y) == 0:
        return float("nan")
    U, _ = stats.mannwhitneyu(x, y, alternative="two-sided")
    return float(2 * U / (len(x) * len(y)) - 1)


def _load_daily() -> pd.DataFrame:
    df = pd.read_parquet(DAILY_SERIES)
    date_col = [c for c in df.columns if "date" in c.lower()]
    if date_col:
        df["date"] = pd.to_datetime(df[date_col[0]])
    df = df.sort_values("date").reset_index(drop=True)
    return df[(df["date"] >= TEST_WINDOW_START) & (df["date"] <= TEST_WINDOW_END)].reset_index(drop=True)


def _load_existing_results() -> dict[str, dict]:
    if RESULTS_FILE.exists():
        return {r["hypothesis_number"]: r for r in json.loads(RESULTS_FILE.read_text())}
    return {}


def _save_results(results_map: dict[str, dict]) -> None:
    records = _sanitise_for_json(list(results_map.values()))
    RESULTS_FILE.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} results → {RESULTS_FILE}")


# ── Wall computation ──────────────────────────────────────────────────────────────

def _compute_walls(chains_dir: Path) -> pd.DataFrame:
    """
    For each date with both C and P param files, compute:
      call_wall, put_wall, underlying, total_oi, has_expiry_dte0,
      max_pain (for expiry dates only, else NaN)

    Returns DataFrame sorted by date.
    """
    c_files = {f.name.split("_")[4]: f for f in chains_dir.glob("qqq_opts_by_param_*_C.parquet")}
    p_files = {f.name.split("_")[4]: f for f in chains_dir.glob("qqq_opts_by_param_*_P.parquet")}
    overlap = sorted(set(c_files.keys()) & set(p_files.keys()))
    print(f"[walls] Building wall table for {len(overlap)} dates...")

    rows = []
    for date_str in overlap:
        try:
            calls = pd.read_parquet(c_files[date_str])
            puts  = pd.read_parquet(p_files[date_str])
        except Exception:
            continue

        underlying = float(calls["underlying_price"].median())
        if underlying <= 0 or pd.isna(underlying):
            continue

        date = pd.Timestamp(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}")

        # Call wall: highest OI call ABOVE underlying, dte 1-30
        c_above = calls[
            (calls["openinterest"] > 0) &
            (calls["price_strike"] > underlying) &
            (calls["dte"].between(WALL_DTE_MIN, WALL_DTE_MAX))
        ]
        call_wall = float(
            c_above.groupby("price_strike")["openinterest"].sum().idxmax()
        ) if len(c_above) > 0 else float("nan")
        call_wall_oi = float(
            c_above.groupby("price_strike")["openinterest"].sum().max()
        ) if len(c_above) > 0 else float("nan")

        # Put wall: highest OI put BELOW underlying, dte 1-30
        p_below = puts[
            (puts["openinterest"] > 0) &
            (puts["price_strike"] < underlying) &
            (puts["dte"].between(WALL_DTE_MIN, WALL_DTE_MAX))
        ]
        put_wall = float(
            p_below.groupby("price_strike")["openinterest"].sum().idxmax()
        ) if len(p_below) > 0 else float("nan")
        put_wall_oi = float(
            p_below.groupby("price_strike")["openinterest"].sum().max()
        ) if len(p_below) > 0 else float("nan")

        # Total OI across all contracts
        total_oi = int(calls["openinterest"].sum()) + int(puts["openinterest"].sum())

        # Expiry detection: any dte=0 options
        has_expiry = bool(
            ((calls["dte"] == 0).any()) or ((puts["dte"] == 0).any())
        )

        # Max pain (only on expiry days — uses dte=0 options)
        max_pain = float("nan")
        if has_expiry:
            c_exp = calls[calls["dte"] == 0][["price_strike", "openinterest"]].rename(
                columns={"openinterest": "c_oi"})
            p_exp = puts[puts["dte"] == 0][["price_strike", "openinterest"]].rename(
                columns={"openinterest": "p_oi"})
            merged = pd.merge(
                c_exp.groupby("price_strike")["c_oi"].sum().reset_index(),
                p_exp.groupby("price_strike")["p_oi"].sum().reset_index(),
                on="price_strike", how="outer"
            ).fillna(0)

            if len(merged) >= 3:
                candidates = merged["price_strike"].values
                total_pain = np.zeros(len(candidates))
                c_oi_arr = merged["c_oi"].values
                p_oi_arr = merged["p_oi"].values

                for i, K in enumerate(candidates):
                    # Puts in the money at K: put strikes > K → writer pays strike - K per unit
                    put_pain   = np.sum(p_oi_arr[candidates > K] * (candidates[candidates > K] - K))
                    # Calls in the money at K: call strikes < K → writer pays K - strike per unit
                    call_pain  = np.sum(c_oi_arr[candidates < K] * (K - candidates[candidates < K]))
                    total_pain[i] = put_pain + call_pain

                max_pain = float(candidates[np.argmin(total_pain)])

        rows.append({
            "date":        date,
            "underlying":  round(underlying, 4),
            "call_wall":   call_wall,
            "put_wall":    put_wall,
            "call_wall_oi": call_wall_oi,
            "put_wall_oi": put_wall_oi,
            "total_oi":    total_oi,
            "has_expiry":  has_expiry,
            "max_pain":    max_pain,
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df["oi_change"] = df["total_oi"].diff()  # overnight OI change
    df["call_wall_shift"] = df["call_wall"].diff()
    df["put_wall_shift"]  = df["put_wall"].diff()
    print(f"[walls] Done — {len(df)} dates, {df['has_expiry'].sum()} expiry dates")
    return df


# ── H61: Open Inside Wall Range → Containment ────────────────────────────────────

def run_h61(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Opens between put_wall and call_wall close inside the same range
    more often than opens outside the range close inside an equivalent-width band.

    Signal: open between put_wall and call_wall
    Outcome: close also between put_wall and call_wall (contained)
    Primary metric: containment_rate_inside_open - containment_rate_outside_open
    Support: diff > 0.10 AND p_binomial < 0.10
    """
    raw = len(walls)
    excl_reason = "Requires valid put_wall and call_wall; OHLC from daily_series"

    work = walls.dropna(subset=["put_wall", "call_wall"]).copy()
    work = work.merge(daily[["date", "open", "close", "log_return"]], on="date", how="inner")
    work = work.dropna(subset=["open", "close"])
    excluded = raw - len(work)

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H61", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="containment_rate_diff_inside_vs_outside_open",
            metric_value=float("nan"), support_threshold=0.10, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid joined dates: {len(work)}",
            data_notes="directly_tested",
        )

    inside_open  = (work["open"] >= work["put_wall"]) & (work["open"] <= work["call_wall"])
    outside_open = ~inside_open

    # Containment: close inside the wall range
    contained = (work["close"] >= work["put_wall"]) & (work["close"] <= work["call_wall"])

    inside_days   = work[inside_open]
    outside_days  = work[outside_open]

    if len(inside_days) < 5 or len(outside_days) < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H61", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=int(inside_open.sum()),
            metric_name="containment_rate_diff_inside_vs_outside_open",
            metric_value=float("nan"), support_threshold=0.10, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few inside ({len(inside_days)}) or outside ({len(outside_days)}) dates",
            data_notes="directly_tested",
        )

    rate_inside  = float(contained[inside_open].mean())
    rate_outside = float(contained[outside_open].mean())
    diff = rate_inside - rate_outside

    n_inside  = len(inside_days)
    n_outside = len(outside_days)
    n_inside_contained  = int(contained[inside_open].sum())
    n_outside_contained = int(contained[outside_open].sum())

    # Binomial test: is inside containment rate > outside?
    binom = stats.binomtest(n_inside_contained, n_inside, p=rate_outside if rate_outside > 0 else 0.5,
                            alternative="greater")
    p_binom = float(binom.pvalue)

    # Also Fisher exact to compare the two rates
    ct = [[n_inside_contained, n_inside - n_inside_contained],
          [n_outside_contained, n_outside - n_outside_contained]]
    _, p_fisher = stats.fisher_exact(ct, alternative="greater")

    pct_inside_open = float(inside_open.mean())

    if diff > 0.10 and p_fisher < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Inside-open sessions contain more often: {rate_inside:.1%} vs {rate_outside:.1%} "
            f"(diff={diff:.3f}, p_fisher={p_fisher:.4f}). "
            f"{n_inside} inside-open, {n_outside} outside-open days."
        )
    elif diff <= 0 or p_fisher > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No containment advantage for inside-open sessions: "
            f"{rate_inside:.1%} vs {rate_outside:.1%} (diff={diff:.3f}, p_fisher={p_fisher:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (inside={rate_inside:.1%} vs outside={rate_outside:.1%}, "
            f"diff={diff:.3f}) but not significant (p_fisher={p_fisher:.4f})"
        )

    print(
        f"  H61: n_inside={n_inside} ({pct_inside_open:.1%}), n_outside={n_outside}, "
        f"rate_inside={rate_inside:.1%}, rate_outside={rate_outside:.1%}, "
        f"diff={diff:.3f}, p={p_fisher:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H61", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_inside,
        metric_name="containment_rate_diff_inside_vs_outside_open",
        metric_value=round(diff, 4),
        support_threshold=0.10, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="strategy_win_rate",
        extra_metrics={
            "n_inside_open":         n_inside,
            "n_outside_open":        n_outside,
            "pct_inside_open":       round(pct_inside_open, 3),
            "containment_rate_inside":  round(rate_inside, 4),
            "containment_rate_outside": round(rate_outside, 4),
            "p_fisher_exact":        round(p_fisher, 4),
            "p_binomial":            round(p_binom, 4),
            "mean_wall_width":       round(float((work["call_wall"] - work["put_wall"]).mean()), 2),
        },
    )


# ── H62: Open Outside Wall Range → Continuation ──────────────────────────────────

def run_h62(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Opens above call_wall → session closes positive and stays above wall.
    Opens below put_wall → session closes negative and stays below wall.

    Signal: open > call_wall (above) or open < put_wall (below)
    Outcome: directional continuation (close in same direction, stays outside wall)
    Primary metric: continuation_rate - 0.50 (binomial vs chance)
    """
    raw = len(walls)
    excl_reason = "Requires valid put_wall and call_wall; OHLC from daily_series"

    work = walls.dropna(subset=["put_wall", "call_wall"]).copy()
    work = work.merge(daily[["date", "open", "close", "log_return"]], on="date", how="inner")
    work = work.dropna(subset=["open", "close"])
    excluded = raw - len(work)

    if len(work) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H62", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="continuation_rate_outside_open_minus_0_5",
            metric_value=float("nan"), support_threshold=0.10, reject_threshold=-0.05,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(work)}",
            data_notes="directly_tested",
        )

    above_open = work["open"] > work["call_wall"]
    below_open = work["open"] < work["put_wall"]
    outside_open = above_open | below_open

    # Continuation definitions
    # Above: close > call_wall (stays above) AND close > open (positive)
    above_cont = above_open & (work["close"] > work["call_wall"]) & (work["close"] > work["open"])
    # Below: close < put_wall (stays below) AND close < open (negative)
    below_cont = below_open & (work["close"] < work["put_wall"]) & (work["close"] < work["open"])
    any_cont = above_cont | below_cont

    n_outside = int(outside_open.sum())
    n_above   = int(above_open.sum())
    n_below   = int(below_open.sum())
    n_cont    = int(any_cont.sum())

    if n_outside < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H62", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=n_outside,
            metric_name="continuation_rate_outside_open_minus_0_5",
            metric_value=float("nan"), support_threshold=0.10, reject_threshold=-0.05,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few outside-open days: {n_outside} (need >= 5)",
            data_notes="directly_tested",
        )

    cont_rate = float(n_cont / n_outside) if n_outside > 0 else float("nan")
    metric    = cont_rate - 0.50

    binom = stats.binomtest(n_cont, n_outside, p=0.50, alternative="greater")
    p_binom = float(binom.pvalue)

    # Return on outside days vs inside days
    outside_returns = work["log_return"][outside_open].values
    inside_returns  = work["log_return"][~outside_open].values
    mean_outside = float(np.mean(abs(outside_returns))) if len(outside_returns) > 0 else float("nan")

    if metric > 0.10 and p_binom < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Continuation rate on outside-open days: {cont_rate:.1%} "
            f"(n={n_outside}, {metric:+.3f} above 50%, p={p_binom:.4f}). "
            f"Above-wall opens: {n_above}, below-wall opens: {n_below}."
        )
    elif metric <= -0.05 or p_binom > 0.40:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No continuation bias: rate={cont_rate:.1%} on {n_outside} outside-open days "
            f"(p={p_binom:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Some continuation ({cont_rate:.1%}, {metric:+.3f} vs 50%) "
            f"but not significant (p={p_binom:.4f}, n={n_outside})"
        )

    print(
        f"  H62: n_outside={n_outside} (above={n_above}, below={n_below}), "
        f"cont_rate={cont_rate:.1%}, p={p_binom:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H62", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_outside,
        metric_name="continuation_rate_outside_open_minus_0_5",
        metric_value=round(metric, 4),
        support_threshold=0.10, reject_threshold=-0.05,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="strategy_win_rate",
        extra_metrics={
            "n_outside_open":        n_outside,
            "n_above_call_wall":     n_above,
            "n_below_put_wall":      n_below,
            "continuation_rate":     round(cont_rate, 4),
            "p_binomial":            round(p_binom, 4),
            "pct_outside_open":      round(float(outside_open.mean()), 3),
        },
    )


# ── H63: Rising Price + Rising OI → Next-Session Continuation ────────────────────

def run_h63(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Up days with rising OI show stronger next-session continuation
    than up days with falling OI.

    Signal: log_return > 0 AND oi_change > 0
    Control: log_return > 0 AND oi_change < 0
    Outcome: next_log_return (positive = continuation)
    Primary metric: mean_next_return_rising_oi - mean_next_return_falling_oi
    """
    raw = len(walls)
    excl_reason = "Requires consecutive-date OI data; 1-day forward shift for next return"

    work = walls.dropna(subset=["oi_change"]).copy()
    work = work.merge(daily[["date", "log_return"]], on="date", how="inner")
    work["next_return"] = work["log_return"].shift(-1)
    work = work.dropna(subset=["log_return", "oi_change", "next_return"])
    excluded = raw - len(work)

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H63", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="mean_next_return_diff_rising_vs_falling_oi_on_up_days",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(work)}",
            data_notes="directly_tested",
        )

    up_day = work["log_return"] > 0
    rising_oi  = up_day & (work["oi_change"] > 0)
    falling_oi = up_day & (work["oi_change"] < 0)

    rising_vals  = work["next_return"][rising_oi].values
    falling_vals = work["next_return"][falling_oi].values

    n_rising  = len(rising_vals)
    n_falling = len(falling_vals)

    if n_rising < 5 or n_falling < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H63", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=n_rising,
            metric_name="mean_next_return_diff_rising_vs_falling_oi_on_up_days",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few up days: rising_oi={n_rising}, falling_oi={n_falling}",
            data_notes="directly_tested",
        )

    mean_rising  = float(np.mean(rising_vals))
    mean_falling = float(np.mean(falling_vals))
    diff = mean_rising - mean_falling

    U_stat, p_mw = stats.mannwhitneyu(rising_vals, falling_vals, alternative="greater")
    cd = _cliffs_delta(rising_vals, falling_vals)

    if diff > 0.001 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Up days with rising OI show better continuation: "
            f"mean_next={mean_rising:.5f} vs {mean_falling:.5f} "
            f"(diff={diff:.5f}, p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"Rising OI on up days does not predict continuation: "
            f"mean_next={mean_rising:.5f} vs {mean_falling:.5f} (diff={diff:.5f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.5f}) but not significant "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(
        f"  H63: n_rising={n_rising}, n_falling={n_falling}, "
        f"diff={diff:.5f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H63", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_rising,
        metric_name="mean_next_return_diff_rising_vs_falling_oi_on_up_days",
        metric_value=round(diff, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="mean_difference",
        extra_metrics={
            "n_up_days_rising_oi":      n_rising,
            "n_up_days_falling_oi":     n_falling,
            "mean_next_return_rising":  round(mean_rising, 6),
            "mean_next_return_falling": round(mean_falling, 6),
            "cliffs_delta":             round(cd, 4),
            "p_mannwhitney":            round(p_mw, 4),
            "u_stat":                   round(float(U_stat), 2),
        },
    )


# ── H64: Expiry Fridays Close Nearer Max Pain ─────────────────────────────────────

def run_h64(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: On weekly expiry Fridays, close is nearer to max pain than open was.

    NOTE: QQQ has 0DTE options every trading day. The `has_expiry` flag (any dte=0 present)
    is True for ALL dates. This function therefore filters to Fridays explicitly (dayofweek==4),
    which are the canonical weekly expiry sessions and match the original hypothesis intent.

    Signal: Fridays where max_pain is computable from dte=0 options
    Outcome: |close - max_pain| < |open - max_pain|  (close moved toward max pain)
    Primary metric: win_rate (fraction of expiry Fridays where price moved toward max pain)
    Support: win_rate > 0.60 AND p_binomial < 0.10

    Lookahead note: max_pain uses same-session EOD dte=0 OI. The open (9:30 AM) is
    observed before this OI is final. Strictly, prior-day dte=1 OI should be used.
    The practical impact is small (0DTE OI set at prior close), but is flagged here.
    """
    raw = len(walls)
    # Filter to Fridays: QQQ has 0DTE every day, so has_expiry=True for all dates.
    # The hypothesis targets weekly expiry Fridays.
    walls_fri = walls[walls["date"].dt.dayofweek == 4].copy()
    expiry_dates = walls_fri[walls_fri["max_pain"].notna()].copy()
    excl_reason = (
        "Filtered to Fridays (weekly expiry). QQQ has 0DTE options every day, so "
        "has_expiry=True for all dates — explicit Friday filter required. "
        "max_pain computed from same-day EOD dte=0 OI (minor lookahead for open comparison)."
    )

    expiry_dates = expiry_dates.merge(
        daily[["date", "open", "close"]], on="date", how="inner"
    ).dropna(subset=["open", "close", "max_pain"])

    n_expiry = len(expiry_dates)

    if n_expiry < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H64", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=n_expiry, rows_excluded=raw - n_expiry,
            exclusion_reason=excl_reason,
            n_observations=n_expiry, n_signals=n_expiry,
            metric_name="max_pain_approach_win_rate",
            metric_value=float("nan"), support_threshold=0.60, reject_threshold=0.50,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few expiry dates with valid max pain: {n_expiry} (need >= 10)",
            data_notes="directly_tested",
        )

    expiry_dates["dist_open"]  = (expiry_dates["open"]  - expiry_dates["max_pain"]).abs()
    expiry_dates["dist_close"] = (expiry_dates["close"] - expiry_dates["max_pain"]).abs()
    expiry_dates["moved_toward"] = expiry_dates["dist_close"] < expiry_dates["dist_open"]

    n_wins    = int(expiry_dates["moved_toward"].sum())
    win_rate  = float(n_wins / n_expiry)
    mean_dist_open  = float(expiry_dates["dist_open"].mean())
    mean_dist_close = float(expiry_dates["dist_close"].mean())

    binom = stats.binomtest(n_wins, n_expiry, p=0.50, alternative="greater")
    p_binom = float(binom.pvalue)

    if win_rate > 0.60 and p_binom < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Price moves toward max pain on {win_rate:.1%} of expiry days "
            f"(n={n_expiry}, wins={n_wins}, p={p_binom:.4f}). "
            f"Mean dist: open={mean_dist_open:.2f} → close={mean_dist_close:.2f}"
        )
    elif win_rate <= 0.50 or p_binom > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No max-pain magnetism: win_rate={win_rate:.1%} "
            f"(n={n_expiry}, p={p_binom:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Win rate={win_rate:.1%} (n={n_expiry}, p={p_binom:.4f}) — "
            f"above 50% but not significant"
        )

    print(
        f"  H64: n_fridays={n_expiry}, wins={n_wins}, win_rate={win_rate:.1%}, "
        f"p={p_binom:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H64", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=n_expiry, rows_excluded=raw - n_expiry,
        exclusion_reason=excl_reason,
        n_observations=n_expiry, n_signals=n_expiry,
        metric_name="max_pain_approach_win_rate_expiry_fridays",
        metric_value=round(win_rate, 4),
        support_threshold=0.60, reject_threshold=0.50,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="strategy_win_rate",
        extra_metrics={
            "n_expiry_fridays":    n_expiry,
            "n_moved_toward":      n_wins,
            "win_rate":            round(win_rate, 4),
            "p_binomial_one_sided": round(p_binom, 4),
            "mean_dist_open":      round(mean_dist_open, 3),
            "mean_dist_close":     round(mean_dist_close, 3),
            "mean_improvement":    round(mean_dist_open - mean_dist_close, 3),
            "filter_note":         "Fridays only (dayofweek==4). QQQ has 0DTE every day; Friday filter required.",
        },
    )


# ── H65: Overnight Wall Shifts → Next-Session Direction ──────────────────────────

def run_h65(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When both call_wall and put_wall shift up overnight, next-session
    return is positive more often than when both shift down.

    Signal: call_wall_shift > 0 AND put_wall_shift > 0 (both walls moved up)
    Control: call_wall_shift < 0 AND put_wall_shift < 0 (both walls moved down)
    Outcome: next-session log_return
    Primary metric: mean_return_both_up - mean_return_both_down
    """
    raw = len(walls)
    excl_reason = "Requires consecutive-date wall calculations; 1-day forward shift for next return"

    work = walls.dropna(subset=["call_wall_shift", "put_wall_shift"]).copy()
    work = work.merge(daily[["date", "log_return"]], on="date", how="inner")
    work["next_return"] = work["log_return"].shift(-1)
    work = work.dropna(subset=["log_return", "next_return", "call_wall_shift", "put_wall_shift"])
    excluded = raw - len(work)

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H65", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="mean_return_diff_both_walls_up_vs_down",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(work)}",
            data_notes="directly_tested",
        )

    both_up   = (work["call_wall_shift"] > 0) & (work["put_wall_shift"] > 0)
    both_down = (work["call_wall_shift"] < 0) & (work["put_wall_shift"] < 0)

    up_vals   = work["next_return"][both_up].values
    down_vals = work["next_return"][both_down].values

    n_up   = len(up_vals)
    n_down = len(down_vals)

    if n_up < 5 or n_down < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H65", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=n_up,
            metric_name="mean_return_diff_both_walls_up_vs_down",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few both-up ({n_up}) or both-down ({n_down}) days",
            data_notes="directly_tested",
        )

    mean_up   = float(np.mean(up_vals))
    mean_down = float(np.mean(down_vals))
    diff = mean_up - mean_down

    U_stat, p_mw = stats.mannwhitneyu(up_vals, down_vals, alternative="greater")
    cd = _cliffs_delta(up_vals, down_vals)

    # Win rate: fraction of both-up days with positive next return
    wr_up   = float((up_vals > 0).mean())
    wr_down = float((down_vals > 0).mean())

    pct_both_up   = float(both_up.mean())
    pct_both_down = float(both_down.mean())

    if diff > 0.001 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Both-walls-up days show higher next-session returns: "
            f"mean_up={mean_up:.5f} vs mean_down={mean_down:.5f} "
            f"(diff={diff:.5f}, p={p_mw:.4f}, Cliff's d={cd:.3f}). "
            f"Win rates: up={wr_up:.1%} down={wr_down:.1%}"
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"Wall shifts have no directional predictive value: "
            f"mean_up={mean_up:.5f} vs mean_down={mean_down:.5f} (diff={diff:.5f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.5f}) but not significant "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(
        f"  H65: n_up={n_up} ({pct_both_up:.1%}), n_down={n_down} ({pct_both_down:.1%}), "
        f"diff={diff:.5f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H65", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_up,
        metric_name="mean_return_diff_both_walls_up_vs_down",
        metric_value=round(diff, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="mean_difference",
        extra_metrics={
            "n_both_walls_up":     n_up,
            "n_both_walls_down":   n_down,
            "pct_both_up":         round(pct_both_up, 3),
            "pct_both_down":       round(pct_both_down, 3),
            "mean_return_both_up": round(mean_up, 6),
            "mean_return_both_down": round(mean_down, 6),
            "win_rate_both_up":    round(wr_up, 3),
            "win_rate_both_down":  round(wr_down, 3),
            "cliffs_delta":        round(cd, 4),
            "p_mannwhitney":       round(p_mw, 4),
            "u_stat":              round(float(U_stat), 2),
        },
    )


# ── H66: Call Wall Resistance — Upper Shadow Ratio ───────────────────────────────

def run_h66(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Sessions where the intraday high reaches within $5 of call_wall show a
    larger upper shadow ratio (high-close)/(high-low) than sessions where high stays
    $10+ below the wall.

    Normalization rationale: raw (high-close)/close conflates wall effect with
    move-size mean-reversion. Shadow ratio expresses give-back as fraction of the
    day's total range, independent of whether the session was a large or small move.

    Exclusion: sessions with range < 0.3% of close (near-flat days, division artefact).

    Mirror test: symmetric put_wall lower-shadow ratio reported in extra_metrics only.
    """
    raw = len(walls)
    excl_reason = "Requires valid call_wall and put_wall; OHLC from daily_series; range >= 0.3% of close"

    work = walls.dropna(subset=["call_wall", "put_wall"]).copy()
    work = work.merge(daily[["date", "open", "high", "low", "close"]], on="date", how="inner")
    work = work.dropna(subset=["high", "low", "close", "call_wall"])

    # Drop near-flat sessions to avoid division artefacts
    work["range_abs"] = work["high"] - work["low"]
    work = work[work["range_abs"] >= 0.003 * work["close"]].copy()
    excluded = raw - len(work)

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H66", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_upper_shadow_ratio_diff_near_vs_far_wall",
            metric_value=float("nan"), support_threshold=0.05, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid sessions after range filter: {len(work)}",
            data_notes="directly_tested",
        )

    dist_high_to_call = work["call_wall"] - work["high"]   # positive = high below wall

    near_wall = (dist_high_to_call >= 0) & (dist_high_to_call < 5)
    far_wall  = dist_high_to_call > 10

    # Upper shadow ratio
    work["upper_shadow_ratio"] = (work["high"] - work["close"]) / work["range_abs"]

    near_vals = work["upper_shadow_ratio"][near_wall].values
    far_vals  = work["upper_shadow_ratio"][far_wall].values

    n_near = len(near_vals)
    n_far  = len(far_vals)
    pct_near = float(near_wall.mean())

    # Mirror: put wall lower shadow ratio
    dist_low_to_put = work["low"] - work["put_wall"]   # positive = low above put wall
    near_put = (dist_low_to_put >= 0) & (dist_low_to_put < 5)
    work["lower_shadow_ratio"] = (work["close"] - work["low"]) / work["range_abs"]
    put_near_vals = work["lower_shadow_ratio"][near_put].values
    put_far_vals  = work["lower_shadow_ratio"][dist_low_to_put > 10].values

    if n_near < 10 or n_far < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H66", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=n_near,
            metric_name="median_upper_shadow_ratio_diff_near_vs_far_wall",
            metric_value=float("nan"), support_threshold=0.05, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few near-wall ({n_near}) or far-wall ({n_far}) sessions (need ≥ 10 each)",
            data_notes="directly_tested",
        )

    med_near = float(np.median(near_vals))
    med_far  = float(np.median(far_vals))
    diff = med_near - med_far

    _, p_mw = stats.mannwhitneyu(near_vals, far_vals, alternative="greater")
    cd = _cliffs_delta(near_vals, far_vals)

    # Raw absolute giveback (transparency)
    abs_giveback_near = float(np.median((work["high"] - work["close"])[near_wall] / work["close"][near_wall]))
    abs_giveback_far  = float(np.median((work["high"] - work["close"])[far_wall]  / work["close"][far_wall]))

    # Mirror put wall
    med_put_near = float(np.median(put_near_vals)) if len(put_near_vals) >= 5 else float("nan")
    med_put_far  = float(np.median(put_far_vals))  if len(put_far_vals)  >= 5 else float("nan")

    if diff > 0.05 and p_mw < 0.10 and abs(cd) >= 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Call wall resistance confirmed: near-wall sessions show higher upper shadow ratio "
            f"{med_near:.3f} vs {med_far:.3f} (diff={diff:.3f}, p_mw={p_mw:.4f} one-sided, "
            f"Cliff's d={cd:.3f}). n_near={n_near}, n_far={n_far}."
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No resistance ceiling: upper shadow ratio near-wall={med_near:.3f} vs "
            f"far-wall={med_far:.3f} (diff={diff:.3f}, p_mw={p_mw:.4f} one-sided). "
            f"n_near={n_near}, n_far={n_far}."
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.3f}) but not significant "
            f"(p_mw={p_mw:.4f}, Cliff's d={cd:.3f}). n_near={n_near}, n_far={n_far}."
        )

    print(
        f"  H66: n_near={n_near} ({pct_near:.1%}), n_far={n_far}, "
        f"shadow_near={med_near:.3f}, shadow_far={med_far:.3f}, "
        f"diff={diff:.3f}, p={p_mw:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H66", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_near,
        metric_name="median_upper_shadow_ratio_diff_near_vs_far_wall",
        metric_value=round(diff, 4),
        support_threshold=0.05, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="mean_difference",
        extra_metrics={
            "n_near_call_wall":            n_near,
            "n_far_call_wall":             n_far,
            "pct_near_wall_days":          round(pct_near, 3),
            "median_shadow_ratio_near":    round(med_near, 4),
            "median_shadow_ratio_far":     round(med_far, 4),
            "p_mannwhitney_one_sided":     round(p_mw, 4),
            "cliffs_delta":                round(cd, 4),
            "median_abs_giveback_near":    round(abs_giveback_near, 4),
            "median_abs_giveback_far":     round(abs_giveback_far, 4),
            "mirror_put_shadow_near":      round(med_put_near, 4) if not np.isnan(med_put_near) else None,
            "mirror_put_shadow_far":       round(med_put_far, 4)  if not np.isnan(med_put_far)  else None,
            "n_near_put_wall":             len(put_near_vals),
        },
    )


# ── H67: High OI Suppresses Daily Range (Exploratory) ────────────────────────────

def run_h67(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Top-quintile total OI days (dte>0 only) show lower daily range than
    bottom-quintile days. Confidence prior: LOW — confounds flagged explicitly.

    Confound: high OI may co-occur with volatile regimes (OI builds during uncertainty).
    Mitigation: exclude dte=0 contracts from OI calculation (0DTE created and expires
    same day, most correlated with contemporaneous vol). Does not fully resolve confound.
    """
    raw = len(walls)
    excl_reason = (
        "Requires total_oi (dte>0) from param files and OHLC from daily_series. "
        "EXPLORATORY — result may reflect regime co-variation, not dealer gamma causation."
    )

    # Recompute oi_dte_gt1 from param files
    chains_dir = CHAINS_DIR
    c_files = {f.name.split("_")[4]: f for f in chains_dir.glob("qqq_opts_by_param_*_C.parquet")}
    p_files = {f.name.split("_")[4]: f for f in chains_dir.glob("qqq_opts_by_param_*_P.parquet")}
    overlap = sorted(set(c_files.keys()) & set(p_files.keys()))

    oi_rows = []
    for d_str in overlap:
        try:
            c = pd.read_parquet(c_files[d_str])
            p = pd.read_parquet(p_files[d_str])
            date = pd.Timestamp(f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}")
            oi_dte_gt1 = (
                int(c[c["dte"] > 0]["openinterest"].sum()) +
                int(p[p["dte"] > 0]["openinterest"].sum())
            )
            oi_total = int(c["openinterest"].sum()) + int(p["openinterest"].sum())
            oi_rows.append({"date": date, "oi_dte_gt1": oi_dte_gt1, "oi_total": oi_total})
        except Exception:
            continue

    oi_df = pd.DataFrame(oi_rows).sort_values("date").reset_index(drop=True)

    work = oi_df.merge(daily[["date", "high", "low", "close"]], on="date", how="inner")
    work = work.dropna(subset=["high", "low", "close", "oi_dte_gt1"])
    work["daily_range"] = (work["high"] - work["low"]) / work["close"]
    excluded = raw - len(work)

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H67", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_range_diff_high_oi_vs_low_oi",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(work)}",
            data_notes="directly_tested",
        )

    q80 = work["oi_dte_gt1"].quantile(0.80)
    q20 = work["oi_dte_gt1"].quantile(0.20)
    top_oi  = work["daily_range"][work["oi_dte_gt1"] >= q80].values
    bot_oi  = work["daily_range"][work["oi_dte_gt1"] <= q20].values
    n_top, n_bot = len(top_oi), len(bot_oi)

    med_top = float(np.median(top_oi))
    med_bot = float(np.median(bot_oi))
    diff = med_top - med_bot   # expected negative

    _, p_mw = stats.mannwhitneyu(top_oi, bot_oi, alternative="less")
    cd = _cliffs_delta(top_oi, bot_oi)

    # Total OI version for comparison
    q80t = work["oi_total"].quantile(0.80)
    q20t = work["oi_total"].quantile(0.20)
    top_t = work["daily_range"][work["oi_total"] >= q80t].values
    bot_t = work["daily_range"][work["oi_total"] <= q20t].values
    med_top_t = float(np.median(top_t)) if len(top_t) >= 5 else float("nan")
    med_bot_t = float(np.median(bot_t)) if len(bot_t) >= 5 else float("nan")

    confound_note = (
        "EXPLORATORY: High OI may co-occur with volatile regimes rather than causing "
        "suppression. Excluding dte=0 OI reduces but does not eliminate this confound. "
        "Total-OI version also reported for comparison."
    )

    if diff < -0.001 and p_mw < 0.10 and abs(cd) >= 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"High-OI sessions show lower range: {med_top:.4f} vs {med_bot:.4f} "
            f"(diff={diff:.4f}, p_mw={p_mw:.4f} one-sided, Cliff's d={cd:.3f}). "
            f"n_top={n_top}, n_bot={n_bot}. {confound_note}"
        )
    elif diff >= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No OI-range suppression: high-OI range={med_top:.4f} vs low-OI={med_bot:.4f} "
            f"(diff={diff:.4f}, p_mw={p_mw:.4f} one-sided). {confound_note}"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.4f}) but not significant "
            f"(p_mw={p_mw:.4f}, Cliff's d={cd:.3f}). {confound_note}"
        )

    print(
        f"  H67: n_top={n_top}, n_bot={n_bot}, "
        f"range_top={med_top:.4f}, range_bot={med_bot:.4f}, "
        f"diff={diff:.4f}, p={p_mw:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H67", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_top,
        metric_name="median_range_diff_high_oi_vs_low_oi",
        metric_value=round(diff, 6),
        support_threshold=-0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="regime_comparison",
        extra_metrics={
            "n_top_oi_quintile":      n_top,
            "n_bot_oi_quintile":      n_bot,
            "oi_dte_gt1_q80":         round(q80, 0),
            "oi_dte_gt1_q20":         round(q20, 0),
            "median_range_high_oi":   round(med_top, 5),
            "median_range_low_oi":    round(med_bot, 5),
            "p_mannwhitney_one_sided": round(p_mw, 4),
            "cliffs_delta":           round(cd, 4),
            "total_oi_version_diff":  round(med_top_t - med_bot_t, 5) if not (np.isnan(med_top_t) or np.isnan(med_bot_t)) else None,
            "exploratory":            True,
        },
    )


# ── H68: Expiry Pinning — Fridays vs Non-Fridays ─────────────────────────────────

def run_h68(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Fridays (daily 0DTE + weekly series expiring) show closer settlement
    to the nearest high-OI wall than Mon-Thu sessions, consistent with academic
    pinning at high-OI strikes on heavy-expiry dates.

    Note: QQQ has 0DTE every session — 'expiry vs non-expiry' is not a valid split.
    Friday/non-Friday is the meaningful expiry-weight comparison in this dataset.

    Also reports dte=0 OI quintile cut as a continuous secondary test.
    """
    raw = len(walls)
    excl_reason = "Requires call_wall and put_wall; close from daily_series"

    work = walls.dropna(subset=["call_wall", "put_wall"]).copy()
    work = work.merge(daily[["date", "close"]], on="date", how="inner")
    work = work.dropna(subset=["close", "call_wall", "put_wall"])
    excluded = raw - len(work)

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H68", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_dist_to_nearest_wall_friday_vs_non_friday",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(work)}",
            data_notes="directly_tested",
        )

    # Normalized distance to nearest wall
    work["dist_call"] = (work["close"] - work["call_wall"]).abs()
    work["dist_put"]  = (work["close"] - work["put_wall"]).abs()
    work["dist_nearest"] = work[["dist_call", "dist_put"]].min(axis=1) / work["close"]

    is_friday = work["date"].dt.dayofweek == 4
    fri_vals  = work["dist_nearest"][is_friday].values
    nfri_vals = work["dist_nearest"][~is_friday].values

    n_fri  = len(fri_vals)
    n_nfri = len(nfri_vals)

    med_fri  = float(np.median(fri_vals))
    med_nfri = float(np.median(nfri_vals))
    diff = med_fri - med_nfri   # expected negative (Fridays closer)

    _, p_mw = stats.mannwhitneyu(fri_vals, nfri_vals, alternative="less")
    cd = _cliffs_delta(fri_vals, nfri_vals)

    # Within-$3 pinning rate
    pct_within_3_fri  = float((work["dist_nearest"][is_friday]  * work["close"][is_friday]  < 3).mean())
    pct_within_3_nfri = float((work["dist_nearest"][~is_friday] * work["close"][~is_friday] < 3).mean())

    # OI quintile secondary cut: dte=0 total OI
    oi_dte0 = walls["total_oi"] - walls.get("oi_dte_gt1", pd.Series(dtype=float))
    oi0_q80 = work["total_oi"].quantile(0.80) if "total_oi" in work.columns else None

    caveats = (
        "Note: QQQ has 0DTE options every session — Friday vs non-Friday is the expiry-weight "
        "comparison (Fridays carry daily + weekly series). Walls average $36 wide; "
        "normalized dist is relative to underlying price (~$573 mean close)."
    )

    if diff < -0.001 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Fridays settle closer to nearest wall: {med_fri:.4f} vs {med_nfri:.4f} "
            f"(diff={diff:.4f}, p_mw={p_mw:.4f} one-sided, Cliff's d={cd:.3f}). "
            f"n_fri={n_fri}, n_nfri={n_nfri}. {caveats}"
        )
    elif diff >= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No Friday pinning: dist_fri={med_fri:.4f} vs dist_nfri={med_nfri:.4f} "
            f"(diff={diff:.4f}, p_mw={p_mw:.4f} one-sided). {caveats}"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.4f}) but not significant "
            f"(p_mw={p_mw:.4f}, Cliff's d={cd:.3f}). {caveats}"
        )

    print(
        f"  H68: n_fri={n_fri}, n_nfri={n_nfri}, "
        f"dist_fri={med_fri:.4f}, dist_nfri={med_nfri:.4f}, "
        f"diff={diff:.4f}, p={p_mw:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H68", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_fri,
        metric_name="median_dist_to_nearest_wall_friday_vs_non_friday",
        metric_value=round(diff, 5),
        support_threshold=-0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="regime_comparison",
        extra_metrics={
            "n_fridays":              n_fri,
            "n_non_fridays":          n_nfri,
            "median_dist_normalized_fri":   round(med_fri, 5),
            "median_dist_normalized_nfri":  round(med_nfri, 5),
            "p_mannwhitney_one_sided":      round(p_mw, 4),
            "cliffs_delta":                 round(cd, 4),
            "pct_within_3pts_friday":       round(pct_within_3_fri, 3),
            "pct_within_3pts_non_friday":   round(pct_within_3_nfri, 3),
            "mean_wall_width":              round(float((work["call_wall"] - work["put_wall"]).mean()), 2),
            "note": "QQQ has 0DTE every session; Friday vs non-Friday is expiry-weight proxy",
        },
    )


# ── H69: Prior-Day Call/Put Volume → Next-Session Direction (Exploratory) ─────────

def run_h69(daily: pd.DataFrame, walls: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Prior-day call_frac (call_vol / total_vol) > 0.55 predicts positive
    next-session return. Exploratory — total EOD volume ≠ buyer-initiated imbalance.

    Confound: 0DTE put volume spikes on volatile sessions for same-day hedging.
    Put-heavy signal may reflect prior-day volatility, not bearish positioning.
    Same-day return reported as extra_metric (contemporaneous check).
    """
    raw = len(walls)
    excl_reason = "Requires daily call_vol and put_vol from param files; log_return from daily_series"

    chains_dir = CHAINS_DIR
    c_files = {f.name.split("_")[4]: f for f in chains_dir.glob("qqq_opts_by_param_*_C.parquet")}
    p_files = {f.name.split("_")[4]: f for f in chains_dir.glob("qqq_opts_by_param_*_P.parquet")}
    overlap = sorted(set(c_files.keys()) & set(p_files.keys()))

    vol_rows = []
    for d_str in overlap:
        try:
            c = pd.read_parquet(c_files[d_str])
            p = pd.read_parquet(p_files[d_str])
            date = pd.Timestamp(f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}")
            vol_rows.append({
                "date": date,
                "call_vol": int(c["volume"].sum()),
                "put_vol":  int(p["volume"].sum()),
            })
        except Exception:
            continue

    vol_df = pd.DataFrame(vol_rows).sort_values("date").reset_index(drop=True)
    vol_df["total_vol"] = vol_df["call_vol"] + vol_df["put_vol"]
    vol_df["call_frac"] = vol_df["call_vol"] / vol_df["total_vol"]

    work = vol_df.merge(daily[["date", "log_return"]], on="date", how="inner")
    work["next_return"]      = work["log_return"].shift(-1)
    work["same_day_return"]  = work["log_return"]
    work = work.dropna(subset=["call_frac", "next_return"])
    excluded = raw - len(work)

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H69", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="mean_next_return_diff_call_heavy_vs_put_heavy",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid dates: {len(work)}",
            data_notes="directly_tested",
        )

    call_heavy = work["call_frac"] > 0.55
    put_heavy  = work["call_frac"] < 0.45

    call_next = work["next_return"][call_heavy].values
    put_next  = work["next_return"][put_heavy].values
    n_call, n_put = len(call_next), len(put_next)

    if n_call < 5 or n_put < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H69", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=n_call,
            metric_name="mean_next_return_diff_call_heavy_vs_put_heavy",
            metric_value=float("nan"), support_threshold=0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few call-heavy ({n_call}) or put-heavy ({n_put}) sessions at 55/45 threshold",
            data_notes="directly_tested",
        )

    mean_call = float(np.mean(call_next))
    mean_put  = float(np.mean(put_next))
    diff = mean_call - mean_put

    _, p_mw = stats.mannwhitneyu(call_next, put_next, alternative="greater")
    cd = _cliffs_delta(call_next, put_next)

    mean_call_frac = float(work["call_frac"].mean())
    pct_call_heavy = float(call_heavy.mean())
    pct_put_heavy  = float(put_heavy.mean())

    # Contemporaneous check: does call_frac predict same-day return?
    call_same = work["same_day_return"][call_heavy].values
    put_same  = work["same_day_return"][put_heavy].values
    same_day_diff = float(np.mean(call_same) - np.mean(put_same)) if len(call_same) > 0 and len(put_same) > 0 else float("nan")

    confound_note = (
        "EXPLORATORY: total EOD volume is not buyer-initiated imbalance. "
        "0DTE put spikes on volatile sessions may make put-heavy = prior-day-volatile. "
        "Same-day return diff reported to check contemporaneous vs predictive signal."
    )

    # Loose thresholds (exploratory)
    if diff > 0.001 and p_mw < 0.15:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Call-heavy days predict positive next session: mean_call={mean_call:.5f} vs "
            f"mean_put={mean_put:.5f} (diff={diff:.5f}, p_mw={p_mw:.4f} one-sided, "
            f"Cliff's d={cd:.3f}). n_call={n_call}, n_put={n_put}. {confound_note}"
        )
    elif diff <= 0 or p_mw > 0.40:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No directional signal from call/put volume balance: "
            f"mean_call={mean_call:.5f} vs mean_put={mean_put:.5f} "
            f"(diff={diff:.5f}, p_mw={p_mw:.4f} one-sided). {confound_note}"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.5f}) but not significant at exploratory threshold "
            f"(p_mw={p_mw:.4f}, Cliff's d={cd:.3f}). {confound_note}"
        )

    print(
        f"  H69: n_call={n_call}, n_put={n_put}, mean_call_frac={mean_call_frac:.3f}, "
        f"diff={diff:.5f}, p={p_mw:.4f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H69", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_call,
        metric_name="mean_next_return_diff_call_heavy_vs_put_heavy",
        metric_value=round(diff, 6),
        support_threshold=0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="mean_difference",
        extra_metrics={
            "n_call_heavy":             n_call,
            "n_put_heavy":              n_put,
            "mean_call_frac_overall":   round(mean_call_frac, 3),
            "pct_call_heavy":           round(pct_call_heavy, 3),
            "pct_put_heavy":            round(pct_put_heavy, 3),
            "mean_next_return_call":    round(mean_call, 6),
            "mean_next_return_put":     round(mean_put, 6),
            "p_mannwhitney_one_sided":  round(p_mw, 4),
            "cliffs_delta":             round(cd, 4),
            "same_day_return_diff":     round(same_day_diff, 6) if not np.isnan(same_day_diff) else None,
            "exploratory":              True,
            "threshold_note":           "Support at p<0.15 (exploratory); total EOD vol ≠ buyer-initiated imbalance",
        },
    )


# ── Dispatch ──────────────────────────────────────────────────────────────────────

WALL_RUNNERS = {
    "H61": run_h61,
    "H62": run_h62,
    "H63": run_h63,
    "H64": run_h64,
    "H65": run_h65,
    "H66": run_h66,
    "H67": run_h67,
    "H68": run_h68,
    "H69": run_h69,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default="all")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    wanted = (
        list(WALL_RUNNERS.keys())
        if args.hypotheses.lower() == "all"
        else [h.strip().upper() for h in args.hypotheses.split(",")]
    )
    unknown = [h for h in wanted if h not in WALL_RUNNERS]
    if unknown:
        print(f"Unknown IDs: {unknown}. Available: {list(WALL_RUNNERS.keys())}")
        sys.exit(1)

    hyp_file = EXPERIMENTS_DIR / "hypotheses.json"
    all_hyps = json.loads(hyp_file.read_text())
    hyp_by_num = {f"H{i+1}": h for i, h in enumerate(all_hyps)}

    daily = _load_daily()
    print(f"Loaded daily_series: {len(daily)} rows")

    walls = _compute_walls(CHAINS_DIR)
    if walls.empty:
        raise SystemExit("No wall data built — check chains/ directory")

    existing = _load_existing_results()

    for hnum in wanted:
        if hnum in existing and not args.force:
            print(f"[skip] {hnum} already in backtest_results.json (use --force to re-run)")
            continue

        hyp = hyp_by_num.get(hnum)
        if hyp is None:
            raise SystemExit(f"{hnum} not found in hypotheses.json (has {len(all_hyps)} entries)")

        print(f"Running {hnum}: {hyp.get('title','')[:60]}...")
        result = WALL_RUNNERS[hnum](daily, walls, hyp)
        existing[hnum] = result.model_dump()
        print(f"  → {result.verdict.value}: {result.verdict_reason[:100]}")

    _save_results(existing)
    print(f"\nCompleted {len(wanted)} wall backtest(s).")
    print("Next: run scripts/17_score_and_report.py")


if __name__ == "__main__":
    main()
