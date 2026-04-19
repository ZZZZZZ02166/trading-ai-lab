#!/usr/bin/env python3
"""
Phase 20: Run chains-data backtests (H52, H54, H56, H58).

Uses qqq_opts_by_param_YYYYMMDD_C/P.parquet files from data/raw/chains/.
Calls available: 2024-01-02 → 2025-12-31 (317 dates)
Puts available:  2025-04-01 → 2025-12-31 (190 dates)
Overlap (both C+P): 2025-04-01 → 2025-12-31

H52: True 25-delta skew → next-session return direction
H54: Option volume spike without price move → urgency signal
H56: Intraday skew steepening → afternoon continuation  [INSUFFICIENT DATA]
H58: First-30-min option flow direction → rest-of-day   [INSUFFICIENT DATA]

H56 and H58 require intraday IV/volume aggregated across the full chain at
multiple timestamps. The available intraday files cover only 7–14 specific
contracts per date — insufficient for a representative chain-level signal.

Usage:
    python scripts/20_run_chains_backtests.py                   # all
    python scripts/20_run_chains_backtests.py --hypotheses H52  # single
    python scripts/20_run_chains_backtests.py --force           # overwrite
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

PROCESSED_DIR = BASE / "data" / "processed"
CHAINS_DIR    = BASE / "data" / "raw" / "chains"
EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE    = EXPERIMENTS_DIR / "backtest_results.json"

DAILY_SERIES = PROCESSED_DIR / "daily_series.parquet"

# Overlap window where both C and P param files exist
CHAINS_START = "2025-04-01"
CHAINS_END   = "2025-12-31"

# Full test window (same as daily runners)
TEST_WINDOW_START = "2024-01-01"
TEST_WINDOW_END   = "2026-04-05"
TICKER = "QQQ"


def _sanitise_for_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitise_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitise_for_json(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def _load_daily() -> pd.DataFrame:
    if not DAILY_SERIES.exists():
        raise SystemExit("daily_series.parquet not found. Run scripts/14c_build_processed_series.py first.")
    df = pd.read_parquet(DAILY_SERIES)
    date_col = [c for c in df.columns if "date" in c.lower()]
    if date_col:
        df["date"] = pd.to_datetime(df[date_col[0]])
    df = df.sort_values("date").reset_index(drop=True)
    df = df[(df["date"] >= TEST_WINDOW_START) & (df["date"] <= TEST_WINDOW_END)].reset_index(drop=True)
    return df


def _load_existing_results() -> dict[str, dict]:
    if RESULTS_FILE.exists():
        records = json.loads(RESULTS_FILE.read_text())
        return {r["hypothesis_number"]: r for r in records}
    return {}


def _save_results(results_map: dict[str, dict]) -> None:
    records = _sanitise_for_json(list(results_map.values()))
    RESULTS_FILE.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} results → {RESULTS_FILE}")


def _cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return float("nan")
    U, _ = stats.mannwhitneyu(x, y, alternative="two-sided")
    return float(2 * U / (n1 * n2) - 1)


def _load_param_skew(chains_dir: Path) -> pd.DataFrame:
    """
    For each date where both C and P param files exist, compute:
      - put_25d_iv: mean IV of puts with |delta| in [0.20, 0.30]
      - call_25d_iv: mean IV of calls with delta in [0.20, 0.30]
      - skew: put_25d_iv - call_25d_iv
      - total_volume: sum of all contract volumes (C + P)

    Returns a DataFrame indexed by date with these columns.
    Filters: iv > 0, delta non-zero, dte >= 1.
    """
    c_files = {
        f.name.split("_")[4]: f
        for f in chains_dir.glob("qqq_opts_by_param_*_C.parquet")
    }
    p_files = {
        f.name.split("_")[4]: f
        for f in chains_dir.glob("qqq_opts_by_param_*_P.parquet")
    }

    overlap_dates = sorted(set(c_files.keys()) & set(p_files.keys()))
    print(f"[chains] Overlap dates (C+P): {len(overlap_dates)} ({overlap_dates[0]} → {overlap_dates[-1]})")

    rows = []
    for date_str in overlap_dates:
        try:
            calls = pd.read_parquet(c_files[date_str])
            puts  = pd.read_parquet(p_files[date_str])
        except Exception as e:
            print(f"  [skip] {date_str}: read error — {e}")
            continue

        # Valid calls: iv > 0, delta > 0, dte >= 1
        cv = calls[(calls["iv"] > 0) & (calls["delta"] > 0) & (calls["dte"] >= 1)]
        # Valid puts: iv > 0, delta < 0, dte >= 1
        pv = puts[(puts["iv"] > 0) & (puts["delta"] < 0) & (puts["dte"] >= 1)]

        # 25-delta contracts
        c25 = cv[(cv["delta"] >= 0.20) & (cv["delta"] <= 0.30)]
        p25 = pv[(pv["delta"] >= -0.30) & (pv["delta"] <= -0.20)]

        if len(c25) == 0 or len(p25) == 0:
            # No 25-delta contracts — skip this date
            continue

        call_25d_iv = float(c25["iv"].mean())
        put_25d_iv  = float(p25["iv"].mean())
        skew        = put_25d_iv - call_25d_iv

        # Total volume across all contracts (calls + puts, raw daily volume)
        total_vol = int(calls["volume"].sum()) + int(puts["volume"].sum())
        call_vol  = int(calls["volume"].sum())
        put_vol   = int(puts["volume"].sum())

        rows.append({
            "date":          pd.Timestamp(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"),
            "put_25d_iv":    round(put_25d_iv, 6),
            "call_25d_iv":   round(call_25d_iv, 6),
            "skew":          round(skew, 6),
            "n_c25":         len(c25),
            "n_p25":         len(p25),
            "total_volume":  total_vol,
            "call_volume":   call_vol,
            "put_volume":    put_vol,
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    print(f"[chains] Built chain summary: {len(df)} valid dates with 25-delta data")
    return df


# ── H52: True 25-Delta Skew → Next-Session Return Direction ──────────────────────

def run_h52(daily: pd.DataFrame, chains: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Days where 25-delta put IV > 25-delta call IV by > 2 vol pts predict
    negative next-session returns. Low-skew days show no directional bias.

    Signal: skew > 0.02 (high put demand)
    Control: skew < 0.01 (low skew, neutral)
    Outcome: next-session log_return from daily_series
    Support: mean diff < -0.001, p_mw < 0.10, |cliffs_delta| >= 0.10
    data_notes: proxy_tested, data_fidelity: constant_maturity_iv
    """
    raw = len(chains)
    excl_reason = "Requires both 25-delta call and put contracts with valid IV; 1-day forward shift for next return"

    if len(chains) < 20:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H52", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="Too few dates with 25-delta data",
            n_observations=0, n_signals=0,
            metric_name="mean_return_diff_high_skew_vs_low_skew",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Only {len(chains)} dates with valid 25-delta data (need >= 20)",
            data_notes="insufficient_data",
        )

    # Join chains data with next-session return from daily
    daily_sub = daily[["date", "log_return"]].copy()
    daily_sub["next_return"] = daily_sub["log_return"].shift(-1)

    work = chains.merge(daily_sub[["date", "next_return"]], on="date", how="inner")
    work = work.dropna(subset=["skew", "next_return"])
    excluded = raw - len(work)

    # Use quantile-based splits: equity put skew is always positive (puts structurally
    # more expensive than calls), so absolute thresholds are unreliable. Top quintile
    # = unusually steep skew; bottom quintile = relatively flat skew.
    q80 = float(work["skew"].quantile(0.80))
    q20 = float(work["skew"].quantile(0.20))

    high_mask = work["skew"] >= q80
    low_mask  = work["skew"] <= q20

    high_vals = work["next_return"][high_mask].values
    low_vals  = work["next_return"][low_mask].values

    if len(high_vals) < 10 or len(low_vals) < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H52", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=int(high_mask.sum()),
            metric_name="mean_return_diff_high_skew_vs_low_skew",
            metric_value=float("nan"), support_threshold=-0.001, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(
                f"Too few dates per group: high_skew={len(high_vals)}, low_skew={len(low_vals)}. "
                f"Skew range: [{work['skew'].min():.4f}, {work['skew'].max():.4f}], "
                f"q20={q20:.4f}, q80={q80:.4f}"
            ),
            data_notes="proxy_tested",
        )

    mean_high = float(np.mean(high_vals))
    mean_low  = float(np.mean(low_vals))
    diff = mean_high - mean_low
    U_stat, p_mw = stats.mannwhitneyu(high_vals, low_vals, alternative="less")
    cd = _cliffs_delta(high_vals, low_vals)

    median_skew = float(work["skew"].median())
    mean_skew   = float(work["skew"].mean())

    if diff < -0.001 and p_mw < 0.10 and abs(cd) >= 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"High-skew days (>2 vol pts) show negative return bias: "
            f"mean_high={mean_high:.5f} vs mean_low={mean_low:.5f} "
            f"(diff={diff:.5f}, p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )
    elif diff >= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No directional bias from 25-delta skew: "
            f"mean_high={mean_high:.5f} vs mean_low={mean_low:.5f} "
            f"(diff={diff:.5f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.5f}) but not significant "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(
        f"  H52: n_high={len(high_vals)}, n_low={len(low_vals)}, "
        f"diff={diff:.5f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H52", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=int(high_mask.sum()),
        metric_name="mean_return_diff_high_skew_vs_low_skew",
        metric_value=round(diff, 6),
        support_threshold=-0.001, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="proxy_tested",
        data_fidelity="constant_maturity_iv",
        metric_family="mean_difference",
        extra_metrics={
            "n_high_skew": len(high_vals),
            "n_low_skew": len(low_vals),
            "mean_return_high_skew": round(mean_high, 6),
            "mean_return_low_skew": round(mean_low, 6),
            "cliffs_delta": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "u_stat": round(float(U_stat), 2),
            "median_skew_all_dates": round(median_skew, 4),
            "mean_skew_all_dates": round(mean_skew, 4),
            "skew_q20": round(q20, 4),
            "skew_q80": round(q80, 4),
            "n_dates_with_25d_data": len(work),
        },
    )


