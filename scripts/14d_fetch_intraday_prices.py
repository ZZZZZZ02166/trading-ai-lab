#!/usr/bin/env python3
"""
Phase 14d: Fetch intraday underlying price bars from yfinance.

Saves:
  data/raw/qqq_intraday_prices_1h.parquet  — 1-hour bars, up to 730 days back (full window)
  data/raw/qqq_intraday_prices_5m.parquet  — 5-minute bars, last ~60 calendar days only

Timestamps are America/New_York (Eastern Time), market session only (9:30–16:00).

Usage:
    python scripts/14d_fetch_intraday_prices.py
    python scripts/14d_fetch_intraday_prices.py --ticker SPY --force
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

RAW_DIR = BASE / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

_ET = ZoneInfo("America/New_York")
TEST_WINDOW_START = "2024-01-01"
TEST_WINDOW_END   = "2026-04-05"


def _fetch_and_save(ticker: str, interval: str, start: str, end: str, out_path: Path) -> int:
    import yfinance as yf  # type: ignore

    print(f"  Downloading {ticker} {interval} bars {start} → {end} ...")
    df = yf.download(
        ticker,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if df is None or df.empty:
        print(f"  WARNING: yfinance returned no data for {ticker} {interval}.")
        return 0

    # Flatten MultiIndex columns if present (yfinance sometimes returns them)
    if isinstance(df.columns, __import__("pandas").MultiIndex):
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]

    # Ensure DatetimeIndex is timezone-aware ET
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
    else:
        df.index = df.index.tz_convert("America/New_York")

    # Keep market session only (9:30–16:00 ET)
    df = df.between_time("09:30", "16:00")

    # Rename index for storage
    df.index.name = "datetime"

    df.to_parquet(out_path)
    first = str(df.index[0])[:19]
    last  = str(df.index[-1])[:19]
    print(f"  [saved] {out_path.relative_to(BASE)} ({len(df)} rows | {first} → {last})")
    return len(df)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="QQQ")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    ticker = args.ticker.upper()

    # ── 1h bars: full test window, capped at 729 days back (yfinance limit) ──
    path_1h = RAW_DIR / f"{ticker.lower()}_intraday_prices_1h.parquet"
    if path_1h.exists() and not args.force:
        print(f"[skip] {path_1h.name} already exists (use --force to refresh)")
    else:
        # yfinance 1h is limited to last 730 days; compute effective start
        earliest_1h = (datetime.now(_ET) - timedelta(days=729)).strftime("%Y-%m-%d")
        start_1h = max(TEST_WINDOW_START, earliest_1h)
        if start_1h > TEST_WINDOW_START:
            print(f"  NOTE: 1h bars start capped at {start_1h} (yfinance 730-day limit; test window starts {TEST_WINDOW_START})")
        n = _fetch_and_save(ticker, "1h", start_1h, TEST_WINDOW_END, path_1h)
        if n == 0:
            print("  1h fetch failed — check yfinance and internet connection.")

    # ── 5m bars: last 60 calendar days ───────────────────────────────────────
    path_5m = RAW_DIR / f"{ticker.lower()}_intraday_prices_5m.parquet"
    if path_5m.exists() and not args.force:
        print(f"[skip] {path_5m.name} already exists (use --force to refresh)")
    else:
        # yfinance 5m is capped at ~60 calendar days; always fetch from today-60
        end_5m   = datetime.now(_ET).strftime("%Y-%m-%d")
        start_5m = (datetime.now(_ET) - timedelta(days=59)).strftime("%Y-%m-%d")
        n = _fetch_and_save(ticker, "5m", start_5m, end_5m, path_5m)
        if n == 0:
            print("  5m fetch failed — check yfinance and internet connection.")

    print("\nDone. Next: python scripts/validate_intraday_ladder.py")


if __name__ == "__main__":
    main()
