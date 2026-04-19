"""
contract_selection_record.py — Audit record for every contract candidate checked on a trade date.

One JSON file per trade date: data/raw/selections/qqq_selection_YYYYMMDD.json
Each file contains a list of ContractSelectionRecord — ALL candidates checked, not just the winner.

Purpose: full reconstruction of which candidates were checked, why each was rejected,
and why the final winner was selected.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ContractSelectionRecord(BaseModel):
    # ── Identity ──────────────────────────────────────────────────────────────────
    trade_date: str           # "YYYY-MM-DD"
    ticker: str               # "QQQ"
    option_symbol: str        # canonical iVol identifier
    option_id: Optional[str] = None

    # ── Snapshot timestamps (ET / America/New_York) ───────────────────────────────
    quote_timestamp: Optional[str] = None
    snapshot_timestamp: Optional[str] = None

    # ── Contract spec ─────────────────────────────────────────────────────────────
    call_put: str             # "C" or "P"
    strike: float
    expiry: str               # "YYYY-MM-DD"
    dte: int                  # calendar days: (expiry - trade_date).days

    # ── Underlying ────────────────────────────────────────────────────────────────
    underlying_last_price: Optional[float] = None
    underlying_mid_price: Optional[float] = None
    moneyness: float          # strike / underlying_price (1.0 = ATM)

    # ── Quote ─────────────────────────────────────────────────────────────────────
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    mid_price: Optional[float] = None
    spread_pct: Optional[float] = None   # (ask - bid) / mid; computed at selection time
    volume: Optional[int] = None
    open_interest: Optional[int] = None
    implied_volatility: Optional[float] = None   # decimal (0.20 = 20%)
    delta: Optional[float] = None

    # ── Selection outcome ─────────────────────────────────────────────────────────
    passed_quality_gates: bool
    rejection_reason: Optional[str] = None  # first failing gate; None if passed
    selection_score: Optional[float] = None # abs(moneyness - 1.0) for ATM ranking; lower = better
    selection_reason: Optional[str] = None  # e.g. "nearest ATM; spread_pct=0.12"
    final_selected: bool = False            # True for the one contract ultimately selected
