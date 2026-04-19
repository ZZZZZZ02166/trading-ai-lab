#!/usr/bin/env python3
"""
Phase 14c: Build processed time series from raw iVolatility data.

Deterministic — no API calls. Reads cached parquet from data/raw/,
computes derived series, writes to data/processed/.

Outputs:
  data/processed/daily_series.parquet
    columns: date, open, high, low, close, volume,
             log_return,
             hv_20_cc, hv_60_cc,       ← close-to-close HV
             hv_20_yz, hv_60_yz,       ← Yang-Zhang HV
             fwd_rv_20,                ← 20-day forward realized vol (ground truth for H9)
             garch_vol,                ← GARCH(1,1) conditional vol
             iv_30d, iv_60d, iv_90d,   ← IVX (if available)
             iv_hv_spread_20_cc,       ← 30d IVX minus 20d CC-HV
             iv_hv_spread_20_yz,       ← 30d IVX minus 20d YZ-HV
             vol_regime_pct,           ← percentile rank of iv_30d (0–1)

  data/processed/intraday_series.parquet  (if intraday data exists)
    columns: date, time, iv, time_bucket (open/mid/close),
             iv_pct_change_from_open, time_minutes_from_open

Usage:
    python scripts/14c_build_processed_series.py
    python scripts/14c_build_processed_series.py --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import numpy as np
import pandas as pd

from app.services.option_math import (
    close_to_close_hv,
    yang_zhang_hv,
    forward_realized_vol,
    garch_vol_forecast,
    iv_hv_spread,
)
from app.services.fill_model import reindex_to_trading_days, drop_leading_nans
from app.services.data_validator import validate_dataframe

RAW_DIR = BASE / "data" / "raw"
PROCESSED_DIR = BASE / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

DAILY_OUT = PROCESSED_DIR / "daily_series.parquet"
INTRADAY_OUT = PROCESSED_DIR / "intraday_series.parquet"


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first column name from candidates that exists in df."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _normalise_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise OHLCV column names to lowercase standard: date, open, high, low, close, volume.
    Handles common iVol naming variations.
    """
    rename = {}
    col_map = {
        "date": ["date", "trade_date", "tradedate", "datetime"],
        "open": ["open", "open_price", "openprice"],
        "high": ["high", "high_price", "highprice"],
        "low": ["low", "low_price", "lowprice"],
        "close": ["close", "close_price", "closeprice", "adj_close"],
        "volume": ["volume", "vol", "trading_volume"],
    }
    for target, candidates in col_map.items():
        for c in candidates:
            if c in df.columns and target not in df.columns:
                rename[c] = target
                break
    return df.rename(columns=rename)


def build_daily_series(force: bool = False) -> None:
    if DAILY_OUT.exists() and not force:
        print(f"daily_series.parquet already exists. Use --force to rebuild.")
        return

    # ── Load prices ─────────────────────────────────────────────────────────────
    prices_path = RAW_DIR / "qqq_eod_prices.parquet"
    if not prices_path.exists():
        raise SystemExit(
            f"qqq_eod_prices.parquet not found. Run scripts/14a_fetch_eod_data.py first."
        )

    prices = pd.read_parquet(prices_path)
    prices = _normalise_ohlc(prices)
    validate_dataframe(
        prices,
        required_cols=["close"],
        min_rows=50,
        name="qqq_eod_prices",
    )

    date_col = _find_col(prices, ["date", "trade_date", "datetime"]) or prices.columns[0]
    prices[date_col] = pd.to_datetime(prices[date_col])
    prices = prices.sort_values(date_col).reset_index(drop=True)

    start_str = str(prices[date_col].min())[:10]
    end_str = str(prices[date_col].max())[:10]
    print(f"Prices loaded: {len(prices)} rows, {start_str} → {end_str}")

    df = prices.copy()
    df["date"] = df[date_col]
    df = df.set_index("date")

    close = df["close"].astype(float)
    df["log_return"] = np.log(close / close.shift(1))

    # ── HV estimators ────────────────────────────────────────────────────────────
    print("Computing HV estimators...")
    df["hv_20_cc"] = close_to_close_hv(close, window=20)
    df["hv_60_cc"] = close_to_close_hv(close, window=60)

    has_ohlc = all(c in df.columns for c in ["open", "high", "low", "close"])
    if has_ohlc:
        ohlc = df[["open", "high", "low", "close"]].astype(float)
        df["hv_20_yz"] = yang_zhang_hv(ohlc, window=20)
        df["hv_60_yz"] = yang_zhang_hv(ohlc, window=60)
    else:
        print("  WARNING: OHLC columns not found — Yang-Zhang HV will be NaN")
        df["hv_20_yz"] = np.nan
        df["hv_60_yz"] = np.nan

    # ── Forward realised vol (ground truth for H9) ────────────────────────────
    print("Computing forward realised vol...")
    df["fwd_rv_20"] = forward_realized_vol(close, horizon=20)

    # ── GARCH conditional vol ─────────────────────────────────────────────────
    print("Fitting GARCH(1,1)...")
    df["garch_vol"] = garch_vol_forecast(df["log_return"])

    # ── IVX series ───────────────────────────────────────────────────────────────
    ivx_path = RAW_DIR / "qqq_ivx.parquet"
    if ivx_path.exists():
        print("Merging IVX data...")
        ivx = pd.read_parquet(ivx_path)
        ivx.columns = [c.lower().strip() for c in ivx.columns]
        ivx_date_col = _find_col(ivx, ["date", "trade_date", "datetime"]) or ivx.columns[0]
        ivx[ivx_date_col] = pd.to_datetime(ivx[ivx_date_col])
        ivx = ivx.set_index(ivx_date_col)

        # Map iVol IVX column names to standardised names.
        # iVol API returns "30d iv mean" / "60d iv mean" etc. (lowercased here).
        iv_col_map = {
            "iv_30d": ["30d iv mean", "ivx30", "ivx_30", "iv30", "iv_30", "ivx30d"],
            "iv_60d": ["60d iv mean", "ivx60", "ivx_60", "iv60", "iv_60", "ivx60d"],
            "iv_90d": ["90d iv mean", "ivx90", "ivx_90", "iv90", "iv_90", "ivx90d"],
        }
        for target, candidates in iv_col_map.items():
            found = _find_col(ivx, candidates)
            if found:
                ivx[target] = ivx[found]

        df = df.join(ivx[["iv_30d", "iv_60d", "iv_90d"]], how="left")

        # IV-HV spreads
        if "iv_30d" in df.columns:
            iv_series = df["iv_30d"].astype(float)
            df["iv_hv_spread_20_cc"] = iv_hv_spread(iv_series, df["hv_20_cc"])
            df["iv_hv_spread_20_yz"] = iv_hv_spread(iv_series, df["hv_20_yz"])

            # Vol regime: rolling percentile rank of 30d IV
            df["vol_regime_pct"] = df["iv_30d"].rolling(252, min_periods=60).rank(pct=True)
    else:
        print("  IVX data not found — IV columns will be absent from daily_series.")
        print("  (Hypotheses requiring IV will be marked insufficient_data)")

    df = df.reset_index()
    df.to_parquet(DAILY_OUT, index=False)
    print(f"\nWrote daily_series.parquet → {DAILY_OUT}")
    print(f"  Rows: {len(df)}, Columns: {list(df.columns)}")


