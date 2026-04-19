#!/usr/bin/env python3
"""
Phase 16: Run intraday-frequency backtests (H13–H26).

Pilot: run H13 and H16 only.
  H13 — U-Shape IV Intraday  (requires intraday_series.parquet)
  H16 — Macro Release Vol Crush  (uses daily IVX + FOMC calendar)

After pilot passes, run all of H13–H26.

Usage:
    python scripts/16_run_intraday_backtests.py                        # all intraday
    python scripts/16_run_intraday_backtests.py --hypotheses H13,H16   # pilot
    python scripts/16_run_intraday_backtests.py --force
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import numpy as np
import pandas as pd
from scipy import stats  # type: ignore

from scipy.stats import spearmanr  # type: ignore

from app.models.backtest_result import BacktestResult, BacktestVerdict, TradeRecord
from app.services.calendar import get_fomc_dates
from app.services.databento_price_client import DatabentoPriceClient
from app.services.intraday_atm_selector import build_ladder, get_atm_snapshot, get_ladder_time_series

PROCESSED_DIR = BASE / "data" / "processed"
EXPERIMENTS_DIR = BASE / "experiments"
RESULTS_FILE = EXPERIMENTS_DIR / "backtest_results.json"

DAILY_SERIES = PROCESSED_DIR / "daily_series.parquet"
INTRADAY_SERIES = PROCESSED_DIR / "intraday_series.parquet"
MONTHLY_DIR = EXPERIMENTS_DIR / "intraday_monthly"
MONTHLY_DIR.mkdir(parents=True, exist_ok=True)

# ── Window constants ─────────────────────────────────────────────────────────
# EOD-only hypotheses (H16, H24): full 2024-2026 range.
EOD_WINDOW_START   = "2024-01-01"
EOD_WINDOW_END     = "2026-04-01"

# Intraday hypotheses (H13, H14, H19, H20, H21, H22, H25): Apr–Dec 2025, monthly batches.
INTRADAY_WINDOW_START = "2025-04-01"
INTRADAY_WINDOW_END   = "2025-12-31"

# Legacy alias used by EOD runners and daily_series filter.
TEST_WINDOW_START = EOD_WINDOW_START
TEST_WINDOW_END   = EOD_WINDOW_END

MONTHLY_BATCHES: dict[str, tuple[str, str]] = {
    "M1": ("2025-04-01", "2025-04-30"),
    "M2": ("2025-05-01", "2025-05-31"),
    "M3": ("2025-06-01", "2025-06-30"),
    "M4": ("2025-07-01", "2025-07-31"),
    "M5": ("2025-08-01", "2025-08-31"),
    "M6": ("2025-09-01", "2025-09-30"),
    "M7": ("2025-10-01", "2025-10-31"),
    "M8": ("2025-11-01", "2025-11-30"),
    "M9": ("2025-12-01", "2025-12-31"),
}

TICKER = "QQQ"

# Run-time window — set by main() via --start-date/--end-date or --month.
# All intraday runners iterate _RUN_START → _RUN_END.
_RUN_START: str       = INTRADAY_WINDOW_START
_RUN_END:   str       = INTRADAY_WINDOW_END
_RUN_MONTH: str | None = None  # set to e.g. "M1" when --month is used

PRE_EVENT_DAYS = 5   # trading days before FOMC to measure elevated IV
POST_EVENT_DAYS = 1  # trading days after FOMC to measure IV drop

# Hypotheses that require intraday_series.parquet or intraday options data
_INTRADAY_REQUIRED = {"H13", "H14", "H15", "H17", "H18", "H19", "H20", "H21", "H22", "H23", "H25"}


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
    """Pre-run data quality gate. Raises SystemExit on any failure."""
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
        raise SystemExit("daily_series.parquet not found.")
    df = pd.read_parquet(DAILY_SERIES)
    date_col = next((c for c in df.columns if "date" in c.lower()), None)
    if date_col:
        df["date"] = pd.to_datetime(df[date_col])
    df = df.sort_values("date").reset_index(drop=True)
    # Lock to frozen test window
    df = df[(df["date"] >= TEST_WINDOW_START) & (df["date"] <= TEST_WINDOW_END)].reset_index(drop=True)
    return df


def _load_intraday() -> pd.DataFrame | None:
    if not INTRADAY_SERIES.exists():
        return None
    return pd.read_parquet(INTRADAY_SERIES)


def _load_existing_results() -> dict[str, dict]:
    if RESULTS_FILE.exists():
        records = json.loads(RESULTS_FILE.read_text())
        return {r["hypothesis_number"]: r for r in records}
    return {}


def _save_results(results_map: dict[str, dict]) -> None:
    records = _sanitise_for_json(list(results_map.values()))
    RESULTS_FILE.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} results → {RESULTS_FILE}")


def _auto_update_downstream() -> None:
    """Run 17_score_and_report.py then 18_export_backtest_vault.py automatically."""
    import subprocess
    scripts = [
        BASE / "scripts" / "17_score_and_report.py",
        BASE / "scripts" / "18_export_backtest_vault.py",
    ]
    for script in scripts:
        if not script.exists():
            print(f"[auto-update] {script.name} not found — skipping")
            continue
        print(f"\n[auto-update] Running {script.name}...")
        result = subprocess.run([sys.executable, str(script)], capture_output=False)
        if result.returncode != 0:
            print(f"[auto-update] {script.name} exited with code {result.returncode}")


# ── H13: U-Shape IV Intraday ──────────────────────────────────────────────────────

def run_h13(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ ATM IV follows a U-shape intraday — elevated at open, dips mid-day,
    rises into the close.

    Uses small strike ladder (±3 listed strikes around ATM) + iVol single-option
    intraday endpoint. Buckets: open ≤ 10:00, mid 11:30–14:00, close ≥ 15:30 (1h bars).
    data_notes = proxy_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)

    open_ivs, mid_ivs, close_ivs = [], [], []
    n_attempted = 0

    n_days_total = len(trading_days)
    for i, day in enumerate(trading_days):
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            ladder = build_ladder(TICKER, date_str, call_put="C", dte_target=0, ladder_width=3)
        except Exception as e:
            print(f"  [{i+1}/{n_days_total}] {date_str}: ladder ERROR — {str(e)[:60]}")
            continue
        if ladder is None or ladder.underlying_1h.empty:
            print(f"  [{i+1}/{n_days_total}] {date_str}: ladder=NONE")
            continue

        ts_df = get_ladder_time_series(ladder, call_put="C")
        if ts_df.empty:
            print(f"  [{i+1}/{n_days_total}] {date_str}: ladder=OK ts_df=EMPTY")
            continue
        ts_df = ts_df[~ts_df["no_data"] & ts_df["iv"].notna()].copy()
        if ts_df.empty:
            print(f"  [{i+1}/{n_days_total}] {date_str}: ladder=OK all_no_data")
            continue

        mins = ts_df.index.hour * 60 + ts_df.index.minute
        open_rows  = ts_df[mins <= 600]              # ≤ 10:00
        mid_rows   = ts_df[(mins >= 690) & (mins <= 840)]   # 11:30–14:00
        close_rows = ts_df[mins >= 930]              # ≥ 15:30

        if open_rows.empty or mid_rows.empty or close_rows.empty:
            print(f"  [{i+1}/{n_days_total}] {date_str}: incomplete buckets open={len(open_rows)} mid={len(mid_rows)} close={len(close_rows)}")
            continue

        o_iv = float(open_rows["iv"].mean())
        m_iv = float(mid_rows["iv"].mean())
        c_iv = float(close_rows["iv"].mean())
        print(f"  [{i+1}/{n_days_total}] {date_str}: OK  open={o_iv:.3f} mid={m_iv:.3f} close={c_iv:.3f}")
        open_ivs.append(o_iv)
        mid_ivs.append(m_iv)
        close_ivs.append(c_iv)

    n_with_data = len(open_ivs)
    gate = _coverage_gate(n_attempted, n_with_data, "H13", hyp,
                          "u_shape_open_minus_mid", 0.0, -0.5, raw)
    if gate:
        return gate

    mean_open  = float(np.mean(open_ivs))
    mean_mid   = float(np.mean(mid_ivs))
    mean_close = float(np.mean(close_ivs))
    open_minus_mid  = mean_open - mean_mid
    close_minus_mid = mean_close - mean_mid

    p_open = p_close = float("nan")
    if n_with_data >= 10:
        _, p_open  = stats.ttest_rel(open_ivs,  mid_ivs)
        _, p_close = stats.ttest_rel(close_ivs, mid_ivs)

    pct = n_with_data / max(n_attempted, 1)
    cov = f" [coverage {n_with_data}/{n_attempted} = {pct:.0%}]" if pct < 0.80 else ""

    u_shape    = open_minus_mid > 0 and close_minus_mid > 0
    significant = not np.isnan(p_open) and p_open < 0.05 and not np.isnan(p_close) and p_close < 0.05

    if u_shape and significant:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"U-shape confirmed: open={mean_open:.3f} mid={mean_mid:.3f} close={mean_close:.3f}. "
                  f"open-mid={open_minus_mid:.4f} p={p_open:.4f}; close-mid={close_minus_mid:.4f} p={p_close:.4f}.{cov}")
    elif u_shape:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"U-shape present but not significant: open-mid={open_minus_mid:.4f} p={p_open:.4f}, "
                  f"close-mid={close_minus_mid:.4f} p={p_close:.4f}.{cov}")
    else:
        verdict = BacktestVerdict.REJECTED
        reason = f"No U-shape: open-mid={open_minus_mid:.4f}, close-mid={close_minus_mid:.4f}.{cov}"

    print(f"  H13: n={n_with_data}, open={mean_open:.3f} mid={mean_mid:.3f} close={mean_close:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H13",
        ticker=TICKER,
        period_start=_RUN_START,
        period_end=_RUN_END,
        raw_rows=raw,
        rows_after_validation=n_with_data,
        rows_excluded=raw - n_with_data,
        exclusion_reason="days without full open/mid/close IV buckets excluded",
        n_observations=n_with_data,
        n_signals=n_with_data,
        metric_name="u_shape_open_minus_mid",
        metric_value=round(open_minus_mid, 4),
        support_threshold=0.0,
        reject_threshold=-0.5,
        verdict=verdict,
        verdict_reason=reason,
        data_notes="proxy_tested",
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_with_data),
            "mean_iv_open":  round(mean_open,  4),
            "mean_iv_mid":   round(mean_mid,   4),
            "mean_iv_close": round(mean_close, 4),
            "open_minus_mid":  round(open_minus_mid,  4),
            "close_minus_mid": round(close_minus_mid, 4),
            "p_open_vs_mid":  round(p_open,  4) if not np.isnan(p_open)  else None,
            "p_close_vs_mid": round(p_close, 4) if not np.isnan(p_close) else None,
            "_raw": {"open_ivs": open_ivs, "mid_ivs": mid_ivs, "close_ivs": close_ivs},
        },
    )


# ── H16: Macro Release Vol Crush ─────────────────────────────────────────────────

def run_h16(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ 30d IVX is systematically elevated in the 5 days before FOMC
    and falls significantly on/after the announcement day.

    Uses: daily_series.parquet (iv_30d column) + FOMC dates from calendar.py
    Ticker: QQQ. Window: TEST_WINDOW_START → TEST_WINDOW_END.
    test_type: proxy_tested — QQQ 30d IVX used as proxy; not tracking specific option contracts.
    """
    raw = len(daily)
    excl_reason = "FOMC events outside window or insufficient pre/post trading days around announcement"
    if "iv_30d" not in daily.columns or daily["iv_30d"].isna().all():
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H16",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
            exclusion_reason="iv_30d column missing — IVX data not fetched",
            n_observations=raw,
            n_signals=0,
            metric_name="mean_iv_drop_post_fomc_vpts",
            metric_value=float("nan"),
            support_threshold=1.0,
            reject_threshold=-0.5,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason="iv_30d column missing — IVX data not fetched or unavailable",
            data_notes="insufficient_data",
        )

    fomc_dates = get_fomc_dates(TEST_WINDOW_START, TEST_WINDOW_END)
    if len(fomc_dates) < 3:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H16",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=raw, rows_excluded=0,
            exclusion_reason=excl_reason,
            n_observations=raw, n_signals=0,
            metric_name="mean_iv_drop_post_fomc_vpts",
            metric_value=float("nan"),
            support_threshold=1.0, reject_threshold=-0.5,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few FOMC events in data range ({len(fomc_dates)} events, need ≥ 3)",
            data_notes="proxy_tested",
        )

    daily = daily.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily_indexed = daily.set_index("date")["iv_30d"].astype(float)

    # Full-sample percentile rank for regime comparison
    overall_pct_rank = daily_indexed.rank(pct=True)

    pre_window_ivs = []     # mean IVX in [-PRE_EVENT_DAYS, -1] relative to FOMC
    pre_window_pcts = []    # percentile rank of mean pre-event IVX
    post_drops = []         # IVX change on announcement day

    trade_records = []

    for fomc_date in fomc_dates:
        fomc_ts = pd.Timestamp(fomc_date)

        # Find trading day index of the FOMC date
        all_dates = daily_indexed.index
        dates_before = all_dates[all_dates <= fomc_ts]
        dates_after = all_dates[all_dates > fomc_ts]

        if len(dates_before) < PRE_EVENT_DAYS + 1 or len(dates_after) < 1:
            continue

        pre_window = dates_before[-(PRE_EVENT_DAYS + 1):-1]  # [-5, -1] trading days
        pre_iv = daily_indexed[pre_window].mean()
        pre_pct = overall_pct_rank[pre_window].mean()

        announcement_day = dates_before[-1]  # last trading day ≤ FOMC date (the day of)
        post_day = dates_after[0]            # first trading day after FOMC

        iv_on_announce = daily_indexed[announcement_day]
        iv_day_after = daily_indexed[post_day]
        iv_drop = iv_on_announce - iv_day_after  # positive = IV fell

        pre_window_ivs.append(float(pre_iv))
        pre_window_pcts.append(float(pre_pct))
        post_drops.append(float(iv_drop))

        trade_records.append(TradeRecord(
            date=str(fomc_date),
            signal=round(float(pre_iv), 4),
            outcome=round(float(iv_drop), 4),
            notes=f"pre_pct={pre_pct:.2f}, pre_iv={pre_iv:.4f}, drop={iv_drop:.4f}",
        ))

    if len(post_drops) < 3:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"],
            hypothesis_title=hyp["title"],
            hypothesis_number="H16",
            ticker=TICKER,
            period_start=TEST_WINDOW_START,
            period_end=TEST_WINDOW_END,
            raw_rows=raw, rows_after_validation=raw,
            rows_excluded=len(fomc_dates) - len(post_drops),
            exclusion_reason=excl_reason,
            n_observations=raw, n_signals=len(post_drops),
            metric_name="mean_iv_drop_post_fomc_vpts",
            metric_value=float("nan"),
            support_threshold=1.0,
            reject_threshold=-0.5,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few FOMC events with full data ({len(post_drops)} valid)",
            data_notes="proxy_tested",
            trades=trade_records,
        )

    mean_drop = float(np.mean(post_drops))
    mean_pre_pct = float(np.mean(pre_window_pcts))
    t_stat, p_value = stats.ttest_1samp(post_drops, popmean=0)

    # In percentage points (vol is decimal, multiply by 100 for display)
    mean_drop_vpts = mean_drop * 100

    support = (mean_pre_pct >= 0.40) and (mean_drop_vpts >= 1.0) and (p_value < 0.05)
    reject = mean_drop_vpts < 0  # mean IV actually rose post-FOMC

    if support:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Pre-FOMC IVX elevated (mean pct rank={mean_pre_pct:.2f}), "
            f"mean drop post-FOMC={mean_drop_vpts:.2f} vol pts, p={p_value:.4f}"
        )
    elif reject:
        verdict = BacktestVerdict.REJECTED
        reason = f"IV rose on average post-FOMC: mean_drop={mean_drop_vpts:.2f} vol pts"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Drop present ({mean_drop_vpts:.2f} vpts) but threshold not met "
            f"(need pre_pct ≥ 0.40 AND drop ≥ 1.0 AND p < 0.05). "
            f"pre_pct={mean_pre_pct:.2f}, p={p_value:.4f}"
        )

    print(f"  H16: {len(post_drops)} FOMC events, mean_drop={mean_drop_vpts:.2f} vpts, pre_pct={mean_pre_pct:.2f}, p={p_value:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H16",
        ticker=TICKER,
        period_start=TEST_WINDOW_START,
        period_end=TEST_WINDOW_END,
        raw_rows=raw, rows_after_validation=raw,
        rows_excluded=len(fomc_dates) - len(post_drops),
        exclusion_reason=excl_reason,
        n_observations=raw,
        n_signals=len(post_drops),
        metric_name="mean_iv_drop_post_fomc_vpts",
        metric_value=round(mean_drop_vpts, 4),
        support_threshold=1.0,
        reject_threshold=-0.5,
        verdict=verdict,
        verdict_reason=reason,
        data_notes="proxy_tested",
        trades=trade_records,
        extra_metrics={
            "n_fomc_events": len(post_drops),
            "mean_pre_iv_pct_rank": round(mean_pre_pct, 4),
            "mean_drop_vpts": round(mean_drop_vpts, 4),
            "t_stat": round(t_stat, 4),
            "p_value": round(p_value, 4),
            "fomc_dates_used": [t.date for t in trade_records],  # already ISO strings
        },
    )


# ── Shared helper ────────────────────────────────────────────────────────────────

def _insufficient(
    hnum: str,
    hyp: dict,
    metric_name: str,
    support_threshold: float,
    reject_threshold: float,
    reason: str,
    raw_rows: int,
) -> BacktestResult:
    """Return a standardised INSUFFICIENT_DATA result."""
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number=hnum,
        ticker=TICKER,
        period_start=_RUN_START,
        period_end=_RUN_END,
        raw_rows=raw_rows,
        rows_after_validation=0,
        rows_excluded=raw_rows,
        exclusion_reason=(
            "Intraday price/options data unavailable — "
            "iVolatility subscription does not include intraday endpoints"
        ),
        n_observations=0,
        n_signals=0,
        metric_name=metric_name,
        metric_value=float("nan"),
        support_threshold=support_threshold,
        reject_threshold=reject_threshold,
        verdict=BacktestVerdict.INSUFFICIENT_DATA,
        verdict_reason=reason,
        data_notes="insufficient_data",
    )


def _ladder_approx_meta(n_attempted: int, n_with_data: int) -> dict:
    """Shared approximation metadata injected into extra_metrics for all ladder runners."""
    pct = round(n_with_data / max(n_attempted, 1), 3)
    meta = {
        "contract_selection_method": "intraday_atm_approx_small_strike_ladder",
        "strike_ladder_width": 3,
        "exact_chain_intraday": False,
        "minute_type": "MINUTE_5",
        "n_days_attempted": n_attempted,
        "n_days_with_ladder_data": n_with_data,
        "pct_days_with_data": pct,
        "intraday_endpoint_used": "single-equity-optionsymbol-rawiv",
        "is_combined": False,
    }
    meta["monthly_batch_mode"] = True
    if _RUN_MONTH:
        meta["month"]       = _RUN_MONTH
        meta["month_start"] = MONTHLY_BATCHES[_RUN_MONTH][0]
        meta["month_end"]   = MONTHLY_BATCHES[_RUN_MONTH][1]
    return meta


def _coverage_gate(
    n_attempted: int, n_with_data: int,
    hnum: str, hyp: dict,
    metric_name: str, support_threshold: float, reject_threshold: float,
    raw_rows: int,
) -> BacktestResult | None:
    """Return INSUFFICIENT_DATA result if day coverage is too low, else None."""
    if n_attempted == 0:
        return _insufficient(hnum, hyp, metric_name, support_threshold, reject_threshold,
                             "No trading days in test window.", raw_rows)
    pct = n_with_data / n_attempted
    if pct < 0.50:
        return _insufficient(
            hnum, hyp, metric_name, support_threshold, reject_threshold,
            f"Insufficient ladder coverage: {n_with_data}/{n_attempted} days ({pct:.0%}). "
            f"Need ≥ 50% days with intraday data.", raw_rows,
        )
    return None


