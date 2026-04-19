#!/usr/bin/env python3
"""
Rigorous iVolatility intraday endpoint probe — v2.

Tests documented retail intraday endpoints with exact documented parameter schemas,
including the previously-omitted `minuteType` parameter.

Probe matrix:
  A. /equities/intraday/single-equity-optionsymbol-rawiv  (by optionSymbol)
  B. /equities/intraday/single-equity-option-rawiv        (by ticker + contract params)
  C. /equities/intraday/equity-options-rawiv              (full-chain control, expected 403)

Contracts used (real data from EOD chain 2025-01-02):
  0DTE call: QQQ   250102C00510000  option_id=136119621  strike=510  expiry=2025-01-02
  1DTE call: QQQ   250103C00510000  option_id=135776661  strike=510  expiry=2025-01-03
  (1DTE used as secondary because 0DTE iv=-1 at settlement)

Output:
  - Console: structured table
  - data/raw/probe_intraday_v2_results.json  (raw probe log)

Usage:
    python scripts/probe_intraday_v2.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv
load_dotenv()

RAW_DIR = BASE / "data" / "raw"

# ── Real contract data ────────────────────────────────────────────────────────
DATE           = "2025-01-02"

# 0DTE call (iv=-1 at EOD, but intraday data may still exist during session)
SYM_0DTE_RAW   = "QQQ   250102C00510000"   # exact 3-space format from iVol
SYM_0DTE_1SP   = "QQQ 250102C00510000"     # 1-space variant (user spec form)
SYM_0DTE_STRIP = "QQQ250102C00510000"      # no-space variant
STRIKE_0DTE    = 510.0
EXPIRY_0DTE    = "2025-01-02"

# 1DTE call (iv=0.2556 — valid contract, still live during session on 2025-01-02)
SYM_1DTE_RAW   = "QQQ   250103C00510000"
SYM_1DTE_STRIP = "QQQ250103C00510000"
STRIKE_1DTE    = 510.0
EXPIRY_1DTE    = "2025-01-03"
OPTION_ID_1DTE = 135776661

TICKER     = "QQQ"
UNDERLYING = 510.17

# minuteType values to try (documented enum)
MT_1  = "MINUTE_1"
MT_5  = "MINUTE_5"
MT_15 = "MINUTE_15"


def _ivol():
    try:
        import ivolatility as ivol  # type: ignore
        return ivol
    except ImportError:
        raise ImportError("pip install ivolatility")


def _api_key() -> str:
    k = os.getenv("IVOLATILITY_API_KEY", "").strip()
    if not k:
        raise SystemExit("IVOLATILITY_API_KEY not set in .env")
    return k


def probe_one(endpoint: str, params: dict, label: str, schema_exact: bool) -> dict:
    """Execute one probe, return structured result dict."""
    ivol = _ivol()
    ivol.setLoginParams(apiKey=_api_key())
    time.sleep(1.1)

    result = {
        "label": label,
        "endpoint": endpoint,
        "params": {k: str(v) for k, v in params.items()},
        "schema_exact": schema_exact,
        "http_status": None,
        "response_type": None,
        "row_count": None,
        "columns": None,
        "response_snippet": None,
        "diagnosis": None,
        "raw_error": None,
    }

    try:
        method = ivol.setMethod(endpoint)
        data = method(**params)

        if data is None:
            result.update(http_status=200, response_type="None", diagnosis="UNCLEAR — returned None")
        elif hasattr(data, "empty") and data.empty:
            result.update(
                http_status=200,
                response_type="DataFrame",
                row_count=0,
                columns=list(data.columns),
                diagnosis="GATED_OR_NO_DATA — empty DataFrame, endpoint reached",
            )
        elif hasattr(data, "__len__"):
            import pandas as pd
            cols = list(data.columns) if hasattr(data, "columns") else []
            snippet = data.head(2).to_dict("records") if hasattr(data, "to_dict") else str(data)[:200]
            result.update(
                http_status=200,
                response_type="DataFrame",
                row_count=len(data),
                columns=cols,
                response_snippet=snippet,
                diagnosis="WORKING",
            )
        else:
            result.update(http_status=200, response_type=type(data).__name__,
                          response_snippet=str(data)[:200], diagnosis="WORKING")

    except Exception as e:
        msg = str(e)
        result["raw_error"] = msg[:300]
        if "403" in msg or "Forbidden" in msg.lower():
            result.update(http_status=403, diagnosis="GATED_BY_SUBSCRIPTION")
        elif "401" in msg or "Unauthorized" in msg.lower():
            result.update(http_status=401, diagnosis="AUTH_FAILURE")
        elif "400" in msg or "Bad Request" in msg.lower():
            # Extract response body if available
            snippet = msg[:200]
            result.update(http_status=400, diagnosis="REQUEST_SCHEMA_STILL_WRONG_OR_PATH_INVALID")
            result["response_snippet"] = snippet
        elif "404" in msg or "not found" in msg.lower():
            result.update(http_status=404, diagnosis="PATH_NOT_FOUND")
        else:
            result.update(http_status="?", diagnosis="UNKNOWN_ERROR")

    return result


def run_probes() -> list[dict]:
    results = []

    print(f"\nBuilding probe matrix for {TICKER} {DATE} ...")
    print(f"  0DTE call: {repr(SYM_0DTE_RAW)}  option_id=136119621")
    print(f"  1DTE call: {repr(SYM_1DTE_RAW)}  option_id={OPTION_ID_1DTE}")

    # ────────────────────────────────────────────────────────────────────────
    # SECTION A — by optionSymbol endpoint
    # Documented required: optionSymbol, date, minuteType
    # Documented optional: minutes (only if minuteType=CUSTOM)
    # ────────────────────────────────────────────────────────────────────────
    endpoint_a = "/equities/intraday/single-equity-optionsymbol-rawiv"
    section_a = [
        # A1-A4: exact user-specified probe matrix (0DTE)
        ("A1 — 0DTE 3-space sym, MINUTE_5",
         dict(optionSymbol=SYM_0DTE_RAW,   date=DATE, minuteType=MT_5),   True),
        ("A2 — 0DTE 1-space sym, MINUTE_5",
         dict(optionSymbol=SYM_0DTE_1SP,   date=DATE, minuteType=MT_5),   True),
        ("A3 — 0DTE no-space sym, MINUTE_5",
         dict(optionSymbol=SYM_0DTE_STRIP, date=DATE, minuteType=MT_5),   True),
        ("A4 — 0DTE 3-space sym, MINUTE_1",
         dict(optionSymbol=SYM_0DTE_RAW,   date=DATE, minuteType=MT_1),   True),
        ("A5 — 0DTE 3-space sym, MINUTE_15",
         dict(optionSymbol=SYM_0DTE_RAW,   date=DATE, minuteType=MT_15),  True),
        # A6-A8: 1DTE call (valid IV; more likely to have intraday data)
        ("A6 — 1DTE 3-space sym, MINUTE_5",
         dict(optionSymbol=SYM_1DTE_RAW,   date=DATE, minuteType=MT_5),   True),
        ("A7 — 1DTE no-space sym, MINUTE_5",
         dict(optionSymbol=SYM_1DTE_STRIP, date=DATE, minuteType=MT_5),   True),
        ("A8 — 1DTE 3-space sym, MINUTE_15",
         dict(optionSymbol=SYM_1DTE_RAW,   date=DATE, minuteType=MT_15),  True),
        # A9: without minuteType (to see if it's truly required or just documented)
        ("A9 — 0DTE no minuteType [undoc fallback]",
         dict(optionSymbol=SYM_0DTE_RAW,   date=DATE),                    False),
    ]

    print(f"\n── Section A: {endpoint_a}")
    for label, params, exact in section_a:
        r = probe_one(endpoint_a, params, label, exact)
        results.append(r)
        _print_row(r)
        if r["diagnosis"] == "WORKING":
            print("  *** WORKING — stopping section A early ***")
            break

    # ────────────────────────────────────────────────────────────────────────
    # SECTION B — by ticker + contract parameters endpoint
    # Documented required: symbol, date, expDate, stoptType (sic), minuteType
    # Note: 'stoptType' appears to be a docs typo; we probe both optType and
    # stoptType variants since the exact param name is unclear.
    # ────────────────────────────────────────────────────────────────────────
    endpoint_b = "/equities/intraday/single-equity-option-rawiv"
    section_b = [
        # B1: exact documented schema with optType=CALL (most likely correct name)
        ("B1 — 0DTE optType=CALL, MINUTE_5 [exact docs]",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_0DTE,
              optType="CALL", minuteType=MT_5),                            True),
        # B2: same with 1DTE
        ("B2 — 1DTE optType=CALL, MINUTE_5",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_1DTE,
              optType="CALL", minuteType=MT_5),                            True),
        # B3: include strike (some endpoints require it)
        ("B3 — 1DTE optType=CALL, strike=510, MINUTE_5",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_1DTE,
              strike=510, optType="CALL", minuteType=MT_5),                True),
        # B4: stoptType variant (literal docs field name, may be typo for optType)
        ("B4 — 0DTE stoptType=CALL [docs literal], MINUTE_5",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_0DTE,
              stoptType="CALL", minuteType=MT_5),                          True),
        # B5: callPut=C (older iVol naming convention)
        ("B5 — 1DTE callPut=C, MINUTE_5 [alt name]",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_1DTE,
              callPut="C", minuteType=MT_5),                               False),
        # B6: optType=C (abbreviated form)
        ("B6 — 1DTE optType=C [undoc abbrev]",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_1DTE,
              optType="C", minuteType=MT_5),                               False),
        # B7: MINUTE_15 with 1DTE
        ("B7 — 1DTE optType=CALL, MINUTE_15",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_1DTE,
              optType="CALL", minuteType=MT_15),                           True),
        # B8: without minuteType (fallback test)
        ("B8 — 1DTE optType=CALL, no minuteType",
         dict(symbol=TICKER, date=DATE, expDate=EXPIRY_1DTE,
              optType="CALL"),                                             False),
    ]

    print(f"\n── Section B: {endpoint_b}")
    for label, params, exact in section_b:
        r = probe_one(endpoint_b, params, label, exact)
        results.append(r)
        _print_row(r)
        if r["diagnosis"] == "WORKING":
            print("  *** WORKING — stopping section B early ***")
            break

    # ────────────────────────────────────────────────────────────────────────
    # SECTION C — full chain control (expected 403)
    # ────────────────────────────────────────────────────────────────────────
    endpoint_c = "/equities/intraday/equity-options-rawiv"
    section_c = [
        ("C1 — chain symbol+date+minuteType",
         dict(symbol=TICKER, date=DATE, minuteType=MT_5),                 True),
        ("C2 — chain symbol+date [no minuteType]",
         dict(symbol=TICKER, date=DATE),                                   False),
    ]

    print(f"\n── Section C: {endpoint_c} (control — expect 403)")
    for label, params, exact in section_c:
        r = probe_one(endpoint_c, params, label, exact)
        results.append(r)
        _print_row(r)

    return results


def _print_row(r: dict) -> None:
    schema_flag = "✓schema" if r["schema_exact"] else "~approx"
    status      = r["http_status"] or "?"
    diagnosis   = r["diagnosis"] or "?"
    rows        = f"{r['row_count']} rows" if r["row_count"] is not None else ""
    print(f"  {r['label']}")
    print(f"    params : {r['params']}")
    print(f"    result : HTTP {status}  [{schema_flag}]  {diagnosis}  {rows}")
    if r.get("response_snippet") and r["diagnosis"] not in ("WORKING",):
        snippet = str(r["response_snippet"])[:120]
        print(f"    snippet: {snippet}")
    print()


def diagnose(results: list[dict]) -> None:
    """Print final per-endpoint diagnosis."""
    print("\n" + "=" * 90)
    print("FINAL DIAGNOSIS")
    print("=" * 90)

    endpoints = {
        "/equities/intraday/single-equity-optionsymbol-rawiv": "A",
        "/equities/intraday/single-equity-option-rawiv":       "B",
        "/equities/intraday/equity-options-rawiv":             "C",
    }

    for ep, section in endpoints.items():
        ep_results = [r for r in results if r["endpoint"] == ep]
        exact_results = [r for r in ep_results if r["schema_exact"]]

        statuses   = [r["http_status"] for r in ep_results]
        diagnoses  = [r["diagnosis"] for r in ep_results]

        working    = any(d == "WORKING" for d in diagnoses)
        any_403    = any(s == 403 for s in statuses)
        all_400    = all(s == 400 for s in statuses)
        exact_400  = all(s == 400 for s in [r["http_status"] for r in exact_results])

        if working:
            verdict = "✅ WORKING"
            rec = "Proceed with runner implementation."
        elif any_403:
            verdict = "🔒 GATED_BY_SUBSCRIPTION"
            rec = "Endpoint exists but access is blocked by account tier. Contact iVolatility."
        elif exact_400 and exact_results:
            verdict = "🟡 REQUEST_SCHEMA_STILL_WRONG  (exact-schema requests also 400)"
            rec = "All exact-schema probes failed with 400. Either the path is wrong OR the documented param schema itself has errors. Check iVolatility docs version vs API version."
        elif all_400:
            verdict = "🔴 PATH_NOT_FOUND or DOCS_MISMATCH"
            rec = "All probes returned 400 — path likely doesn't exist at this tier."
        else:
            verdict = "❓ UNCLEAR"
            rec = "Mixed results — manual investigation needed."

        print(f"\nSection {section}: {ep}")
        print(f"  Verdict     : {verdict}")
        print(f"  HTTP codes  : {sorted(set(statuses))}")
        print(f"  Exact-schema: {len(exact_results)} probes, codes={sorted(set(r['http_status'] for r in exact_results))}")
        print(f"  Recommend   : {rec}")

    # H13-H25 runner recommendation
    print("\n── Runner Recommendation ──────────────────────────────────────────────────────")
    any_working = any(r["diagnosis"] == "WORKING" for r in results
                      if r["endpoint"] != "/equities/intraday/equity-options-rawiv")
    if any_working:
        print("  ✅ At least one intraday single-option endpoint is accessible.")
        print("  → Proceed with intraday_atm_selector.py and update H13/H14/H19/H20/H21/H22/H25 runners.")
    else:
        all_gated = all(r["diagnosis"] in ("GATED_BY_SUBSCRIPTION",)
                        for r in results
                        if r["endpoint"] != "/equities/intraday/equity-options-rawiv"
                        and r["schema_exact"])
        if all_gated:
            print("  🔒 All single-option paths are subscription-gated (403).")
            print("  → H13/H14/H19/H20/H21/H22/H25 must remain INSUFFICIENT_DATA until tier is upgraded.")
        else:
            print("  🟡 No single-option path returned data. Could be schema mismatch or entitlement.")
            print("  → Contact iVolatility: share exact probe params + response bodies.")
            print("  → H13/H14/H19/H20/H21/H22/H25 remain INSUFFICIENT_DATA for now.")


def main():
    print("iVolatility Intraday Endpoint Probe — v2")
    print(f"Date: {DATE}  Ticker: {TICKER}")
    print("=" * 90)

    results = run_probes()

    # Save JSON log
    out_path = RAW_DIR / "probe_intraday_v2_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "probe_date": datetime.now().isoformat(),
            "contract_date": DATE,
            "ticker": TICKER,
            "contracts": {
                "0DTE_call": {"symbol": SYM_0DTE_RAW, "option_id": 136119621,
                              "strike": STRIKE_0DTE, "expiry": EXPIRY_0DTE},
                "1DTE_call": {"symbol": SYM_1DTE_RAW, "option_id": OPTION_ID_1DTE,
                              "strike": STRIKE_1DTE, "expiry": EXPIRY_1DTE},
            },
            "results": results,
        }, f, indent=2)
    print(f"\n[log saved] {out_path.relative_to(BASE)}")

    diagnose(results)
    print()


if __name__ == "__main__":
    main()
