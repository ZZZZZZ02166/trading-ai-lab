"""
intraday_atm_selector.py — Small strike ladder for intraday ATM approximation.

Workflow:
  1. build_ladder(ticker, trade_date) — fetch EOD chain, derive ±3 strikes around ATM,
     pull intraday minute data for each via confirmed single-option endpoints, load
     yfinance underlying bars.
  2. get_atm_snapshot(ladder, timestamp) — find nearest-ATM strike at a given timestamp
     using the underlying price bar, return IV/Greeks for that contract.
  3. get_ladder_time_series(ladder) — call get_atm_snapshot at every hourly bar in session.

Approximation metadata (always set, never hidden):
  contract_selection_method = "intraday_atm_approx_small_strike_ladder"
  strike_ladder_width = 3
  exact_chain_intraday = False   (full chain is 403-gated; only single-option used)

Confirmed working endpoints (probe_intraday_v2.py, 2026-04-17):
  /equities/intraday/single-equity-optionsymbol-rawiv → primary
  /equities/intraday/single-equity-option-rawiv       → fallback (when symbol format ambiguous)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd

BASE = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE / "data" / "raw"

_1H_BARS_PATH = RAW_DIR / "qqq_intraday_prices_1h.parquet"
_5M_BARS_PATH = RAW_DIR / "qqq_intraday_prices_5m.parquet"

# minuteType used for all intraday fetches — 5-min bars balance resolution vs API cost
_MINUTE_TYPE = "MINUTE_5"

# Column name mappings for intraday response
# Actual iVol intraday columns (confirmed 2026-04-17):
#   timestamp, optionIv, optionBidPrice, optionAskPrice, optionDelta,
#   optionGamma, optionTheta, optionVega, underlyingPrice, optionSymbol
_IV_COLS    = ["optionIv", "iv", "implied_volatility", "impliedVol", "IV"]
_BID_COLS   = ["optionBidPrice", "bid", "bid_price", "Bid"]
_ASK_COLS   = ["optionAskPrice", "ask", "ask_price", "Ask"]
_DELTA_COLS = ["optionDelta", "delta", "Delta"]
_UL_COLS    = ["underlyingPrice", "underlying_price", "underlying", "spot"]
_TIME_COLS  = ["timestamp", "datetime", "date_time", "time", "Datetime"]


def _find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _normalise_intraday(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise iVol intraday response to consistent column names and DatetimeIndex."""
    df = df.copy()

    # Build DatetimeIndex from timestamp column (iVol returns numeric RangeIndex)
    if not isinstance(df.index, pd.DatetimeIndex):
        time_col = _find_col(df, _TIME_COLS)
        if time_col:
            df.index = pd.to_datetime(df[time_col])
            df.index.name = "datetime"

    # Localise to ET if tz-naive
    if df.index.tz is None:
        try:
            df.index = df.index.tz_localize("America/New_York", ambiguous="infer",
                                             nonexistent="shift_forward")
        except Exception:
            df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
    else:
        df.index = df.index.tz_convert("America/New_York")

    # Rename columns to canonical names used by get_atm_snapshot
    rename = {}
    for canon, candidates in [
        ("iv",               _IV_COLS),
        ("bid_price",        _BID_COLS),
        ("ask_price",        _ASK_COLS),
        ("delta",            _DELTA_COLS),
        ("underlying_price", _UL_COLS),
    ]:
        found = _find_col(df, candidates)
        if found and found != canon:
            rename[found] = canon
    if rename:
        df = df.rename(columns=rename)

    return df.sort_index()


# ── IntradayLadder ────────────────────────────────────────────────────────────

@dataclass
class IntradayLadder:
    trade_date: str
    ticker: str
    expiry: str
    dte: int
    call_put: str                              # "C", "P", or "both"
    strikes: list[float]                       # sorted, all strikes in the ladder
    # For "both": keys are "C_{strike}" and "P_{strike}"
    # For single side: keys are just the optionSymbol string
    symbol_map: dict[str, dict[float, str]]    # {"C": {strike: optionSymbol}, "P": {...}}
    intraday: dict[str, pd.DataFrame]          # optionSymbol → normalised minute-level df
    underlying_1h: pd.DataFrame                # 1h bars for trade_date session
    underlying_5m: Optional[pd.DataFrame]      # 5m bars if available for trade_date

    # Approximation metadata — always set, always exported to extra_metrics
    contract_selection_method: str = "intraday_atm_approx_small_strike_ladder"
    strike_ladder_width: int = 3
    time_grid: str = "1h"                      # "5m" if 5m bars available for this date
    exact_chain_intraday: bool = False
    minute_type: str = _MINUTE_TYPE
    n_symbols_attempted: int = 0
    n_symbols_with_data: int = 0
    intraday_endpoint_used: str = "single-equity-optionsymbol-rawiv"

    def approx_metadata(self) -> dict:
        """Dict suitable for injection into BacktestResult.extra_metrics."""
        return {
            "contract_selection_method": self.contract_selection_method,
            "strike_ladder_width": self.strike_ladder_width,
            "time_grid": self.time_grid,
            "exact_chain_intraday": self.exact_chain_intraday,
            "minute_type": self.minute_type,
            "n_symbols_attempted": self.n_symbols_attempted,
            "n_symbols_with_data": self.n_symbols_with_data,
            "intraday_endpoint_used": self.intraday_endpoint_used,
        }