def _iv_near(df_iv: "pd.DataFrame", ts: "pd.Timestamp", tol_minutes: int = 10) -> "float | None":
    """Return IV from normalised intraday DataFrame at the bar nearest to ts."""
    tol = pd.Timedelta(minutes=tol_minutes)
    win = df_iv[(df_iv.index >= ts - tol) & (df_iv.index <= ts + tol)]
    if win.empty or "iv" not in win.columns:
        return None
    iv_vals = win["iv"].dropna()
    if iv_vals.empty:
        return None
    deltas = np.abs((win.index - ts).total_seconds())
    return float(win.iloc[int(deltas.argmin())]["iv"])


# ── H14: 0DTE Straddle Sold at Open vs Noon ──────────────────────────────────

def run_h14(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: 0DTE ATM straddle sold at open (09:30) earns more than one sold at noon.

    Proxy: ladder mid-price at 9:30 and 12:30 bars. EOD P&L = straddle_price - |close - strike|.
    data_notes = proxy_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)

    open_pnls, noon_pnls = [], []
    n_attempted = 0
    trades = []

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            ladder = build_ladder(TICKER, date_str, call_put="both", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        eod_close = float(ladder.underlying_1h.iloc[-1]["close"])
        ts_open = pd.Timestamp(date_str + " 09:30", tz="America/New_York")
        ts_noon = pd.Timestamp(date_str + " 12:30", tz="America/New_York")

        sc_o = get_atm_snapshot(ladder, ts_open, "C")
        sp_o = get_atm_snapshot(ladder, ts_open, "P")
        sc_n = get_atm_snapshot(ladder, ts_noon, "C")
        sp_n = get_atm_snapshot(ladder, ts_noon, "P")

        if any(s is None for s in [sc_o, sp_o, sc_n, sp_n]):
            continue
        if any(s["mid_price"] is None for s in [sc_o, sp_o, sc_n, sp_n]):
            continue

        straddle_open = sc_o["mid_price"] + sp_o["mid_price"]
        straddle_noon = sc_n["mid_price"] + sp_n["mid_price"]
        pnl_open = straddle_open - abs(eod_close - sc_o["strike"])
        pnl_noon = straddle_noon - abs(eod_close - sc_n["strike"])

        open_pnls.append(pnl_open)
        noon_pnls.append(pnl_noon)

        if len(trades) < 20:
            trades.append(TradeRecord(
                date=date_str, signal=round(straddle_open, 4),
                outcome=round(pnl_open - pnl_noon, 4),
                notes=f"open={pnl_open:.3f} noon={pnl_noon:.3f} K={sc_o['strike']} close={eod_close:.2f}",
            ))

    n_with_data = len(open_pnls)
    gate = _coverage_gate(n_attempted, n_with_data, "H14", hyp,
                          "open_vs_noon_pnl_diff", 0.5, -0.5, raw)
    if gate:
        return gate

    mean_open = float(np.mean(open_pnls))
    mean_noon = float(np.mean(noon_pnls))
    diff = mean_open - mean_noon

    diffs = [o - n for o, n in zip(open_pnls, noon_pnls)]
    t_stat, p_val = (stats.ttest_1samp(diffs, popmean=0) if len(diffs) >= 10
                     else (float("nan"), float("nan")))

    pct = n_with_data / max(n_attempted, 1)
    cov = f" [coverage {n_with_data}/{n_attempted} = {pct:.0%}]" if pct < 0.80 else ""

    if diff > 0.5 and not np.isnan(p_val) and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"Open entry better: open_pnl={mean_open:.3f} noon={mean_noon:.3f} diff={diff:.3f} p={p_val:.4f}.{cov}"
    elif diff < 0:
        verdict = BacktestVerdict.REJECTED
        reason = f"Noon entry outperforms open: diff={diff:.3f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Open slightly better (diff={diff:.3f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H14: n={n_with_data}, open_pnl={mean_open:.3f}, noon_pnl={mean_noon:.3f}, diff={diff:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H14", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=raw - n_with_data,
        exclusion_reason="days without open+noon straddle snapshots excluded",
        n_observations=n_with_data, n_signals=n_with_data,
        metric_name="open_vs_noon_pnl_diff", metric_value=round(diff, 4),
        support_threshold=0.5, reject_threshold=-0.5,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        trades=trades,
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_with_data),
            "mean_open_pnl": round(mean_open, 4), "mean_noon_pnl": round(mean_noon, 4),
            "mean_diff": round(diff, 4),
            "p_value": round(p_val, 4) if not np.isnan(p_val) else None,
            "_raw": {"open_pnls": open_pnls, "noon_pnls": noon_pnls},
        },
    )


# ── H15: First-Hour RV Predicts Full-Day RV ──────────────────────────────────

def run_h15(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: First-hour (9:30–10:30) realized volatility predicts full-day realized vol.

    Both RVs computed from 5-min intraday returns (Databento EQUS.MINI).
    Window: EOD_WINDOW_START → EOD_WINDOW_END (full 2024-2026, single pass).
    First-hour: 12 bars (9:30–10:25). Full-day: 78 bars (9:30–15:55).
    Test: Spearman r. Support: r >= 0.40 AND p < 0.05.
    data_notes = directly_tested.
    """
    raw = len(daily)
    # H15 always uses the full EOD window, regardless of _RUN_START/_RUN_END
    trading_days = pd.bdate_range(start=EOD_WINDOW_START, end=EOD_WINDOW_END)
    db = DatabentoPriceClient()

    first_hour_rvs: list[float] = []
    full_day_rvs: list[float] = []
    n_attempted = 0

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception as e:
            print(f"  [H15] {date_str}: fetch error — {str(e)[:60]}")
            continue
        if bars.empty:
            continue

        first_hour = bars.between_time("09:30", "10:29")  # 12 bars: 9:30…10:25
        if len(first_hour) < 8 or len(bars) < 50:
            continue

        fh_rv = float(first_hour["close"].pct_change().dropna().std())
        fd_rv = float(bars["close"].pct_change().dropna().std())
        if np.isnan(fh_rv) or np.isnan(fd_rv) or fh_rv <= 0 or fd_rv <= 0:
            continue

        first_hour_rvs.append(fh_rv)
        full_day_rvs.append(fd_rv)

    n = len(first_hour_rvs)
    if n < 20:
        return _insufficient("H15", hyp, "spearman_r_fh_rv_vs_fd_rv", 0.40, -0.10,
                             f"Too few trading days with Databento data: {n} (need ≥ 20).", raw)

    r, p = spearmanr(first_hour_rvs, full_day_rvs)
    r, p = float(r), float(p)

    if r >= 0.40 and p < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"First-hour RV predicts full-day RV: r={r:.3f} p={p:.4f} n={n}."
    elif r < 0:
        verdict = BacktestVerdict.REJECTED
        reason = f"Negative correlation: r={r:.3f}. n={n}."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Positive but weak/insignificant: r={r:.3f} p={p:.4f} n={n}."

    print(f"  H15: n={n}, spearman_r={r:.3f}, p={p:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H15", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=n, rows_excluded=n_attempted - n,
        exclusion_reason="days with missing or incomplete 5-min Databento data excluded",
        n_observations=n, n_signals=n,
        metric_name="spearman_r_fh_rv_vs_fd_rv", metric_value=round(r, 4),
        support_threshold=0.40, reject_threshold=-0.10,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "spearman_r": round(r, 4), "p_value": round(p, 4),
            "n_days": n, "n_attempted": n_attempted,
            "data_source": "databento_equs_mini_5min",
            "_raw": {"first_hour_rvs": first_hour_rvs, "full_day_rvs": full_day_rvs},
        },
    )


# ── H17: Gamma Scalping P&L Peaks in 30-Min Vol Spike ────────────────────────

def run_h17(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Intraday gamma scalping P&L is highest when all realised vol concentrates
    in a single 30-min spike window rather than being distributed across the day.

    Uses Databento 5-min price bars (slot RVs) + iVol 5-min option data (gamma/theta).
    Window: Apr–Dec 2025, monthly batches (iVol option data constraint).
    13 half-hour slots (each 6 bars); spike day = max slot RV > 2× mean of other slots.
    Gamma P&L = Σ [0.5·γ·(dS)² − |θ|·dt] per bar; dt = 5/390.
    Test: ttest_ind(spike_pnls, flat_pnls). Support: mean_spike > mean_flat AND p < 0.05 AND n_spike ≥ 5.
    data_notes = directly_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)
    db = DatabentoPriceClient()

    spike_pnls: list[float] = []
    flat_pnls:  list[float] = []
    n_attempted = 0

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1

        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            continue
        if bars.empty or len(bars) < 60:
            continue

        # 13 half-hour slots; each = 6 bars → 5 within-slot returns
        slot_bars_list = [bars.iloc[i * 6:(i + 1) * 6] for i in range(13)]
        window_rvs = [
            float(sb["close"].pct_change().dropna().std())
            for sb in slot_bars_list if len(sb) >= 5
        ]
        if len(window_rvs) < 10:
            continue

        max_rv   = max(window_rvs)
        mean_rv  = sum(window_rvs) / len(window_rvs)
        spike_ratio = max_rv / (mean_rv + 1e-10)

        # Full-day returns aligned to bars (for gamma P&L lookup)
        bar_returns = bars["close"].pct_change().fillna(0)

        # Intraday option ladder (gamma/theta)
        try:
            ladder = build_ladder(TICKER, date_str, call_put="C", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None:
            continue
        # Get hourly ATM snapshots to identify option symbols per hour
        ts_df = get_ladder_time_series(ladder, call_put="C")
        if ts_df.empty:
            continue
        ts_df = ts_df[~ts_df["no_data"] & ts_df["option_symbol"].notna()].copy()
        if ts_df.empty:
            continue

        # Γ-scalp P&L = Σ_bars [0.5·γ·(dS)² − |θ|·dt]
        # gamma/theta from ladder.intraday[symbol] as optionGamma/optionTheta (raw iVol columns)
        DT = 5 / 390
        pnl = 0.0
        ts_index = ts_df.index
        for bar_time, close_px in bars["close"].items():
            # Find the hourly ATM snapshot nearest to this 5-min bar
            delta_secs = abs((ts_index - bar_time).total_seconds())
            nearest_snap = ts_df.iloc[int(delta_secs.argmin())]
            opt_sym = nearest_snap.get("option_symbol")
            if not opt_sym:
                continue

            raw_df = ladder.intraday.get(opt_sym)
            if raw_df is None or raw_df.empty:
                continue

            # Find nearest raw 5-min bar within ±7 minutes
            tol = pd.Timedelta(minutes=7)
            window = raw_df[(raw_df.index >= bar_time - tol) & (raw_df.index <= bar_time + tol)]
            if window.empty:
                continue
            delta_s2 = abs((window.index - bar_time).total_seconds())
            raw_row = window.iloc[int(delta_s2.argmin())]

            gamma = float(raw_row.get("optionGamma", 0) or 0)
            theta = float(raw_row.get("theta", raw_row.get("optionTheta", 0)) or 0)
            if gamma == 0 and theta == 0:
                continue

            ret = float(bar_returns.get(bar_time, 0))
            dS = close_px * ret
            pnl += 0.5 * gamma * dS ** 2 - abs(theta) * DT

        if spike_ratio >= 2.0:
            spike_pnls.append(pnl)
        else:
            flat_pnls.append(pnl)

    n_spike, n_flat = len(spike_pnls), len(flat_pnls)
    if n_spike < 5 or n_flat < 5:
        return _insufficient("H17", hyp, "mean_gamma_pnl_spike_vs_flat", 0.0, -0.5,
                             f"Too few days: spike={n_spike}, flat={n_flat} (need ≥ 5 each).", raw)

    mean_spike = float(np.mean(spike_pnls))
    mean_flat  = float(np.mean(flat_pnls))
    _, p = stats.ttest_ind(spike_pnls, flat_pnls)
    p = float(p)

    if mean_spike > mean_flat and p < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Gamma P&L higher on vol-spike days: spike={mean_spike:.4f} flat={mean_flat:.4f} "
                  f"p={p:.4f} n_spike={n_spike} n_flat={n_flat}.")
    elif mean_spike <= mean_flat:
        verdict = BacktestVerdict.REJECTED
        reason = f"No spike premium: spike={mean_spike:.4f} ≤ flat={mean_flat:.4f}."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"Spike > flat but not significant: spike={mean_spike:.4f} flat={mean_flat:.4f} "
                  f"p={p:.4f} n_spike={n_spike} n_flat={n_flat}.")

    print(f"  H17: spike={n_spike}d flat={n_flat}d mean_spike={mean_spike:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H17", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_spike + n_flat,
        rows_excluded=n_attempted - (n_spike + n_flat),
        exclusion_reason="days without full bar data or option ladder excluded",
        n_observations=n_spike + n_flat, n_signals=n_spike,
        metric_name="mean_gamma_pnl_spike_vs_flat", metric_value=round(mean_spike - mean_flat, 4),
        support_threshold=0.0, reject_threshold=-0.5,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_spike + n_flat),
            "mean_pnl_spike_days": round(mean_spike, 4),
            "mean_pnl_flat_days":  round(mean_flat, 4),
            "n_spike_days": n_spike, "n_flat_days": n_flat,
            "p_value": round(p, 4),
            "data_source": "databento_equs_mini_5min + ivol_intraday",
            "_raw": {"spike_pnls": spike_pnls, "flat_pnls": flat_pnls},
        },
    )


# ── H18: Intraday Mean Reversion Strongest in 10:00–11:30 ────────────────────

def run_h18(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ intraday price mean reversion is strongest in the 10:00–11:30 ET window.

    13 non-overlapping 30-min slots across the day (78 bars total, 6 bars/slot).
    Slot indexing: 0=9:30-10:00, 1=10:00-10:30, 2=10:30-11:00, 3=11:00-11:30, …
    Target "10:00-11:30" = slots 1, 2, 3.
    Mean reversion per slot = −autocorr(lag=1) of within-slot 5-min returns.
    Test: ttest_ind(target_revs, other_revs). Support: mean_target > mean_other AND p < 0.05.
    Window: EOD_WINDOW_START → EOD_WINDOW_END (full 2024-2026, single pass, Databento only).
    data_notes = directly_tested.
    """
    raw = len(daily)
    # H18 always uses the full EOD window, regardless of _RUN_START/_RUN_END
    trading_days = pd.bdate_range(start=EOD_WINDOW_START, end=EOD_WINDOW_END)
    db = DatabentoPriceClient()

    window_revs: dict[int, list[float]] = {i: [] for i in range(13)}
    n_attempted = 0

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception as e:
            print(f"  [H18] {date_str}: fetch error — {str(e)[:60]}")
            continue
        if len(bars) < 70:
            continue

        for slot in range(13):
            slot_bars = bars.iloc[slot * 6:(slot + 1) * 6]
            if len(slot_bars) < 5:
                continue
            slot_rets = slot_bars["close"].pct_change().dropna()
            if len(slot_rets) < 3:
                continue
            ac = slot_rets.autocorr(lag=1)
            if not np.isnan(ac):
                window_revs[slot].append(-float(ac))  # positive = mean-reverting

    n_days = min(len(window_revs[1]), len(window_revs[2]), len(window_revs[3]))
    if n_days < 20:
        return _insufficient("H18", hyp, "mean_reversion_1000_1130_vs_other", 0.10, -0.10,
                             f"Too few trading days with Databento data: {n_days} (need ≥ 20).", raw)

    # Target = slots 1, 2, 3 (10:00–11:30)
    target_revs = window_revs[1] + window_revs[2] + window_revs[3]
    other_revs: list[float] = []
    for s in [0, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        other_revs.extend(window_revs[s])

    if len(target_revs) < 5 or len(other_revs) < 5:
        return _insufficient("H18", hyp, "mean_reversion_1000_1130_vs_other", 0.10, -0.10,
                             f"Insufficient obs: target={len(target_revs)} other={len(other_revs)}.", raw)

    mean_target = float(np.mean(target_revs))
    mean_other  = float(np.mean(other_revs))
    _, p = stats.ttest_ind(target_revs, other_revs)
    p = float(p)

    slot_means = {str(i): round(float(np.mean(window_revs[i])), 4) if window_revs[i] else None
                  for i in range(13)}

    if mean_target > mean_other and p < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"10:00-11:30 more mean-reverting: target={mean_target:.4f} other={mean_other:.4f} "
                  f"p={p:.4f} n_target={len(target_revs)}.")
    elif mean_target <= mean_other:
        verdict = BacktestVerdict.REJECTED
        reason = f"10:00-11:30 not more reverting: target={mean_target:.4f} ≤ other={mean_other:.4f}."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"Target > other but not significant: target={mean_target:.4f} other={mean_other:.4f} "
                  f"p={p:.4f}.")

    print(f"  H18: n_days≈{n_days}, target={mean_target:.4f} other={mean_other:.4f} p={p:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H18", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=n_days, rows_excluded=n_attempted - n_days,
        exclusion_reason="days with incomplete 5-min bar coverage excluded",
        n_observations=n_days, n_signals=len(target_revs),
        metric_name="mean_reversion_1000_1130_vs_other", metric_value=round(mean_target - mean_other, 4),
        support_threshold=0.10, reject_threshold=-0.10,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "mean_reversion_target_1000_1130": round(mean_target, 4),
            "mean_reversion_other_slots": round(mean_other, 4),
            "diff": round(mean_target - mean_other, 4),
            "p_value": round(p, 4),
            "n_target_obs": len(target_revs), "n_other_obs": len(other_revs),
            "slot_means": slot_means,
            "data_source": "databento_equs_mini_5min",
            "_raw": {"target_revs": target_revs, "other_revs": other_revs},
        },
    )


# ── H19: IV Skew Steepens After Afternoon Decline >0.75% ─────────────────────

