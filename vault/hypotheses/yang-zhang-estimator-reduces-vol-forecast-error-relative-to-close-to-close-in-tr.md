---
hypothesis_id: ba5d4d45-c6a0-4b7e-abc2-410a248558fb
status: candidate
confidence: 0.81
tags: ['yang-zhang', 'volatility-estimator', 'realized-volatility', 'forecasting', 'historical-volatility']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Yang-Zhang Estimator Reduces Vol Forecast Error Relative to Close-to-Close in Trending Markets

**Status:** candidate | **Confidence:** ████████░░ 81%

#yang_zhang #volatility_estimator #realized_volatility #forecasting #historical_volatility

## Claim

When the underlying asset exhibits a directional trend (absolute 5-day return > 2%), the Yang-Zhang volatility estimator produces a realized volatility estimate that better predicts next-period volatility (lower MSPE) compared to close-to-close returns. The efficiency advantage of Yang-Zhang (approximately 14× vs. 1× for close-to-close) is most pronounced in markets with significant overnight gaps or intraday price ranges.

## Rationale

Sinclair's Volatility Trading provides the theoretical derivation and efficiency comparison of all major vol estimators: close-to-close (1×), Parkinson (4.9×), Garman-Klass (7.4×), Rogers-Satchell (≈5×), and Yang-Zhang (14×). The efficiency gain means that Yang-Zhang achieves the same estimation accuracy with far fewer observations, which is especially valuable in trending or gapping markets where close-to-close misses the intraday range and overnight gaps entirely. The vol estimator theme in this knowledge base confirms this from multiple sources. A testable hypothesis is whether the efficiency advantage translates directly to lower hedging error when using Yang-Zhang as the realized-vol input for delta-hedging decisions.

## How to Test

Using daily OHLC data for SPX (or a single large-cap stock) 2010-2023: compute all five estimators on rolling 21-day windows. In each window, classify the market as trending (|5d return| > 2%) or mean-reverting. Measure next-21d forecast error (MSPE) for each estimator separately for trending and non-trending periods. Falsified if Yang-Zhang MSPE is not significantly lower than close-to-close MSPE in trending periods. Secondary test: does using Yang-Zhang as the implied-vol anchor for hedging reduce P&L variance vs. close-to-close?

**Data required:** SPX or individual stock OHLC daily data 2010-2023; ORATS for implied vol comparison

### Variables Needed

- `yang_zhang_estimator`
- `realized_volatility`
- `close_to_close_vol`
- `mspe`
- `trending_regime`

### What Would Support It

Yang-Zhang MSPE < close-to-close MSPE by > 30% in trending periods; advantage shrinks in non-trending periods

### What Would Falsify It

No significant MSPE difference between estimators in trending periods, or Yang-Zhang underperforms in some trending conditions

## Source Themes

- [[High-Efficiency Volatility Estimators: Parkinson, Garman-Klass, Rogers-Satchell]]
- [[Historical vs. Implied Volatility: Forecasting and the Variance Premium]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
