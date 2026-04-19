"""
databento_price_client.py — Cached Databento intraday price bar client.

Fetches 1-min OHLCV from Databento EQUS.MINI, converts UTC → America/New_York,
filters to regular session (9:30–16:00 ET), and resamples to the requested interval.

At 5-min: 78 bars/day (9:30, 9:35, …, 15:55).

Auth:
    DATABENTO_API_KEY in .env — never hardcode.

Cache layout:
    data/raw/databento/
        {ticker}_1m_{YYYYMM}.parquet   ← raw 1-min, market hours, ET timezone
        {ticker}_{interval}_{YYYYMM}.parquet  ← resampled (derived, cached on first use)
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).resolve().parent.parent.parent
DATABENTO_DIR = BASE / "data" / "raw" / "databento"
DATABENTO_DIR.mkdir(parents=True, exist_ok=True)

_RESAMPLE_AGG = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
_ET = "America/New_York"


def _get_api_key() -> str:
    key = os.getenv("DATABENTO_API_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "DATABENTO_API_KEY not set in .env. "
            "Add it to .env — do NOT hardcode or paste into chat."
        )
    return key


class DatabentoPriceClient:
    """
    Cached Databento OHLCV client. All methods check parquet cache first.

    Dataset: EQUS.MINI (available from 2023-03-28)
    Schema: ohlcv-1m
    """

    def __init__(self, force: bool = False):
        self.force = force

    # ── Cache helpers ─────────────────────────────────────────────────────────

    def _cache_path(self, name: str) -> Path:
        return DATABENTO_DIR / f"{name}.parquet"

    def _load_cache(self, name: str) -> pd.DataFrame | None:
        p = self._cache_path(name)
        if p.exists() and not self.force:
            return pd.read_parquet(p)
        return None

    def _save_cache(self, df: pd.DataFrame, name: str) -> None:
        self._cache_path(name).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self._cache_path(name))

    # ── Fetch raw 1-min for a calendar month ─────────────────────────────────

    def _fetch_1m_month(self, ticker: str, year: int, month: int) -> pd.DataFrame:
        """
        Fetch full calendar month of 1-min bars from Databento.
        Returns DataFrame with DatetimeTZDtype index (America/New_York), market hours only.
        """
        import databento as db  # type: ignore

        start = f"{year:04d}-{month:02d}-01"
        # End = first day of next month
        if month == 12:
            end = f"{year + 1:04d}-01-01"
        else:
            end = f"{year:04d}-{month + 1:02d}-01"

        print(f"  [databento] Fetching EQUS.MINI ohlcv-1m {ticker} {start} → {end}")
        client = db.Historical(_get_api_key())
        data = client.timeseries.get_range(
            dataset="EQUS.MINI",
            symbols=[ticker],
            schema="ohlcv-1m",
            start=start,
            end=end,
            stype_in="raw_symbol",
        )
        df = data.to_df()
        if df.empty:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        # Keep only price/volume columns; index is ts_event (UTC)
        cols = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
        df = df[cols].copy()

        # Databento prices are in fixed-point (1e-9 scale for equities)
        for col in ["open", "high", "low", "close"]:
            if col in df.columns and df[col].abs().max() > 1_000_000:
                df[col] = df[col] / 1_000_000_000

        # Convert UTC → ET and filter to regular session
        df.index = df.index.tz_convert(_ET)
        df = df.between_time("09:30", "15:59")  # inclusive of 9:30, last bar at 15:5x

        return df

    def get_month_bars(
        self,
        ticker: str,
        year_month: str,
        interval: str = "5min",
    ) -> pd.DataFrame:
        """
        Prefetch/cache an entire month's bars at the requested interval.
        year_month: "YYYYMM" string, e.g. "202504"
        """
        year, month = int(year_month[:4]), int(year_month[4:])
        return self._get_resampled(ticker, year, month, interval)

    # ── Internal: get resampled bars for a month ──────────────────────────────

    def _get_resampled(self, ticker: str, year: int, month: int, interval: str) -> pd.DataFrame:
        yyyymm = f"{year:04d}{month:02d}"
        t = ticker.lower()

        # Check resampled cache first
        resamp_key = f"{t}_{interval.replace('min', 'm')}_{yyyymm}"
        cached = self._load_cache(resamp_key)
        if cached is not None:
            if not isinstance(cached.index, pd.DatetimeIndex):
                cached.index = pd.to_datetime(cached.index, utc=True).tz_convert(_ET)
            elif cached.index.tzinfo is None:
                cached.index = cached.index.tz_localize(_ET)
            return cached

        # Load or fetch 1-min
        raw_key = f"{t}_1m_{yyyymm}"
        df1m = self._load_cache(raw_key)
        if df1m is None:
            df1m = self._fetch_1m_month(ticker, year, month)
            if df1m.empty:
                return df1m
            self._save_cache(df1m, raw_key)
            print(f"  [saved] data/raw/databento/{raw_key}.parquet ({len(df1m)} rows)")
        else:
            if not isinstance(df1m.index, pd.DatetimeIndex):
                df1m.index = pd.to_datetime(df1m.index, utc=True).tz_convert(_ET)
            elif df1m.index.tzinfo is None:
                df1m.index = df1m.index.tz_localize(_ET)

        if interval == "1min":
            return df1m

        # Resample
        agg = {k: v for k, v in _RESAMPLE_AGG.items() if k in df1m.columns}
        df_rs = df1m.resample(interval).agg(agg).dropna(subset=["close"])
        # Remove any bars outside market hours introduced by resample alignment
        df_rs = df_rs.between_time("09:30", "15:59")

        self._save_cache(df_rs, resamp_key)
        print(f"  [saved] data/raw/databento/{resamp_key}.parquet ({len(df_rs)} rows)")
        return df_rs

    # ── Public: get bars for a single trading day ─────────────────────────────

    def get_bars(
        self,
        ticker: str,
        trade_date: str,
        interval: str = "5min",
    ) -> pd.DataFrame:
        """
        Return OHLCV bars for one trading day, regular session only (9:30–15:55 ET).
        At 5-min: 78 bars per day. Index is tz-aware America/New_York.
        interval: "1min" | "5min" | "15min" | "30min"
        Fetches 1-min from Databento if not cached (UTC → ET conversion, filter 09:30-16:00),
        then resamples. Cache: data/raw/databento/{ticker}_{interval}_{YYYYMM}.parquet (per month)
        """
        dt = pd.Timestamp(trade_date)
        month_df = self._get_resampled(ticker, dt.year, dt.month, interval)
        if month_df.empty:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        day_mask = month_df.index.date == dt.date()
        return month_df.loc[day_mask].copy()
