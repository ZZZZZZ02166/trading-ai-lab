---
hypothesis_id: b51fd510-56f0-4917-b7dc-e80bf3fdfa1c
status: candidate
confidence: 0.8
tags: ['garch', 'volatility-forecasting', 'historical-volatility', 'implied-volatility', 'straddle', 'entry-timing']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# GARCH(1,1) Forecast Outperforms Rolling HV for Timing Straddle Entry

**Status:** candidate | **Confidence:** ████████░░ 80%

#garch #volatility_forecasting #historical_volatility #implied_volatility #straddle #entry_timing

## Claim

When GARCH(1,1) forecasts a vol level below current ATM implied volatility, selling a 30-day ATM straddle generates higher risk-adjusted returns than when entry is timed using a simple 30-day rolling historical volatility filter. GARCH's mean-reversion term predicts the direction of vol change more accurately than rolling HV, particularly after vol spikes.

## Rationale

Sinclair's Volatility Trading provides both theoretical justification (GARCH captures clustering and mean reversion; rolling HV is IGARCH with no mean reversion) and empirical evidence that GARCH forecasts dominate simple estimators for near-term vol prediction. The term structure theme in this knowledge base shows that GARCH term structure (expected vol trajectory) can be compared to the market's implied term structure to identify richness or cheapness. If GARCH forecasts mean reversion to a lower vol level and the market has not priced this in (flat or upward-sloping term structure), the entry has positive edge by construction.

## How to Test

Fit GARCH(1,1) to trailing 2 years of daily SPX returns, updated monthly. Compare GARCH 30-day forecast to ATM 30-day IV (from ORATS). Entry rule A: enter short straddle when GARCH forecast < ATM IV. Entry rule B: enter when 30-day rolling HV < ATM IV. Track risk-adjusted returns (Sharpe) for 100+ entry-exit cycles per rule from 2005-2023. Falsified if GARCH-based Sharpe is not significantly higher than rolling-HV-based Sharpe. Report t-statistic and confidence interval.

**Data required:** SPX daily returns 2003-2023 (2-year burn-in for GARCH), ORATS 30-day ATM IV

### Variables Needed

- `garch_forecast`
- `implied_volatility`
- `historical_volatility`
- `straddle_returns`
- `sharpe`

### What Would Support It

Sharpe ratio of GARCH-timed entries > rolling-HV-timed entries; difference statistically significant; improvement concentrated in post-spike periods

### What Would Falsify It

No significant Sharpe difference between timing methods, or rolling HV outperforms GARCH

## Source Themes

- [[Volatility Term Structure: Contango, Backwardation, and Calendar Spreads]]
- [[Historical vs. Implied Volatility: Forecasting and the Variance Premium]]
- [[Implied Volatility Mean Reversion and Variance Swaps]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