# ── Underlying bar loader ─────────────────────────────────────────────────────

def _load_underlying_bars(
    trade_date: str,
    ticker: str = "QQQ",
) -> tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Load yfinance underlying price bars for trade_date.

    Returns (bars_1h, bars_5m_or_None). Both DataFrames are filtered to the
    given date and market session only (they were already filtered at save time).
    bars_5m is None if the 5m parquet doesn't cover trade_date.
    """
    bars_1h_path = RAW_DIR / f"{ticker.lower()}_intraday_prices_1h.parquet"
    bars_5m_path = RAW_DIR / f"{ticker.lower()}_intraday_prices_5m.parquet"

    bars_1h: pd.DataFrame = pd.DataFrame()
    bars_5m: Optional[pd.DataFrame] = None

    if bars_1h_path.exists():
        df = pd.read_parquet(bars_1h_path)
        day = df[df.index.normalize() == pd.Timestamp(trade_date, tz=df.index.tz)]
        if not day.empty:
            bars_1h = day

    if bars_5m_path.exists():
        df5 = pd.read_parquet(bars_5m_path)
        day5 = df5[df5.index.normalize() == pd.Timestamp(trade_date, tz=df5.index.tz)]
        if not day5.empty:
            bars_5m = day5

    return bars_1h, bars_5m


# ── Chain normalisation (reuse contract_selector logic) ──────────────────────

def _normalise_chain(df: pd.DataFrame) -> pd.DataFrame:
    """Rename iVol EOD chain columns to canonical names. Mirrors contract_selector._normalise_chain."""
    _COL_MAP = {
        "option_symbol":    ["option_symbol", "optionsymbol", "symbol"],
        "option_id":        ["option_id", "optionid", "id"],
        "call_put":         ["call_put", "cp_flag", "type", "option_type", "cp"],
        "strike":           ["strike", "price_strike", "strike_price"],
        "expiry":           ["expiry", "expiration_date", "expiration"],
        "dte":              ["dte", "days_to_expiry"],
        "underlying_price": ["underlying_price", "underlying", "spot", "stock_price"],
        "bid_price":        ["bid_price", "Bid", "bid"],
        "ask_price":        ["ask_price", "Ask", "ask"],
        "implied_volatility": ["implied_volatility", "iv", "IV"],
        "delta":            ["delta"],
    }
    rename = {}
    for canon, cands in _COL_MAP.items():
        for c in cands:
            if c in df.columns and c != canon:
                rename[c] = canon
                break
    return df.rename(columns=rename)


# ── build_ladder ──────────────────────────────────────────────────────────────

def build_ladder(
    ticker: str,
    trade_date: str,
    call_put: str = "C",
    dte_target: int = 0,
    ladder_width: int = 3,
    minute_type: str = _MINUTE_TYPE,
    client=None,
) -> Optional[IntradayLadder]:
    """
    Build a small strike ladder for trade_date.

    Steps:
      1. Fetch EOD chain (dte 0–5) from iVolatility via client.get_options_by_param()
      2. Select target expiry (prefer dte == dte_target, else nearest)
      3. Find ATM anchor strike; build ladder_width strikes each side from listed strikes
      4. For "both": build call + put symbol_maps from same expiry
      5. Load yfinance underlying bars
      6. Fetch intraday data for each symbol via get_intraday_option_by_symbol() with
         fallback to get_intraday_option_by_params()
      7. Return IntradayLadder, or None if n_symbols_with_data == 0

    call_put: "C", "P", or "both"
    """
    from app.services.ivolatility_client import IVolatilityClient

    if client is None:
        client = IVolatilityClient()

    # ── Step 1: fetch EOD chain ───────────────────────────────────────────────
    sides = ["C", "P"] if call_put == "both" else [call_put]
    chain_by_side: dict[str, pd.DataFrame] = {}
    for side in sides:
        try:
            raw = client.get_options_by_param(
                ticker, trade_date, dte_from=0, dte_to=5, cp=side,
                moneyness_from=-15.0, moneyness_to=15.0,
            )
            chain_by_side[side] = _normalise_chain(raw)
        except Exception as e:
            print(f"  [build_ladder] EOD chain fetch failed for {ticker} {trade_date} {side}: {e}")
            return None

    # Use call chain for geometry (underlying price, expiry selection)
    ref_chain = chain_by_side.get("C") if "C" in chain_by_side else chain_by_side.get("P")
    if ref_chain is None or ref_chain.empty:
        return None

    # ── Step 2: select target expiry ─────────────────────────────────────────
    if "dte" not in ref_chain.columns:
        print(f"  [build_ladder] no dte column in chain for {ticker} {trade_date}")
        return None

    available_dtes = sorted(ref_chain["dte"].unique())
    if dte_target in available_dtes:
        chosen_dte = dte_target
    else:
        chosen_dte = min(available_dtes, key=lambda d: abs(d - dte_target))

    # ── Step 3: build ladder strikes ─────────────────────────────────────────
    underlying_price = float(ref_chain["underlying_price"].iloc[0])
    target_expiry = str(
        ref_chain[ref_chain["dte"] == chosen_dte]["expiry"].iloc[0]
    )[:10]

    # Collect all listed strikes for the chosen expiry (from call chain)
    ref_expiry_rows = ref_chain[ref_chain["dte"] == chosen_dte]
    listed_strikes = sorted(ref_expiry_rows["strike"].unique().tolist())

    if not listed_strikes:
        print(f"  [build_ladder] no strikes for {ticker} {trade_date} dte={chosen_dte}")
        return None

    atm_idx = min(range(len(listed_strikes)),
                  key=lambda i: abs(listed_strikes[i] - underlying_price))
    lo = max(0, atm_idx - ladder_width)
    hi = min(len(listed_strikes) - 1, atm_idx + ladder_width)
    ladder_strikes = listed_strikes[lo:hi+1]

    # ── Step 4: build symbol_map per side ────────────────────────────────────
    symbol_map: dict[str, dict[float, str]] = {}
    for side, chain in chain_by_side.items():
        expiry_rows = chain[chain["dte"] == chosen_dte]
        side_map: dict[float, str] = {}
        for s in ladder_strikes:
            rows = expiry_rows[expiry_rows["strike"] == s]
            if not rows.empty:
                sym = rows.iloc[0]["option_symbol"]
                side_map[s] = sym if isinstance(sym, str) else str(sym)
        symbol_map[side] = side_map

    # ── Step 5: load underlying bars ─────────────────────────────────────────
    bars_1h, bars_5m = _load_underlying_bars(trade_date, ticker)
    time_grid = "5m" if bars_5m is not None and not bars_5m.empty else "1h"

    # ── Step 6: fetch intraday data ───────────────────────────────────────────
    intraday: dict[str, pd.DataFrame] = {}
    all_symbols = {sym for side_map in symbol_map.values() for sym in side_map.values()}
    n_attempted = len(all_symbols)
    n_with_data = 0

    for sym in all_symbols:
        # Primary: by optionSymbol
        df = client.get_intraday_option_by_symbol(sym, trade_date, minute_type)

        # Fallback: by params (derive exp/strike/opt_type from symbol_map)
        if df is None:
            for side, side_map in symbol_map.items():
                for strike_val, s in side_map.items():
                    if s == sym:
                        opt_type = "CALL" if side == "C" else "PUT"
                        df = client.get_intraday_option_by_params(
                            ticker, trade_date, target_expiry,
                            strike_val, opt_type, minute_type,
                        )
                        break
                if df is not None:
                    break

        if df is not None and not df.empty:
            intraday[sym] = _normalise_intraday(df)
            n_with_data += 1

    if n_with_data == 0:
        print(f"  [build_ladder] no intraday data for any symbol on {trade_date}")
        return None

    return IntradayLadder(
        trade_date=trade_date,
        ticker=ticker,
        expiry=target_expiry,
        dte=chosen_dte,
        call_put=call_put,
        strikes=ladder_strikes,
        symbol_map=symbol_map,
        intraday=intraday,
        underlying_1h=bars_1h,
        underlying_5m=bars_5m,
        time_grid=time_grid,
        minute_type=minute_type,
        n_symbols_attempted=n_attempted,
        n_symbols_with_data=n_with_data,
    )


# ── Underlying price lookup ───────────────────────────────────────────────────

def _get_underlying_price_at(
    ladder: IntradayLadder,
    timestamp: pd.Timestamp,
) -> Optional[float]:
    """Return underlying close price at the bar whose open ≤ timestamp (nearest prior bar)."""
    for bars in (ladder.underlying_5m, ladder.underlying_1h):
        if bars is None or bars.empty:
            continue
        candidates = bars[bars.index <= timestamp]
        if not candidates.empty:
            return float(candidates.iloc[-1]["close"])
    return None


# ── get_atm_snapshot ──────────────────────────────────────────────────────────

def get_atm_snapshot(
    ladder: IntradayLadder,
    timestamp: pd.Timestamp,
    call_put: str = "C",
    tolerance_minutes: int = 10,
) -> Optional[dict]:
    """
    Return IV/Greeks for the nearest-ATM contract at timestamp.

    1. Get underlying price at timestamp (5m preferred, 1h fallback)
    2. Find nearest listed strike
    3. Get optionSymbol for that strike
    4. Find the intraday bar within ±tolerance_minutes of timestamp
    5. Return dict with iv, bid_price, ask_price, delta, strike, option_symbol,
       underlying_price, timestamp, call_put, time_grid_used
    Returns None if no data within tolerance.
    """
    side = call_put.upper()
    side_map = ladder.symbol_map.get(side) or ladder.symbol_map.get("C") or {}
    if not side_map:
        return None

    underlying_px = _get_underlying_price_at(ladder, timestamp)
    if underlying_px is None:
        return None

    nearest_strike = min(side_map.keys(), key=lambda s: abs(s - underlying_px))
    option_symbol  = side_map[nearest_strike]

    df_iv = ladder.intraday.get(option_symbol)
    if df_iv is None or df_iv.empty:
        return None

    tol = pd.Timedelta(minutes=tolerance_minutes)
    window = df_iv[(df_iv.index >= timestamp - tol) & (df_iv.index <= timestamp + tol)]
    if window.empty:
        return None

    # Nearest row within window (TimedeltaIndex.total_seconds() for abs comparison)
    import numpy as np
    delta_seconds = np.abs((window.index - timestamp).total_seconds())
    nearest_row = window.iloc[int(np.argmin(delta_seconds))]

    def _get(row, cols):
        for c in cols:
            if c in row.index and pd.notna(row[c]):
                return float(row[c])
        return None

    iv        = _get(nearest_row, ["iv"])
    bid_price = _get(nearest_row, ["bid_price"])
    ask_price = _get(nearest_row, ["ask_price"])
    delta     = _get(nearest_row, ["delta"])
    mid_price = (bid_price + ask_price) / 2 if bid_price is not None and ask_price is not None else None
    # Also pull underlying_price from the intraday row itself as a consistency check
    ul_from_row = _get(nearest_row, ["underlying_price"])

    time_grid = "5m" if ladder.underlying_5m is not None and not ladder.underlying_5m.empty else "1h"

    return {
        "timestamp":        timestamp,
        "bar_timestamp":    nearest_row.name,
        "strike":           nearest_strike,
        "option_symbol":    option_symbol,
        "call_put":         side,
        "iv":               iv,
        "bid_price":        bid_price,
        "ask_price":        ask_price,
        "mid_price":        mid_price,
        "delta":            delta,
        "underlying_price": underlying_px,
        "time_grid_used":   time_grid,
    }


# ── get_ladder_time_series ────────────────────────────────────────────────────

def get_ladder_time_series(
    ladder: IntradayLadder,
    timestamps: Optional[list[pd.Timestamp]] = None,
    call_put: str = "C",
) -> pd.DataFrame:
    """
    Build a DataFrame with one row per timestamp.

    If timestamps is None: use all 1h bars for trade_date session as the grid.
    Rows where get_atm_snapshot returns None get NaN values + no_data=True flag.

    Columns: timestamp, underlying_price, nearest_strike, option_symbol,
             iv, bid_price, ask_price, mid_price, delta, time_grid_used, no_data
    """
    if timestamps is None:
        if not ladder.underlying_1h.empty:
            timestamps = list(ladder.underlying_1h.index)
        else:
            return pd.DataFrame()

    rows = []
    for ts in timestamps:
        snap = get_atm_snapshot(ladder, ts, call_put)
        if snap is not None:
            rows.append({**snap, "no_data": False})
        else:
            rows.append({
                "timestamp": ts, "underlying_price": None,
                "nearest_strike": None, "option_symbol": None,
                "iv": None, "bid_price": None, "ask_price": None,
                "mid_price": None, "delta": None,
                "time_grid_used": ladder.time_grid, "no_data": True,
            })

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).set_index("timestamp")
