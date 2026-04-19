"""
ivolatility_client.py — Cached wrapper around the iVolatility Python package.

Correct call pattern (v1.9+):
    method = ivol.setMethod('/endpoint/path')
    df = method(param1=val1, param2=val2, from_=date)  # 'from_' maps to 'from'

Auth:
    ivol.setLoginParams(apiKey=KEY)  — reads from .env only, never hardcoded.

Rate limit: 1 req/sec. All data cached as parquet in data/raw/ subdirectories.

Confirmed working endpoints (tested 2026-04-17, probe_intraday_v2.py):
    /equities/eod/stock-prices              → OHLCV, params: symbol, from_, to
    /equities/eod/ivx                       → constant-maturity IV, params: symbol, from_, to
    /equities/eod/stock-opts-by-param       → options chain by DTE+moneyness range
    /equities/eod/single-stock-option-raw-iv → single contract history by optionId or symbol
    /equities/intraday/single-equity-optionsymbol-rawiv
                                            → intraday by optionSymbol (3-space OCC format)
                                              required: optionSymbol, date, minuteType
    /equities/intraday/single-equity-option-rawiv
                                            → intraday by ticker+contract params
                                              required: symbol, date, expDate, strike, optType, minuteType

Subscription-limited (403 Forbidden on this account):
    /equities/eod/options-rawiv             → full EOD chain raw IV (higher tier)
    /equities/intraday/equity-options-rawiv → full intraday chain (higher tier)

Valid minuteType values: MINUTE_1, MINUTE_5, MINUTE_15, CUSTOM (requires minutes=N)

Directory layout:
    data/raw/
        qqq_eod_prices.parquet
        qqq_ivx.parquet
        chains/    ← stock-opts-by-param snapshots: qqq_opts_by_param_YYYYMMDD.parquet
                      intraday single-option cache: intraday_{safe_symbol}_{date}.parquet
        contracts/ ← single contract EOD history: {option_id}.parquet
        selections/ ← written by contract_selector (audit logs)
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE / "data" / "raw"
CHAINS_DIR = RAW_DIR / "chains"
CONTRACTS_DIR = RAW_DIR / "contracts"

for _d in (RAW_DIR, CHAINS_DIR, CONTRACTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

_RATE_LIMIT_SLEEP = 1.05


def _get_api_key() -> str:
    key = os.getenv("IVOLATILITY_API_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "IVOLATILITY_API_KEY not set in .env. "
            "Add it to .env — do NOT hardcode or paste into chat."
        )
    return key


def _ivol():
    try:
        import ivolatility as ivol  # type: ignore
        return ivol
    except ImportError:
        raise ImportError("Run: pip install ivolatility")


def _auth_and_method(endpoint: str):
    """Authenticate and return a callable for the given endpoint."""
    ivol = _ivol()
    ivol.setLoginParams(apiKey=_get_api_key())
    return ivol.setMethod(endpoint)


class IVolatilityClient:
    """
    Cached iVolatility data client.

    All methods check parquet cache first; only hit the API when missing or force=True.
    Correct call pattern: _auth_and_method('/endpoint')(**params)
    """

    def __init__(self, force: bool = False):
        self.force = force

    # ── Cache helpers ─────────────────────────────────────────────────────────────

    def _cache_path(self, name: str, subdir: Path | None = None) -> Path:
        base = subdir if subdir else RAW_DIR
        return base / f"{name}.parquet"

    def _load_cache(self, name: str, subdir: Path | None = None) -> pd.DataFrame | None:
        p = self._cache_path(name, subdir)
        if p.exists() and not self.force:
            print(f"  [cache] {p.relative_to(BASE)}")
            return pd.read_parquet(p)
        return None

    def _save_cache(self, df: pd.DataFrame, name: str, subdir: Path | None = None) -> None:
        path = self._cache_path(name, subdir)
        df.to_parquet(path, index=False)
        print(f"  [saved] {path.relative_to(BASE)} ({len(df)} rows)")

    def _fetch(self, endpoint: str, **params) -> pd.DataFrame:
        """
        Call iVolatility API. Raises ValueError on empty response.
        Correct pattern: ivol.setMethod('/endpoint')(**params)
        """
        method = _auth_and_method(endpoint)
        time.sleep(_RATE_LIMIT_SLEEP)
        result = method(**params)
        if result is None or (isinstance(result, pd.DataFrame) and result.empty):
            raise ValueError(
                f"iVolatility '{endpoint}' returned empty. "
                f"Params: {params}. Check entitlement and date range."
            )
        if not isinstance(result, pd.DataFrame):
            result = pd.DataFrame(result)
        return result

    # ── EOD underlying data ───────────────────────────────────────────────────────

    def get_eod_prices(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """
        Daily OHLCV. Columns: date, open, high, low, close, volume, ...
        Cache: data/raw/{ticker}_eod_prices.parquet
        """
        cache_key = f"{ticker.lower()}_eod_prices"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached

        print(f"  Fetching EOD prices: {ticker} {start} → {end}")
        df = self._fetch("/equities/eod/stock-prices", symbol=ticker, from_=start, to=end)
        df.columns = [c.lower().strip() for c in df.columns]
        self._save_cache(df, cache_key)
        return df

    def get_ivx(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """
        Constant-maturity IV index. Columns include: date, 30d IV Mean, 30d IV Call, 30d IV Put, ...
        Cache: data/raw/{ticker}_ivx.parquet
        """
        cache_key = f"{ticker.lower()}_ivx"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached

        print(f"  Fetching IVX: {ticker} {start} → {end}")
        df = self._fetch("/equities/eod/ivx", symbol=ticker, from_=start, to=end)
        self._save_cache(df, cache_key)
        return df

    # ── Options chain (contract discovery) ───────────────────────────────────────

    def get_options_by_param(
        self,
        ticker: str,
        trade_date: str,
        dte_from: int = 0,
        dte_to: int = 5,
        cp: str = "C",
        moneyness_from: float = -10.0,
        moneyness_to: float = 10.0,
    ) -> pd.DataFrame:
        """
        Fetch options candidates by DTE range and moneyness range for one trade_date.

        Uses /equities/eod/stock-opts-by-param — confirmed working.
        Returns full option rows with: option_symbol, dte, expiration_date, call_put,
        price_strike, iv, delta, Ask, Bid, underlying_price, calc_OTM, option_id.

        calc_OTM: percentage from ATM; 0 = ATM, positive = OTM, negative = ITM.
        iv = -1.0 means no valid IV — filter these out before use.

        Cache: data/raw/chains/qqq_opts_by_param_YYYYMMDD_{cp}.parquet
        """
        date_compact = trade_date.replace("-", "")
        cache_key = f"{ticker.lower()}_opts_by_param_{date_compact}_{cp.upper()}"
        cached = self._load_cache(cache_key, subdir=CHAINS_DIR)
        if cached is not None:
            return cached

        print(f"  Fetching options by param: {ticker} {trade_date} DTE={dte_from}-{dte_to} {cp}")
        try:
            df = self._fetch(
                "/equities/eod/stock-opts-by-param",
                symbol=ticker,
                tradeDate=trade_date,
                dteFrom=dte_from,
                dteTo=dte_to,
                cp=cp,
                moneynessFrom=moneyness_from,
                moneynessTo=moneyness_to,
            )
        except ValueError as e:
            raise ValueError(
                f"stock-opts-by-param failed for {ticker} {trade_date}: {e}"
            ) from e

        self._save_cache(df, cache_key, subdir=CHAINS_DIR)
        return df

    def get_options_by_param_range(
        self,
        ticker: str,
        start: str,
        end: str,
        dte_from: int = 0,
        dte_to: int = 5,
        cp: str = "C",
        moneyness_from: float = -5.0,
        moneyness_to: float = 5.0,
        skip_existing: bool = True,
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch options candidates for every trading day in [start, end].
        Returns dict of {date_str: DataFrame}.
        """
        trading_days = pd.bdate_range(start=start, end=end)
        results: dict[str, pd.DataFrame] = {}
        for dt in trading_days:
            date_str = dt.strftime("%Y-%m-%d")
            date_compact = dt.strftime("%Y%m%d")
            cache_key = f"{ticker.lower()}_opts_by_param_{date_compact}_{cp.upper()}"
            if skip_existing and not self.force and self._cache_path(cache_key, CHAINS_DIR).exists():
                results[date_str] = pd.read_parquet(self._cache_path(cache_key, CHAINS_DIR))
                continue
            try:
                df = self.get_options_by_param(ticker, date_str, dte_from, dte_to, cp, moneyness_from, moneyness_to)
                results[date_str] = df
            except ValueError as e:
                print(f"  [warn] {date_str}: {e}")
        return results

    # ── Single contract history ───────────────────────────────────────────────────

    def get_contract_history(
        self,
        option_id: int | None = None,
        option_symbol: str | None = None,
        start: str = "",
        end: str = "",
    ) -> pd.DataFrame:
        """
        Historical EOD data for ONE selected option contract.

        Provide either option_id (preferred — numeric iVol ID) or option_symbol.
        Uses /equities/eod/single-stock-option-raw-iv.

        Cache: data/raw/contracts/{option_id_or_symbol}.parquet
        """
        if option_id is not None:
            cache_key = f"contract_{option_id}"
            id_params = {"optionId": option_id}
        elif option_symbol is not None:
            safe = option_symbol.strip().replace(" ", "_").replace("/", "_")
            cache_key = f"contract_{safe}"
            id_params = {"symbol": option_symbol.strip()}
        else:
            raise ValueError("Provide either option_id or option_symbol.")

        cached = self._load_cache(cache_key, subdir=CONTRACTS_DIR)
        if cached is not None:
            return cached

        label = option_id or option_symbol
        print(f"  Fetching contract history: {label} {start} → {end}")
        df = self._fetch(
            "/equities/eod/single-stock-option-raw-iv",
            **id_params,
            from_=start,
            to=end,
        )
        self._save_cache(df, cache_key, subdir=CONTRACTS_DIR)
        return df

    # ── Intraday single-option (confirmed working 2026-04-17) ────────────────────

    def get_intraday_option_by_symbol(
        self,
        option_symbol: str,
        trade_date: str,
        minute_type: str = "MINUTE_5",
    ) -> pd.DataFrame | None:
        """
        Intraday raw IV + Greeks for one contract, identified by OCC optionSymbol.

        Confirmed working endpoint: /equities/intraday/single-equity-optionsymbol-rawiv
        Required params: optionSymbol (exact OCC format with spaces), date, minuteType

        optionSymbol must use the exact spacing from EOD chain (e.g. "QQQ   250102C00510000").
        minute_type: MINUTE_1 | MINUTE_5 | MINUTE_15 | CUSTOM

        Returns None on any API failure (logs reason). Caller should fall back to
        get_intraday_option_by_params() if this returns None.

        Cache: data/raw/chains/intraday_{safe_symbol}_{date_compact}_{minute_type}.parquet
        """
        sym_exact = option_symbol  # preserve OCC spacing — do NOT strip
        safe = option_symbol.strip().replace(" ", "_")
        date_compact = trade_date.replace("-", "")
        cache_key = f"intraday_{safe}_{date_compact}_{minute_type}"
        cached = self._load_cache(cache_key, subdir=CHAINS_DIR)
        if cached is not None:
            return cached

        print(f"  Fetching intraday by symbol: {sym_exact.strip()} {trade_date} {minute_type}")
        try:
            df = self._fetch(
                "/equities/intraday/single-equity-optionsymbol-rawiv",
                optionSymbol=sym_exact,
                date=trade_date,
                minuteType=minute_type,
            )
            self._save_cache(df, cache_key, subdir=CHAINS_DIR)
            return df
        except Exception as e:
            print(f"  [intraday by symbol] {sym_exact.strip()} {trade_date}: {str(e)[:100]}")
            return None

    def get_intraday_option_by_params(
        self,
        ticker: str,
        trade_date: str,
        exp_date: str,
        strike: float,
        opt_type: str,
        minute_type: str = "MINUTE_5",
    ) -> pd.DataFrame | None:
        """
        Intraday raw IV + Greeks identified by ticker + contract parameters.

        Confirmed working endpoint: /equities/intraday/single-equity-option-rawiv
        Required params: symbol, date, expDate, strike, optType, minuteType

        opt_type: "CALL" or "PUT"
        minute_type: MINUTE_1 | MINUTE_5 | MINUTE_15 | CUSTOM

        Returns None on failure. Use as fallback when get_intraday_option_by_symbol()
        fails (e.g. optionSymbol format uncertain for a given contract).

        Cache: data/raw/chains/intraday_{ticker}_{date}_{exp}_{strike}_{opt_type}_{minute_type}.parquet
        """
        safe_strike = str(int(strike * 1000)).zfill(8)
        date_compact = trade_date.replace("-", "")
        exp_compact  = exp_date.replace("-", "")
        cache_key = (
            f"intraday_{ticker.lower()}_{date_compact}_{exp_compact}"
            f"_{safe_strike}_{opt_type.upper()}_{minute_type}"
        )
        cached = self._load_cache(cache_key, subdir=CHAINS_DIR)
        if cached is not None:
            return cached

        print(f"  Fetching intraday by params: {ticker} {trade_date} exp={exp_date} K={strike} {opt_type} {minute_type}")
        try:
            df = self._fetch(
                "/equities/intraday/single-equity-option-rawiv",
                symbol=ticker,
                date=trade_date,
                expDate=exp_date,
                strike=int(strike) if strike == int(strike) else strike,
                optType=opt_type.upper(),
                minuteType=minute_type,
            )
            self._save_cache(df, cache_key, subdir=CHAINS_DIR)
            return df
        except Exception as e:
            print(f"  [intraday by params] {ticker} {trade_date} K={strike} {opt_type}: {str(e)[:100]}")
            return None