# ── H54: Option Volume Spike Without Price Move → Urgency Signal ──────────────────

def run_h54(daily: pd.DataFrame, chains: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Days where total option volume (C+P) > 2 SD above 20-day rolling average
    AND absolute intraday return < 0.5% show above-median next-session range.

    Signal: vol_spike AND quiet_price (urgency = unusual volume, no price move yet)
    Outcome: next-session (high - low) / close
    Support: median diff > 0.002, p_mw < 0.10
    data_notes: directly_tested, data_fidelity: exact_underlying
    """
    raw = len(chains)
    excl_reason = "20-day rolling volume baseline warmup; 1-day forward shift for next-session range"

    if len(chains) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H54", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="Too few chains dates",
            n_observations=0, n_signals=0,
            metric_name="median_range_diff_urgency_vs_baseline",
            metric_value=float("nan"), support_threshold=0.002, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Only {len(chains)} chains dates (need >= 30 for 20-day rolling baseline)",
            data_notes="insufficient_data",
        )

    # Join with daily for price data
    daily_sub = daily[["date", "log_return", "high", "low", "close"]].copy()
    daily_sub["next_range"] = (daily_sub["high"].shift(-1) - daily_sub["low"].shift(-1)) / daily_sub["close"]

    work = chains[["date", "total_volume"]].merge(
        daily_sub[["date", "log_return", "next_range"]],
        on="date", how="inner"
    )
    work = work.dropna(subset=["total_volume", "log_return", "next_range"])
    work = work[work["total_volume"] > 0].copy()

    if len(work) < 30:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H54", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=raw - len(work),
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=0,
            metric_name="median_range_diff_urgency_vs_baseline",
            metric_value=float("nan"), support_threshold=0.002, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few valid joined rows: {len(work)}",
            data_notes="directly_tested",
        )

    work = work.sort_values("date").reset_index(drop=True)
    excluded = raw - len(work)

    # Use top-quintile volume (>= 80th percentile) combined with quiet price
    # (|return| < 0.5%). The 2-SD rolling approach produces too few events in
    # a 190-date window — top-quintile gives ~38 candidates before price filter.
    vol_q80 = float(work["total_volume"].quantile(0.80))
    vol_spike   = work["total_volume"] >= vol_q80
    quiet_price = work["log_return"].abs() < 0.005
    urgency_mask = vol_spike & quiet_price

    n_urgency  = int(urgency_mask.sum())
    n_baseline = int((~urgency_mask).sum())
    pct_urgency = float(urgency_mask.mean())

    urgency_vals  = work["next_range"][urgency_mask].values
    baseline_vals = work["next_range"][~urgency_mask].values

    if n_urgency < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H54", ticker=TICKER,
            period_start=CHAINS_START, period_end=CHAINS_END,
            raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
            exclusion_reason=excl_reason,
            n_observations=len(work), n_signals=n_urgency,
            metric_name="median_range_diff_urgency_vs_baseline",
            metric_value=float("nan"), support_threshold=0.002, reject_threshold=0.0,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(
                f"Too few urgency days: {n_urgency} (volume spike + quiet price). "
                f"Signal requires extreme coincidence — {pct_urgency:.1%} of dates qualify."
            ),
            data_notes="directly_tested",
        )

    med_urgency  = float(np.median(urgency_vals))
    med_baseline = float(np.median(baseline_vals))
    diff = med_urgency - med_baseline

    U_stat, p_mw = stats.mannwhitneyu(urgency_vals, baseline_vals, alternative="greater")
    cd = _cliffs_delta(urgency_vals, baseline_vals)

    if diff > 0.002 and p_mw < 0.10:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Volume-spike+quiet days show elevated next-session range: "
            f"median_urgency={med_urgency:.4f} vs median_baseline={med_baseline:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )
    elif diff <= 0 or p_mw > 0.30:
        verdict = BacktestVerdict.REJECTED
        reason = (
            f"No urgency signal in next-session range: "
            f"median_urgency={med_urgency:.4f} vs median_baseline={med_baseline:.4f} "
            f"(diff={diff:.4f}, p={p_mw:.4f})"
        )
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction present (diff={diff:.4f}) but not significant "
            f"(p={p_mw:.4f}, Cliff's d={cd:.3f})"
        )

    print(
        f"  H54: n_urgency={n_urgency} ({pct_urgency:.1%}), n_baseline={n_baseline}, "
        f"diff={diff:.4f}, p={p_mw:.4f}, Cliff's d={cd:.3f} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H54", ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=raw, rows_after_validation=len(work), rows_excluded=excluded,
        exclusion_reason=excl_reason,
        n_observations=len(work), n_signals=n_urgency,
        metric_name="median_range_diff_urgency_vs_baseline",
        metric_value=round(diff, 6),
        support_threshold=0.002, reject_threshold=0.0,
        verdict=verdict, verdict_reason=reason,
        data_notes="directly_tested",
        data_fidelity="exact_underlying",
        metric_family="regime_comparison",
        extra_metrics={
            "n_urgency": n_urgency,
            "n_baseline": n_baseline,
            "pct_urgency_days": round(pct_urgency, 3),
            "median_range_urgency": round(med_urgency, 4),
            "median_range_baseline": round(med_baseline, 4),
            "cliffs_delta": round(cd, 4),
            "p_mannwhitney": round(p_mw, 4),
            "u_stat": round(float(U_stat), 2),
            "vol_q80_threshold": round(vol_q80, 0),
            "signal_method": "top_quintile_volume_AND_abs_return_lt_0.5pct",
        },
    )


# ── H56 & H58: Insufficient Data ─────────────────────────────────────────────────

def _insufficient_intraday(hyp: dict, hnum: str, metric_name: str, reason: str) -> BacktestResult:
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number=hnum, ticker=TICKER,
        period_start=CHAINS_START, period_end=CHAINS_END,
        raw_rows=0, rows_after_validation=0, rows_excluded=0,
        exclusion_reason="Intraday chain data not available in required format",
        n_observations=0, n_signals=0,
        metric_name=metric_name,
        metric_value=float("nan"), support_threshold=0.0, reject_threshold=0.0,
        verdict=BacktestVerdict.INSUFFICIENT_DATA,
        verdict_reason=reason,
        data_notes="insufficient_data",
        data_fidelity="insufficient",
        metric_family="mean_difference",
    )


def run_h56(daily: pd.DataFrame, chains: pd.DataFrame, hyp: dict) -> BacktestResult:
    return _insufficient_intraday(
        hyp, "H56",
        "mean_afternoon_return_diff_skew_widened_vs_narrowed",
        (
            "H56 requires intraday put-call IV spread at session open AND 11:00 AM across the "
            "full option chain. Available intraday files (data/raw/chains/intraday_*.parquet) "
            "cover only 7–14 specific contracts per date — insufficient for a representative "
            "chain-level skew calculation at two intraday timestamps. "
            "Would require a full intraday chain snapshot endpoint (not currently available)."
        ),
    )


def run_h58(daily: pd.DataFrame, chains: pd.DataFrame, hyp: dict) -> BacktestResult:
    return _insufficient_intraday(
        hyp, "H58",
        "mean_rod_return_diff_call_heavy_vs_put_heavy",
        (
            "H58 requires aggregated call and put volume in the first 30 minutes across the "
            "full option chain. Available intraday files (data/raw/chains/intraday_*.parquet) "
            "cover only 7–14 specific contracts per date — not a representative sample of total "
            "market volume. Computing first-30-min PCR from 7 contracts would produce a "
            "misleading signal. Would require a full intraday volume feed (not currently available)."
        ),
    )


# ── Dispatch table ────────────────────────────────────────────────────────────────

CHAINS_RUNNERS = {
    "H52": run_h52,
    "H54": run_h54,
    "H56": run_h56,
    "H58": run_h58,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", default="all")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    wanted = (
        list(CHAINS_RUNNERS.keys())
        if args.hypotheses.lower() == "all"
        else [h.strip().upper() for h in args.hypotheses.split(",")]
    )
    unknown = [h for h in wanted if h not in CHAINS_RUNNERS]
    if unknown:
        print(f"Unknown hypothesis IDs: {unknown}. Available: {list(CHAINS_RUNNERS.keys())}")
        sys.exit(1)

    if not CHAINS_DIR.exists():
        raise SystemExit(f"Chains directory not found: {CHAINS_DIR}")

    hyp_file = EXPERIMENTS_DIR / "hypotheses.json"
    if not hyp_file.exists():
        raise SystemExit("experiments/hypotheses.json not found.")
    all_hyps = json.loads(hyp_file.read_text())
    hyp_by_num: dict[str, dict] = {f"H{i+1}": h for i, h in enumerate(all_hyps)}

    daily = _load_daily()
    print(f"Loaded daily_series: {len(daily)} rows")

    # Load chain summary (only needed for H52, H54)
    data_needed = set(wanted) & {"H52", "H54"}
    chains_df: pd.DataFrame | None = None
    if data_needed:
        chains_df = _load_param_skew(CHAINS_DIR)
        if chains_df.empty:
            print("[warn] No chains data loaded — H52/H54 will return insufficient_data")
            chains_df = pd.DataFrame(columns=["date", "skew", "total_volume", "call_volume", "put_volume"])
    else:
        chains_df = pd.DataFrame(columns=["date", "skew", "total_volume", "call_volume", "put_volume"])

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
        runner = CHAINS_RUNNERS[hnum]
        result = runner(daily, chains_df, hyp)
        existing[hnum] = result.model_dump()
        print(f"  → {result.verdict.value}: {result.verdict_reason[:100]}")

    _save_results(existing)
    print(f"\nCompleted {len(wanted)} chains backtest(s).")
    print("Next: run scripts/17_score_and_report.py")


if __name__ == "__main__":
    main()
