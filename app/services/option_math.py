"""
option_math.py — Pure mathematical functions for volatility estimation and analysis.

No I/O. No API calls. Accepts and returns pandas Series/DataFrames.

Functions:
  close_to_close_hv(prices, window, trading_days)
  yang_zhang_hv(ohlc, window, trading_days)
  garch_vol_forecast(returns, p, q)
  rmse(actual, predicted)
  forward_realized_vol(prices, horizon, trading_days)
  iv_hv_spread(iv_series, hv_series)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252


def close_to_close_hv(prices: pd.Series, window: int = 20, trading_days: int = TRADING_DAYS_PER_YEAR) -> pd.Series:
    """
    Rolling close-to-close historical volatility (annualised).

    Args:
        prices: Series of closing prices, DatetimeIndex.
        window: Rolling window in trading days.
        trading_days: Number of trading days per year for annualisation.

    Returns:
        Series of annualised HV, same index as prices.
    """
    log_returns = np.log(prices / prices.shift(1))
    rolling_std = log_returns.rolling(window).std(ddof=1)
    return rolling_std * np.sqrt(trading_days)


def yang_zhang_hv(
    ohlc: pd.DataFrame,
    window: int = 20,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> pd.Series:
    """
    Rolling Yang-Zhang volatility estimator (annualised).

    Yang-Zhang = sqrt(σ²_overnight + k·σ²_OC + (1-k)·σ²_RS)

    Where:
      σ²_overnight = variance of overnight log-returns (close-to-open)
      σ²_OC        = variance of open-to-close log-returns
      σ²_RS        = Rogers-Satchell variance
      k            = optimal coefficient = 0.34 / (1.34 + (n+1)/(n-1))

    Args:
        ohlc: DataFrame with columns open, high, low, close (lowercase), DatetimeIndex.
        window: Rolling window in trading days.
        trading_days: Number of trading days per year for annualisation.

    Returns:
        Series of annualised YZ-HV, same index as ohlc.
    """
    o = ohlc["open"]
    h = ohlc["high"]
    l = ohlc["low"]
    c = ohlc["close"]

    # Overnight return: open today / close yesterday
    log_oc_lag = np.log(o / c.shift(1))  # overnight
    # Open-to-close return
    log_co = np.log(c / o)               # open-to-close

    # Rogers-Satchell component: E[ln(H/C)·ln(H/O) + ln(L/C)·ln(L/O)]
    log_ho = np.log(h / o)
    log_hc = np.log(h / c)
    log_lo = np.log(l / o)
    log_lc = np.log(l / c)
    rs = log_ho * log_hc + log_lo * log_lc  # Rogers-Satchell per bar

    n = window
    k = 0.34 / (1.34 + (n + 1) / (n - 1))

    # Rolling variances (sum / n-1 for unbiased)
    mean_oc_lag = log_oc_lag.rolling(n).mean()
    mean_co = log_co.rolling(n).mean()

    var_overnight = ((log_oc_lag - mean_oc_lag) ** 2).rolling(n).sum() / (n - 1)
    var_oc = ((log_co - mean_co) ** 2).rolling(n).sum() / (n - 1)
    var_rs = rs.rolling(n).mean()

    yz_var = var_overnight + k * var_oc + (1 - k) * var_rs
    yz_var = yz_var.clip(lower=0)  # guard against floating-point negatives

    return np.sqrt(yz_var * trading_days)


def garch_vol_forecast(returns: pd.Series, p: int = 1, q: int = 1) -> pd.Series:
    """
    GARCH(p,q) conditional volatility forecast (annualised).

    Fits one global GARCH model over the full returns series and returns
    the in-sample conditional volatility (annualised).

    Args:
        returns: Series of log-returns (not percent, not annualised).
        p: ARCH lag order.
        q: GARCH lag order.

    Returns:
        Series of annualised conditional volatility, same index as returns.
        Returns NaN series if fitting fails.
    """
    try:
        from arch import arch_model  # type: ignore

        model = arch_model(returns.dropna() * 100, vol="Garch", p=p, q=q, dist="normal")
        res = model.fit(disp="off", show_warning=False)
        cond_vol = res.conditional_volatility / 100  # back to log-return scale
        # Annualise and reindex to original index
        annualised = cond_vol * np.sqrt(TRADING_DAYS_PER_YEAR)
        return annualised.reindex(returns.index)
    except Exception:
        return pd.Series(np.nan, index=returns.index)


def forward_realized_vol(
    prices: pd.Series,
    horizon: int = 20,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> pd.Series:
    """
    Rolling forward realised volatility — the close-to-close HV over the NEXT
    `horizon` trading days from each date.

    Used as the 'ground truth' benchmark for comparing HV estimators.

    Args:
        prices: Series of closing prices, DatetimeIndex.
        horizon: Look-ahead window in trading days.
        trading_days: Number of trading days per year for annualisation.

    Returns:
        Series of annualised forward-realised vol. NaN for last `horizon` rows.
    """
    log_returns = np.log(prices / prices.shift(1))
    # Reverse-rolling: compute std over the NEXT n observations
    forward_std = log_returns.iloc[::-1].rolling(horizon).std(ddof=1).iloc[::-1]
    return forward_std * np.sqrt(trading_days)


def rmse(actual: pd.Series, predicted: pd.Series) -> float:
    """Root mean squared error between two aligned Series, ignoring NaNs."""
    mask = actual.notna() & predicted.notna()
    if mask.sum() == 0:
        return float("nan")
    return float(np.sqrt(((actual[mask] - predicted[mask]) ** 2).mean()))


def iv_hv_spread(iv_series: pd.Series, hv_series: pd.Series) -> pd.Series:
    """
    Daily IV minus HV spread.

    Both inputs should be annualised decimal volatility (e.g. 0.20 = 20%).
    """
    return iv_series - hv_series