def run_h19(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: IV skew (OTM put IV minus ATM IV) steepens after PM decline > 0.75%.

    Proxy: OTM put = lowest put strike in ±3 ladder (~most OTM available).
    Decline detected using Databento 5-min bar closes:
      px_1230 = close of 12:30 bar ≈ price at 12:35 ET
      px_1330 = close of 13:30 bar ≈ price at 13:35 ET
    IV snapshots use iVol intraday data via _iv_near (correct 5-min bars).
    data_notes = proxy_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)

    db_client = DatabentoPriceClient()
    delta_skews = []
    n_attempted = 0
    n_signals = 0
    trades = []

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1

        # Load Databento 5-min bars for point-in-time price detection
        try:
            bars = db_client.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            bars = pd.DataFrame()

        def _db_px(time_str: str) -> "float | None":
            # close of 5-min bar labeled time_str ≈ price 5 min later
            if bars.empty:
                return None
            ts = pd.Timestamp(date_str + " " + time_str, tz="America/New_York")
            tol = pd.Timedelta(minutes=7)
            w = bars[(bars.index >= ts - tol) & (bars.index <= ts + tol)]
            if w.empty:
                return None
            nearest = w.iloc[int(np.abs((w.index - ts).total_seconds()).argmin())]
            return float(nearest["close"])

        px_before = _db_px("12:30")  # close of 12:30 bar ≈ price at 12:35
        px_after  = _db_px("13:30")  # close of 13:30 bar ≈ price at 13:35
        if px_before is None or px_after is None:
            continue

        pct_chg = (px_after - px_before) / px_before

        try:
            ladder = build_ladder(TICKER, date_str, call_put="both", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        if pct_chg > -0.0075:   # only process afternoon declines > 0.75%
            continue
        n_signals += 1

        ts_1230 = pd.Timestamp(date_str + " 12:30", tz="America/New_York")
        ts_1330 = pd.Timestamp(date_str + " 13:30", tz="America/New_York")

        c_map = ladder.symbol_map.get("C", {})
        p_map = ladder.symbol_map.get("P", {})
        if not c_map or not p_map:
            continue

        atm_strike    = min(c_map.keys(), key=lambda s: abs(s - px_before))
        otm_candidates = [s for s in sorted(p_map.keys()) if s < atm_strike]
        if not otm_candidates:
            continue
        otm_strike = otm_candidates[0]

        atm_sym = c_map.get(atm_strike)
        otm_sym = p_map.get(otm_strike)
        if not atm_sym or not otm_sym:
            continue

        df_atm = ladder.intraday.get(atm_sym)
        df_otm = ladder.intraday.get(otm_sym)
        if df_atm is None or df_otm is None:
            continue

        atm_iv_before = _iv_near(df_atm, ts_1230)
        atm_iv_after  = _iv_near(df_atm, ts_1330)
        otm_iv_before = _iv_near(df_otm, ts_1230)
        otm_iv_after  = _iv_near(df_otm, ts_1330)

        if any(v is None or v <= 0 for v in [atm_iv_before, atm_iv_after, otm_iv_before, otm_iv_after]):
            continue

        skew_before = otm_iv_before - atm_iv_before
        skew_after  = otm_iv_after  - atm_iv_after
        d_skew      = skew_after - skew_before
        delta_skews.append(d_skew)

        if len(trades) < 20:
            trades.append(TradeRecord(
                date=date_str, signal=round(pct_chg * 100, 4), outcome=round(d_skew, 4),
                notes=f"pm_decline={pct_chg:.3%} skew_Δ={d_skew:.4f} otm_K={otm_strike} atm_K={atm_strike}",
            ))

    n_with_data = len(delta_skews)
    _raw_data = {"delta_skews": delta_skews, "n_signals": n_signals}
    if n_signals < 5 or n_with_data < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H19", ticker=TICKER,
            period_start=_RUN_START, period_end=_RUN_END,
            raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=n_attempted - n_with_data,
            exclusion_reason="days without PM decline or missing OTM/ATM IV excluded",
            n_observations=n_attempted, n_signals=n_signals,
            metric_name="mean_skew_change_after_pm_decline",
            metric_value=0.0, support_threshold=0.0, reject_threshold=-0.05,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(f"Too few PM-decline signal days: {n_signals} signals, "
                            f"{n_with_data} with complete IV data (need ≥ 5)."),
            data_notes="proxy_tested", trades=trades,
            extra_metrics={
                **_ladder_approx_meta(n_attempted, n_with_data),
                "n_signal_days": n_signals,
                "approx_note": "OTM put = lowest strike in ±3 ladder; 5-min Databento decline detection",
                "_raw": _raw_data,
            },
        )

    mean_d_skew = float(np.mean(delta_skews))
    t_stat, p_val = (stats.ttest_1samp(delta_skews, popmean=0) if n_with_data >= 5
                     else (float("nan"), float("nan")))
    cov = f" [signal days {n_with_data}/{n_signals}]"

    if mean_d_skew > 0 and not np.isnan(p_val) and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"Skew steepens after PM decline: mean_Δskew={mean_d_skew:.4f} p={p_val:.4f}.{cov}"
    elif mean_d_skew < 0:
        verdict = BacktestVerdict.REJECTED
        reason = f"Skew flattened after PM decline: mean_Δskew={mean_d_skew:.4f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Skew steepened (mean={mean_d_skew:.4f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H19: {n_with_data} signal days, mean_Δskew={mean_d_skew:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H19", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=n_attempted - n_with_data,
        exclusion_reason="days without PM decline or missing OTM/ATM IV excluded",
        n_observations=n_attempted, n_signals=n_signals,
        metric_name="mean_skew_change_after_pm_decline",
        metric_value=round(mean_d_skew, 4),
        support_threshold=0.0, reject_threshold=-0.05,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        trades=trades,
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_with_data),
            "n_signal_days": n_signals, "mean_skew_change": round(mean_d_skew, 4),
            "p_value": round(p_val, 4) if not np.isnan(p_val) else None,
            "approx_note": "OTM put = lowest strike in ±3 ladder; 5-min Databento decline detection",
            "_raw": _raw_data,
        },
    )


# ── H20: Delta-Threshold Hedging vs Fixed-Time Hedging ───────────────────────

def run_h20(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: ±0.10 delta-triggered hedging uses less total hedge activity than fixed 1h.

    Metric: ratio = threshold_cost / fixed_cost per day (< 1.0 = threshold cheaper).
    data_notes = proxy_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)

    ratios = []
    n_attempted = 0

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            ladder = build_ladder(TICKER, date_str, call_put="C", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        ts_df = get_ladder_time_series(ladder, call_put="C")
        if ts_df.empty:
            continue
        ts_df = ts_df[~ts_df["no_data"] & ts_df["delta"].notna()].copy()
        if len(ts_df) < 3:
            continue

        deltas = ts_df["delta"].values
        cost_a = float(np.sum(np.abs(np.diff(deltas))))
        if cost_a < 1e-8:
            continue

        threshold = 0.10
        last_hedge = deltas[0]
        cost_b = 0.0
        for d in deltas[1:]:
            drift = abs(d - last_hedge)
            if drift >= threshold:
                cost_b += drift
                last_hedge = d

        ratios.append(cost_b / cost_a)

    n_with_data = len(ratios)
    gate = _coverage_gate(n_attempted, n_with_data, "H20", hyp,
                          "threshold_vs_fixed_hedge_cost_ratio", 0.9, 1.1, raw)
    if gate:
        return gate

    mean_ratio = float(np.mean(ratios))
    t_stat, p_val = (stats.ttest_1samp(ratios, popmean=1.0) if n_with_data >= 10
                     else (float("nan"), float("nan")))
    pct = n_with_data / max(n_attempted, 1)
    cov = f" [coverage {n_with_data}/{n_attempted} = {pct:.0%}]" if pct < 0.80 else ""

    if mean_ratio < 0.9 and not np.isnan(p_val) and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"Threshold hedging cheaper: ratio={mean_ratio:.3f} < 0.9, p={p_val:.4f}.{cov}"
    elif mean_ratio >= 1.0:
        verdict = BacktestVerdict.REJECTED
        reason = f"Fixed hedging cheaper or equal: ratio={mean_ratio:.3f} ≥ 1.0.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Threshold appears cheaper (ratio={mean_ratio:.3f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H20: n={n_with_data}, ratio={mean_ratio:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H20", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=raw - n_with_data,
        exclusion_reason="days without delta time series excluded",
        n_observations=n_with_data, n_signals=sum(1 for r in ratios if r < 1.0),
        metric_name="threshold_vs_fixed_hedge_cost_ratio",
        metric_value=round(mean_ratio, 4),
        support_threshold=0.9, reject_threshold=1.1,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_with_data),
            "mean_ratio": round(mean_ratio, 4),
            "pct_days_threshold_cheaper": round(sum(1 for r in ratios if r < 1.0) / max(len(ratios), 1), 3),
            "p_value": round(p_val, 4) if not np.isnan(p_val) else None,
            "approx_note": "1h bars; threshold=0.10 delta change; cost = cumulative |Δdelta|",
            "_raw": {"ratios": ratios},
        },
    )


# ── H21: Options Bid-Ask Widest in First 15 Minutes ──────────────────────────

def run_h21(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ options bid-ask spread is widest at open and narrows toward midday.

    Proxy: spread_pct = (ask - bid) / mid at each 1h bar.
    open = 9:30 bar, midday = 11:30–13:30 bars.
    data_notes = proxy_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)

    open_spreads, mid_spreads = [], []
    n_attempted = 0
    trades = []

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            ladder = build_ladder(TICKER, date_str, call_put="C", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        ts_df = get_ladder_time_series(ladder, call_put="C")
        if ts_df.empty:
            continue
        ts_df = ts_df[~ts_df["no_data"] &
                      ts_df["bid_price"].notna() & ts_df["ask_price"].notna() &
                      (ts_df["bid_price"] > 0) & (ts_df["ask_price"] > 0)].copy()
        if len(ts_df) < 3:
            continue

        ts_df["mid"]        = (ts_df["bid_price"] + ts_df["ask_price"]) / 2
        ts_df["spread_pct"] = (ts_df["ask_price"] - ts_df["bid_price"]) / ts_df["mid"]

        mins = ts_df.index.hour * 60 + ts_df.index.minute
        open_rows = ts_df[mins <= 570]               # ≤ 9:30
        mid_rows  = ts_df[(mins >= 690) & (mins <= 810)]   # 11:30–13:30

        if open_rows.empty or mid_rows.empty:
            continue

        o_sp = float(open_rows["spread_pct"].mean())
        m_sp = float(mid_rows["spread_pct"].mean())
        open_spreads.append(o_sp)
        mid_spreads.append(m_sp)

        if len(trades) < 20:
            trades.append(TradeRecord(
                date=date_str, signal=round(o_sp, 4), outcome=round(o_sp - m_sp, 4),
                notes=f"open={o_sp:.4f} mid={m_sp:.4f}",
            ))

    n_with_data = len(open_spreads)
    gate = _coverage_gate(n_attempted, n_with_data, "H21", hyp,
                          "spread_open_minus_midday_pct", 0.05, -0.05, raw)
    if gate:
        return gate

    mean_open = float(np.mean(open_spreads))
    mean_mid  = float(np.mean(mid_spreads))
    diff      = mean_open - mean_mid

    t_stat, p_val = (stats.ttest_rel(open_spreads, mid_spreads) if n_with_data >= 10
                     else (float("nan"), float("nan")))
    pct = n_with_data / max(n_attempted, 1)
    cov = f" [coverage {n_with_data}/{n_attempted} = {pct:.0%}]" if pct < 0.80 else ""

    if diff > 0.05 and not np.isnan(p_val) and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"Open wider: open={mean_open:.4f} mid={mean_mid:.4f} diff={diff:.4f} p={p_val:.4f}.{cov}"
    elif diff < 0:
        verdict = BacktestVerdict.REJECTED
        reason = f"Midday spread wider: diff={diff:.4f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Open wider (diff={diff:.4f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H21: n={n_with_data}, open={mean_open:.4f}, mid={mean_mid:.4f}, diff={diff:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H21", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=raw - n_with_data,
        exclusion_reason="days without bid/ask time series excluded",
        n_observations=n_with_data,
        n_signals=sum(1 for o, m in zip(open_spreads, mid_spreads) if o > m),
        metric_name="spread_open_minus_midday_pct",
        metric_value=round(diff, 4),
        support_threshold=0.05, reject_threshold=-0.05,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        trades=trades,
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_with_data),
            "mean_open_spread": round(mean_open, 4),
            "mean_midday_spread": round(mean_mid, 4),
            "diff": round(diff, 4),
            "p_value": round(p_val, 4) if not np.isnan(p_val) else None,
            "approx_note": "1h bars (not 15-min); open = 9:30 bar, midday = 11:30–13:30 bars",
            "_raw": {"open_spreads": open_spreads, "mid_spreads": mid_spreads},
        },
    )


# ── H22: IV Responds Asymmetrically to Up vs Down 5-Min Moves ────────────────

def run_h22(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: ATM IV rises more after a negative 1h return than it falls after an equal positive.

    Underlying returns from Databento 5-min bar closes at each iVol snapshot time.
      ul_close at ts = close of 5-min bar nearest to ts ≈ price at ts+5min
      ul_ret = log(px@ts / px@prev_ts) — aligns with iv_chg = iv[ts] - iv[prev_ts]
    IV changes from ladder time series (iVol hourly snapshots).
    data_notes = proxy_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)

    db_client = DatabentoPriceClient()
    down_iv_changes: list[float] = []
    up_iv_changes:   list[float] = []
    n_attempted = 0
    n_days_with_data = 0

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            ladder = build_ladder(TICKER, date_str, call_put="C", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        ts_df = get_ladder_time_series(ladder, call_put="C")
        if ts_df.empty:
            continue
        ts_df = ts_df[~ts_df["no_data"] & ts_df["iv"].notna()].copy()
        if len(ts_df) < 3:
            continue

        try:
            bars = db_client.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            bars = pd.DataFrame()

        def _ul_px_at(ts: "pd.Timestamp") -> float:
            # close of nearest 5-min bar ≈ price at ts+5min (correct hourly snapshot alignment)
            if bars.empty:
                return float("nan")
            tol = pd.Timedelta(minutes=7)
            w = bars[(bars.index >= ts - tol) & (bars.index <= ts + tol)]
            if w.empty:
                return float("nan")
            return float(w.iloc[int(np.abs((w.index - ts).total_seconds()).argmin())]["close"])

        ts_df["ul_close"] = [_ul_px_at(ts) for ts in ts_df.index]
        ts_df["ul_ret"]   = np.log(ts_df["ul_close"] / ts_df["ul_close"].shift(1))
        ts_df["iv_chg"]   = ts_df["iv"] - ts_df["iv"].shift(1)
        valid = ts_df.dropna(subset=["ul_ret", "iv_chg"])
        if valid.empty:
            continue

        n_days_with_data += 1
        for _, row in valid.iterrows():
            if row["ul_ret"] < 0:
                down_iv_changes.append(float(row["iv_chg"]))
            elif row["ul_ret"] > 0:
                up_iv_changes.append(float(row["iv_chg"]))

    gate = _coverage_gate(n_attempted, n_days_with_data, "H22", hyp,
                          "mean_iv_change_down_minus_up", 0.001, -0.001, raw)
    if gate:
        return gate
    if len(down_iv_changes) < 5 or len(up_iv_changes) < 5:
        return _insufficient("H22", hyp, "mean_iv_change_down_minus_up", 0.001, -0.001,
                             f"Too few bars: down={len(down_iv_changes)}, up={len(up_iv_changes)}.", raw)

    mean_down = float(np.mean(down_iv_changes))
    mean_up   = float(np.mean(up_iv_changes))
    diff      = mean_down - mean_up

    t_stat, p_val = stats.ttest_ind(down_iv_changes, up_iv_changes)
    pct = n_days_with_data / max(n_attempted, 1)
    cov = f" [coverage {n_days_with_data}/{n_attempted} = {pct:.0%}]" if pct < 0.80 else ""

    if diff > 0 and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"IV asymmetry confirmed: down={mean_down:.4f} up={mean_up:.4f} diff={diff:.4f} p={p_val:.4f}.{cov}"
    elif diff <= 0:
        verdict = BacktestVerdict.REJECTED
        reason = f"No asymmetry: down iv_chg={mean_down:.4f} ≤ up={mean_up:.4f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Direction correct (diff={diff:.4f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H22: n_down={len(down_iv_changes)}, n_up={len(up_iv_changes)}, diff={diff:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H22", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw,
        rows_after_validation=len(down_iv_changes) + len(up_iv_changes),
        rows_excluded=raw - n_days_with_data,
        exclusion_reason="days without IV/return pairs excluded",
        n_observations=n_days_with_data,
        n_signals=len(down_iv_changes),
        metric_name="mean_iv_change_down_minus_up",
        metric_value=round(diff, 4),
        support_threshold=0.001, reject_threshold=-0.001,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_days_with_data),
            "mean_iv_chg_down": round(mean_down, 4),
            "mean_iv_chg_up":   round(mean_up,   4),
            "diff": round(diff, 4),
            "n_down_bars": len(down_iv_changes),
            "n_up_bars":   len(up_iv_changes),
            "p_value": round(p_val, 4) if not np.isnan(p_val) else None,
            "approx_note": "5-min Databento closes at iVol snapshot times; IV changes hourly",
            "_raw": {"down_iv_changes": down_iv_changes, "up_iv_changes": up_iv_changes},
        },
    )


# ── H23: Pin Risk on Expiration Fridays Near Large OI ────────────────────────

def run_h23(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ price tends to gravitate toward high-open-interest strikes in the
    final 30 minutes on 0DTE expiration Fridays.

    Requires: intraday price bars (last 30 min) + strike-level open interest data.
    """
    return _insufficient(
        "H23", hyp,
        metric_name="final30_range_vs_nearby_oi_strike",
        support_threshold=0.0,
        reject_threshold=-0.5,
        reason=(
            "Requires intraday price bars (last 30 minutes) and strike-level open interest "
            "data to identify pinning. Intraday data unavailable."
        ),
        raw_rows=len(daily),
    )


# ── H24: Last-30-Min Daily Range Predicts Overnight Gap (proxy) ──────────────

def run_h24(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Intraday realised vol in the last 30 minutes predicts overnight gap magnitude.

    Proxy test: full-day OHLC range (high-low)/open used as proxy for within-day
    vol intensity; overnight gap = |log(open_{t+1} / close_t)| computed from daily data.

    Evidence strength: proxy_tested — cannot isolate last-30-min vol without intraday bars.
    """
    raw = len(daily)
    required = ["high", "low", "open", "close"]
    df = daily.dropna(subset=required).copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    excl = raw - len(df)
    excl_reason = "rows dropped for missing OHLC values"

    if len(df) < 30:
        return _insufficient(
            "H24", hyp,
            metric_name="daily_range_vs_overnight_gap_spearman_r",
            support_threshold=0.15,
            reject_threshold=-0.10,
            reason=f"Too few valid rows after OHLC dropna: {len(df)} (need ≥ 30).",
            raw_rows=raw,
        )

    # Daily range as proxy for within-day vol intensity
    df["daily_range"] = (df["high"] - df["low"]) / df["open"]
    # Overnight gap magnitude: |log(open_{t+1} / close_t)|
    df["overnight_gap_abs"] = np.log(df["open"].shift(-1) / df["close"]).abs()

    valid = df.dropna(subset=["daily_range", "overnight_gap_abs"]).copy()
    n_valid = len(valid)

    if n_valid < 20:
        return _insufficient(
            "H24", hyp,
            metric_name="daily_range_vs_overnight_gap_spearman_r",
            support_threshold=0.15,
            reject_threshold=-0.10,
            reason=f"Too few paired observations after shift: {n_valid}.",
            raw_rows=raw,
        )

    r, p = stats.spearmanr(valid["daily_range"], valid["overnight_gap_abs"])
    r = float(r)
    p = float(p)

    # Build sample trade records (top 20 by overnight gap)
    top = valid.nlargest(20, "overnight_gap_abs")
    trade_records = [
        TradeRecord(
            date=str(row["date"].date()),
            signal=round(float(row["daily_range"]), 4),
            outcome=round(float(row["overnight_gap_abs"]), 4),
            notes=f"range={row['daily_range']:.4f}, gap={row['overnight_gap_abs']:.4f}",
        )
        for _, row in top.iterrows()
    ]

    support = r > 0.15 and p < 0.05
    reject = r < -0.10

    if support:
        verdict = BacktestVerdict.SUPPORTED
        reason = (
            f"Positive correlation between daily range and overnight gap: "
            f"r={r:.3f}, p={p:.4f} ({n_valid} obs). "
            f"Higher within-day vol precedes larger overnight gaps."
        )
    elif reject:
        verdict = BacktestVerdict.REJECTED
        reason = f"Negative correlation: r={r:.3f} — higher vol days have smaller overnight gaps."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (
            f"Direction {'positive' if r > 0 else 'negative'} (r={r:.3f}, p={p:.4f}) "
            f"but threshold not met (need r > 0.15 AND p < 0.05)."
        )

    print(
        f"  H24 proxy: daily_range→overnight_gap r={r:.3f}, p={p:.4f}, n={n_valid} → {verdict.value}"
    )

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H24",
        ticker=TICKER,
        period_start=TEST_WINDOW_START,
        period_end=TEST_WINDOW_END,
        raw_rows=raw,
        rows_after_validation=n_valid,
        rows_excluded=raw - n_valid,
        exclusion_reason="1 row lost to forward shift for overnight gap; OHLC NaN rows excluded",
        n_observations=n_valid,
        n_signals=n_valid,
        metric_name="daily_range_vs_overnight_gap_spearman_r",
        metric_value=round(r, 4),
        support_threshold=0.15,
        reject_threshold=-0.10,
        verdict=verdict,
        verdict_reason=reason,
        data_notes="proxy_tested",
        trades=trade_records,
        extra_metrics={
            "spearman_r": round(r, 4),
            "p_value": round(p, 4),
            "n_observations": n_valid,
            "mean_daily_range": round(float(valid["daily_range"].mean()), 4),
            "mean_overnight_gap_abs": round(float(valid["overnight_gap_abs"].mean()), 4),
        },
    )


