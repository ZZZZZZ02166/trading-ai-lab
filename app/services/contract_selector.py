"""
contract_selector.py — Chain-based contract discovery, quality filtering, and selection audit.

Workflow per trade_date:
  1. Load EOD chain snapshot from data/raw/chains/ (fetches via client if missing)
  2. Normalise column names to canonical schema
  3. Compute DTE and moneyness where missing
  4. Filter to dte in [0, 5] and (optionally) by call_put
  5. Apply strict quality gates to each candidate
  6. Rank survivors by |moneyness - 1.0| (nearest ATM wins)
  7. Select top candidate; return None if all fail
  8. Persist all candidates + selection outcome to data/raw/selections/

Public API:
  ContractSelector.select_atm_contract(trade_date, call_put) -> ContractRecord | None
  ContractSelector.load_audit_log(trade_date) -> list[ContractSelectionRecord]
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from app.models.contract_record import ContractRecord
from app.models.contract_selection_record import ContractSelectionRecord
from app.services.data_validator import apply_contract_quality_gates, validate_chain_response
from app.services.ivolatility_client import IVolatilityClient

BASE = Path(__file__).resolve().parent.parent.parent
SELECTIONS_DIR = BASE / "data" / "raw" / "selections"
SELECTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Canonical column name mappings from iVol response → our schema.
# stock-opts-by-param returns: c_date, option_symbol, dte, expiration_date, call_put,
#   price_strike, iv, delta, Ask, Bid, underlying_price, calc_OTM, option_id
_COL_MAP = {
    "option_symbol":       ["option_symbol", "optionsymbol", "symbol", "option"],
    "option_id":           ["option_id", "optionid", "id"],
    "call_put":            ["call_put", "cp_flag", "type", "option_type", "putcall", "cp"],
    "strike":              ["strike", "price_strike", "strike_price", "strikeprice"],
    "expiry":              ["expiry", "expiration_date", "expiration", "expirydate", "expire_date"],
    "dte":                 ["dte", "days_to_expiry", "daystoexpiry"],
    "underlying_price":    ["underlying_price", "underlying", "spot", "stock_price", "close"],
    "underlying_last_price": ["underlying_last", "underlying_last_price", "stock_close"],
    "underlying_mid_price":  ["underlying_mid", "underlying_mid_price"],
    "bid_price":           ["bid_price", "Bid", "bid"],
    "ask_price":           ["ask_price", "Ask", "ask"],
    "mid_price":           ["mid_price", "mid"],
    "last_price":          ["last_price", "last"],
    "volume":              ["volume", "vol", "trading_volume"],
    "open_interest":       ["open_interest", "openinterest", "oi"],
    "implied_volatility":  ["implied_volatility", "iv", "impliedvol", "implied_vol", "ivol"],
    "delta":               ["delta"],
    "gamma":               ["gamma"],
    "theta":               ["theta"],
    "vega":                ["vega"],
    "rho":                 ["rho"],
    "calc_otm":            ["calc_OTM", "calc_otm", "otm_pct"],
    "quote_timestamp":     ["quote_timestamp", "quotetime", "quote_time"],
    "snapshot_timestamp":  ["snapshot_timestamp", "snapshottime", "snapshot_time", "datetime"],
}


def _find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _normalise_chain(df: pd.DataFrame) -> pd.DataFrame:
    """Rename iVol chain columns to our canonical names where found."""
    rename = {}
    for canonical, candidates in _COL_MAP.items():
        found = _find_col(df, candidates)
        if found and found != canonical:
            rename[found] = canonical
    return df.rename(columns=rename)


def _compute_dte(row: pd.Series, trade_date: str) -> int:
    """Compute DTE from expiry and trade_date if dte column is missing."""
    try:
        td = datetime.strptime(trade_date, "%Y-%m-%d").date()
        exp_str = str(row.get("expiry", ""))[:10]
        exp = datetime.strptime(exp_str, "%Y-%m-%d").date()
        return (exp - td).days
    except (ValueError, TypeError):
        return -1


def _compute_moneyness(row: pd.Series) -> Optional[float]:
    """moneyness = strike / underlying_price. Returns None if inputs invalid."""
    strike = row.get("strike")
    ul = row.get("underlying_price") or row.get("underlying_last_price")
    try:
        if strike and ul and float(ul) > 0:
            return round(float(strike) / float(ul), 6)
    except (TypeError, ValueError):
        pass
    return None


def _compute_spread_pct(row: pd.Series) -> Optional[float]:
    bid = row.get("bid_price")
    ask = row.get("ask_price")
    try:
        bid, ask = float(bid), float(ask)
        mid = (bid + ask) / 2.0
        if mid > 0:
            return round((ask - bid) / mid, 6)
    except (TypeError, ValueError):
        pass
    return None


def _normalise_call_put(v: str) -> str:
    v = str(v).strip().upper()
    if v in ("C", "CALL"):
        return "C"
    if v in ("P", "PUT"):
        return "P"
    return v


class ContractSelector:
    """
    Selects the best contract from an EOD chain snapshot for a given trade date.

    Usage:
        selector = ContractSelector(client=IVolatilityClient())
        record = selector.select_atm_contract("QQQ", "2024-01-15", call_put="C")
    """

    def __init__(self, client: Optional[IVolatilityClient] = None, force: bool = False):
        self.client = client or IVolatilityClient(force=force)

    def select_atm_contract(
        self,
        ticker: str,
        trade_date: str,
        call_put: Optional[str] = None,
        dte_min: int = 0,
        dte_max: int = 5,
    ) -> Optional[ContractRecord]:
        """
        Select the nearest ATM contract from the EOD chain for trade_date.

        Args:
            ticker:     Ticker symbol ("QQQ").
            trade_date: "YYYY-MM-DD".
            call_put:   "C", "P", or None (select either).
            dte_min:    Minimum DTE (calendar days). Default 0.
            dte_max:    Maximum DTE (calendar days). Default 5.

        Returns:
            ContractRecord for the selected contract, or None if no valid contract found.
            Also persists full candidate audit log to data/raw/selections/.
        """
        # ── 1. Fetch options chain via stock-opts-by-param ────────────────────────
        # Pass call_put to narrow the API response; default to "C" if unspecified.
        cp_param = call_put if call_put in ("C", "P") else "C"
        try:
            raw_chain = self.client.get_options_by_param(
                ticker, trade_date,
                dte_from=dte_min, dte_to=dte_max,
                cp=cp_param,
            )
        except ValueError as e:
            print(f"  [selector] Chain unavailable for {ticker} {trade_date}: {e}")
            return None

        # ── 2. Validate chain response ────────────────────────────────────────────
        try:
            validate_chain_response(raw_chain, trade_date, ticker)
        except ValueError as e:
            print(f"  [selector] Chain validation failed for {ticker} {trade_date}: {e}")
            return None

        # ── 3. Normalise columns ──────────────────────────────────────────────────
        df = _normalise_chain(raw_chain.copy())
        # Lower-case after rename so _COL_MAP candidates (e.g. "Ask") still match
        df.columns = [c.lower().strip() for c in df.columns]

        # ── 4. Drop rows with invalid IV (iVol encodes missing IV as -1.0) ────────
        if "implied_volatility" in df.columns:
            df = df[pd.to_numeric(df["implied_volatility"], errors="coerce") > 0]

        # ── 5. Compute DTE where missing ──────────────────────────────────────────
        if "dte" not in df.columns:
            df["dte"] = df.apply(lambda r: _compute_dte(r, trade_date), axis=1)
        else:
            df["dte"] = pd.to_numeric(df["dte"], errors="coerce").fillna(-1).astype(int)

        # ── 6. Compute moneyness where missing ────────────────────────────────────
        if "moneyness" not in df.columns:
            df["moneyness"] = df.apply(_compute_moneyness, axis=1)

        # ── 7. Compute spread_pct where missing ───────────────────────────────────
        if "spread_pct" not in df.columns:
            df["spread_pct"] = df.apply(_compute_spread_pct, axis=1)

        # ── 8. Filter by DTE scope (redundant with API params, safety net) ────────
        df = df[df["dte"].between(dte_min, dte_max)]

        # ── 9. Filter by call_put ─────────────────────────────────────────────────
        if call_put is not None:
            target_cp = _normalise_call_put(call_put)
            if "call_put" in df.columns:
                df["call_put"] = df["call_put"].apply(_normalise_call_put)
                df = df[df["call_put"] == target_cp]

        if df.empty:
            print(f"  [selector] No candidates remain after DTE/IV/call_put filter for {ticker} {trade_date}")
            self._save_audit([], trade_date, ticker)
            return None

        # ── 10. Apply quality gates + build audit records ─────────────────────────
        candidates: list[ContractSelectionRecord] = []
        passed: list[tuple[float, int, dict]] = []  # (selection_score, row_idx, row_dict)

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_dict["trade_date"] = trade_date
            row_dict["ticker"] = ticker

            ok, reason = apply_contract_quality_gates(row_dict)

            # Ranking: prefer calc_otm (|%OTM|, 0=ATM) when available, else |moneyness-1|
            calc_otm = row_dict.get("calc_otm")
            mono = row_dict.get("moneyness")
            if calc_otm is not None:
                try:
                    score = abs(float(calc_otm))
                except (TypeError, ValueError):
                    score = abs(float(mono) - 1.0) if mono is not None else 9999.0
            else:
                score = abs(float(mono) - 1.0) if mono is not None else 9999.0

            csr = ContractSelectionRecord(
                trade_date=trade_date,
                ticker=ticker,
                option_symbol=str(row_dict.get("option_symbol", f"unknown_{idx}")),
                option_id=str(row_dict["option_id"]) if row_dict.get("option_id") is not None else None,
                quote_timestamp=_safe_str(row_dict.get("quote_timestamp")),
                snapshot_timestamp=_safe_str(row_dict.get("snapshot_timestamp")),
                call_put=str(row_dict.get("call_put", "?"))[:1].upper(),
                strike=float(row_dict.get("strike", 0)),
                expiry=str(row_dict.get("expiry", ""))[:10],
                dte=int(row_dict.get("dte", -1)),
                underlying_last_price=_safe_float(row_dict.get("underlying_last_price") or row_dict.get("underlying_price")),
                underlying_mid_price=_safe_float(row_dict.get("underlying_mid_price")),
                moneyness=float(mono) if mono is not None else 0.0,
                bid_price=_safe_float(row_dict.get("bid_price")),
                ask_price=_safe_float(row_dict.get("ask_price")),
                mid_price=_safe_float(row_dict.get("mid_price")),
                spread_pct=_safe_float(row_dict.get("spread_pct")),
                volume=_safe_int(row_dict.get("volume")),
                open_interest=_safe_int(row_dict.get("open_interest")),
                implied_volatility=_safe_float(row_dict.get("implied_volatility")),
                delta=_safe_float(row_dict.get("delta")),
                passed_quality_gates=ok,
                rejection_reason=reason,
                selection_score=round(score, 6),
                final_selected=False,
            )
            candidates.append(csr)

            if ok:
                passed.append((score, idx, row_dict))

        # ── 11. Select winner (lowest score = nearest ATM) ────────────────────────
        if not passed:
            print(f"  [selector] All {len(candidates)} candidates failed quality gates for {ticker} {trade_date}")
            self._save_audit(candidates, trade_date, ticker)
            return None

        passed.sort(key=lambda t: t[0])
        best_score, best_idx, best_row = passed[0]
        best_symbol = str(best_row.get("option_symbol", ""))

        # Mark winner in audit records and add selection_reason
        for csr in candidates:
            if csr.option_symbol == best_symbol:
                csr.final_selected = True
                csr.selection_reason = (
                    f"nearest ATM; score={best_score:.4f}; "
                    f"spread_pct={csr.spread_pct:.3f}" if csr.spread_pct is not None
                    else f"nearest ATM; score={best_score:.4f}"
                )
                break

        self._save_audit(candidates, trade_date, ticker)

        # ── 12. Build and return ContractRecord ───────────────────────────────────
        underlying_price = _safe_float(
            best_row.get("underlying_price") or best_row.get("underlying_last_price")
        )
        if underlying_price is None or underlying_price <= 0:
            print(f"  [selector] Selected contract {best_symbol} has no valid underlying_price — skipping")
            return None

        try:
            result = ContractRecord(
                trade_date=trade_date,
                option_symbol=best_symbol,
                option_id=_safe_str(best_row.get("option_id")),
                ticker=ticker,
                call_put=str(best_row.get("call_put", "C"))[:1].upper(),
                strike=float(best_row.get("strike", 0)),
                expiry=str(best_row.get("expiry", ""))[:10],
                dte=int(best_row.get("dte", 0)),
                underlying_price=underlying_price,
                moneyness=round(float(best_row.get("strike", 0)) / underlying_price, 6),
                bid_price=_safe_float(best_row.get("bid_price")),
                ask_price=_safe_float(best_row.get("ask_price")),
                mid_price=_safe_float(best_row.get("mid_price")),
                last_price=_safe_float(best_row.get("last_price")),
                volume=_safe_int(best_row.get("volume")),
                open_interest=_safe_int(best_row.get("open_interest")),
                implied_volatility=_safe_float(best_row.get("implied_volatility")),
                delta=_safe_float(best_row.get("delta")),
                gamma=_safe_float(best_row.get("gamma")),
                theta=_safe_float(best_row.get("theta")),
                vega=_safe_float(best_row.get("vega")),
                rho=_safe_float(best_row.get("rho")),
                underlying_last_price=_safe_float(best_row.get("underlying_last_price")),
                underlying_mid_price=_safe_float(best_row.get("underlying_mid_price")),
                quote_timestamp=_safe_str(best_row.get("quote_timestamp")),
                snapshot_timestamp=_safe_str(best_row.get("snapshot_timestamp")),
                fetch_date=trade_date,
            )
        except Exception as e:
            print(f"  [selector] Failed to build ContractRecord for {best_symbol}: {e}")
            return None

        print(
            f"  [selector] Selected: {best_symbol} | DTE={result.dte} | "
            f"strike={result.strike} | mono={result.moneyness:.4f} | "
            f"IV={result.implied_volatility:.3f}" if result.implied_volatility else
            f"  [selector] Selected: {best_symbol} | DTE={result.dte} | strike={result.strike}"
        )
        return result

    def _save_audit(
        self,
        candidates: list[ContractSelectionRecord],
        trade_date: str,
        ticker: str,
    ) -> None:
        """Persist candidate audit log as JSON."""
        date_compact = trade_date.replace("-", "")
        path = SELECTIONS_DIR / f"{ticker.lower()}_selection_{date_compact}.json"
        records = [c.model_dump() for c in candidates]
        path.write_text(json.dumps(records, indent=2, default=str))

    def load_audit_log(self, trade_date: str, ticker: str = "QQQ") -> list[ContractSelectionRecord]:
        """Load a previously saved selection audit log."""
        date_compact = trade_date.replace("-", "")
        path = SELECTIONS_DIR / f"{ticker.lower()}_selection_{date_compact}.json"
        if not path.exists():
            return []
        raw = json.loads(path.read_text())
        return [ContractSelectionRecord(**r) for r in raw]


# ── Helpers ───────────────────────────────────────────────────────────────────────

def _safe_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        f = float(v)
        return f if pd.notna(f) else None
    except (TypeError, ValueError):
        return None


def _safe_int(v) -> Optional[int]:
    if v is None:
        return None
    try:
        f = float(v)
        return int(f) if pd.notna(f) else None
    except (TypeError, ValueError):
        return None


def _safe_str(v) -> Optional[str]:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return str(v)
