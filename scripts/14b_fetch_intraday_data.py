#!/usr/bin/env python3
"""
Phase 14b: Fetch and cache QQQ intraday chain snapshots from iVolatility.

Needed for: H13 (U-shape IV intraday) and all other intraday hypotheses.

Fetches one parquet per trading day via the intraday chain endpoint:
  data/raw/chains/qqq_intraday_chain_YYYYMMDD.parquet

IMPORTANT: The intraday chain endpoint is PROVISIONAL. If your iVolatility
subscription does not include intraday data, all fetches will return None and
this script will stop cleanly after 3 consecutive failures. H13 will then be
marked INSUFFICIENT_DATA, which is a valid pilot outcome.

Skips dates already cached unless --force is passed.
Respects 1 req/sec rate limit.

Usage:
    python scripts/14b_fetch_intraday_data.py
    python scripts/14b_fetch_intraday_data.py --start 2024-01-02 --end 2024-01-05 --limit 3
    python scripts/14b_fetch_intraday_data.py --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv
load_dotenv()

import pandas as pd

from app.services.ivolatility_client import IVolatilityClient, CHAINS_DIR

DEFAULT_TICKER = "QQQ"
DEFAULT_START  = "2024-01-01"


def get_default_end() -> str:
    from datetime import date
    return date.today().isoformat()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch QQQ intraday chain snapshots from iVolatility"
    )
    parser.add_argument("--ticker",  default=DEFAULT_TICKER)
    parser.add_argument("--start",   default=DEFAULT_START)
    parser.add_argument("--end",     default=None)
    parser.add_argument("--force",   action="store_true", help="Re-fetch even if cached")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit to first N trading days (0 = all). Useful for testing.",
    )
    args = parser.parse_args()

    end = args.end or get_default_end()
    trading_days = pd.bdate_range(start=args.start, end=end)

    if args.limit > 0:
        trading_days = trading_days[: args.limit]
        print(f"  Limited to first {args.limit} trading day(s) (--limit flag)")

    print(f"Fetching intraday chain: {args.ticker} {args.start} → {end}")
    print(f"Total trading days to process: {len(trading_days)}")
    print(f"Cache dir: {CHAINS_DIR}")
    print("(Each day = 1 API call, ~1 sec apart)")
    print()

    client = IVolatilityClient(force=args.force)

    success = 0
    skipped = 0
    failed  = 0
    consecutive_failures = 0

    for i, dt in enumerate(trading_days):
        date_str    = dt.strftime("%Y-%m-%d")
        date_compact = dt.strftime("%Y%m%d")
        cache_key   = f"{args.ticker.lower()}_intraday_chain_{date_compact}"
        cache_path  = CHAINS_DIR / f"{cache_key}.parquet"

        if cache_path.exists() and not args.force:
            skipped += 1
            consecutive_failures = 0
            if (i + 1) % 20 == 0:
                print(f"  [{i+1}/{len(trading_days)}] {date_str} — cached")
            continue

        df = client.get_intraday_option(args.ticker, date_str)
        if df is not None:
            success += 1
            consecutive_failures = 0
            print(f"  [{i+1}/{len(trading_days)}] {date_str} — OK ({len(df)} rows)")
        else:
            failed += 1
            consecutive_failures += 1
            print(f"  [{i+1}/{len(trading_days)}] {date_str} — FAILED")
            if consecutive_failures >= 3:
                print(
                    "\n  STOPPING: 3 consecutive intraday chain failures.\n"
                    "  The intraday endpoint is likely unavailable on this subscription tier.\n"
                    "  H13 and other intraday hypotheses will be marked INSUFFICIENT_DATA.\n"
                    "  Daily hypotheses (H9, H16) can still proceed with EOD data."
                )
                break

    print(f"\nIntraday fetch complete:")
    print(f"  Success:          {success}")
    print(f"  Skipped (cached): {skipped}")
    print(f"  Failed:           {failed}")

    if success == 0 and failed > 0:
        print(
            "\nNo intraday data fetched. Continuing with EOD-only backtests.\n"
            "H13 will be marked INSUFFICIENT_DATA — this is a valid pilot outcome."
        )
    elif success > 0:
        print(f"\nIntraday chain data cached → {CHAINS_DIR}")

    print("\nNext: run scripts/14c_build_processed_series.py")


if __name__ == "__main__":
    main()