# ── H25: 0DTE Straddle After Morning Reversal ─────────────────────────────────

def run_h25(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: 0DTE straddle P&L variance is lower when sold after a morning reversal.

    Signal: |9:30-open → 10:30-close| > 0.6% AND 10:30→11:30 retraces ≥ 30%.
    Prices from Databento 5-min bars (close of the bar at each timestamp) — NOT 1h bar closes,
    which lag by ~60 min and caused the signal to almost never fire.
    Straddle entry at 11:30. EOD P&L = straddle_mid - |eod_close - strike|.
    Metric: 1 - (var_reversal / var_non_reversal); > 0 = reversal days have tighter P&L.
    data_notes = proxy_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)
    db = DatabentoPriceClient()

    reversal_pnls:     list[float] = []
    non_reversal_pnls: list[float] = []
    n_attempted = 0
    n_signals   = 0
    trades      = []

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1

        # Point-in-time prices from Databento 5-min bars
        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            bars = pd.DataFrame()

        def _db_px(time_str: str) -> "float | None":
            if bars.empty:
                return None
            ts = pd.Timestamp(date_str + " " + time_str, tz="America/New_York")
            tol = pd.Timedelta(minutes=7)
            w = bars[(bars.index >= ts - tol) & (bars.index <= ts + tol)]
            if w.empty:
                return None
            nearest = w.iloc[int(np.abs((w.index - ts).total_seconds()).argmin())]
            return float(nearest["close"])

        px_930  = _db_px("09:30")   # close of 9:30 bar = price at 9:35
        px_1030 = _db_px("10:30")   # close of 10:30 bar = price at 10:35
        px_1130 = _db_px("11:30")   # close of 11:30 bar = price at 11:35

        # Fallback: if Databento unavailable, skip rather than use 1h close (which lags ~60 min)
        if any(v is None for v in [px_930, px_1030, px_1130]):
            continue

        move_to_1030      = (px_1030 - px_930) / px_930
        move_1030_to_1130 = (px_1130 - px_1030) / px_1030

        is_signal = (
            abs(move_to_1030) > 0.006
            and abs(move_1030_to_1130) > 0
            and (move_1030_to_1130 / move_to_1030) < -0.30
        )

        # Option data: straddle snapshot at 11:30, EOD close from 1h bars
        try:
            ladder = build_ladder(TICKER, date_str, call_put="both", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        eod_close = float(ladder.underlying_1h.iloc[-1]["close"])
        ts_1130 = pd.Timestamp(date_str + " 11:30", tz="America/New_York")
        sc = get_atm_snapshot(ladder, ts_1130, "C")
        sp = get_atm_snapshot(ladder, ts_1130, "P")
        if sc is None or sp is None or sc["mid_price"] is None or sp["mid_price"] is None:
            continue

        strike       = sc["strike"]
        straddle_mid = sc["mid_price"] + sp["mid_price"]
        pnl          = straddle_mid - abs(eod_close - strike)

        if is_signal:
            n_signals += 1
            reversal_pnls.append(pnl)
            if len(trades) < 20:
                trades.append(TradeRecord(
                    date=date_str, signal=round(move_to_1030 * 100, 4), outcome=round(pnl, 4),
                    notes=f"move={move_to_1030:.3%} retrace={move_1030_to_1130:.3%} straddle={straddle_mid:.3f}",
                ))
        else:
            non_reversal_pnls.append(pnl)

    n_with_data = len(reversal_pnls) + len(non_reversal_pnls)

    # Always include _raw so combine step can pool across months even if insufficient per month
    _raw_data = {"reversal_pnls": reversal_pnls, "non_reversal_pnls": non_reversal_pnls}

    if n_with_data < 10 or len(reversal_pnls) < 5 or len(non_reversal_pnls) < 5:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H25", ticker=TICKER,
            period_start=_RUN_START, period_end=_RUN_END,
            raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=n_attempted - n_with_data,
            exclusion_reason="days without complete Databento bars or option ladder excluded",
            n_observations=n_with_data, n_signals=n_signals,
            metric_name="1_minus_var_ratio_reversal_vs_non", metric_value=float("nan"),
            support_threshold=0.0, reject_threshold=-0.1,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=(f"Too few observations: reversal={len(reversal_pnls)}, "
                            f"non-reversal={len(non_reversal_pnls)} (need ≥ 5 each)."),
            data_notes="proxy_tested",
            extra_metrics={
                **_ladder_approx_meta(n_attempted, n_with_data),
                "n_reversal_days": len(reversal_pnls),
                "n_non_reversal_days": len(non_reversal_pnls),
                "_raw": _raw_data,
            },
        )

    var_rev = float(np.var(reversal_pnls))
    var_non = float(np.var(non_reversal_pnls))
    ratio   = var_rev / max(var_non, 1e-10)
    metric  = 1.0 - ratio   # > 0 means reversal days have lower variance

    _, p_val = (stats.levene(reversal_pnls, non_reversal_pnls)
                if len(reversal_pnls) >= 3 and len(non_reversal_pnls) >= 3
                else (float("nan"), float("nan")))
    pct = n_with_data / max(n_attempted, 1)
    cov = f" [{n_signals} reversal / {len(non_reversal_pnls)} non-reversal days]"

    if metric > 0 and not np.isnan(p_val) and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Lower variance on reversal days: ratio={ratio:.3f} Levene p={p_val:.4f}.{cov}")
    elif metric < -0.1:
        verdict = BacktestVerdict.REJECTED
        reason = f"Higher variance on reversal days: ratio={ratio:.3f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"ratio={ratio:.3f} metric={metric:.3f} Levene p={p_val:.4f}.{cov}"

    print(f"  H25: {n_signals} reversal days, var_ratio={ratio:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H25", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=raw - n_with_data,
        exclusion_reason="days without 11:30 straddle snapshot excluded",
        n_observations=n_with_data, n_signals=n_signals,
        metric_name="1_minus_var_ratio_reversal_vs_non",
        metric_value=round(metric, 4),
        support_threshold=0.0, reject_threshold=-0.1,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        trades=trades,
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_with_data),
            "n_reversal_days": len(reversal_pnls),
            "n_non_reversal_days": len(non_reversal_pnls),
            "var_reversal": round(var_rev, 4),
            "var_non_reversal": round(var_non, 4),
            "var_ratio": round(ratio, 4),
            "mean_pnl_reversal": round(float(np.mean(reversal_pnls)), 4),
            "mean_pnl_non_reversal": round(float(np.mean(non_reversal_pnls)), 4),
            "levene_p": round(p_val, 4) if not np.isnan(p_val) else None,
            "approx_note": "Databento 5-min bars; signal: |move|>0.6% open→10:30 AND retrace≥30% by 11:30",
            "_raw": _raw_data,
        },
    )


# ── H26: VIX Futures Roll Yield by Time of Day ───────────────────────────────

def run_h26(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Intraday VIX futures roll yield (front-month futures minus VIX spot) is
    concentrated in the first and last hour of trading.

    Requires: intraday VIX futures and VIX spot data by time of day.
    """
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"],
        hypothesis_title=hyp["title"],
        hypothesis_number="H26",
        ticker="VX",
        period_start=TEST_WINDOW_START,
        period_end=TEST_WINDOW_END,
        raw_rows=len(daily),
        rows_after_validation=0,
        rows_excluded=len(daily),
        exclusion_reason="VIX futures intraday data not present in current dataset",
        n_observations=0,
        n_signals=0,
        metric_name="vix_roll_yield_first_last_hour_vs_mid",
        metric_value=float("nan"),
        support_threshold=0.0,
        reject_threshold=-0.5,
        verdict=BacktestVerdict.INSUFFICIENT_DATA,
        verdict_reason=(
            "Requires intraday VIX futures and VIX spot data by time of day. "
            "VIX futures data not present — this test requires a separate data source "
            "(e.g., CBOE futures settlement files or a futures data vendor)."
        ),
        data_notes="insufficient_data",
    )


# ── H27: Intraday Realized Vol Is U-Shaped ───────────────────────────────────────

def run_h27(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: 30-min realized vol is highest at open (slot 0) and close (slot 12) and
    lowest at midday (slots 5–8, 11:30–13:30). Tests Sinclair's Volatility Trading p.48.

    Uses Databento 5-min bars, full 2024-2026 window.
    slot_rv = pct_change().std() within each 6-bar slot (bars sliced first, returns computed inside).
    data_notes = directly_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=EOD_WINDOW_START, end=EOD_WINDOW_END)
    db = DatabentoPriceClient()

    slot0_rvs: list[float] = []   # 9:30–9:55 (open)
    slot12_rvs: list[float] = []  # 15:30–15:55 (close)
    midday_rvs: list[float] = []  # slots 5–8: 11:30–13:25

    n_attempted = 0
    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            continue
        if len(bars) < 70:
            continue

        def _slot_rv(slot: int) -> float:
            sb = bars.iloc[slot * 6:(slot + 1) * 6]
            return float(sb["close"].pct_change().dropna().std())

        rv0  = _slot_rv(0)
        rv12 = _slot_rv(12)
        rv_mid = [_slot_rv(s) for s in (5, 6, 7, 8)]

        if any(np.isnan(v) for v in [rv0, rv12] + rv_mid):
            continue

        slot0_rvs.append(rv0)
        slot12_rvs.append(rv12)
        midday_rvs.extend(rv_mid)

    n_with_data = len(slot0_rvs)
    if n_with_data < 20:
        return _insufficient("H27", hyp, "rv_open_close_vs_midday_ratio", 1.10, 1.0,
                             f"Too few days: {n_with_data} (need ≥ 20).", raw)

    open_close_rvs = slot0_rvs + slot12_rvs
    mean_oc = float(np.mean(open_close_rvs))
    mean_mid = float(np.mean(midday_rvs))
    rv_ratio = mean_oc / (mean_mid + 1e-12)

    _, p_val = stats.ttest_ind(open_close_rvs, midday_rvs)
    cov = f" [n_days={n_with_data}]"

    if rv_ratio >= 1.10 and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"U-shape confirmed: open+close RV={mean_oc:.5f} vs midday RV={mean_mid:.5f} ratio={rv_ratio:.3f} p={p_val:.4f}.{cov}"
    elif rv_ratio <= 1.0:
        verdict = BacktestVerdict.REJECTED
        reason = f"No U-shape: open+close RV={mean_oc:.5f} ≤ midday RV={mean_mid:.5f} ratio={rv_ratio:.3f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Direction correct (ratio={rv_ratio:.3f}) but not significant or below 1.10 threshold (p={p_val:.4f}).{cov}"

    print(f"  H27: n={n_with_data}, oc_rv={mean_oc:.5f}, mid_rv={mean_mid:.5f}, ratio={rv_ratio:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H27", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=n_attempted - n_with_data,
        exclusion_reason="days with <70 bars excluded",
        n_observations=n_with_data, n_signals=n_with_data,
        metric_name="rv_open_close_vs_midday_ratio",
        metric_value=round(rv_ratio, 4),
        support_threshold=1.10, reject_threshold=1.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "mean_rv_open_close": round(mean_oc, 6),
            "mean_rv_midday": round(mean_mid, 6),
            "rv_ratio": round(rv_ratio, 4),
            "p_value": round(float(p_val), 4),
            "_raw": {"open_close_rvs": open_close_rvs, "midday_rvs": midday_rvs},
        },
    )


# ── H28: Variance Premium Is Largest in the 15–20% IVX Regime ────────────────────

def run_h28(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: The variance premium (iv_30d − fwd_rv_20) is significantly larger when
    iv_30d is in the 15–20% range than when it is below 15% or above 20%.

    Tests Sinclair/Passarelli: moderate-IV regime is the variance-premium sweet spot.
    Uses same daily_series as H1. No option data or intraday bars needed.
    data_notes = directly_tested.
    """
    raw = len(daily)
    needed = ["iv_30d", "fwd_rv_20"]
    for col in needed:
        if col not in daily.columns or daily[col].isna().all():
            return _insufficient("H28", hyp, "variance_premium_by_ivx_regime", 0.0, -1.0,
                                 f"Column {col} missing from daily_series.", raw)

    df = daily[["date", "iv_30d", "fwd_rv_20"]].copy().dropna()
    df["vp"] = (df["iv_30d"] - df["fwd_rv_20"]) * 100  # vol-points, same as H1

    vp_low  = df.loc[df["iv_30d"] < 0.15,  "vp"].tolist()
    vp_mid  = df.loc[(df["iv_30d"] >= 0.15) & (df["iv_30d"] < 0.20), "vp"].tolist()
    vp_high = df.loc[df["iv_30d"] >= 0.20, "vp"].tolist()

    n_low, n_mid, n_high = len(vp_low), len(vp_mid), len(vp_high)
    print(f"  H28: buckets: low={n_low} mid={n_mid} high={n_high}")

    if n_mid < 10:
        return _insufficient("H28", hyp, "variance_premium_by_ivx_regime", 0.0, -1.0,
                             f"Too few mid-regime days: {n_mid} (need ≥ 10).", raw)

    mean_low  = float(np.mean(vp_low))  if vp_low  else float("nan")
    mean_mid  = float(np.mean(vp_mid))
    mean_high = float(np.mean(vp_high)) if vp_high else float("nan")

    # Primary test: mid vs (low + high) combined
    others = vp_low + vp_high
    _, p_mid_vs_others = (stats.ttest_ind(vp_mid, others) if len(others) >= 5
                          else (float("nan"), float("nan")))

    mean_others = float(np.mean(others)) if others else float("nan")
    diff = mean_mid - mean_others

    if diff > 0 and not np.isnan(p_mid_vs_others) and p_mid_vs_others < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Mid-regime (15–20%) VP={mean_mid:.2f} vpts > others={mean_others:.2f} vpts "
                  f"diff={diff:.2f} p={p_mid_vs_others:.4f}. low={mean_low:.2f} high={mean_high:.2f}.")
    elif diff <= 0:
        verdict = BacktestVerdict.REJECTED
        reason = (f"Mid-regime VP={mean_mid:.2f} ≤ others={mean_others:.2f} vpts. "
                  f"low={mean_low:.2f} high={mean_high:.2f}.")
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"Direction correct (mid={mean_mid:.2f} > others={mean_others:.2f}) "
                  f"but not significant (p={p_mid_vs_others:.4f}).")

    print(f"  H28: low={mean_low:.2f} mid={mean_mid:.2f} high={mean_high:.2f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H28", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df), rows_excluded=raw - len(df),
        exclusion_reason="rows with missing iv_30d or fwd_rv_20 excluded",
        n_observations=len(df), n_signals=n_mid,
        metric_name="variance_premium_by_ivx_regime",
        metric_value=round(diff, 4),
        support_threshold=0.0, reject_threshold=-1.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "mean_vp_low":  round(mean_low,  4) if not np.isnan(mean_low)  else None,
            "mean_vp_mid":  round(mean_mid,  4),
            "mean_vp_high": round(mean_high, 4) if not np.isnan(mean_high) else None,
            "n_low": n_low, "n_mid": n_mid, "n_high": n_high,
            "p_mid_vs_others": round(float(p_mid_vs_others), 4) if not np.isnan(p_mid_vs_others) else None,
            "_raw": {"vp_low": vp_low, "vp_mid": vp_mid, "vp_high": vp_high},
        },
    )


# ── H29: 0DTE Straddle P&L % Higher When Sold at 14:00 vs. 12:00 ────────────────

def run_h29(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: 0DTE ATM straddle sold at 14:00 ET generates higher P&L as % of premium
    than the same structure sold at 12:00 ET. Theta acceleration (charm) in the final
    2 hours makes afternoon entry more efficient per dollar of premium collected.

    Source: Natenberg, Option Volatility and Pricing p.1094–1099.
    Extends H14 (open > noon, supported) further into the afternoon.
    Uses iVol for option snapshots + Databento for EOD close.
    data_notes = directly_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)
    db = DatabentoPriceClient()

    pnl_pct_1200: list[float] = []
    pnl_pct_1400: list[float] = []
    n_attempted = 0
    trades = []

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1

        # Databento bars for EOD close
        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            bars = pd.DataFrame()
        if bars.empty or len(bars) < 50:
            continue
        eod_close = float(bars.iloc[-1]["close"])  # 15:55 bar close = market close

        try:
            ladder = build_ladder(TICKER, date_str, call_put="both", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        ts_1200 = pd.Timestamp(date_str + " 12:00", tz="America/New_York")
        ts_1400 = pd.Timestamp(date_str + " 14:00", tz="America/New_York")

        sc_12 = get_atm_snapshot(ladder, ts_1200, "C")
        sp_12 = get_atm_snapshot(ladder, ts_1200, "P")
        sc_14 = get_atm_snapshot(ladder, ts_1400, "C")
        sp_14 = get_atm_snapshot(ladder, ts_1400, "P")

        if any(x is None for x in [sc_12, sp_12, sc_14, sp_14]):
            continue
        if any(x["mid_price"] is None for x in [sc_12, sp_12, sc_14, sp_14]):
            continue

        straddle_12 = sc_12["mid_price"] + sp_12["mid_price"]
        straddle_14 = sc_14["mid_price"] + sp_14["mid_price"]

        if straddle_12 < 0.01 or straddle_14 < 0.01:
            continue

        pnl_12 = straddle_12 - abs(eod_close - sc_12["strike"])
        pnl_14 = straddle_14 - abs(eod_close - sc_14["strike"])

        pct_12 = pnl_12 / straddle_12
        pct_14 = pnl_14 / straddle_14

        pnl_pct_1200.append(pct_12)
        pnl_pct_1400.append(pct_14)

        if len(trades) < 20:
            trades.append(TradeRecord(
                date=date_str,
                signal=round(straddle_14, 4),
                outcome=round(pct_14 - pct_12, 4),
                notes=f"straddle_12={straddle_12:.3f} pct_12={pct_12:.3f} straddle_14={straddle_14:.3f} pct_14={pct_14:.3f}",
            ))

    n_with_data = len(pnl_pct_1200)
    _raw_data = {"pnl_pct_1200": pnl_pct_1200, "pnl_pct_1400": pnl_pct_1400}

    if n_with_data < 10:
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H29", ticker=TICKER,
            period_start=_RUN_START, period_end=_RUN_END,
            raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=n_attempted - n_with_data,
            exclusion_reason="days without valid 12:00 and 14:00 straddle snapshots excluded",
            n_observations=n_attempted, n_signals=n_with_data,
            metric_name="pnl_pct_1400_minus_1200",
            metric_value=0.0, support_threshold=0.0, reject_threshold=-0.05,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few days: {n_with_data} (need ≥ 10).",
            data_notes="directly_tested", trades=trades,
            extra_metrics={**_ladder_approx_meta(n_attempted, n_with_data), "_raw": _raw_data},
        )

    mean_12 = float(np.mean(pnl_pct_1200))
    mean_14 = float(np.mean(pnl_pct_1400))
    diff = mean_14 - mean_12
    _, p_val = stats.ttest_rel(pnl_pct_1400, pnl_pct_1200)
    cov = f" [n={n_with_data}]"

    if diff > 0 and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"14:00 entry more efficient: pnl_pct_14={mean_14:.3f} > pnl_pct_12={mean_12:.3f} diff={diff:.3f} p={p_val:.4f}.{cov}"
    elif diff < -0.05:
        verdict = BacktestVerdict.REJECTED
        reason = f"12:00 entry is better: pnl_pct_12={mean_12:.3f} > pnl_pct_14={mean_14:.3f} diff={diff:.3f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Direction {'correct' if diff>0 else 'wrong'} (diff={diff:.3f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H29: n={n_with_data}, pnl_pct_12={mean_12:.3f}, pnl_pct_14={mean_14:.3f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H29", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_with_data, rows_excluded=n_attempted - n_with_data,
        exclusion_reason="days without valid 12:00 and 14:00 straddle snapshots excluded",
        n_observations=n_with_data, n_signals=n_with_data,
        metric_name="pnl_pct_1400_minus_1200",
        metric_value=round(diff, 4),
        support_threshold=0.0, reject_threshold=-0.05,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        trades=trades,
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_with_data),
            "mean_pnl_pct_1200": round(mean_12, 4),
            "mean_pnl_pct_1400": round(mean_14, 4),
            "diff": round(diff, 4),
            "p_value": round(float(p_val), 4),
            "_raw": _raw_data,
        },
    )


