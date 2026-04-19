#!/usr/bin/env python3
"""
Phase 14e: Validate the intraday ATM ladder approach.

Phase A — Probe intraday endpoint paths using REAL optionSymbols/option_ids
           from EOD chain for DATE = 2025-01-02. Much more reliable than
           the earlier probe_intraday_endpoints.py which used synthetic params.

Phase B — If a working path is found: build 7-strike ladder for that date and
           print per-symbol row counts + IV at open/mid/close buckets.

Phase C — Show ATM selection at each hourly bar using yfinance underlying prices.

Stop condition: if Phase A finds no working path (all 403/400), print clear
message. Runner implementations will remain INSUFFICIENT_DATA.

Usage:
    python scripts/validate_intraday_ladder.py
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

# ── Config ────────────────────────────────────────────────────────────────────
TICKER   = "QQQ"
DATE     = "2025-01-02"
DATE_C   = "20250102"


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


def _probe(endpoint: str, params: dict, label: str = "") -> tuple[str, object]:
    """Try one endpoint+params combo. Returns (status_str, result_or_None)."""
    ivol = _ivol()
    ivol.setLoginParams(apiKey=_api_key())
    time.sleep(1.1)
    try:
        method = ivol.setMethod(endpoint)
        result = method(**params)
        if result is None:
            return ("None returned", None)
        if hasattr(result, "empty") and result.empty:
            return ("Empty DataFrame — endpoint accessible but no data", result)
        if hasattr(result, "__len__"):
            import pandas as pd
            cols = list(result.columns) if hasattr(result, "columns") else []
            return (f"✅ OK — {len(result)} rows | cols: {cols[:8]}", result)
        return (f"✅ OK — type={type(result).__name__}", result)
    except Exception as e:
        msg = str(e)
        if "403" in msg or "Forbidden" in msg.lower():
            return ("❌ 403 Forbidden — subscription tier", None)
        if "404" in msg or "not found" in msg.lower():
            return ("🔴 404 Not Found", None)
        if "400" in msg or "Bad Request" in msg.lower():
            return (f"🟡 400 Bad Request ({msg[:80]})", None)
        if "401" in msg or "Unauthorized" in msg.lower():
            return ("❌ 401 Unauthorized", None)
        return (f"⚠️  Error: {msg[:100]}", None)


# ── Phase A ───────────────────────────────────────────────────────────────────

def phase_a() -> tuple[str | None, dict | None, object | None]:
    """
    Probe intraday endpoints with REAL chain data.
    Returns (working_endpoint, working_params, first_result) or (None, None, None).
    """
    import pandas as pd

    chain_path = BASE / "data" / "raw" / "chains" / f"qqq_opts_by_param_{DATE_C}_C.parquet"
    if not chain_path.exists():
        print("  ERROR: EOD chain parquet not found. Run scripts/14b_fetch_eod_options.py first.")
        return None, None, None

    df = pd.read_parquet(chain_path)
    # Filter out rows with invalid IV (-1) and pick nearest-ATM contracts (0DTE preferred)
    dte0 = df[df["dte"] == 0].copy() if (df["dte"] == 0).any() else df.copy()
    valid = dte0[dte0["iv"] > 0].copy() if (dte0["iv"] > 0).any() else dte0.copy()
    if valid.empty:
        valid = dte0.copy()

    underlying = float(df["underlying_price"].iloc[0])
    print(f"  Underlying price on {DATE}: {underlying:.2f}")

    # Sort by distance from ATM
    valid = valid.copy()
    valid["_atm_dist"] = (valid["price_strike"] - underlying).abs()
    valid = valid.sort_values("_atm_dist").reset_index(drop=True)

    atm_row = valid.iloc[0]
    atm_symbol  = atm_row["option_symbol"].strip()
    atm_option_id = int(atm_row["option_id"])
    atm_stocks_id = int(atm_row["stocks_id"])
    atm_strike    = float(atm_row["price_strike"])
    atm_expiry    = str(atm_row["expiration_date"])[:10]

    print(f"\n  ATM contract on {DATE}:")
    print(f"    option_symbol : '{atm_symbol}'")
    print(f"    option_id     : {atm_option_id}")
    print(f"    stocks_id     : {atm_stocks_id}")
    print(f"    strike        : {atm_strike}")
    print(f"    expiry        : {atm_expiry}")

    # Build symbol variants
    sym_raw     = atm_symbol
    sym_strip   = atm_symbol.replace(" ", "")

    # Also grab an ITM symbol for fallback (usually has more data)
    itm_rows = valid[valid["price_strike"] < underlying - 2]
    itm_row  = itm_rows.iloc[0] if not itm_rows.empty else atm_row
    itm_symbol = itm_row["option_symbol"].strip()
    itm_option_id = int(itm_row["option_id"])

    candidates = [
        # Single-option by optionSymbol  — raw and stripped variants
        ("/equities/intraday/single-equity-optionsymbol-rawiv",
         {"optionSymbol": sym_raw,   "date": DATE},   "sym raw + date"),
        ("/equities/intraday/single-equity-optionsymbol-rawiv",
         {"optionSymbol": sym_strip, "date": DATE},   "sym stripped + date"),
        ("/equities/intraday/single-equity-optionsymbol-rawiv",
         {"symbol": sym_strip, "date": DATE},          "symbol= stripped"),
        ("/equities/intraday/single-equity-optionsymbol-rawiv",
         {"optionSymbol": sym_strip, "from_": DATE, "to": DATE}, "sym stripped + from/to"),

        # Single-option by optionId
        ("/equities/intraday/single-stock-option-raw-iv",
         {"optionId": atm_option_id, "date": DATE},           "optionId + date"),
        ("/equities/intraday/single-stock-option-raw-iv",
         {"optionId": atm_option_id, "from_": DATE, "to": DATE}, "optionId + from/to"),
        ("/equities/intraday/single-stock-option-raw-iv",
         {"symbol": sym_strip, "from_": DATE, "to": DATE},    "sym + from/to"),

        # By ticker + contract params
        ("/equities/intraday/option-by-ticker-raw-iv",
         {"symbol": TICKER, "date": DATE, "expiration": atm_expiry,
          "strike": atm_strike, "callPut": "C"},               "ticker variant"),
        ("/equities/intraday/equity-options-rawiv",
         {"symbol": TICKER, "date": DATE, "optionId": atm_option_id}, "chain + optionId"),

        # ITM contract (more likely to have data)
        ("/equities/intraday/single-equity-optionsymbol-rawiv",
         {"optionSymbol": itm_symbol.replace(" ", ""), "date": DATE}, "ITM sym"),
        ("/equities/intraday/single-stock-option-raw-iv",
         {"optionId": itm_option_id, "from_": DATE, "to": DATE},      "ITM optionId"),

        # Other naming variants from docs
        ("/equities/intraday/equity-option-raw-iv",
         {"optionSymbol": sym_strip, "date": DATE},            "equity-option-raw-iv"),
        ("/equities/intraday/single-option-raw-iv",
         {"optionSymbol": sym_strip, "date": DATE},            "single-option-raw-iv"),
        ("/equities/intraday/option-raw-iv",
         {"optionSymbol": sym_strip, "date": DATE},            "option-raw-iv"),
    ]

    print(f"\n── Phase A: Probing {len(candidates)} intraday path/param combinations ──")
    working_endpoint = None
    working_params   = None
    working_result   = None

    for endpoint, params, label in candidates:
        status, result = _probe(endpoint, params, label)
        print(f"  [{label:<35}] {endpoint}")
        print(f"     → {status}")
        if "✅" in status or ("Empty DataFrame" in status):
            print(f"\n  *** WORKING PATH FOUND: {endpoint} ***")
            working_endpoint = endpoint
            working_params   = params
            working_result   = result
            break

    return working_endpoint, working_params, working_result


# ── Phase B ───────────────────────────────────────────────────────────────────

def phase_b(working_endpoint: str, working_params_template: dict) -> None:
    """Build 7-strike ladder and fetch intraday for each symbol."""
    import pandas as pd

    chain_path = BASE / "data" / "raw" / "chains" / f"qqq_opts_by_param_{DATE_C}_C.parquet"
    df = pd.read_parquet(chain_path)

    dte0 = df[df["dte"] == 0].copy() if (df["dte"] == 0).any() else df.copy()
    underlying = float(df["underlying_price"].iloc[0])

    dte0["_atm_dist"] = (dte0["price_strike"] - underlying).abs()
    dte0 = dte0.sort_values("_atm_dist").reset_index(drop=True)

    # Sorted by strike
    sorted_strikes = sorted(dte0["price_strike"].unique().tolist())
    atm_idx = min(range(len(sorted_strikes)),
                  key=lambda i: abs(sorted_strikes[i] - underlying))
    lo = max(0, atm_idx - 3)
    hi = min(len(sorted_strikes) - 1, atm_idx + 3)
    ladder_strikes = sorted_strikes[lo:hi+1]

    print(f"\n── Phase B: 7-strike ladder around ${underlying:.2f} ──")
    print(f"  Ladder strikes: {ladder_strikes}")

    # Build symbol map
    symbol_map = {}
    option_id_map = {}
    for s in ladder_strikes:
        rows = dte0[dte0["price_strike"] == s]
        if not rows.empty:
            symbol_map[s] = rows.iloc[0]["option_symbol"].strip()
            option_id_map[s] = int(rows.iloc[0]["option_id"])

    print(f"\n  {'Strike':>8}  {'optionSymbol':<35}  {'option_id':>10}")
    for s in ladder_strikes:
        sym = symbol_map.get(s, "—")
        oid = option_id_map.get(s, "—")
        atm_flag = " ◄ ATM" if abs(s - underlying) == min(abs(x - underlying) for x in ladder_strikes) else ""
        print(f"  {s:>8.1f}  {sym:<35}  {str(oid):>10}{atm_flag}")

    # Determine which param style works (from Phase A template)
    # The working_params_template has real ATM values; adapt for each strike
    print(f"\n  Fetching intraday data for each symbol...")
    intraday_data = {}
    n_with_data = 0

    ivol = _ivol()
    ivol.setLoginParams(apiKey=_api_key())

    for s in ladder_strikes:
        sym = symbol_map.get(s)
        oid = option_id_map.get(s)
        if sym is None:
            continue

        sym_strip = sym.replace(" ", "")
        # Adapt params based on which template worked
        if "optionSymbol" in working_params_template:
            params = dict(working_params_template)
            params["optionSymbol"] = sym_strip if sym_strip == sym else sym
        elif "optionId" in working_params_template:
            params = dict(working_params_template)
            params["optionId"] = oid
        elif "symbol" in working_params_template and working_params_template.get("symbol") != TICKER:
            params = dict(working_params_template)
            params["symbol"] = sym_strip
        else:
            params = dict(working_params_template)

        time.sleep(1.1)
        try:
            method = ivol.setMethod(working_endpoint)
            result = method(**params)
            if result is not None and hasattr(result, "empty") and not result.empty:
                intraday_data[s] = result
                n_with_data += 1
                rows_n = len(result)
                first_ts = str(result.index[0] if hasattr(result, 'index') else result.iloc[0, 0])[:16]
                last_ts  = str(result.index[-1] if hasattr(result, 'index') else result.iloc[-1, 0])[:16]
                print(f"    ${s:>7.1f} → {rows_n:4d} rows  [{first_ts} → {last_ts}]")
            else:
                print(f"    ${s:>7.1f} → no data (empty)")
        except Exception as e:
            print(f"    ${s:>7.1f} → ERROR: {str(e)[:80]}")

    print(f"\n  Symbols with data: {n_with_data}/{len(ladder_strikes)}")

    if intraday_data:
        # Show IV at open/mid/close buckets for ATM contract
        atm_strike = ladder_strikes[min(range(len(ladder_strikes)),
                                         key=lambda i: abs(ladder_strikes[i] - underlying))]
        if atm_strike in intraday_data:
            df_iv = intraday_data[atm_strike]
            print(f"\n  IV time series for ATM (${atm_strike:.1f}):")
            print(f"  Columns: {list(df_iv.columns)[:10]}")
            print(df_iv.head(10).to_string())


# ── Phase C ───────────────────────────────────────────────────────────────────

def phase_c() -> None:
    """Show ATM selection at each hourly bar using yfinance underlying prices."""
    import pandas as pd

    print(f"\n── Phase C: Underlying price bars for {DATE} ──")

    p5m = BASE / "data" / "raw" / "qqq_intraday_prices_5m.parquet"
    p1h = BASE / "data" / "raw" / "qqq_intraday_prices_1h.parquet"

    bars_used = "none"

    if p5m.exists():
        df5 = pd.read_parquet(p5m)
        day_rows = df5[df5.index.date.astype(str) == DATE]
        if not day_rows.empty:
            print(f"  Using 5m bars ({len(day_rows)} rows for {DATE})")
            bars_used = "5m"
            df_bars = day_rows.resample("1h").first().dropna()
        else:
            print(f"  5m file exists but no rows for {DATE}")

    if bars_used == "none" and p1h.exists():
        df1 = pd.read_parquet(p1h)
        day_rows = df1[df1.index.date.astype(str) == DATE]
        if not day_rows.empty:
            bars_used = "1h"
            df_bars = day_rows
            print(f"  Using 1h bars ({len(day_rows)} rows for {DATE})")
        else:
            print(f"  1h bars: no rows for {DATE} (outside 730-day window?)")

    if bars_used == "none":
        print("  No underlying price bars available for this date.")
        return

    chain_path = BASE / "data" / "raw" / "chains" / f"qqq_opts_by_param_{DATE_C}_C.parquet"
    df_chain = pd.read_parquet(chain_path)
    dte0 = df_chain[df_chain["dte"] == 0].copy() if (df_chain["dte"] == 0).any() else df_chain.copy()
    sorted_strikes = sorted(dte0["price_strike"].unique().tolist())

    print(f"\n  {'Timestamp':<22}  {'Underlying':>10}  {'Nearest Strike':>14}  {'Ladder [lo..hi]'}")
    for ts, row in df_bars.iterrows():
        px = row["close"]
        nearest = min(sorted_strikes, key=lambda s: abs(s - px))
        nearest_idx = sorted_strikes.index(nearest)
        lo = max(0, nearest_idx - 3)
        hi = min(len(sorted_strikes) - 1, nearest_idx + 3)
        ladder = sorted_strikes[lo:hi+1]
        ts_str = str(ts)[:19]
        print(f"  {ts_str:<22}  {px:>10.2f}  {nearest:>14.1f}  {ladder}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Validating intraday ATM ladder approach")
    print(f"Ticker={TICKER}, Date={DATE}")
    print("=" * 90)

    working_endpoint, working_params, working_result = phase_a()

    if working_endpoint is None:
        print("\n" + "=" * 90)
        print("RESULT: No intraday endpoint returned data.")
        print("All single-option intraday paths returned 400 (not found) or 403 (subscription-gated).")
        print("Runners for H13, H14, H19, H20, H21, H22, H25 will remain INSUFFICIENT_DATA.")
        print("\nNext step: Contact iVolatility about single-option intraday entitlement.")
    else:
        phase_b(working_endpoint, working_params)

    phase_c()

    print("\n" + "=" * 90)
    print("Done.")


if __name__ == "__main__":
    main()