def build_intraday_series(force: bool = False) -> None:
    if INTRADAY_OUT.exists() and not force:
        print(f"intraday_series.parquet already exists. Use --force to rebuild.")
        return

    intraday_files = sorted(RAW_DIR.glob("qqq_intraday_iv_*.parquet"))
    if not intraday_files:
        print("No intraday parquet files found in data/raw/ — skipping intraday series.")
        print("H13 and other intraday hypotheses will be marked INSUFFICIENT_DATA.")
        return

    print(f"Building intraday series from {len(intraday_files)} daily files...")
    frames = []
    for f in intraday_files:
        df = pd.read_parquet(f)
        df.columns = [c.lower().strip() for c in df.columns]
        date_str = f.stem.split("_")[-1]  # e.g. "20240102"
        df["date"] = pd.to_datetime(date_str, format="%Y%m%d")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    # Detect time column
    time_col = _find_col(combined, ["time", "datetime", "timestamp", "ts"])
    if time_col:
        combined[time_col] = pd.to_datetime(combined[time_col])
        # Minutes from 9:30 AM ET (market open)
        market_open = pd.Timestamp("09:30:00").time()
        combined["time_minutes_from_open"] = (
            pd.to_datetime(combined[time_col].dt.strftime("%H:%M:%S"), format="%H:%M:%S")
            - pd.to_datetime(str(market_open), format="%H:%M:%S")
        ).dt.total_seconds() / 60

        # Bucket assignment: open (0–30 min), mid (90–210 min), close (330–390 min)
        combined["time_bucket"] = pd.cut(
            combined["time_minutes_from_open"],
            bins=[-1, 30, 90, 210, 330, 390],
            labels=["open", "early", "mid", "late", "close"],
        )

        # IV percent change from each day's first observation
        iv_col = _find_col(combined, ["iv", "implied_vol", "implied_volatility"])
        if iv_col:
            combined["iv"] = combined[iv_col].astype(float)
            first_iv = combined.groupby("date")["iv"].transform("first")
            combined["iv_pct_change_from_open"] = (combined["iv"] - first_iv) / first_iv.replace(0, np.nan)

    combined.to_parquet(INTRADAY_OUT, index=False)
    print(f"Wrote intraday_series.parquet → {INTRADAY_OUT}")
    print(f"  Rows: {len(combined)}, Columns: {list(combined.columns)[:8]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--daily-only", action="store_true")
    parser.add_argument("--intraday-only", action="store_true")
    args = parser.parse_args()

    if not args.intraday_only:
        print("=== Building daily series ===")
        build_daily_series(force=args.force)

    if not args.daily_only:
        print("\n=== Building intraday series ===")
        build_intraday_series(force=args.force)

    print("\nProcessed series complete.")
    print("Next: run scripts/15_run_daily_backtests.py --hypotheses H9")


if __name__ == "__main__":
    main()