# ── H30: Opening 30-Min Burst Predicts Short-Term Reversal ───────────────────────

def run_h30(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: On days where the first 30-min QQQ return exceeds ±0.5%, the subsequent
    90-min return (10:00–11:30) reliably opposes the opening move.

    Successor to H18 (rejected unconditional autocorr). This is CONDITIONAL: only
    large opening moves are tested, making the claim actionable.

    Source: Sinclair, Positional Option Trading — opening auction overshoots theory.
    Uses Databento 5-min bars, full 2024-2026 window. data_notes = directly_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=EOD_WINDOW_START, end=EOD_WINDOW_END)
    db = DatabentoPriceClient()

    signed_reversals: list[float] = []
    burst_returns: list[float] = []
    n_attempted = 0

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1
        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            continue
        if len(bars) < 24:
            continue

        # First 30-min: bars 0-5 (9:30–9:55)
        # open_px = open of 9:30 bar = true market open (NOT a prior close)
        open_px = float(bars.iloc[0]["open"])
        close_slot0 = float(bars.iloc[5]["close"])  # 9:55 close ≈ 10:00
        if open_px <= 0:
            continue
        burst = (close_slot0 - open_px) / open_px

        # Only process if opening burst > 0.5%
        if abs(burst) <= 0.005:
            continue

        # Next 90-min: bars 6-23 (10:00–11:25, slots 2-4)
        slot2_open = float(bars.iloc[6]["open"])    # 10:00 open = true 10:00 price
        slot4_close = float(bars.iloc[23]["close"]) # 11:25 close ≈ 11:30
        if slot2_open <= 0:
            continue
        reversal_ret = (slot4_close - slot2_open) / slot2_open

        # signed_reversal > 0 means reversal occurred (opposite direction to burst)
        burst_direction = 1.0 if burst > 0 else -1.0
        signed_reversal = -burst_direction * reversal_ret

        signed_reversals.append(signed_reversal)
        burst_returns.append(burst)

    n_burst = len(signed_reversals)
    if n_burst < 20:
        return _insufficient("H30", hyp, "mean_signed_reversal_after_burst", 0.0, -0.001,
                             f"Too few burst days: {n_burst} (need ≥ 20).", raw)

    mean_rev = float(np.mean(signed_reversals))
    reversal_prop = sum(1 for x in signed_reversals if x > 0) / n_burst
    _, p_val = stats.ttest_1samp(signed_reversals, popmean=0)
    cov = f" [n_burst={n_burst}/{n_attempted}]"

    if mean_rev > 0 and reversal_prop > 0.55 and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"Reversal confirmed: mean_signed_rev={mean_rev:.4f} prop={reversal_prop:.2f} p={p_val:.4f}.{cov}"
    elif mean_rev <= 0:
        verdict = BacktestVerdict.REJECTED
        reason = f"No reversal: mean_signed_rev={mean_rev:.4f} (momentum persists).{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Direction correct (mean={mean_rev:.4f} prop={reversal_prop:.2f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H30: n_burst={n_burst}, mean_rev={mean_rev:.4f}, prop={reversal_prop:.2f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H30", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=n_burst, rows_excluded=n_attempted - n_burst,
        exclusion_reason="days with |first-30min return| ≤ 0.5% excluded (no burst signal)",
        n_observations=n_attempted, n_signals=n_burst,
        metric_name="mean_signed_reversal_after_burst",
        metric_value=round(mean_rev, 4),
        support_threshold=0.0, reject_threshold=-0.001,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "mean_signed_reversal": round(mean_rev, 4),
            "reversal_proportion": round(reversal_prop, 4),
            "p_value": round(float(p_val), 4),
            "n_burst_days": n_burst,
            "_raw": {"signed_reversals": signed_reversals, "burst_returns": burst_returns},
        },
    )


# ── H31: Bid-Ask Spread Widens Following Vol-Spike Slots ─────────────────────────

def run_h31(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ 0DTE ATM option bid-ask spread is wider in 30-min slots that follow
    a vol-spike slot (slot RV > 2× day's median slot RV) vs. normal-vol slots.

    Successor to H21 (inconclusive time-of-day test). Tests the vol-conditional
    mechanism: market makers widen spreads to manage gamma inventory after spikes.
    Source: Baird, Option Market Making Ch.1–3.
    Uses iVol bid-ask + Databento 5-min for slot RV. data_notes = directly_tested.
    """
    raw = len(daily)
    trading_days = pd.bdate_range(start=_RUN_START, end=_RUN_END)
    db = DatabentoPriceClient()

    spike_spreads: list[float] = []
    normal_spreads: list[float] = []
    n_attempted = 0
    n_days_with_data = 0

    for day in trading_days:
        date_str = day.strftime("%Y-%m-%d")
        n_attempted += 1

        try:
            bars = db.get_bars(TICKER, date_str, interval="5min")
        except Exception:
            bars = pd.DataFrame()
        if len(bars) < 70:
            continue

        try:
            ladder = build_ladder(TICKER, date_str, call_put="C", dte_target=0, ladder_width=3)
        except Exception:
            continue
        if ladder is None or ladder.underlying_1h.empty:
            continue

        ts_df = get_ladder_time_series(ladder, call_put="C")
        if ts_df.empty:
            continue
        clean_ts = ts_df[
            ~ts_df["no_data"] & ts_df["bid_price"].notna() & ts_df["ask_price"].notna() &
            (ts_df["bid_price"] > 0) & (ts_df["ask_price"] > 0)
        ].copy()
        clean_ts["spread"] = clean_ts["ask_price"] - clean_ts["bid_price"]
        if clean_ts.empty:
            continue

        # 30-min RV for all 13 slots
        slot_rvs = []
        for s in range(13):
            sb = bars.iloc[s * 6:(s + 1) * 6]
            rv = float(sb["close"].pct_change().dropna().std())
            slot_rvs.append(rv if not np.isnan(rv) else 0.0)

        day_median_rv = float(np.median([v for v in slot_rvs if v > 0]))
        if day_median_rv <= 0:
            continue

        day_contributed = False
        base_ts = pd.Timestamp(date_str + " 09:30", tz="America/New_York")

        for i in range(12):  # slot i → look at spread in slot i+1
            slot_start_i1 = base_ts + pd.Timedelta(minutes=30 * (i + 1))
            tol = pd.Timedelta(minutes=12)
            w = clean_ts[
                (clean_ts.index >= slot_start_i1 - tol) &
                (clean_ts.index <= slot_start_i1 + tol)
            ]
            if w.empty:
                continue
            spread_val = float(w.iloc[0]["spread"])
            if slot_rvs[i] > 2.0 * day_median_rv:
                spike_spreads.append(spread_val)
            else:
                normal_spreads.append(spread_val)
            day_contributed = True

        if day_contributed:
            n_days_with_data += 1

    gate = _coverage_gate(n_attempted, n_days_with_data, "H31", hyp,
                          "spread_after_spike_vs_normal_slot", 0.0, -0.5, raw)
    if gate:
        return gate

    if len(spike_spreads) < 20 or len(normal_spreads) < 20:
        # Store _raw so monthly combine can pool across months; don't use _insufficient() here
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H31", ticker=TICKER,
            period_start=_RUN_START, period_end=_RUN_END,
            raw_rows=raw, rows_after_validation=n_days_with_data, rows_excluded=n_attempted - n_days_with_data,
            exclusion_reason="days without slot RV and bid-ask data excluded",
            n_observations=n_days_with_data, n_signals=len(spike_spreads),
            metric_name="spread_after_spike_vs_normal_slot", metric_value=float("nan"),
            support_threshold=0.0, reject_threshold=-0.5,
            verdict=BacktestVerdict.INSUFFICIENT_DATA,
            verdict_reason=f"Too few observations: spike={len(spike_spreads)}, normal={len(normal_spreads)} (need ≥ 20 each).",
            data_notes="directly_tested",
            extra_metrics={
                **_ladder_approx_meta(n_attempted, n_days_with_data),
                "_raw": {"spike_spreads": spike_spreads, "normal_spreads": normal_spreads},
            },
        )

    mean_spike  = float(np.mean(spike_spreads))
    mean_normal = float(np.mean(normal_spreads))
    diff = mean_spike - mean_normal
    _, p_val = stats.ttest_ind(spike_spreads, normal_spreads)
    cov = f" [n_spike={len(spike_spreads)}, n_normal={len(normal_spreads)}]"

    if diff > 0 and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = f"Spread widens after vol spike: spike={mean_spike:.4f} > normal={mean_normal:.4f} diff={diff:.4f} p={p_val:.4f}.{cov}"
    elif diff <= 0:
        verdict = BacktestVerdict.REJECTED
        reason = f"No widening: spike spread={mean_spike:.4f} ≤ normal={mean_normal:.4f}.{cov}"
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = f"Direction correct (diff={diff:.4f}) but not significant (p={p_val:.4f}).{cov}"

    print(f"  H31: spike={mean_spike:.4f}, normal={mean_normal:.4f}, diff={diff:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H31", ticker=TICKER,
        period_start=_RUN_START, period_end=_RUN_END,
        raw_rows=raw, rows_after_validation=n_days_with_data, rows_excluded=n_attempted - n_days_with_data,
        exclusion_reason="days without slot RV and bid-ask data excluded",
        n_observations=n_days_with_data,
        n_signals=len(spike_spreads),
        metric_name="spread_after_spike_vs_normal_slot",
        metric_value=round(diff, 4),
        support_threshold=0.0, reject_threshold=-0.5,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            **_ladder_approx_meta(n_attempted, n_days_with_data),
            "mean_spike_spread":  round(mean_spike,  4),
            "mean_normal_spread": round(mean_normal, 4),
            "diff": round(diff, 4),
            "p_value": round(float(p_val), 4),
            "_raw": {"spike_spreads": spike_spreads, "normal_spreads": normal_spreads},
        },
    )


# ── Monthly combine ──────────────────────────────────────────────────────────────

def _combine_intraday_months(
    hnum: str,
    hyp: dict,
    month_results: dict[str, dict],
) -> BacktestResult:
    """
    Combine M1-M4 BacktestResult dicts for one intraday hypothesis into a full-window result.

    Pools raw observation lists from extra_metrics["_raw"], re-runs the hypothesis
    stats on the pooled data, and labels the result as full_window_combined.

    month_results: {"M1": result_dict, ...} — only present months included.
    """
    raw = len(pd.bdate_range(INTRADAY_WINDOW_START, INTRADAY_WINDOW_END))
    n_attempted_total = sum(r.get("extra_metrics", {}).get("n_days_attempted", 0) for r in month_results.values())
    n_with_data_total = sum(r.get("extra_metrics", {}).get("n_days_with_ladder_data", 0) for r in month_results.values())

    def _pool(key: str) -> list:
        out: list = []
        for r in month_results.values():
            out.extend(r.get("extra_metrics", {}).get("_raw", {}).get(key, []))
        return out

    months_run = sorted(month_results.keys())
    coverage_note = f"combined from {'+'.join(months_run)}: {n_with_data_total}/{n_attempted_total} days"

    combined_meta: dict = {
        "contract_selection_method": "intraday_atm_approx_small_strike_ladder",
        "strike_ladder_width": 3,
        "exact_chain_intraday": False,
        "minute_type": "MINUTE_5",
        "n_days_attempted": n_attempted_total,
        "n_days_with_ladder_data": n_with_data_total,
        "pct_days_with_data": round(n_with_data_total / max(n_attempted_total, 1), 3),
        "intraday_endpoint_used": "single-equity-optionsymbol-rawiv",
        "is_combined": True,
        "monthly_batch_mode": True,
        "full_window_combined_from_month_batches": True,
        "months_combined": months_run,
        "month_summary": {
            m: {
                "n_days_attempted": r.get("extra_metrics", {}).get("n_days_attempted", 0),
                "n_days_with_data": r.get("extra_metrics", {}).get("n_days_with_ladder_data", 0),
                "metric_value":     r.get("metric_value"),
                "verdict":          r.get("verdict"),
            }
            for m, r in month_results.items()
        },
    }

    pct = n_with_data_total / max(n_attempted_total, 1)
    if pct < 0.50:
        return _insufficient(hnum, hyp,
                             list(month_results.values())[0].get("metric_name", "metric"),
                             list(month_results.values())[0].get("support_threshold", 0.0),
                             list(month_results.values())[0].get("reject_threshold", 0.0),
                             f"Insufficient coverage across months: {coverage_note}", raw)

    cov_warn = f" [coverage {pct:.0%} — below 80%]" if pct < 0.80 else ""

    # ── H13: U-shape ──────────────────────────────────────────────────────
    if hnum == "H13":
        open_ivs  = _pool("open_ivs");  mid_ivs = _pool("mid_ivs");  close_ivs = _pool("close_ivs")
        n = len(open_ivs)
        if n < 10:
            return _insufficient(hnum, hyp, "u_shape_open_minus_mid", 0.0, -0.5,
                                 f"Pooled obs too few: {n}. {coverage_note}", raw)
        m_o, m_m, m_c = float(np.mean(open_ivs)), float(np.mean(mid_ivs)), float(np.mean(close_ivs))
        opm, cpm = m_o - m_m, m_c - m_m
        _, p_o = stats.ttest_rel(open_ivs, mid_ivs)
        _, p_c = stats.ttest_rel(close_ivs, mid_ivs)
        u = opm > 0 and cpm > 0
        sig = p_o < 0.05 and p_c < 0.05
        verdict = (BacktestVerdict.SUPPORTED if u and sig else
                   BacktestVerdict.INCONCLUSIVE if u else BacktestVerdict.REJECTED)
        reason = (f"Combined {coverage_note}. open={m_o:.3f} mid={m_m:.3f} close={m_c:.3f}. "
                  f"open-mid={opm:.4f} p={p_o:.4f}; close-mid={cpm:.4f} p={p_c:.4f}.{cov_warn}")
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H13", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
            exclusion_reason="days without full open/mid/close IV buckets excluded",
            n_observations=n, n_signals=n,
            metric_name="u_shape_open_minus_mid", metric_value=round(opm, 4),
            support_threshold=0.0, reject_threshold=-0.5,
            verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
            extra_metrics={**combined_meta, "mean_iv_open": round(m_o,4), "mean_iv_mid": round(m_m,4),
                           "mean_iv_close": round(m_c,4), "open_minus_mid": round(opm,4),
                           "close_minus_mid": round(cpm,4),
                           "p_open_vs_mid": round(float(p_o),4), "p_close_vs_mid": round(float(p_c),4)},
        )

    # ── H14: straddle open vs noon ────────────────────────────────────────
    if hnum == "H14":
        open_pnls = _pool("open_pnls");  noon_pnls = _pool("noon_pnls")
        n = len(open_pnls)
        if n < 10:
            return _insufficient(hnum, hyp, "open_vs_noon_pnl_diff", 0.5, -0.5,
                                 f"Pooled obs too few: {n}.", raw)
        m_o, m_n = float(np.mean(open_pnls)), float(np.mean(noon_pnls))
        diff = m_o - m_n
        diffs = [o - x for o, x in zip(open_pnls, noon_pnls)]
        _, p = stats.ttest_1samp(diffs, popmean=0)
        verdict = (BacktestVerdict.SUPPORTED if diff > 0.5 and p < 0.05 else
                   BacktestVerdict.REJECTED if diff < 0 else BacktestVerdict.INCONCLUSIVE)
        reason = f"Combined {coverage_note}. open={m_o:.3f} noon={m_n:.3f} diff={diff:.3f} p={p:.4f}.{cov_warn}"
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H14", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
            exclusion_reason="days without open+noon snapshots excluded",
            n_observations=n, n_signals=n,
            metric_name="open_vs_noon_pnl_diff", metric_value=round(diff, 4),
            support_threshold=0.5, reject_threshold=-0.5,
            verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
            extra_metrics={**combined_meta, "mean_open_pnl": round(m_o,4),
                           "mean_noon_pnl": round(m_n,4), "mean_diff": round(diff,4),
                           "p_value": round(float(p),4)},
        )

    # ── H19: skew after PM decline ────────────────────────────────────────
    if hnum == "H19":
        delta_skews = _pool("delta_skews")
        n_signals = sum(r.get("extra_metrics", {}).get("_raw", {}).get("n_signals", 0) for r in month_results.values())
        n = len(delta_skews)
        if n < 5:
            return _insufficient(hnum, hyp, "mean_skew_change_after_pm_decline", 0.0, -0.05,
                                 f"Too few signal days: {n}.", raw)
        m = float(np.mean(delta_skews))
        _, p = stats.ttest_1samp(delta_skews, popmean=0)
        verdict = (BacktestVerdict.SUPPORTED if m > 0 and p < 0.05 else
                   BacktestVerdict.REJECTED if m < 0 else BacktestVerdict.INCONCLUSIVE)
        reason = f"Combined {coverage_note}. mean_Δskew={m:.4f} p={p:.4f} ({n} signal days).{cov_warn}"
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H19", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n, rows_excluded=n_attempted_total - n,
            exclusion_reason="days without PM decline or missing OTM/ATM IV excluded",
            n_observations=n_attempted_total, n_signals=n_signals,
            metric_name="mean_skew_change_after_pm_decline", metric_value=round(m, 4),
            support_threshold=0.0, reject_threshold=-0.05,
            verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
            extra_metrics={**combined_meta, "n_signal_days": n_signals,
                           "mean_skew_change": round(m, 4), "p_value": round(float(p), 4)},
        )

    # ── H20: delta threshold vs fixed hedging ─────────────────────────────
    if hnum == "H20":
        ratios = _pool("ratios")
        n = len(ratios)
        if n < 10:
            return _insufficient(hnum, hyp, "threshold_vs_fixed_hedge_cost_ratio", 0.9, 1.1,
                                 f"Pooled obs too few: {n}.", raw)
        m = float(np.mean(ratios))
        _, p = stats.ttest_1samp(ratios, popmean=1.0)
        verdict = (BacktestVerdict.SUPPORTED if m < 0.9 and p < 0.05 else
                   BacktestVerdict.REJECTED if m >= 1.0 else BacktestVerdict.INCONCLUSIVE)
        reason = f"Combined {coverage_note}. ratio={m:.3f} p={p:.4f}.{cov_warn}"
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H20", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
            exclusion_reason="days without delta time series excluded",
            n_observations=n, n_signals=sum(1 for r in ratios if r < 1.0),
            metric_name="threshold_vs_fixed_hedge_cost_ratio", metric_value=round(m, 4),
            support_threshold=0.9, reject_threshold=1.1,
            verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
            extra_metrics={**combined_meta, "mean_ratio": round(m, 4),
                           "pct_days_threshold_cheaper": round(sum(1 for r in ratios if r < 1.0)/max(n,1), 3),
                           "p_value": round(float(p), 4)},
        )

    # ── H21: bid-ask spread open vs midday ────────────────────────────────
    if hnum == "H21":
        open_spreads = _pool("open_spreads");  mid_spreads = _pool("mid_spreads")
        n = len(open_spreads)
        if n < 10:
            return _insufficient(hnum, hyp, "spread_open_minus_midday_pct", 0.05, -0.05,
                                 f"Pooled obs too few: {n}.", raw)
        m_o, m_m = float(np.mean(open_spreads)), float(np.mean(mid_spreads))
        diff = m_o - m_m
        _, p = stats.ttest_rel(open_spreads, mid_spreads)
        verdict = (BacktestVerdict.SUPPORTED if diff > 0.05 and p < 0.05 else
                   BacktestVerdict.REJECTED if diff < 0 else BacktestVerdict.INCONCLUSIVE)
        reason = f"Combined {coverage_note}. open={m_o:.4f} mid={m_m:.4f} diff={diff:.4f} p={p:.4f}.{cov_warn}"
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H21", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
            exclusion_reason="days without bid/ask time series excluded",
            n_observations=n, n_signals=sum(1 for o, m in zip(open_spreads, mid_spreads) if o > m),
            metric_name="spread_open_minus_midday_pct", metric_value=round(diff, 4),
            support_threshold=0.05, reject_threshold=-0.05,
            verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
            extra_metrics={**combined_meta, "mean_open_spread": round(m_o,4),
                           "mean_midday_spread": round(m_m,4), "diff": round(diff,4),
                           "p_value": round(float(p),4)},
        )

    # ── H22: IV asymmetry down vs up ──────────────────────────────────────
    if hnum == "H22":
        down_chg = _pool("down_iv_changes");  up_chg = _pool("up_iv_changes")
        if len(down_chg) < 5 or len(up_chg) < 5:
            return _insufficient(hnum, hyp, "mean_iv_change_down_minus_up", 0.001, -0.001,
                                 f"Too few bars: down={len(down_chg)}, up={len(up_chg)}.", raw)
        m_d, m_u = float(np.mean(down_chg)), float(np.mean(up_chg))
        diff = m_d - m_u
        _, p = stats.ttest_ind(down_chg, up_chg)
        verdict = (BacktestVerdict.SUPPORTED if diff > 0 and p < 0.05 else
                   BacktestVerdict.REJECTED if diff <= 0 else BacktestVerdict.INCONCLUSIVE)
        reason = (f"Combined {coverage_note}. down={m_d:.4f} up={m_u:.4f} diff={diff:.4f} "
                  f"p={p:.4f} ({len(down_chg)} down, {len(up_chg)} up bars).{cov_warn}")
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H22", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=len(down_chg)+len(up_chg), rows_excluded=raw-n_with_data_total,
            exclusion_reason="days without IV/return pairs excluded",
            n_observations=n_with_data_total, n_signals=len(down_chg),
            metric_name="mean_iv_change_down_minus_up", metric_value=round(diff, 4),
            support_threshold=0.001, reject_threshold=-0.001,
            verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
            extra_metrics={**combined_meta, "mean_iv_chg_down": round(m_d,4),
                           "mean_iv_chg_up": round(m_u,4), "diff": round(diff,4),
                           "n_down_bars": len(down_chg), "n_up_bars": len(up_chg),
                           "p_value": round(float(p),4)},
        )

    # ── H25: reversal straddle ────────────────────────────────────────────
    if hnum == "H25":
        rev_pnls = _pool("reversal_pnls");  non_pnls = _pool("non_reversal_pnls")
        n_total = len(rev_pnls) + len(non_pnls)
        if n_total < 10 or len(rev_pnls) < 5 or len(non_pnls) < 5:
            return _insufficient(hnum, hyp, "1_minus_var_ratio_reversal_vs_non", 0.0, -0.1,
                                 f"Too few obs: reversal={len(rev_pnls)}, non={len(non_pnls)}.", raw)
        var_r, var_n = float(np.var(rev_pnls)), float(np.var(non_pnls))
        ratio = var_r / max(var_n, 1e-10)
        metric = 1.0 - ratio
        _, p = (stats.levene(rev_pnls, non_pnls) if len(rev_pnls) >= 3 and len(non_pnls) >= 3
                else (float("nan"), float("nan")))
        verdict = (BacktestVerdict.SUPPORTED if metric > 0 and not np.isnan(p) and p < 0.05 else
                   BacktestVerdict.REJECTED if metric < -0.1 else BacktestVerdict.INCONCLUSIVE)
        reason = (f"Combined {coverage_note}. ratio={ratio:.3f} metric={metric:.3f} "
                  f"Levene p={p:.4f} ({len(rev_pnls)} reversal, {len(non_pnls)} non).{cov_warn}")
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H25", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n_total, rows_excluded=raw - n_total,
            exclusion_reason="days without 11:30 straddle snapshot excluded",
            n_observations=n_total, n_signals=len(rev_pnls),
            metric_name="1_minus_var_ratio_reversal_vs_non", metric_value=round(metric, 4),
            support_threshold=0.0, reject_threshold=-0.1,
            verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
            extra_metrics={**combined_meta,
                           "n_reversal_days": len(rev_pnls), "n_non_reversal_days": len(non_pnls),
                           "var_reversal": round(var_r,4), "var_non_reversal": round(var_n,4),
                           "var_ratio": round(ratio,4), "levene_p": round(float(p),4) if not np.isnan(p) else None},
        )

    # ── H17: gamma scalp P&L spike vs flat ───────────────────────────────────
    if hnum == "H17":
        spike_pnls = _pool("spike_pnls")
        flat_pnls  = _pool("flat_pnls")
        n_spike, n_flat = len(spike_pnls), len(flat_pnls)
        if n_spike < 5 or n_flat < 5:
            return _insufficient(hnum, hyp, "mean_gamma_pnl_spike_vs_flat", 0.0, -0.5,
                                 f"Too few pooled days: spike={n_spike} flat={n_flat}.", raw)
        mean_spike = float(np.mean(spike_pnls))
        mean_flat  = float(np.mean(flat_pnls))
        _, p = stats.ttest_ind(spike_pnls, flat_pnls)
        p = float(p)
        verdict = (BacktestVerdict.SUPPORTED   if mean_spike > mean_flat and p < 0.05 else
                   BacktestVerdict.REJECTED    if mean_spike <= mean_flat else
                   BacktestVerdict.INCONCLUSIVE)
        reason = (f"Combined {coverage_note}. spike={mean_spike:.4f} flat={mean_flat:.4f} "
                  f"p={p:.4f} n_spike={n_spike} n_flat={n_flat}.{cov_warn}")
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H17", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n_spike + n_flat,
            rows_excluded=raw - (n_spike + n_flat),
            exclusion_reason="days without full bar data or option ladder excluded",
            n_observations=n_spike + n_flat, n_signals=n_spike,
            metric_name="mean_gamma_pnl_spike_vs_flat",
            metric_value=round(mean_spike - mean_flat, 4),
            support_threshold=0.0, reject_threshold=-0.5,
            verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
            extra_metrics={**combined_meta,
                           "mean_pnl_spike_days": round(mean_spike, 4),
                           "mean_pnl_flat_days":  round(mean_flat, 4),
                           "n_spike_days": n_spike, "n_flat_days": n_flat,
                           "p_value": round(p, 4)},
        )

    # ── H29: 0DTE straddle P&L% 14:00 vs 12:00 ──────────────────────────────
    if hnum == "H29":
        pct_12 = _pool("pnl_pct_1200");  pct_14 = _pool("pnl_pct_1400")
        n = min(len(pct_12), len(pct_14))
        if n < 10:
            return _insufficient(hnum, hyp, "pnl_pct_1400_minus_1200", 0.0, -0.05,
                                 f"Too few paired days: {n}. {coverage_note}", raw)
        diff = float(np.mean(pct_14)) - float(np.mean(pct_12))
        _, p = stats.ttest_rel(pct_14[:n], pct_12[:n])
        p = float(p)
        verdict = (BacktestVerdict.SUPPORTED   if diff > 0 and p < 0.05 else
                   BacktestVerdict.REJECTED    if diff < -0.05 else
                   BacktestVerdict.INCONCLUSIVE)
        reason = (f"Combined {coverage_note}. mean_1400={np.mean(pct_14):.4f} "
                  f"mean_1200={np.mean(pct_12):.4f} diff={diff:.4f} p={p:.4f} n={n}.{cov_warn}")
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H29", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
            exclusion_reason="days without 12:00 and 14:00 ATM snapshots excluded",
            n_observations=n, n_signals=n,
            metric_name="pnl_pct_1400_minus_1200", metric_value=round(diff, 4),
            support_threshold=0.0, reject_threshold=-0.05,
            verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
            extra_metrics={**combined_meta,
                           "mean_pnl_pct_1200": round(float(np.mean(pct_12)), 4),
                           "mean_pnl_pct_1400": round(float(np.mean(pct_14)), 4),
                           "n_paired_days": n, "p_value": round(p, 4)},
        )

    # ── H31: bid-ask spread after vol-spike slots ─────────────────────────────
    if hnum == "H31":
        spike_sp = _pool("spike_spreads");  normal_sp = _pool("normal_spreads")
        n_spike, n_normal = len(spike_sp), len(normal_sp)
        if n_spike < 20 or n_normal < 20:
            return _insufficient(hnum, hyp, "spread_after_spike_vs_normal_slot", 0.0, -0.01,
                                 f"Too few obs: spike={n_spike} normal={n_normal}. {coverage_note}", raw)
        m_spike = float(np.mean(spike_sp))
        m_normal = float(np.mean(normal_sp))
        diff = m_spike - m_normal
        _, p = stats.ttest_ind(spike_sp, normal_sp)
        p = float(p)
        verdict = (BacktestVerdict.SUPPORTED   if diff > 0 and p < 0.05 else
                   BacktestVerdict.REJECTED    if diff <= 0 else
                   BacktestVerdict.INCONCLUSIVE)
        reason = (f"Combined {coverage_note}. spike={m_spike:.4f} normal={m_normal:.4f} "
                  f"diff={diff:.4f} p={p:.4f} n_spike={n_spike} n_normal={n_normal}.{cov_warn}")
        return BacktestResult(
            hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
            hypothesis_number="H31", ticker=TICKER,
            period_start=INTRADAY_WINDOW_START, period_end=INTRADAY_WINDOW_END,
            raw_rows=raw, rows_after_validation=n_spike + n_normal,
            rows_excluded=raw - (n_spike + n_normal),
            exclusion_reason="slot pairs without both RV and bid-ask data excluded",
            n_observations=n_spike + n_normal, n_signals=n_spike,
            metric_name="spread_after_spike_vs_normal_slot", metric_value=round(diff, 4),
            support_threshold=0.0, reject_threshold=-0.01,
            verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
            extra_metrics={**combined_meta,
                           "mean_spread_after_spike": round(m_spike, 4),
                           "mean_spread_after_normal": round(m_normal, 4),
                           "n_spike_slots": n_spike, "n_normal_slots": n_normal,
                           "p_value": round(p, 4)},
        )

    raise ValueError(f"No combine logic defined for {hnum}")


def _load_monthly_results(month: str) -> dict[str, dict]:
    """Load a monthly results file. Returns {hnum: result_dict}."""
    path = MONTHLY_DIR / f"backtest_results_{month}.json"
    if not path.exists():
        return {}
    records = json.loads(path.read_text())
    return {r["hypothesis_number"]: r for r in records}


def _save_monthly_results(results_map: dict[str, dict], month: str) -> None:
    path = MONTHLY_DIR / f"backtest_results_{month}.json"
    records = _sanitise_for_json(list(results_map.values()))
    path.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} monthly results → {path}")


# ── H32: Parkinson Estimator vs Close-to-Close for 5-Day RV Forecasting ─────────

def run_h32(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Parkinson estimator produces lower RMSE than CC when forecasting
    next-5-day realized vol. data_notes = directly_tested.
    """
    raw = len(daily)
    needed = ["high", "low", "close"]
    df = daily.dropna(subset=needed).copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    if len(df) < 40:
        return _insufficient("H32", hyp, "rmse_ratio_parkinson_vs_cc", 1.0, 1.05,
                             f"Too few rows: {len(df)}", raw)

    WINDOW = 20
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))

    # Parkinson rolling estimator (annualized)
    df["ln_hl2"] = np.log(df["high"] / df["low"]) ** 2
    pk_var = df["ln_hl2"].rolling(WINDOW).mean() / (4 * np.log(2))
    df["park_vol"] = np.sqrt(pk_var * 252)

    # Close-to-close rolling estimator (annualized)
    df["cc_vol"] = df["log_return"].rolling(WINDOW).std() * np.sqrt(252)

    # 5-day forward realized vol (annualized)
    fwd_rv_list = []
    for i in range(len(df)):
        window = df["log_return"].iloc[i + 1: i + 6]
        if len(window) == 5:
            fwd_rv_list.append(float(np.std(window, ddof=1) * np.sqrt(252)))
        else:
            fwd_rv_list.append(float("nan"))
    df["fwd_rv_5d"] = fwd_rv_list

    valid = df.dropna(subset=["park_vol", "cc_vol", "fwd_rv_5d"]).copy()
    n = len(valid)

    if n < 20:
        return _insufficient("H32", hyp, "rmse_ratio_parkinson_vs_cc", 1.0, 1.05,
                             f"Too few valid paired rows: {n}", raw)

    rmse_park = float(np.sqrt(np.mean((valid["park_vol"] - valid["fwd_rv_5d"]) ** 2)))
    rmse_cc   = float(np.sqrt(np.mean((valid["cc_vol"]   - valid["fwd_rv_5d"]) ** 2)))
    ratio = rmse_park / rmse_cc if rmse_cc > 0 else float("nan")

    # Diebold-Mariano: test if squared errors differ
    err_park = (valid["park_vol"] - valid["fwd_rv_5d"]) ** 2
    err_cc   = (valid["cc_vol"]   - valid["fwd_rv_5d"]) ** 2
    d = err_park - err_cc
    _, p = stats.ttest_1samp(d, 0.0)

    # Subgroup: days where H/L range > 1.5%
    valid["range_pct"] = (valid["high"] - valid["low"]) / valid["open"].fillna(valid["close"])
    wide = valid[valid["range_pct"] > 0.015]
    ratio_wide = float("nan")
    if len(wide) >= 10:
        rmse_park_w = float(np.sqrt(np.mean((wide["park_vol"] - wide["fwd_rv_5d"]) ** 2)))
        rmse_cc_w   = float(np.sqrt(np.mean((wide["cc_vol"]   - wide["fwd_rv_5d"]) ** 2)))
        ratio_wide = rmse_park_w / rmse_cc_w if rmse_cc_w > 0 else float("nan")

    SUPPORT_THRESHOLD = 0.95
    REJECT_THRESHOLD  = 1.0
    if ratio < SUPPORT_THRESHOLD and not np.isnan(p) and p < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Parkinson RMSE ratio={ratio:.4f} < {SUPPORT_THRESHOLD} p={p:.4f} n={n}. "
                  f"Wide-range subgroup ratio={ratio_wide:.4f}.")
    elif ratio >= REJECT_THRESHOLD:
        verdict = BacktestVerdict.REJECTED
        reason = f"Parkinson RMSE ratio={ratio:.4f} >= 1.0 — CC performs as well or better."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"Direction correct (ratio={ratio:.4f} < 1.0) but not significant "
                  f"(p={p:.4f}, need p<0.05 AND ratio<{SUPPORT_THRESHOLD}).")

    print(f"  H32: ratio={ratio:.4f} p={p:.4f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H32", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
        exclusion_reason="rows with missing OHLC or insufficient forward window excluded",
        n_observations=n, n_signals=int((valid["range_pct"] > 0.015).sum()),
        metric_name="rmse_ratio_parkinson_vs_cc",
        metric_value=round(ratio, 4),
        support_threshold=SUPPORT_THRESHOLD, reject_threshold=REJECT_THRESHOLD,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "rmse_parkinson": round(rmse_park, 6), "rmse_cc": round(rmse_cc, 6),
            "p_dm_test": round(float(p), 4), "n_wide_range": len(wide),
            "rmse_ratio_wide_range": round(ratio_wide, 4) if not np.isnan(ratio_wide) else None,
        },
    )


