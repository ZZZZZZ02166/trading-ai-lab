---
hypothesis_id: 283f3c9d-766f-469c-bde4-9d37599dae2f
status: candidate
confidence: 0.85
tags: ['variance-premium', 'implied-volatility', 'realized-volatility', 'straddle', 'short-vol']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Realised Vol vs. Implied: Short Straddle Edge Persists When IV Exceeds 30-Day HV

**Status:** candidate | **Confidence:** ████████░░ 85%

#variance_premium #implied_volatility #realized_volatility #straddle #short_vol

## Claim

When implied volatility consistently exceeds realised volatility (30-day HV) by more than 2 percentage points, short ATM straddles generate positive expected returns after delta-hedging costs. The variance premium — IV minus realised vol — predicts straddle P&L more reliably than the absolute level of IV.

## Rationale

Sinclair's Volatility Trading documents empirical evidence of a persistent variance premium in equity indices, where implied volatility systematically overestimates realised volatility. Natenberg's Option Volatility and Pricing establishes that straddle P&L is approximately (realised vol - implied vol) × vega per unit time. Together these two sources converge on the testable claim that the sign and magnitude of IV-HV spread is the primary predictor of short-straddle profitability, not the absolute level of either. The gamma-theta tradeoff theme confirms that theta collected equals the cost of gamma exposure only when implied vol matches realised; any persistent gap is extractable edge.

## How to Test

Backtest using daily SPX options data (ORATS or CBOE) from 2005-2023. Each Monday: measure 30-day ATM IV and trailing 30-day close-to-close HV. If IV - HV > 2pp, sell ATM straddle, delta-hedge daily at close, close at 21 DTE. Falsified if average P&L is negative across 100+ trades when the spread condition is met. Control for VIX regime (below/above 20) to check if the edge is regime-dependent.

**Data required:** ORATS daily options data with IV surface, SPX daily returns 2005-2023

### Variables Needed

- `implied_volatility`
- `realized_volatility`
- `straddle_pnl`
- `delta`
- `vega`

### What Would Support It

Positive average P&L on 100+ short straddle entries when IV-HV spread > 2pp; Sharpe > 0.5 before transaction costs

### What Would Falsify It

Negative average P&L in the IV-HV > 2pp subsample, or no significant difference in P&L between high-spread and low-spread environments

## Source Themes

- [[Gamma and Theta: The Core Greeks Tradeoff]]
- [[Historical vs. Implied Volatility: Forecasting and the Variance Premium]]
- [[Straddle Strategies: Long and Short Volatility Expressions]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
- `9e3a85506c46`
