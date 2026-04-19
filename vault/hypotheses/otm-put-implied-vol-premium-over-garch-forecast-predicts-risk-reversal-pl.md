---
hypothesis_id: 8d1dbce5-93df-4850-84a5-c39ea46590d0
status: candidate
confidence: 0.78
tags: ['volatility-skew', 'garch', 'risk-reversal', 'otm-puts', 'insurance-demand', 'implied-volatility']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# OTM Put Implied Vol Premium Over GARCH Forecast Predicts Risk-Reversal P&L

**Status:** candidate | **Confidence:** ███████░░░ 78%

#volatility_skew #garch #risk_reversal #otm_puts #insurance_demand #implied_volatility

## Claim

When the implied volatility of 25-delta SPX puts exceeds the GARCH(1,1) volatility forecast by more than 4 percentage points, selling the 25-delta put (or selling the risk-reversal — short put, long call) generates positive expected returns. The excess premium in OTM puts, beyond what the vol model predicts, is a measurable and tradeable structural premium driven by insurance demand.

## Rationale

The volatility skew theme in this knowledge base documents the persistent structural premium in OTM puts driven by institutional insurance demand. Sinclair quantifies the skew-premium empirically: OTM put IV consistently exceeds ATM IV and realised vol for downside strikes. The GARCH theme provides a forecast baseline: if GARCH predicts the vol level that would be 'fair' for the OTM put given fat-tail dynamics, the excess above that forecast is pure insurance premium. Risk-reversals (short OTM put, long OTM call) are the natural vehicle to harvest this premium while limiting upside risk. The skew theme identifies that the premium is structural, not cyclical — it persists even when adjusting for historical kurtosis.

## How to Test

Using ORATS daily data 2005-2023: each month, fit GARCH(1,1) to trailing SPX returns. Compute 'fair' 25-delta put IV from GARCH + Black-Scholes. If market 25-delta put IV exceeds GARCH-fair IV by > 4pp, sell 25-delta SPX put (or risk-reversal). Track 21-day P&L across 100+ qualifying periods. Falsified if average P&L is negative in periods where the excess premium condition is met, or if the 4pp threshold is not a significant predictor of sign of return. Test sensitivity to threshold choice (2pp, 4pp, 6pp).

**Data required:** ORATS 25-delta put IV and 25-delta call IV daily series 2005-2023; SPX daily returns for GARCH fitting

### Variables Needed

- `volatility_skew`
- `otm_put_iv`
- `garch_forecast`
- `risk_reversal_pnl`

### What Would Support It

Positive average P&L when excess premium > 4pp; Sharpe > 0.4; premium threshold is monotonically predictive of return sign

### What Would Falsify It

Negative average P&L in high-excess-premium periods, or no monotonic relationship between excess premium and P&L

## Source Themes

- [[Volatility Skew and Structural OTM Put Premium]]
- [[Historical vs. Implied Volatility: Forecasting and the Variance Premium]]
- [[Volatility Term Structure: Contango, Backwardation, and Calendar Spreads]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
- `ddc2a298cd88`