# ── H33: IV Mean Reversion Faster in Low-Vol (<15%) Than High-Vol (>30%) Regime ──

def run_h33(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: AR(1) mean-reversion speed is greater (faster reversion) in IVX < 15%
    regime than in IVX > 30% regime. data_notes = directly_tested.
    """
    raw = len(daily)
    if "iv_30d" not in daily.columns or daily["iv_30d"].isna().all():
        return _insufficient("H33", hyp, "ar1_reversion_speed_low_vs_high", 0.0, -0.1,
                             "iv_30d column missing.", raw)

    df = daily[["date", "iv_30d"]].dropna().copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    if len(df) < 60:
        return _insufficient("H33", hyp, "ar1_reversion_speed_low_vs_high", 0.0, -0.1,
                             f"Too few rows: {len(df)}", raw)

    # Deviation from rolling 252-day mean (capped at available data)
    df["rolling_mean"] = df["iv_30d"].rolling(min(252, len(df) // 2), min_periods=20).mean()
    df["deviation"] = df["iv_30d"] - df["rolling_mean"]
    df["dev_lag1"] = df["deviation"].shift(1)
    df = df.dropna(subset=["deviation", "dev_lag1", "rolling_mean"])

    def _ar1_beta(sub: pd.DataFrame) -> tuple[float, int]:
        if len(sub) < 10:
            return float("nan"), len(sub)
        slope, _, _, _, _ = stats.linregress(sub["dev_lag1"], sub["deviation"])
        return float(slope), len(sub)

    low  = df[df["iv_30d"] < 0.15]
    mid  = df[(df["iv_30d"] >= 0.15) & (df["iv_30d"] < 0.30)]
    high = df[df["iv_30d"] >= 0.30]

    beta_low,  n_low  = _ar1_beta(low)
    beta_mid,  n_mid  = _ar1_beta(mid)
    beta_high, n_high = _ar1_beta(high)

    # Reversion speed = |1 - beta| (higher = faster mean reversion)
    speed_low  = abs(1 - beta_low)  if not np.isnan(beta_low)  else float("nan")
    speed_high = abs(1 - beta_high) if not np.isnan(beta_high) else float("nan")
    diff = speed_low - speed_high  # positive = low regime reverts faster

    print(f"  H33: n_low={n_low} n_mid={n_mid} n_high={n_high}")
    print(f"       beta_low={beta_low:.4f} speed_low={speed_low:.4f} | "
          f"beta_high={beta_high:.4f} speed_high={speed_high:.4f} diff={diff:.4f}")

    # Bootstrap test for diff in AR(1) betas
    p = float("nan")
    if n_low >= 10 and n_high >= 10:
        rng = np.random.default_rng(42)
        n_boot = 2000
        boot_diffs = []
        for _ in range(n_boot):
            sl = low.sample(n=len(low), replace=True, random_state=None)
            sh = high.sample(n=len(high), replace=True, random_state=None)
            bl, _ = _ar1_beta(sl)
            bh, _ = _ar1_beta(sh)
            if not np.isnan(bl) and not np.isnan(bh):
                boot_diffs.append(abs(1 - bl) - abs(1 - bh))
        if boot_diffs:
            p = float(np.mean(np.array(boot_diffs) <= 0))  # one-sided: H0: speed_low <= speed_high

    SUPPORT = 0.02
    REJECT  = -0.01
    if not np.isnan(diff) and diff > SUPPORT and (np.isnan(p) or p < 0.10):
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Low-regime reverts faster: speed_low={speed_low:.4f} speed_high={speed_high:.4f} "
                  f"diff={diff:.4f} boot_p={p:.4f} n_low={n_low} n_high={n_high}.")
    elif not np.isnan(diff) and diff < REJECT:
        verdict = BacktestVerdict.REJECTED
        reason = (f"High-regime reverts faster: speed_low={speed_low:.4f} speed_high={speed_high:.4f} "
                  f"diff={diff:.4f}.")
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"diff={diff:.4f} not conclusive (need >{SUPPORT} or p<0.10). "
                  f"speed_low={speed_low:.4f} speed_high={speed_high:.4f} boot_p={p:.4f}.")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H33", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df), rows_excluded=raw - len(df),
        exclusion_reason="rows with missing iv_30d or insufficient rolling window excluded",
        n_observations=len(df), n_signals=n_low,
        metric_name="ar1_reversion_speed_low_vs_high",
        metric_value=round(diff, 4) if not np.isnan(diff) else float("nan"),
        support_threshold=SUPPORT, reject_threshold=REJECT,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "beta_low": round(beta_low, 4) if not np.isnan(beta_low) else None,
            "beta_mid": round(beta_mid, 4) if not np.isnan(beta_mid) else None,
            "beta_high": round(beta_high, 4) if not np.isnan(beta_high) else None,
            "speed_low": round(speed_low, 4) if not np.isnan(speed_low) else None,
            "speed_high": round(speed_high, 4) if not np.isnan(speed_high) else None,
            "n_low": n_low, "n_mid": n_mid, "n_high": n_high,
            "bootstrap_p": round(p, 4) if not np.isnan(p) else None,
        },
    )


# ── H34: Forward Variance Premium (Term Structure Implied > Realized Forward Vol) ─

def run_h34(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Implied forward vol from 30/60d IVX term structure exceeds realized
    forward vol by >1 vol point on average. data_notes = directly_tested.
    """
    raw = len(daily)
    needed = ["iv_30d", "iv_60d", "close"]
    if not all(c in daily.columns for c in needed):
        return _insufficient("H34", hyp, "mean_implied_minus_realized_fwd_vol_vpts", 1.0, 0.0,
                             "iv_30d or iv_60d missing from daily_series.", raw)

    df = daily[["date", "iv_30d", "iv_60d", "close"]].dropna().copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    if len(df) < 60:
        return _insufficient("H34", hyp, "mean_implied_minus_realized_fwd_vol_vpts", 1.0, 0.0,
                             f"Too few rows: {len(df)}", raw)

    # Implied forward vol annualized: sigma_fwd = sqrt(sigma_60d^2 * 60 - sigma_30d^2 * 30) / 30
    # Both sigma values are already annualized. Convert to per-day variance first.
    # variance_30d = iv_30d^2 * (30/365) / (30/365) = iv_30d^2 (annualized)
    # Forward annualized variance = (iv_60d^2 * 60 - iv_30d^2 * 30) / 30
    fwd_var = df["iv_60d"] ** 2 * 60 - df["iv_30d"] ** 2 * 30
    df["implied_fwd_vol"] = np.where(fwd_var > 0, np.sqrt(fwd_var / 30), float("nan"))

    # Realized forward vol: CC RV over ~21 trading days starting ~21 trading days later
    FWD_OFFSET = 21   # approx 30 calendar days ≈ 21 trading days
    FWD_LENGTH = 21
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))

    realized_fwd = []
    for i in range(len(df)):
        start_i = i + FWD_OFFSET
        end_i   = start_i + FWD_LENGTH
        window = df["log_return"].iloc[start_i:end_i]
        if len(window) >= 10:
            realized_fwd.append(float(np.std(window, ddof=1) * np.sqrt(252)))
        else:
            realized_fwd.append(float("nan"))
    df["realized_fwd_vol"] = realized_fwd

    valid = df.dropna(subset=["implied_fwd_vol", "realized_fwd_vol"]).copy()
    n = len(valid)

    if n < 20:
        return _insufficient("H34", hyp, "mean_implied_minus_realized_fwd_vol_vpts", 1.0, 0.0,
                             f"Too few paired obs after fwd window shift: {n}", raw)

    diff_vpts = (valid["implied_fwd_vol"] - valid["realized_fwd_vol"]) * 100  # vol-points
    mean_diff = float(diff_vpts.mean())
    _, p = stats.ttest_1samp(diff_vpts.dropna(), 0.0)
    p = float(p)

    SUPPORT = 1.0   # vol points
    REJECT  = 0.0
    if mean_diff > SUPPORT and p < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Forward variance premium confirmed: mean diff={mean_diff:.2f} vol pts "
                  f"p={p:.4f} n={n}.")
    elif mean_diff <= REJECT:
        verdict = BacktestVerdict.REJECTED
        reason = f"No forward variance premium: mean diff={mean_diff:.2f} vol pts (<=0)."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"Direction present (diff={mean_diff:.2f} vpts) but threshold/significance not met "
                  f"(need >1.0 AND p<0.05). p={p:.4f} n={n}.")

    print(f"  H34: mean_fwd_premium={mean_diff:.3f} vpts p={p:.4f} n={n} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H34", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=n, rows_excluded=raw - n,
        exclusion_reason="rows without paired fwd window or missing iv_30d/iv_60d excluded",
        n_observations=n, n_signals=int((diff_vpts > SUPPORT).sum()),
        metric_name="mean_implied_minus_realized_fwd_vol_vpts",
        metric_value=round(mean_diff, 4),
        support_threshold=SUPPORT, reject_threshold=REJECT,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "mean_implied_fwd_vol": round(float(valid["implied_fwd_vol"].mean() * 100), 3),
            "mean_realized_fwd_vol": round(float(valid["realized_fwd_vol"].mean() * 100), 3),
            "p_ttest": round(p, 4), "n_obs": n,
        },
    )


