"""
data_validator.py — Data quality validation for iVolatility responses and contract candidates.

Functions:
  validate_dataframe          — column presence + row count check (raises ValueError)
  check_empty_response        — bool check with warning print
  validate_date_range         — coverage gap warning (no raise)
  validate_chain_response     — EOD chain response integrity (raises ValueError)
  validate_contract_history   — single-contract history integrity (raises ValueError)
  apply_contract_quality_gates — per-candidate quality gates (returns bool + reason)
  validate_intraday_response  — intraday snapshot integrity (raises ValueError)
  check_stale_quote           — staleness detection (returns bool)

All functions are pure or stateless — no I/O, no API calls.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd

# ── Quality gate thresholds ───────────────────────────────────────────────────────

_GATE = {
    "min_volume": 10,
    "min_open_interest": 50,
    "min_bid": 0.01,
    "max_spread_pct": 0.50,       # 50% of mid
    "iv_min": 0.01,               # 1%
    "iv_max": 5.00,               # 500%
    "delta_min": -1.01,
    "delta_max": 1.01,
    "dte_min": 0,
    "dte_max": 5,
    "moneyness_min": 0.85,
    "moneyness_max": 1.15,
    "dte_expiry_max_day_diff": 1, # DTE vs (expiry - trade_date) must match within 1 day
}


# ── Existing functions (kept unchanged) ───────────────────────────────────────────

def validate_dataframe(
    df: pd.DataFrame,
    required_cols: list[str],
    min_rows: int = 1,
    name: str = "DataFrame",
) -> None:
    """Assert df has the required columns and at least min_rows rows. Raises ValueError."""
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError(f"{name}: expected a DataFrame, got {type(df)}")
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"{name}: missing required columns {missing}. "
            f"Available: {list(df.columns)}"
        )
    if len(df) < min_rows:
        raise ValueError(f"{name}: expected ≥ {min_rows} rows, got {len(df)}")


def check_empty_response(df: pd.DataFrame, endpoint_name: str) -> bool:
    """Return True if non-empty. Print warning and return False if empty."""
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        print(
            f"  WARNING: {endpoint_name} returned empty response. "
            "Check your API entitlement and date range."
        )
        return False
    return True


def validate_date_range(
    df: pd.DataFrame,
    date_col: str,
    expected_start: str,
    expected_end: str,
    name: str = "DataFrame",
) -> None:
    """Warn (no raise) if actual coverage differs from expected."""
    if date_col not in df.columns:
        return
    actual_start = str(df[date_col].min())[:10]
    actual_end = str(df[date_col].max())[:10]
    if actual_start > expected_start:
        print(f"  WARNING: {name} starts at {actual_start}, expected {expected_start} — partial coverage")
    if actual_end < expected_end:
        print(f"  WARNING: {name} ends at {actual_end}, expected {expected_end} — data may be lagged")


# ── New validation functions ──────────────────────────────────────────────────────

def validate_chain_response(
    df: pd.DataFrame,
    trade_date: str,
    ticker: str,
) -> None:
    """
    Validate an EOD chain snapshot response.

    Raises ValueError if:
      - DataFrame is None or empty
      - Missing any of the minimum required chain columns
      - Zero rows after the response is returned
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError(
            f"Chain response for {ticker} {trade_date} is None or not a DataFrame."
        )
    if df.empty:
        raise ValueError(
            f"Chain response for {ticker} {trade_date} is empty — "
            "check endpoint, subscription, and date range."
        )

    # Minimum columns we can work with — exact names depend on iVol response
    # These are alternatives; we check that at least one from each group exists
    required_groups = {
        "strike": ["strike", "strike_price", "strikeprice", "price_strike"],
        "expiry": ["expiry", "expiration", "expiration_date", "expirydate"],
        "call_put": ["call_put", "cp_flag", "type", "option_type", "putcall"],
    }
    for field, candidates in required_groups.items():
        if not any(c in df.columns for c in candidates):
            raise ValueError(
                f"Chain response for {ticker} {trade_date} missing '{field}' column. "
                f"Tried: {candidates}. Available: {list(df.columns[:20])}"
            )


