---
hypothesis_id: 30f2d80f-6991-4803-b2c3-1dd456fef311
status: candidate
confidence: 0.74
tags: ['condor', 'straddle', 'defined-risk', 'pnl-distribution', 'vix', 'skewness']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Condor P&L Distribution Is Positively Skewed Relative to Straddle When Vol Is Elevated

**Status:** candidate | **Confidence:** ███████░░░ 74%

#condor #straddle #defined_risk #pnl_distribution #vix #skewness

## Claim

When implied volatility is elevated (VIX > 25), an iron condor on SPX with wings 15% OTM generates a more positively skewed P&L distribution over 21 days compared to a short ATM straddle, even though the condor has lower expected P&L. The defined-risk structure of the condor reduces left-tail exposure to levels that improve the risk-adjusted return per unit of maximum loss.

## Rationale

The multi-leg volatility strategies theme documents how strangles and condors differ in P&L distribution from straddles: condors cap both the gain and the loss, while straddles have unlimited loss. Natenberg and other sources explain that the wing positions in a condor function as insurance against tail moves, paid for by capping upside. When IV is elevated (VIX > 25), the expected move is large, and the probability of a tail event that breaches condor wings is higher — but the premium collected is also higher. The question is whether the premium is sufficient to cover the expected wing loss, and whether the conditional P&L distribution (given elevated vol) favours the condor's defined-risk structure over the straddle's unlimited-risk profile.

## How to Test

Using ORATS SPX data 2010-2023: filter to weeks where VIX > 25 at entry. For each entry: sell ATM straddle, and separately sell iron condor with 15% OTM wings. Hold 21 days, delta-hedge daily. Compute P&L distribution statistics (mean, standard deviation, skewness, kurtosis, Sharpe, max loss realised) for each strategy. Falsified if iron condor P&L skewness is not significantly higher (more positive) than straddle P&L skewness in high-VIX periods. Also test whether Sharpe per unit of max risk is higher for condor.

**Data required:** ORATS SPX options with full surface 2010-2023; VIX daily close for regime filter

### Variables Needed

- `implied_volatility`
- `vix`
- `condor_pnl`
- `straddle_pnl`
- `pnl_skewness`

### What Would Support It

Condor P&L skewness > straddle P&L skewness in VIX > 25 periods; condor Sharpe-per-max-risk > straddle Sharpe-per-max-risk

### What Would Falsify It

No significant difference in P&L distribution shape between condor and straddle in high-VIX periods

## Source Themes

- [[Multi-Leg Volatility Strategies: Straddles, Strangles, Butterflies, and Condors]]
- [[Straddle Strategies: Long and Short Volatility Expressions]]
- [[Gamma and Theta: The Core Greeks Tradeoff]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
- `9e3a85506c46`
