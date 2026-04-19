"""
contract_record.py — Pydantic schema for a raw options contract record.

Canonical data model for a single option contract on a single date, as stored in
data/raw/chains/<date>.parquet or data/raw/contracts/<symbol>.parquet.

Field naming rules (strict — no ambiguity):
  - bid_price / ask_price / mid_price / last_price  → always option prices, never IVs
  - implied_volatility                               → always decimal (0.20 = 20%)
  - dte                                              → calendar days (not trading days)
  - moneyness                                        → strike / underlying_price (1.0 = ATM)
  - option_id                                        → numeric ID from iVol if present
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, field_validator


class ContractRecord(BaseModel):
    # ── Temporal ───────────────────────────────────────────────────────────────
    trade_date: str                     # "YYYY-MM-DD" — date of this snapshot

    # ── Contract identity ──────────────────────────────────────────────────────
    option_symbol: str                  # canonical iVol option identifier string
    option_id: Optional[str] = None     # numeric/internal iVol ID (if returned)
    ticker: str                         # underlying ticker, e.g. "QQQ"
    call_put: str                       # "C" or "P" — normalised on ingest
    strike: float
    expiry: str                         # "YYYY-MM-DD"
    dte: int                            # calendar days to expiry (expiry - trade_date)

    # ── Underlying ─────────────────────────────────────────────────────────────
    underlying_price: float
    moneyness: float                    # strike / underlying_price (1.0 = ATM)

    # ── Quote prices (always prices, never IVs) ────────────────────────────────
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    mid_price: Optional[float] = None   # stored; computed as (bid+ask)/2 if absent
    last_price: Optional[float] = None

    # ── Activity ───────────────────────────────────────────────────────────────
    volume: Optional[int] = None
    open_interest: Optional[int] = None

    # ── Greeks + IV (all from iVol model) ─────────────────────────────────────
    implied_volatility: Optional[float] = None   # decimal (0.20 = 20%)
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None               # per calendar day
    vega: Optional[float] = None                # per 1% vol move
    rho: Optional[float] = None

    # ── Optional enrichment fields ─────────────────────────────────────────────
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    trade_count: Optional[int] = None

    # ── Timestamps (all ISO 8601 strings, always ET / America/New_York) ────────
    quote_timestamp: Optional[str] = None
    # ^ Time the option quote (bid/ask) was recorded — critical for intraday staleness checks.
    #   For EOD chain snapshots this is typically the closing quote time (e.g. "2024-01-02T16:00:00-05:00").
    #   For intraday snapshots this is the exact minute timestamp.

    trade_timestamp: Optional[str] = None
    # ^ Time of the last actual trade in this contract on trade_date.
    #   Different from quote_timestamp: a quote can be live even if no trade has occurred.

    snapshot_timestamp: Optional[str] = None
    # ^ Time the full chain snapshot was taken (for intraday: the 1-min bar timestamp).
    #   Use this as the alignment anchor when joining across contracts in the same snapshot.
    #   For EOD data this equals the end-of-session timestamp.

    # ── Underlying price fields (separate definitions, no mixing) ──────────────
    # underlying_price (above) = the reference spot used for moneyness/DTE computation.
    #   For EOD this is the closing price. For intraday it is the concurrent mid or last.
    #   Must be set explicitly — never derived silently from another field.

    underlying_last_price: Optional[float] = None
    # ^ Last trade price of the underlying on this date/timestamp.
    #   May differ from underlying_price if underlying_price = mid or theoretical.

    underlying_bid: Optional[float] = None
    # ^ Best bid of underlying at quote_timestamp. Used for underlying_mid_price computation.

    underlying_ask: Optional[float] = None
    # ^ Best ask of underlying at quote_timestamp.

    underlying_mid_price: Optional[float] = None
    # ^ (underlying_bid + underlying_ask) / 2, stored explicitly.
    #   Computed at ingest time; stored to avoid ambiguity in downstream code.

    underlying_timestamp: Optional[str] = None
    # ^ Timestamp (ET) of the underlying quote used for underlying_bid/ask/mid.
    #   May differ from quote_timestamp if quotes are not perfectly synchronised.

    # ── Data quality metadata ──────────────────────────────────────────────────
    data_source: str = "ivolatility"
    fetch_date: Optional[str] = None            # "YYYY-MM-DD" when fetched

    # ── Validators ─────────────────────────────────────────────────────────────

    @field_validator("call_put")
    @classmethod
    def _normalise_call_put(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ("C", "P"):
            raise ValueError(f"call_put must be 'C' or 'P', got '{v}'")
        return v

    # ── Computed properties ────────────────────────────────────────────────────

    @property
    def spread(self) -> Optional[float]:
        """Bid-ask spread in price units. None if either side is missing."""
        if self.bid_price is not None and self.ask_price is not None:
            return self.ask_price - self.bid_price
        return None

    @property
    def spread_pct(self) -> Optional[float]:
        """(ask - bid) / mid_price. None if mid is zero or unavailable."""
        m = self.effective_mid
        s = self.spread
        if m is None or s is None or m == 0:
            return None
        return s / m

    @property
    def effective_mid(self) -> Optional[float]:
        """Mid price — stored mid_price if set, else (bid_price + ask_price) / 2."""
        if self.mid_price is not None:
            return self.mid_price
        if self.bid_price is not None and self.ask_price is not None:
            return (self.bid_price + self.ask_price) / 2
        return None

    def is_otm(self) -> bool:
        if self.call_put == "C":
            return self.strike > self.underlying_price
        return self.strike < self.underlying_price

    def is_itm(self) -> bool:
        return not self.is_otm()