# ── H35: High Volume Days Have Higher Realized Volatility ─────────────────────────

def run_h35(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When QQQ daily volume exceeds the 60-day median, same-day |return|
    is at least 40% higher. Spearman r(volume, |return|) > 0.50. directly_tested.
    """
    raw = len(daily)
    needed = ["volume", "close"]
    if not all(c in daily.columns for c in needed):
        return _insufficient("H35", hyp, "spearman_r_volume_vs_abs_return", 0.50, 0.0,
                             "volume or close missing.", raw)

    df = daily[["date", "volume", "close"]].dropna().copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df["abs_return"] = df["log_return"].abs()
    df = df.dropna(subset=["log_return", "volume"]).copy()

    if len(df) < 30:
        return _insufficient("H35", hyp, "spearman_r_volume_vs_abs_return", 0.50, 0.0,
                             f"Too few rows: {len(df)}", raw)

    r, p = stats.spearmanr(df["volume"], df["abs_return"])
    r, p = float(r), float(p)

    # High vs low volume median absolute return
    median_vol = df["volume"].rolling(60, min_periods=20).median().shift(1)
    df["vol_median"] = median_vol
    df2 = df.dropna(subset=["vol_median"])
    high_v = df2[df2["volume"] > df2["vol_median"]]["abs_return"]
    low_v  = df2[df2["volume"] <= df2["vol_median"]]["abs_return"]
    ratio_medians = (high_v.median() / low_v.median()) if low_v.median() > 0 else float("nan")

    SUPPORT = 0.50
    REJECT  = 0.30
    if r > SUPPORT and p < 0.001:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Spearman r={r:.4f} > {SUPPORT} p={p:.6f}. "
                  f"High-vol-day median |ret| {ratio_medians:.2f}x low-vol-day.")
    elif r < REJECT:
        verdict = BacktestVerdict.REJECTED
        reason = f"Spearman r={r:.4f} < {REJECT} — weak volume-volatility link."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"r={r:.4f} direction correct but below threshold {SUPPORT} "
                  f"or p={p:.6f} not strong enough.")

    print(f"  H35: spearman_r={r:.4f} p={p:.6f} ratio_medians={ratio_medians:.2f} → {verdict.value}")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H35", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df), rows_excluded=raw - len(df),
        exclusion_reason="rows with missing volume or close excluded",
        n_observations=len(df), n_signals=int((df["volume"] > df["volume"].median()).sum()),
        metric_name="spearman_r_volume_vs_abs_return",
        metric_value=round(r, 4),
        support_threshold=SUPPORT, reject_threshold=REJECT,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "p_spearman": round(p, 6), "n_high_vol_days": len(high_v),
            "n_low_vol_days": len(low_v),
            "median_abs_return_high": round(float(high_v.median()), 6),
            "median_abs_return_low":  round(float(low_v.median()),  6),
            "ratio_high_vs_low": round(ratio_medians, 4) if not np.isnan(ratio_medians) else None,
        },
    )


# ── H36: OTM Put IV Skew Mean-Reverts Within 5 Days After Extreme Levels ──────────

def run_h36(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When 25-delta put IV exceeds equidistant call IV by 6+ vol points,
    skew narrows ≥2 vol points over the following 5 trading days.
    Requires per-strike IV data not present in daily_series. insufficient_data.
    """
    raw = len(daily)
    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H36", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=0, rows_excluded=raw,
        exclusion_reason="Per-strike IV data (25-delta put vs call) not available in daily_series",
        n_observations=0, n_signals=0,
        metric_name="mean_skew_change_after_extreme_skew",
        metric_value=float("nan"),
        support_threshold=2.0, reject_threshold=1.0,
        verdict=BacktestVerdict.INSUFFICIENT_DATA,
        verdict_reason=(
            "Requires daily 25-delta put IV and 25-delta call IV from iVolatility option chain. "
            "daily_series contains only at-the-money IVX (30d/60d/90d). "
            "Need iVolatility single-stock-option-raw-iv with delta filtering."
        ),
        data_notes="insufficient_data",
        extra_metrics={},
    )


# ── H37: Iron Condor P&L Higher in 15-25% IVX Regime Than >30% (Proxy via VP) ────

def run_h37(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ iron condors generate higher risk-adjusted P&L in IVX 15-25% regime
    than in IVX >30% regime.

    Proxy: variance premium (iv_30d - fwd_rv_20) is used as a condor P&L proxy —
    positive VP means the straddle premium exceeds RV, which is the same condition
    under which a condor profits (strikes not breached). Group VP by IVX regime.
    data_notes = proxy_tested.
    """
    raw = len(daily)
    needed = ["iv_30d", "fwd_rv_20"]
    if not all(c in daily.columns for c in needed):
        return _insufficient("H37", hyp, "sharpe_ratio_mid_vs_fear_regime", 0.0, -0.5,
                             "iv_30d or fwd_rv_20 missing.", raw)

    df = daily[["date", "iv_30d", "fwd_rv_20"]].dropna().copy()
    if len(df) < 30:
        return _insufficient("H37", hyp, "sharpe_ratio_mid_vs_fear_regime", 0.0, -0.5,
                             f"Too few rows: {len(df)}", raw)

    df["vp"] = (df["iv_30d"] - df["fwd_rv_20"]) * 100  # variance premium in vol-points

    mid  = df[(df["iv_30d"] >= 0.15) & (df["iv_30d"] < 0.25)]["vp"]
    fear = df[df["iv_30d"] >= 0.30]["vp"]
    low  = df[df["iv_30d"] < 0.15]["vp"]

    def _sharpe(s: pd.Series) -> float:
        if len(s) < 5 or s.std() == 0:
            return float("nan")
        return float(s.mean() / s.std())

    sharpe_mid  = _sharpe(mid)
    sharpe_fear = _sharpe(fear)
    sharpe_low  = _sharpe(low)
    diff = sharpe_mid - sharpe_fear if not (np.isnan(sharpe_mid) or np.isnan(sharpe_fear)) else float("nan")

    p = float("nan")
    if len(mid) >= 5 and len(fear) >= 5:
        _, p = stats.ttest_ind(mid, fear)
        p = float(p)

    print(f"  H37: n_mid={len(mid)} n_fear={len(fear)} sharpe_mid={sharpe_mid:.3f} "
          f"sharpe_fear={sharpe_fear:.3f} diff={diff:.3f}")

    SUPPORT = 0.2
    REJECT  = -0.2
    if not np.isnan(diff) and diff > SUPPORT and (np.isnan(p) or p < 0.05):
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Mid-regime (15-25%) Sharpe={sharpe_mid:.3f} > fear (>30%) Sharpe={sharpe_fear:.3f} "
                  f"diff={diff:.3f} p={p:.4f} n_mid={len(mid)} n_fear={len(fear)}.")
    elif not np.isnan(diff) and diff < REJECT:
        verdict = BacktestVerdict.REJECTED
        reason = (f"Fear-regime VP Sharpe={sharpe_fear:.3f} >= mid-regime={sharpe_mid:.3f}. "
                  f"Hypothesis not supported.")
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"diff={diff:.3f} not conclusive. sharpe_mid={sharpe_mid:.3f} "
                  f"sharpe_fear={sharpe_fear:.3f} p={p:.4f}.")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H37", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df), rows_excluded=raw - len(df),
        exclusion_reason="rows with missing iv_30d or fwd_rv_20 excluded",
        n_observations=len(df), n_signals=len(mid),
        metric_name="sharpe_ratio_mid_vs_fear_regime",
        metric_value=round(diff, 4) if not np.isnan(diff) else float("nan"),
        support_threshold=SUPPORT, reject_threshold=REJECT,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "sharpe_mid_15_25": round(sharpe_mid, 4) if not np.isnan(sharpe_mid) else None,
            "sharpe_fear_30plus": round(sharpe_fear, 4) if not np.isnan(sharpe_fear) else None,
            "sharpe_low_sub15": round(sharpe_low, 4) if not np.isnan(sharpe_low) else None,
            "n_mid": len(mid), "n_fear": len(fear), "n_low": len(low),
            "p_ttest": round(p, 4) if not np.isnan(p) else None,
        },
    )


# ── H38: Skewness-Adjusted Kelly Reduces Max Drawdown vs Standard Kelly ───────────

def run_h38(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: Skewness-corrected Kelly fraction reduces max drawdown >25% vs standard
    Kelly with <20% return sacrifice for a simulated short straddle on QQQ.
    Uses variance premium series as straddle P&L proxy. directly_tested.
    """
    raw = len(daily)
    needed = ["iv_30d", "fwd_rv_20"]
    if not all(c in daily.columns for c in needed):
        return _insufficient("H38", hyp, "drawdown_ratio_skew_kelly_vs_standard", 1.0, 1.0,
                             "iv_30d or fwd_rv_20 missing.", raw)

    df = daily[["date", "iv_30d", "fwd_rv_20"]].dropna().copy()
    df = df.sort_values("date").reset_index(drop=True)

    if len(df) < 30:
        return _insufficient("H38", hyp, "drawdown_ratio_skew_kelly_vs_standard", 1.0, 1.0,
                             f"Too few rows: {len(df)}", raw)

    # Straddle P&L proxy: variance premium per day (sell IV, buy back realized vol)
    pnl = (df["iv_30d"] - df["fwd_rv_20"]).values  # fractional units, daily proxy

    mu    = float(np.mean(pnl))
    sigma = float(np.std(pnl, ddof=1))
    if sigma == 0:
        return _insufficient("H38", hyp, "drawdown_ratio_skew_kelly_vs_standard", 1.0, 1.0,
                             "Zero variance in P&L series.", raw)

    # Third central moment (for skewness correction)
    lambda3 = float(np.mean((pnl - mu) ** 3))

    # Standard Kelly: f* = mu/sigma^2
    f_standard = mu / (sigma ** 2)

    # Skewness-adjusted Kelly (Sinclair): f* ≈ mu/(mu^2 + sigma^2) + lambda3*mu^2/(mu^2+sigma^2)^3
    denom = mu ** 2 + sigma ** 2
    f_skew = mu / denom + lambda3 * mu ** 2 / (denom ** 3) if denom > 0 else f_standard

    # Cap fractions to avoid instability (real Kelly never > 1 or < 0)
    f_standard = float(np.clip(f_standard, 0.01, 1.0))
    f_skew     = float(np.clip(f_skew,     0.01, 1.0))

    def _simulate(pnl_series: np.ndarray, frac: float) -> tuple[float, float]:
        """Returns (cumulative_log_return, max_drawdown)."""
        wealth = 1.0
        peak   = 1.0
        max_dd = 0.0
        cum_ret = 0.0
        for r in pnl_series:
            wealth *= (1 + frac * r)
            wealth = max(wealth, 1e-9)
            if wealth > peak:
                peak = wealth
            dd = (peak - wealth) / peak
            if dd > max_dd:
                max_dd = dd
        cum_ret = wealth - 1.0
        return cum_ret, max_dd

    cum_std, dd_std  = _simulate(pnl, f_standard)
    cum_skew, dd_skew = _simulate(pnl, f_skew)

    dd_ratio  = dd_skew / dd_std  if dd_std  > 0 else float("nan")
    ret_ratio = cum_skew / cum_std if cum_std > 0 else float("nan")
    dd_reduction_pct = (1 - dd_ratio) * 100 if not np.isnan(dd_ratio) else float("nan")
    ret_sacrifice_pct = (1 - ret_ratio) * 100 if not np.isnan(ret_ratio) else float("nan")

    print(f"  H38: f_std={f_standard:.4f} f_skew={f_skew:.4f} skewness_lambda3={lambda3:.6f}")
    print(f"       dd_std={dd_std:.4f} dd_skew={dd_skew:.4f} dd_reduction={dd_reduction_pct:.1f}%")
    print(f"       cum_std={cum_std:.4f} cum_skew={cum_skew:.4f} ret_sacrifice={ret_sacrifice_pct:.1f}%")

    # Support: drawdown reduction >25% AND return sacrifice <20%
    supported = (not np.isnan(dd_reduction_pct) and dd_reduction_pct > 25 and
                 not np.isnan(ret_sacrifice_pct) and ret_sacrifice_pct < 20)
    rejected  = (not np.isnan(dd_reduction_pct) and dd_reduction_pct < 10)

    metric = dd_reduction_pct if not np.isnan(dd_reduction_pct) else float("nan")

    if supported:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Skew-adjusted Kelly reduces max DD by {dd_reduction_pct:.1f}% "
                  f"(f_std={f_standard:.3f} → f_skew={f_skew:.3f}) with only "
                  f"{ret_sacrifice_pct:.1f}% return sacrifice. lambda3={lambda3:.4f}.")
    elif rejected:
        verdict = BacktestVerdict.REJECTED
        reason = (f"DD reduction only {dd_reduction_pct:.1f}% < 10% threshold. "
                  f"Skewness correction provides minimal benefit.")
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"DD reduction={dd_reduction_pct:.1f}% return_sacrifice={ret_sacrifice_pct:.1f}%. "
                  f"Thresholds not both met (need DD_red>25% AND ret_sac<20%).")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H38", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df), rows_excluded=raw - len(df),
        exclusion_reason="rows with missing iv_30d or fwd_rv_20 excluded",
        n_observations=len(df), n_signals=len(df),
        metric_name="dd_reduction_pct_skew_kelly_vs_standard",
        metric_value=round(metric, 4) if not np.isnan(metric) else float("nan"),
        support_threshold=25.0, reject_threshold=10.0,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "f_standard_kelly": round(f_standard, 4),
            "f_skew_adjusted_kelly": round(f_skew, 4),
            "lambda3_skewness_moment": round(lambda3, 6),
            "max_dd_standard": round(dd_std, 4),
            "max_dd_skew_adjusted": round(dd_skew, 4),
            "dd_reduction_pct": round(dd_reduction_pct, 2) if not np.isnan(dd_reduction_pct) else None,
            "cum_return_standard": round(cum_std, 4),
            "cum_return_skew_adjusted": round(cum_skew, 4),
            "return_sacrifice_pct": round(ret_sacrifice_pct, 2) if not np.isnan(ret_sacrifice_pct) else None,
        },
    )


# ── H39: QQQ Realized Vol Has Hurst Exponent > 0.5 (Persistent Clustering) ───────

