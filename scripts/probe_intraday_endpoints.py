#!/usr/bin/env python3
"""
Probe every plausible iVolatility intraday endpoint path to find what is
accessible under the current subscription.

Tries single-option and option-chain variants with a known-good date/contract.
Reports: 200 OK (with row count), empty response, or error code.

Usage:
    python scripts/probe_intraday_endpoints.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv
load_dotenv()

# ── Probe config ──────────────────────────────────────────────────────────────
TICKER   = "QQQ"
DATE     = "2025-01-02"   # known good trading day with data
EXP_DATE = "2025-01-03"   # 1DTE expiry the day after
STRIKE   = 510.0           # approximate ATM for QQQ in Jan 2025
CP       = "C"

# ── Candidate intraday endpoint paths (from docs + naming pattern variants) ──
SINGLE_OPTION_PATHS = [
    # From docs page 6 — "Single Option with Raw IV & Greeks by Ticker"
    "/equities/intraday/single-stock-option-raw-iv",
    "/equities/intraday/single-equity-option-raw-iv",
    "/equities/intraday/single-equity-optionsymbol-rawiv",
    "/equities/intraday/option-raw-iv",
    "/equities/intraday/equity-option-raw-iv",
    "/equities/intraday/single-option-raw-iv",
    "/equities/intraday/options-raw-iv",
    "/equities/intraday/raw-iv",
    "/equities/intraday/ivs",
    "/equities/intraday/equity-options-rawiv",
    "/equities/intraday/stock-option-raw-iv",
]

CHAIN_PATHS = [
    # From docs page 6 — "Option Chain with Raw IV & Greeks"
    "/equities/intraday/option-chain-raw-iv",
    "/equities/intraday/equity-options-chains",
    "/equities/intraday/equity-options-chain",
    "/equities/intraday/options-chain-raw-iv",
    "/equities/intraday/chain-raw-iv",
    "/equities/intraday/options-chain",
    "/equities/intraday/equity-options-chain-raw-iv",
    "/equities/intraday/stock-options-chain",
]

# Params to try for each path (try multiple param name styles)
SINGLE_PARAM_SETS = [
    # Style A — camelCase iVol convention
    dict(symbol=TICKER, date=DATE, expiration=EXP_DATE, strike=STRIKE, callPut=CP),
    dict(symbol=TICKER, date=DATE, expiration=EXP_DATE, strike=STRIKE, optionType=CP),
    dict(symbol=TICKER, date=DATE, expirationDate=EXP_DATE, strike=STRIKE, callPut=CP),
    dict(ticker=TICKER, date=DATE, expiration=EXP_DATE, strike=STRIKE, callPut=CP),
    # Style B — with from_/to instead of date
    dict(symbol=TICKER, from_=DATE, to=DATE, expiration=EXP_DATE, strike=STRIKE, callPut=CP),
]

CHAIN_PARAM_SETS = [
    dict(symbol=TICKER, date=DATE),
    dict(symbol=TICKER, date=DATE, expiration=EXP_DATE),
    dict(ticker=TICKER, date=DATE),
    dict(symbol=TICKER, from_=DATE, to=DATE),
]


def _ivol():
    try:
        import ivolatility as ivol  # type: ignore
        return ivol
    except ImportError:
        raise ImportError("pip install ivolatility")


def probe(endpoint: str, params: dict, label: str) -> str:
    """Try one endpoint+params combo. Returns a short status string."""
    ivol = _ivol()
    api_key = os.getenv("IVOLATILITY_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("IVOLATILITY_API_KEY not set in .env")
    ivol.setLoginParams(apiKey=api_key)
    time.sleep(1.1)  # rate limit

    try:
        method = ivol.setMethod(endpoint)
        result = method(**params)

        if result is None:
            return "None returned"
        if hasattr(result, "empty") and result.empty:
            return "Empty DataFrame (0 rows) — endpoint accessible but no data"
        if hasattr(result, "__len__"):
            cols = list(result.columns) if hasattr(result, "columns") else []
            return f"✅ OK — {len(result)} rows | cols: {cols[:8]}"
        return f"✅ OK — type={type(result).__name__}"
    except Exception as e:
        msg = str(e)
        if "403" in msg or "Forbidden" in msg.lower():
            return "❌ 403 Forbidden — subscription tier"
        if "404" in msg or "not found" in msg.lower():
            return "🔴 404 Not Found — wrong path"
        if "400" in msg or "Bad Request" in msg.lower():
            return f"🟡 400 Bad Request — wrong params? ({msg[:80]})"
        if "401" in msg or "Unauthorized" in msg.lower():
            return "❌ 401 Unauthorized — check API key"
        return f"⚠️  Error: {msg[:100]}"


def main():
    print(f"Probing iVolatility intraday endpoints")
    print(f"Ticker={TICKER}, Date={DATE}, Exp={EXP_DATE}, Strike={STRIKE}, CP={CP}")
    print("=" * 90)

    print("\n── Single Option paths ──────────────────────────────────────────────────────────")
    # Try just the first param set per path to avoid rate-limit hammering
    # If we get 400 we'll try additional param sets
    for path in SINGLE_OPTION_PATHS:
        params = SINGLE_PARAM_SETS[0]
        status = probe(path, params, path)
        print(f"{path:<55} {status}")
        # If 400 (wrong params), try other param styles
        if "400" in status:
            for i, alt_params in enumerate(SINGLE_PARAM_SETS[1:], 1):
                alt_status = probe(path, alt_params, f"{path} [style {i+1}]")
                print(f"  └─ alt params style {i+1}: {alt_status}")
                if "✅" in alt_status or ("Empty" in alt_status):
                    break

    print("\n── Option Chain paths ───────────────────────────────────────────────────────────")
    for path in CHAIN_PATHS:
        params = CHAIN_PARAM_SETS[0]
        status = probe(path, params, path)
        print(f"{path:<55} {status}")
        if "400" in status:
            for i, alt_params in enumerate(CHAIN_PARAM_SETS[1:], 1):
                alt_status = probe(path, alt_params, f"{path} [style {i+1}]")
                print(f"  └─ alt params style {i+1}: {alt_status}")
                if "✅" in alt_status or ("Empty" in alt_status):
                    break

    print("\n" + "=" * 90)
    print("✅ = working endpoint  ❌ = subscription-gated  🔴 = wrong path  🟡 = wrong params")


if __name__ == "__main__":
    main()
