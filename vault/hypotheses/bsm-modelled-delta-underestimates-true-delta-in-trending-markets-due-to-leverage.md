---
hypothesis_id: d4d4b007-ded8-4fd4-bb5d-39b19ca32d1c
status: candidate
confidence: 0.77
tags: ['bsm', 'delta', 'leverage-effect', 'realized-volatility', 'fat-tails', 'delta-error']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# BSM-Modelled Delta Underestimates True Delta in Trending Markets Due to Leverage Effect

**Status:** candidate | **Confidence:** ███████░░░ 77%

#bsm #delta #leverage_effect #realized_volatility #fat_tails #delta_error

## Claim

When an equity index declines by more than 1% in a day, the actual delta of a long ATM put exceeds the BSM-modelled delta by a measurable amount, because the leverage effect (vol rises as price falls) causes the put to gain more value than BSM predicts. This delta underestimation is largest for strikes near ATM and for short-dated options (< 30 DTE), where the convexity from the leverage effect is most concentrated.

## Rationale

The BSM assumptions theme in this knowledge base documents that the leverage effect — negative correlation between returns and volatility — is one of the six stylised facts of volatility that BSM ignores. Sinclair quantifies the leverage effect empirically: a 1% down move in SPX is typically accompanied by a 0.5–1.0 vol-point increase in ATM IV, which is not captured by a static-vol delta. Multiple books note that BSM produces systematic delta errors in high-volatility or trending regimes because it assumes constant vol. The testable consequence is that hedgers using BSM deltas will be systematically under-hedged on the downside, and this residual exposure can be measured directly.

## How to Test

Using SPX options data (ORATS) on days with |return| > 1% from 2010-2023: for each day, compute BSM delta at the start of the day using prevailing IV. Measure actual P&L of the option vs. BSM-predicted P&L (delta × price change). Compute residual (actual - predicted) and regress on price return (to test sign and magnitude of leverage-effect delta error). Falsified if the residual delta error is not significantly positive (in the direction of the leverage effect) on down-days. Secondary test: does sticky-delta adjustment (re-pricing the option at the new moneyness level using the vol surface) eliminate the error?

**Data required:** ORATS full IV surface with daily snapshots 2010-2023; SPX intraday or daily returns

### Variables Needed

- `delta`
- `implied_volatility`
- `leverage_effect`
- `bsm_delta_error`
- `returns`

### What Would Support It

Statistically significant delta underestimation on down days (actual put gain > BSM-predicted); effect larger for short-dated ATM options

### What Would Falsify It

No systematic delta residual on large-move days, or residual is symmetric (equal on up and down days)

## Source Themes

- [[Black-Scholes-Merton Assumptions and Their Violations]]
- [[Delta and Moneyness: Directional Sensitivity]]
- [[Volatility Skew and Structural OTM Put Premium]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
- `9e3a85506c46`