def _hurst_rs(series: np.ndarray, n_segments: int = 20) -> float:
    """Estimate Hurst exponent via R/S analysis over log-spaced window sizes."""
    n = len(series)
    if n < 20:
        return float("nan")
    min_w = max(8, n // 20)
    max_w = n // 2
    windows = np.unique(np.geomspace(min_w, max_w, n_segments).astype(int))
    rs_vals = []
    win_vals = []
    for w in windows:
        sub_rs = []
        for start in range(0, n - w + 1, w):
            chunk = series[start: start + w]
            m = np.mean(chunk)
            dev = np.cumsum(chunk - m)
            R = dev.max() - dev.min()
            S = np.std(chunk, ddof=1)
            if S > 0:
                sub_rs.append(R / S)
        if sub_rs:
            rs_vals.append(np.mean(sub_rs))
            win_vals.append(w)
    if len(win_vals) < 4:
        return float("nan")
    log_w  = np.log(win_vals)
    log_rs = np.log(rs_vals)
    H, _ = np.polyfit(log_w, log_rs, 1)
    return float(H)


def run_h39(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ 5-day realized vol has Hurst exponent H > 0.5 (persistent).
    Post-VIX-spike clustering is stronger. directly_tested.
    """
    raw = len(daily)
    needed = ["close", "iv_30d"]
    df = daily[["date", "close", "iv_30d"]].dropna(subset=["close"]).copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df = df.dropna(subset=["log_return"])

    if len(df) < 60:
        return _insufficient("H39", hyp, "hurst_exponent_5d_rv", 0.55, 0.50,
                             f"Too few rows: {len(df)}", raw)

    # 5-day rolling realized vol (annualized)
    df["rv_5d"] = df["log_return"].rolling(5).std() * np.sqrt(252)
    rv_series = df["rv_5d"].dropna().values

    H_full = _hurst_rs(rv_series)

    # Bootstrap test H=0.5 null
    rng = np.random.default_rng(42)
    n_boot = 1000
    boot_H = []
    for _ in range(n_boot):
        shuffled = rng.permutation(rv_series)
        boot_H.append(_hurst_rs(shuffled))
    boot_H = np.array(boot_H)
    p_val = float(np.mean(boot_H >= H_full))  # fraction of shuffled H >= observed H

    # Subgroup: post-VIX-spike (large IV 1-day change)
    df["iv_change"] = df["iv_30d"].diff().abs()
    spike_mask = df["iv_change"] > df["iv_change"].quantile(0.90)
    post_spike_indices = []
    for idx in df.index[spike_mask]:
        post_spike_indices.extend(range(idx + 1, min(idx + 11, len(rv_series))))
    valid_spike_idx = sorted(set(i for i in post_spike_indices if i < len(rv_series)))
    post_spike_rv = rv_series[valid_spike_idx] if valid_spike_idx else np.array([])
    calm_mask = np.ones(len(rv_series), dtype=bool)
    if valid_spike_idx:
        calm_mask[valid_spike_idx] = False
    calm_rv = rv_series[calm_mask]

    H_spike = _hurst_rs(post_spike_rv) if len(post_spike_rv) >= 20 else float("nan")
    H_calm  = _hurst_rs(calm_rv)       if len(calm_rv)       >= 20 else float("nan")

    print(f"  H39: H_full={H_full:.4f} p_bootstrap={p_val:.4f} "
          f"H_spike={H_spike:.4f} H_calm={H_calm:.4f}")

    SUPPORT = 0.55
    REJECT  = 0.50
    if not np.isnan(H_full) and H_full > SUPPORT and p_val < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Hurst H={H_full:.4f} > {SUPPORT} bootstrap_p={p_val:.4f}. "
                  f"Post-spike H={H_spike:.4f} calm H={H_calm:.4f}.")
    elif not np.isnan(H_full) and H_full < REJECT:
        verdict = BacktestVerdict.REJECTED
        reason = f"H={H_full:.4f} < 0.50 — vol is mean-reverting (anti-persistent)."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"H={H_full:.4f} between 0.50-{SUPPORT} — direction right but "
                  f"below significance threshold or bootstrap_p={p_val:.4f} not significant.")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H39", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(rv_series), rows_excluded=raw - len(rv_series),
        exclusion_reason="rows with missing close or insufficient 5-day window excluded",
        n_observations=len(rv_series), n_signals=int(H_full > SUPPORT) if not np.isnan(H_full) else 0,
        metric_name="hurst_exponent_5d_rv",
        metric_value=round(H_full, 4) if not np.isnan(H_full) else float("nan"),
        support_threshold=SUPPORT, reject_threshold=REJECT,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "H_full": round(H_full, 4) if not np.isnan(H_full) else None,
            "H_post_spike": round(H_spike, 4) if not np.isnan(H_spike) else None,
            "H_calm_periods": round(H_calm, 4) if not np.isnan(H_calm) else None,
            "bootstrap_p": round(p_val, 4),
            "n_rv_obs": len(rv_series),
        },
    )


# ── H40: Calendar Spread P&L Positive When Front IV > GARCH Forward Vol by 2+ pts ─

def run_h40(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: When QQQ front-month IV exceeds GARCH-implied forward vol by >2 vol pts,
    the long calendar spread generates positive P&L >60% of the time.
    Proxy: high signal days have higher subsequent VP (iv_30d > fwd_rv_20). directly_tested.
    """
    raw = len(daily)
    needed = ["iv_30d", "garch_vol", "fwd_rv_20"]
    if not all(c in daily.columns for c in needed):
        return _insufficient("H40", hyp, "win_rate_calendar_signal_days", 0.60, 0.50,
                             "iv_30d, garch_vol, or fwd_rv_20 missing.", raw)

    df = daily[["date", "iv_30d", "garch_vol", "fwd_rv_20"]].dropna().copy()
    if len(df) < 30:
        return _insufficient("H40", hyp, "win_rate_calendar_signal_days", 0.60, 0.50,
                             f"Too few rows: {len(df)}", raw)

    # Signal: front IV > GARCH forward vol by > 2 vol pts
    # GARCH vol is already annualized (same units as iv_30d)
    df["signal_strength"] = (df["iv_30d"] - df["garch_vol"]) * 100  # vol-points
    signal_days    = df[df["signal_strength"] > 2.0].copy()
    nonsignal_days = df[df["signal_strength"] <= 2.0].copy()

    if len(signal_days) < 10:
        return _insufficient("H40", hyp, "win_rate_calendar_signal_days", 0.60, 0.50,
                             f"Too few signal days: {len(signal_days)} (need ≥ 10)", raw)

    # Win = calendar spread profits = VP positive on signal days
    signal_days["win"] = signal_days["fwd_rv_20"] < signal_days["iv_30d"]
    win_rate_signal    = float(signal_days["win"].mean())
    win_rate_nonsignal = float(nonsignal_days["fwd_rv_20"].lt(nonsignal_days["iv_30d"]).mean()) if len(nonsignal_days) >= 5 else float("nan")

    # Binomial test: H0 win_rate = 0.50
    n_signal = len(signal_days)
    n_wins   = int(signal_days["win"].sum())
    _, p_binom = stats.binom_test(n_wins, n_signal, 0.5, alternative="greater") if hasattr(stats, "binom_test") else (None, float("nan"))
    if np.isnan(p_binom):
        from scipy.stats import binomtest
        p_binom = float(binomtest(n_wins, n_signal, 0.5, alternative="greater").pvalue)

    mean_vp_signal = float((signal_days["iv_30d"] - signal_days["fwd_rv_20"]).mean() * 100)

    print(f"  H40: n_signal={n_signal} win_rate={win_rate_signal:.3f} p={p_binom:.4f} "
          f"mean_vp_signal={mean_vp_signal:.2f}vpts")

    SUPPORT = 0.60
    REJECT  = 0.50
    if win_rate_signal > SUPPORT and p_binom < 0.05:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Signal days win_rate={win_rate_signal:.3f} > {SUPPORT} p={p_binom:.4f} "
                  f"n={n_signal} mean_VP={mean_vp_signal:.2f}vpts.")
    elif win_rate_signal <= REJECT:
        verdict = BacktestVerdict.REJECTED
        reason = f"Signal win_rate={win_rate_signal:.3f} <= {REJECT}."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"win_rate={win_rate_signal:.3f} direction right but "
                  f"not above {SUPPORT} threshold or p={p_binom:.4f} not significant.")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H40", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df), rows_excluded=raw - len(df),
        exclusion_reason="rows with missing iv_30d, garch_vol, or fwd_rv_20 excluded",
        n_observations=len(df), n_signals=n_signal,
        metric_name="win_rate_calendar_signal_days",
        metric_value=round(win_rate_signal, 4),
        support_threshold=SUPPORT, reject_threshold=REJECT,
        verdict=verdict, verdict_reason=reason, data_notes="proxy_tested",
        extra_metrics={
            "n_signal_days": n_signal, "n_nonsignal_days": len(nonsignal_days),
            "n_wins_on_signal": n_wins,
            "win_rate_nonsignal": round(win_rate_nonsignal, 4) if not np.isnan(win_rate_nonsignal) else None,
            "mean_vp_signal_vpts": round(mean_vp_signal, 3),
            "p_binomial": round(p_binom, 4),
        },
    )


# ── H41: QQQ Fat-Tail Kurtosis > 3 and 2x Higher in High-IV Than Low-IV Regime ───

def run_h41(daily: pd.DataFrame, hyp: dict) -> BacktestResult:
    """
    Claim: QQQ daily returns have excess kurtosis > 1.0 (fat tails), and
    kurtosis in IVX>25% regime is >= 2x kurtosis in IVX<15% regime.
    directly_tested.
    """
    from scipy.stats import kurtosis as _kurtosis
    raw = len(daily)
    needed = ["close", "iv_30d"]
    df = daily[["date", "close", "iv_30d"]].dropna().copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df = df.dropna(subset=["log_return", "iv_30d"])

    if len(df) < 40:
        return _insufficient("H41", hyp, "excess_kurtosis_full_and_ratio_high_vs_low", 1.0, 0.0,
                             f"Too few rows: {len(df)}", raw)

    # Full-sample excess kurtosis
    ek_full = float(_kurtosis(df["log_return"], fisher=True))  # excess kurtosis

    # By IV regime
    low  = df[df["iv_30d"] < 0.15]["log_return"]
    mid  = df[(df["iv_30d"] >= 0.15) & (df["iv_30d"] < 0.25)]["log_return"]
    high = df[df["iv_30d"] >= 0.25]["log_return"]

    ek_low  = float(_kurtosis(low,  fisher=True)) if len(low)  >= 10 else float("nan")
    ek_mid  = float(_kurtosis(mid,  fisher=True)) if len(mid)  >= 10 else float("nan")
    ek_high = float(_kurtosis(high, fisher=True)) if len(high) >= 10 else float("nan")

    ratio_high_vs_low = ek_high / ek_low if (not np.isnan(ek_low) and ek_low > 0) else float("nan")

    # Test H0: excess kurtosis = 0 (normal) via bootstrap
    rng = np.random.default_rng(42)
    n_boot = 2000
    boot_ek = [float(_kurtosis(rng.choice(df["log_return"].values, size=len(df), replace=True), fisher=True))
               for _ in range(n_boot)]
    p_ek = float(np.mean(np.array(boot_ek) <= 0))  # one-sided: H0 ek <= 0

    # Test regime difference via Mann-Whitney U
    p_regime = float("nan")
    if len(low) >= 10 and len(high) >= 10:
        _, p_regime = stats.mannwhitneyu(high.abs(), low.abs(), alternative="greater")
        p_regime = float(p_regime)

    print(f"  H41: ek_full={ek_full:.3f} ek_low={ek_low:.3f} ek_high={ek_high:.3f} "
          f"ratio={ratio_high_vs_low:.2f} p_ek={p_ek:.4f}")

    # Composite metric: excess kurtosis full
    metric = ek_full
    SUPPORT = 1.0
    REJECT  = 0.0
    regime_confirmed = (not np.isnan(ratio_high_vs_low) and ratio_high_vs_low >= 2.0
                        and not np.isnan(p_regime) and p_regime < 0.05)

    if ek_full > SUPPORT and p_ek < 0.05 and regime_confirmed:
        verdict = BacktestVerdict.SUPPORTED
        reason = (f"Excess kurtosis={ek_full:.3f} > 1.0 p={p_ek:.4f}. "
                  f"High-IV EK={ek_high:.3f} vs low-IV EK={ek_low:.3f} ratio={ratio_high_vs_low:.2f}x "
                  f"(>= 2x required) p_regime={p_regime:.4f}.")
    elif ek_full > SUPPORT and p_ek < 0.05:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"Full-sample EK confirmed ({ek_full:.3f} > 1.0, p={p_ek:.4f}) but "
                  f"regime ratio={ratio_high_vs_low:.2f}x or p_regime={p_regime:.4f} not sufficient for full support.")
    elif ek_full <= REJECT:
        verdict = BacktestVerdict.REJECTED
        reason = f"Excess kurtosis={ek_full:.3f} <= 0 — returns are platykurtic."
    else:
        verdict = BacktestVerdict.INCONCLUSIVE
        reason = (f"EK={ek_full:.3f} direction correct but not significant (p={p_ek:.4f}) "
                  f"or below threshold. regime_ratio={ratio_high_vs_low:.2f}.")

    return BacktestResult(
        hypothesis_id=hyp["hypothesis_id"], hypothesis_title=hyp["title"],
        hypothesis_number="H41", ticker=TICKER,
        period_start=EOD_WINDOW_START, period_end=EOD_WINDOW_END,
        raw_rows=raw, rows_after_validation=len(df), rows_excluded=raw - len(df),
        exclusion_reason="rows with missing close or iv_30d excluded",
        n_observations=len(df), n_signals=int(len(high)),
        metric_name="excess_kurtosis_full",
        metric_value=round(ek_full, 4),
        support_threshold=SUPPORT, reject_threshold=REJECT,
        verdict=verdict, verdict_reason=reason, data_notes="directly_tested",
        extra_metrics={
            "excess_kurtosis_full": round(ek_full, 4),
            "excess_kurtosis_low_iv": round(ek_low, 4) if not np.isnan(ek_low) else None,
            "excess_kurtosis_mid_iv": round(ek_mid, 4) if not np.isnan(ek_mid) else None,
            "excess_kurtosis_high_iv": round(ek_high, 4) if not np.isnan(ek_high) else None,
            "ratio_high_vs_low": round(ratio_high_vs_low, 3) if not np.isnan(ratio_high_vs_low) else None,
            "n_low": len(low), "n_mid": len(mid), "n_high": len(high),
            "p_kurtosis_bootstrap": round(p_ek, 4),
            "p_regime_mannwhitney": round(p_regime, 4) if not np.isnan(p_regime) else None,
        },
    )


# ── Dispatch ────────────────────────────────────────────────────────────────────

INTRADAY_RUNNERS: dict[str, callable] = {
    "H13": run_h13,
    "H14": run_h14,
    "H15": run_h15,
    "H16": run_h16,
    "H17": run_h17,
    "H18": run_h18,
    "H19": run_h19,
    "H20": run_h20,
    "H21": run_h21,
    "H22": run_h22,
    "H23": run_h23,
    "H24": run_h24,
    "H25": run_h25,
    "H26": run_h26,
    "H27": run_h27,
    "H28": run_h28,
    "H29": run_h29,
    "H30": run_h30,
    "H31": run_h31,
    "H32": run_h32,
    "H33": run_h33,
    "H34": run_h34,
    "H35": run_h35,
    "H36": run_h36,
    "H37": run_h37,
    "H38": run_h38,
    "H39": run_h39,
    "H40": run_h40,
    "H41": run_h41,
}


_INTRADAY_HYPOTHESES = {"H13", "H14", "H17", "H19", "H20", "H21", "H22", "H25", "H29", "H31"}


def main():
    global _RUN_START, _RUN_END, _RUN_MONTH
    parser = argparse.ArgumentParser(
        description=(
            "Run intraday backtests.\n\n"
            "Intraday rule: use --month M1/M2/.../M9 to run one monthly batch (Apr–Dec 2025).\n"
            "After all months: use --combine-months to merge into full-window result.\n"
            "EOD-only hypotheses (H16, H24) always use the full 2024-2026 window."
        )
    )
    parser.add_argument("--hypotheses", default="all", help="Comma-separated: H13,H16 or all")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--start-date", default=None, help="Custom run start YYYY-MM-DD (ad-hoc override)")
    parser.add_argument("--end-date",   default=None, help="Custom run end   YYYY-MM-DD (ad-hoc override)")
    parser.add_argument(
        "--month", choices=list(MONTHLY_BATCHES.keys()), default=None,
        help="Run a single monthly batch for intraday hypotheses. Sets start/end automatically.",
    )
    parser.add_argument(
        "--combine-months", action="store_true",
        help="Combine completed M1-M4 monthly files into a full-window result and write to main results.",
    )
    parser.add_argument(
        "--no-downstream", action="store_true",
        help="Skip automatic downstream update (17_score_and_report + 18_export_backtest_vault).",
    )
    args = parser.parse_args()

    # ── Resolve window ──────────────────────────────────────────────────────────
    if args.month:
        _RUN_MONTH = args.month
        _RUN_START, _RUN_END = MONTHLY_BATCHES[args.month]
    if args.start_date:
        _RUN_START = args.start_date
    if args.end_date:
        _RUN_END = args.end_date

    # ── Load hypothesis registry ────────────────────────────────────────────────
    hyp_file = EXPERIMENTS_DIR / "hypotheses.json"
    if not hyp_file.exists():
        raise SystemExit("experiments/hypotheses.json not found.")
    all_hyps = json.loads(hyp_file.read_text())
    hyp_by_num: dict[str, dict] = {f"H{i+1}": h for i, h in enumerate(all_hyps)}

    wanted = (
        list(INTRADAY_RUNNERS.keys())
        if args.hypotheses.lower() == "all"
        else [h.strip().upper() for h in args.hypotheses.split(",")]
    )
    unknown = [h for h in wanted if h not in INTRADAY_RUNNERS]
    if unknown:
        print(f"Unknown: {unknown}. Available: {list(INTRADAY_RUNNERS.keys())}")
        sys.exit(1)

    # ── Combine-months mode ─────────────────────────────────────────────────────
    if args.combine_months:
        intraday_wanted = [h for h in wanted if h in _INTRADAY_HYPOTHESES]
        print(f"Combining monthly results for: {intraday_wanted}")
        all_month_data: dict[str, dict[str, dict]] = {}
        for m in list(MONTHLY_BATCHES.keys()):
            mr = _load_monthly_results(m)
            if mr:
                print(f"  Loaded {m}: {list(mr.keys())}")
            for hnum, rdict in mr.items():
                all_month_data.setdefault(hnum, {})[m] = rdict

        existing = _load_existing_results()
        for hnum in intraday_wanted:
            mdata = all_month_data.get(hnum, {})
            if not mdata:
                print(f"  [skip] {hnum} — no monthly data found")
                continue
            hyp = hyp_by_num.get(hnum)
            if hyp is None:
                print(f"  [skip] {hnum} — not in hypotheses.json")
                continue
            try:
                result = _combine_intraday_months(hnum, hyp, mdata)
                existing[hnum] = result.model_dump()
                print(f"  {hnum} combined ({'+'.join(sorted(mdata.keys()))}): "
                      f"{result.verdict.value} — {result.verdict_reason[:70]}")
            except Exception as e:
                print(f"  [error] {hnum} combine failed: {e}")

        _save_results(existing)
        print(f"\nCombined {len(intraday_wanted)} intraday hypothesis(es) → {RESULTS_FILE}")
        if not args.no_downstream:
            _auto_update_downstream()
        return

    # ── Normal run mode ─────────────────────────────────────────────────────────
    daily = _load_daily()
    print(f"Loaded daily_series: {len(daily)} rows | EOD window: {EOD_WINDOW_START} → {EOD_WINDOW_END}")
    if _RUN_MONTH:
        print(f"Run window: {_RUN_MONTH} ({_RUN_START} → {_RUN_END})")
    else:
        print(f"Run window: {_RUN_START} → {_RUN_END}")
    _validate_daily_series(daily)

    existing = _load_existing_results()
    monthly_new: dict[str, dict] = {}

    for hnum in wanted:
        if hnum in existing and not args.force:
            print(f"[skip] {hnum} already in results (use --force)")
            continue

        hyp = hyp_by_num.get(hnum)
        if hyp is None:
            raise SystemExit(
                f"{hnum} not found in hypotheses.json — check H-number ordering "
                f"(hypotheses.json has {len(all_hyps)} entries: H1–H{len(all_hyps)})"
            )

        print(f"Running {hnum}: {hyp.get('title', '')[:60]}...")
        runner = INTRADAY_RUNNERS[hnum]
        result = runner(daily, hyp)

        rdict = result.model_dump()
        existing[hnum] = rdict
        if hnum in _INTRADAY_HYPOTHESES and _RUN_MONTH:
            monthly_new[hnum] = rdict
        print(f"  → {result.verdict.value}: {result.verdict_reason[:80]}")

    _save_results(existing)

    if monthly_new and _RUN_MONTH:
        existing_monthly = _load_monthly_results(_RUN_MONTH)
        existing_monthly.update(monthly_new)
        _save_monthly_results(existing_monthly, _RUN_MONTH)

    print(f"\nCompleted {len(wanted)} intraday backtest(s).")
    if _RUN_MONTH:
        remaining = [m for m in MONTHLY_BATCHES if m != _RUN_MONTH]
        print(f"Month {_RUN_MONTH} done. Remaining: {remaining}")
        print("After all months: python scripts/16_run_intraday_backtests.py --combine-months")
    elif not args.no_downstream:
        _auto_update_downstream()


if __name__ == "__main__":
    main()