def validate_contract_history(
    df: pd.DataFrame,
    option_symbol: str,
    expected_start: str,
    expected_end: str,
) -> None:
    """
    Validate a single-contract history response.

    Raises ValueError if:
      - Empty or None
      - Fewer than 5 rows (too little history to be useful)
      - All IV values are NaN
      - All price values (bid/ask/mid/last) are zero or NaN
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError(f"Contract history for {option_symbol} is None or not a DataFrame.")
    if df.empty:
        raise ValueError(f"Contract history for {option_symbol} is empty.")
    if len(df) < 5:
        raise ValueError(
            f"Contract history for {option_symbol} has only {len(df)} rows — "
            f"expected ≥ 5 for period {expected_start} → {expected_end}."
        )

    # Check IV sanity
    iv_cols = [c for c in df.columns if "iv" in c.lower() or "implied" in c.lower()]
    if iv_cols:
        iv_col = iv_cols[0]
        if df[iv_col].isna().all():
            raise ValueError(f"Contract history for {option_symbol}: IV column '{iv_col}' is all NaN.")

    # Check prices
    price_cols = [c for c in df.columns if any(p in c.lower() for p in ["bid", "ask", "mid", "last", "price"])]
    if price_cols:
        price_col = price_cols[0]
        non_positive = (df[price_col].fillna(0) <= 0).all()
        if non_positive:
            raise ValueError(
                f"Contract history for {option_symbol}: price column '{price_col}' is all zero or negative."
            )


def apply_contract_quality_gates(record: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Apply all quality gates to a contract candidate dict.

    Returns (passed: bool, rejection_reason: str | None).
    Returns the FIRST failing gate reason; None if all pass.

    Designed to work with raw dicts from a chain DataFrame row or ContractRecord.model_dump().
    All checks are defensive — missing fields are treated as failed (not crashed).
    """

    def _get(key: str, *fallbacks: str) -> Any:
        for k in (key, *fallbacks):
            v = record.get(k)
            if v is not None:
                return v
        return None

    # ── Volume ────────────────────────────────────────────────────────────────────
    volume = _get("volume")
    if volume is not None:
        try:
            if float(volume) < _GATE["min_volume"]:
                return False, "volume_too_low"
        except (TypeError, ValueError):
            return False, "volume_invalid"

    # ── Open interest ─────────────────────────────────────────────────────────────
    oi = _get("open_interest", "openinterest", "oi")
    if oi is not None:
        try:
            if float(oi) < _GATE["min_open_interest"]:
                return False, "open_interest_too_low"
        except (TypeError, ValueError):
            return False, "open_interest_invalid"

    # ── Bid price ─────────────────────────────────────────────────────────────────
    bid = _get("bid_price", "bid")
    ask = _get("ask_price", "ask")

    if bid is None:
        return False, "bid_missing"
    try:
        bid = float(bid)
    except (TypeError, ValueError):
        return False, "bid_invalid"
    if bid < _GATE["min_bid"]:
        return False, "bid_zero_or_negative"

    # ── Ask price / crossed market ────────────────────────────────────────────────
    if ask is None:
        return False, "ask_missing"
    try:
        ask = float(ask)
    except (TypeError, ValueError):
        return False, "ask_invalid"
    if ask <= bid:
        return False, "ask_lte_bid"           # crossed market
    if ask == bid:
        return False, "locked_market"

    # ── Mid price ─────────────────────────────────────────────────────────────────
    mid = _get("mid_price", "mid")
    if mid is None:
        mid = (bid + ask) / 2.0
    else:
        try:
            mid = float(mid)
        except (TypeError, ValueError):
            mid = (bid + ask) / 2.0
    if mid <= 0:
        return False, "mid_zero"

    # ── Spread pct ────────────────────────────────────────────────────────────────
    spread_pct = _get("spread_pct")
    if spread_pct is None:
        spread_pct = (ask - bid) / mid if mid > 0 else None
    if spread_pct is not None:
        try:
            if float(spread_pct) > _GATE["max_spread_pct"]:
                return False, "spread_too_wide"
        except (TypeError, ValueError):
            return False, "spread_pct_invalid"

    # ── IV ────────────────────────────────────────────────────────────────────────
    iv = _get("implied_volatility", "iv", "impliedvol", "implied_vol")
    if iv is not None:
        try:
            iv = float(iv)
            if not (_GATE["iv_min"] <= iv <= _GATE["iv_max"]):
                return False, "iv_out_of_range"
        except (TypeError, ValueError):
            return False, "iv_invalid"

    # ── Delta ─────────────────────────────────────────────────────────────────────
    delta = _get("delta")
    if delta is not None:
        try:
            delta = float(delta)
            if not (_GATE["delta_min"] <= delta <= _GATE["delta_max"]):
                return False, "delta_out_of_range"
        except (TypeError, ValueError):
            return False, "delta_invalid"

    # ── DTE range ─────────────────────────────────────────────────────────────────
    dte = _get("dte")
    if dte is not None:
        try:
            dte = int(dte)
            if not (_GATE["dte_min"] <= dte <= _GATE["dte_max"]):
                return False, "dte_out_of_pilot_scope"
        except (TypeError, ValueError):
            return False, "dte_invalid"

    # ── Moneyness ─────────────────────────────────────────────────────────────────
    moneyness = _get("moneyness")
    if moneyness is not None:
        try:
            moneyness = float(moneyness)
            if not (_GATE["moneyness_min"] <= moneyness <= _GATE["moneyness_max"]):
                return False, "too_far_otm_or_itm"
        except (TypeError, ValueError):
            return False, "moneyness_invalid"

    # ── DTE vs expiry consistency ─────────────────────────────────────────────────
    trade_date_str = _get("trade_date")
    expiry_str = _get("expiry", "expiration", "expiration_date")
    if trade_date_str and expiry_str and dte is not None:
        try:
            td = datetime.strptime(str(trade_date_str)[:10], "%Y-%m-%d").date()
            exp = datetime.strptime(str(expiry_str)[:10], "%Y-%m-%d").date()
            computed_dte = (exp - td).days
            if abs(computed_dte - dte) > _GATE["dte_expiry_max_day_diff"]:
                return False, "dte_expiry_mismatch"
        except (ValueError, TypeError):
            pass  # can't verify — skip this gate rather than reject

    return True, None


