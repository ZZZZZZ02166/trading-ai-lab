"""
fill_model.py — Time series fill utilities + execution-aware options fill model.

Two sections:
  1. Time series fill  — forward_fill, reindex_to_trading_days, drop_leading_nans
     Used by build_processed_series to handle gaps in daily data.

  2. Execution fill    — FillMode, FillResult, compute_fill
     Used by backtests to model realistic entry/exit prices given bid/ask quotes.
     Prefer no-trade over fabricated precision when data quality is poor.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, Optional

import pandas as pd


def forward_fill(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """
    Forward-fill NaN values within each column, up to `limit` consecutive rows.

    Args:
        df:    DataFrame to fill.
        limit: Maximum number of consecutive NaNs to fill. Default 5 (one week).

    Returns:
        New DataFrame with NaNs filled.
    """
    return df.ffill(limit=limit)


def reindex_to_trading_days(
    df: pd.DataFrame,
    start: str,
    end: str,
    date_col: str = "date",
    fill: bool = True,
    fill_limit: int = 5,
) -> pd.DataFrame:
    """
    Reindex a DataFrame to a complete trading-day calendar between start and end.

    Useful when iVolatility returns only dates with data (skipping weekends/holidays)
    and you need a contiguous daily index for rolling window computations.

    Args:
        df:         DataFrame with a date column.
        start:      ISO date string "YYYY-MM-DD".
        end:        ISO date string "YYYY-MM-DD".
        date_col:   Column name containing dates.
        fill:       Whether to forward-fill missing rows after reindex.
        fill_limit: Max consecutive NaNs to fill.

    Returns:
        DataFrame indexed by date, with all business days present.
    """
    bday_range = pd.bdate_range(start=start, end=end)
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    df = df.reindex(bday_range)
    df.index.name = date_col
    if fill:
        df = forward_fill(df, limit=fill_limit)
    return df.reset_index()


def drop_leading_nans(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Drop leading rows where `col` is NaN (e.g. warm-up period for rolling windows).

    Returns a copy with rows before the first valid value in `col` removed.
    """
    first_valid = df[col].first_valid_index()
    if first_valid is None:
        return df.iloc[0:0]  # all NaN — return empty
    return df.loc[first_valid:].copy()


# ── Execution fill model ──────────────────────────────────────────────────────────


class FillMode(str, Enum):
    OPTIMISTIC   = "optimistic"    # fill at mid_price — best case, unrealistic
    REALISTIC    = "realistic"     # mid ± slippage_factor × spread (default)
    CONSERVATIVE = "conservative"  # buy at ask / sell at bid — worst case


@dataclass
class FillResult:
    filled: bool
    fill_price: Optional[float]    # None if trade was skipped
    fill_mode: FillMode
    rejection_reason: Optional[str]  # why trade was skipped; None if filled
    commission: float                # per-contract commission in dollars
    total_cost: float                # abs(fill_price × multiplier) + commission; 0 if not filled


def _get_field(record: Any, *keys: str) -> Optional[float]:
    """Extract the first non-None numeric field from a dict or object."""
    for key in keys:
        v = record.get(key) if isinstance(record, dict) else getattr(record, key, None)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def compute_fill(
    record: Any,
    side: Literal["buy", "sell"],
    mode: FillMode = FillMode.REALISTIC,
    slippage_factor: float = 0.10,
    commission_per_contract: float = 0.65,
    multiplier: int = 100,
    skip_if_spread_pct_over: float = 0.50,
    skip_if_no_quote: bool = True,
) -> FillResult:
    """
    Compute a realistic fill price for one options contract.

    Args:
        record:                  ContractRecord or dict with bid_price/ask_price/mid_price.
        side:                    "buy" or "sell".
        mode:                    Fill mode (OPTIMISTIC / REALISTIC / CONSERVATIVE).
        slippage_factor:         Fraction of spread added to mid for REALISTIC fills.
        commission_per_contract: Fixed commission per contract in dollars.
        multiplier:              Options contract multiplier (standard = 100).
        skip_if_spread_pct_over: Skip the trade if spread_pct exceeds this threshold.
        skip_if_no_quote:        Skip the trade if bid or ask is missing.

    Returns:
        FillResult. If filled=False, fill_price is None and total_cost is 0.

    Rules:
      - Missing bid or ask → skip if skip_if_no_quote=True
      - Spread too wide    → skip (rejection_reason="spread_too_wide")
      - OPTIMISTIC         → fill at mid_price
      - REALISTIC          → buy: mid + slippage×spread; sell: mid - slippage×spread
      - CONSERVATIVE       → buy at ask_price; sell at bid_price
    """
    bid = _get_field(record, "bid_price", "bid")
    ask = _get_field(record, "ask_price", "ask")
    mid = _get_field(record, "mid_price", "mid")

    # ── Missing quote ─────────────────────────────────────────────────────────────
    if (bid is None or ask is None) and skip_if_no_quote:
        return FillResult(
            filled=False,
            fill_price=None,
            fill_mode=mode,
            rejection_reason="no_quote",
            commission=0.0,
            total_cost=0.0,
        )

    # ── Compute mid if not stored ─────────────────────────────────────────────────
    if mid is None and bid is not None and ask is not None:
        mid = (bid + ask) / 2.0

    # ── Spread check ──────────────────────────────────────────────────────────────
    if bid is not None and ask is not None and mid and mid > 0:
        spread = ask - bid
        spread_pct = spread / mid
        if spread_pct > skip_if_spread_pct_over:
            return FillResult(
                filled=False,
                fill_price=None,
                fill_mode=mode,
                rejection_reason="spread_too_wide",
                commission=0.0,
                total_cost=0.0,
            )
    else:
        spread = 0.0

    # ── Compute fill price ────────────────────────────────────────────────────────
    if mode == FillMode.OPTIMISTIC:
        if mid is None:
            return FillResult(
                filled=False,
                fill_price=None,
                fill_mode=mode,
                rejection_reason="no_mid_for_optimistic_fill",
                commission=0.0,
                total_cost=0.0,
            )
        fill_price = mid

    elif mode == FillMode.REALISTIC:
        if mid is None:
            return FillResult(
                filled=False,
                fill_price=None,
                fill_mode=mode,
                rejection_reason="no_mid_for_realistic_fill",
                commission=0.0,
                total_cost=0.0,
            )
        slippage = slippage_factor * spread
        fill_price = mid + slippage if side == "buy" else mid - slippage

    else:  # CONSERVATIVE
        if side == "buy":
            if ask is None:
                return FillResult(
                    filled=False,
                    fill_price=None,
                    fill_mode=mode,
                    rejection_reason="no_ask_for_conservative_buy",
                    commission=0.0,
                    total_cost=0.0,
                )
            fill_price = ask
        else:
            if bid is None:
                return FillResult(
                    filled=False,
                    fill_price=None,
                    fill_mode=mode,
                    rejection_reason="no_bid_for_conservative_sell",
                    commission=0.0,
                    total_cost=0.0,
                )
            fill_price = bid

    if fill_price is None or fill_price <= 0:
        return FillResult(
            filled=False,
            fill_price=None,
            fill_mode=mode,
            rejection_reason="fill_price_zero_or_negative",
            commission=0.0,
            total_cost=0.0,
        )

    total_cost = abs(fill_price * multiplier) + commission_per_contract
    return FillResult(
        filled=True,
        fill_price=round(fill_price, 4),
        fill_mode=mode,
        rejection_reason=None,
        commission=commission_per_contract,
        total_cost=round(total_cost, 4),
    )
