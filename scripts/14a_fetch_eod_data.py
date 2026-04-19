#!/usr/bin/env python3
"""
Phase 14a: Fetch and cache QQQ EOD data from iVolatility.

Fetches:
  1. QQQ daily OHLCV prices (for HV estimation)
  2. QQQ IVX (30d/60d/90d constant-maturity IV index) (for vol regime + event studies)

All data cached as parquet in data/raw/. Skips fetch if cache already exists.
Use --force to re-fetch.

Prerequisites:
  - IVOLATILITY_API_KEY set in .env (regenerate if previously shared in plaintext)
  - pip install ivolatility pyarrow

Usage:
    python scripts/14a_fetch_eod_data.py
    python scripts/14a_fetch_eod_data.py --force
    python scripts/14a_fetch_eod_data.py --start 2024-01-01 --end 2024-06-30
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv
load_dotenv()

from app.services.ivolatility_client import IVolatilityClient
from app.services.data_validator import validate_dataframe, validate_date_range

DEFAULT_TICKER = "QQQ"
DEFAULT_START = "2024-01-01"


def get_default_end() -> str:
    from datetime import date
    return date.today().isoformat()


def main():
    parser = argparse.ArgumentParser(description="Fetch QQQ EOD data from iVolatility")
    parser.add_argument("--ticker", default=DEFAULT_TICKER)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=None)
    parser.add_argument("--force", action="store_true", help="Re-fetch even if cache exists")
    args = parser.parse_args()

    end = args.end or get_default_end()
    print(f"Fetching EOD data: {args.ticker} {args.start} → {end}")

    client = IVolatilityClient(force=args.force)

    # ── 1. EOD prices ────────────────────────────────────────────────────────────
    print("\n[1/2] EOD prices (OHLCV)...")
    try:
        prices = client.get_eod_prices(args.ticker, args.start, end)
        validate_dataframe(prices, required_cols=[], min_rows=50, name="EOD prices")
        validate_date_range(prices, date_col=_detect_date_col(prices), expected_start=args.start, expected_end=end, name="EOD prices")
        print(f"  OK — {len(prices)} rows | columns: {list(prices.columns)[:6]}")
    except Exception as e:
        print(f"  ERROR fetching EOD prices: {e}")
        sys.exit(1)

    # ── 2. IVX ───────────────────────────────────────────────────────────────────
    print("\n[2/2] IVX (constant-maturity IV index)...")
    try:
        ivx = client.get_ivx(args.ticker, args.start, end)
        validate_dataframe(ivx, required_cols=[], min_rows=50, name="IVX")
        validate_date_range(ivx, date_col=_detect_date_col(ivx), expected_start=args.start, expected_end=end, name="IVX")
        print(f"  OK — {len(ivx)} rows | columns: {list(ivx.columns)[:8]}")
    except Exception as e:
        print(f"  ERROR fetching IVX: {e}")
        print("  IVX may require a specific subscription tier. Continuing without it.")

    print(f"\nAll EOD data cached → {BASE / 'data' / 'raw'}")
    print("Next: run scripts/14b_fetch_intraday_data.py")


def _detect_date_col(df) -> str:
    """Find the date column regardless of exact naming convention."""
    for candidate in ["date", "trade_date", "tradeDate", "Date", "datetime"]:
        if candidate in df.columns:
            return candidate
    return df.columns[0]  # fallback to first column


if __name__ == "__main__":
    main()