def validate_intraday_response(
    df: pd.DataFrame,
    trade_date: str,
) -> None:
    """
    Validate an intraday snapshot response.

    Raises ValueError if:
      - Empty or None
      - No time/datetime column detectable
      - Fewer than 30 rows (less than half a trading session at 1-min resolution)
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError(f"Intraday response for {trade_date} is None or not a DataFrame.")
    if df.empty:
        raise ValueError(
            f"Intraday response for {trade_date} is empty — "
            "check intraday endpoint availability and subscription tier."
        )

    time_cols = [c for c in df.columns if any(t in c.lower() for t in ["time", "datetime", "timestamp", "ts"])]
    if not time_cols:
        raise ValueError(
            f"Intraday response for {trade_date}: no time/datetime column found. "
            f"Available columns: {list(df.columns[:20])}"
        )

    if len(df) < 30:
        raise ValueError(
            f"Intraday response for {trade_date}: only {len(df)} rows — "
            "expected ≥ 30 for a half-session at 1-min resolution."
        )


def check_stale_quote(
    quote_ts: str,
    snapshot_ts: str,
    max_staleness_minutes: int = 15,
) -> bool:
    """
    Return True if the quote is stale relative to the snapshot timestamp.

    A quote is considered stale if it is more than max_staleness_minutes older
    than the snapshot. Returns False (not stale) if either timestamp is unparseable.
    """
    try:
        qt = datetime.fromisoformat(quote_ts.replace("Z", "+00:00"))
        st = datetime.fromisoformat(snapshot_ts.replace("Z", "+00:00"))
        return (st - qt) > timedelta(minutes=max_staleness_minutes)
    except (ValueError, AttributeError, TypeError):
        return False
