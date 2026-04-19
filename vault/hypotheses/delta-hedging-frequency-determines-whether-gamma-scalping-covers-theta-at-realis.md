---
hypothesis_id: b284b9e7-d361-415b-89cc-a1b9ab236f67
status: candidate
confidence: 0.88
tags: ['gamma-scalping', 'delta-hedging', 'path-dependency', 'realized-volatility', 'hedging-frequency']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Delta-Hedging Frequency Determines Whether Gamma Scalping Covers Theta at Realised Vol

**Status:** candidate | **Confidence:** ████████░░ 88%

#gamma_scalping #delta_hedging #path_dependency #realized_volatility #hedging_frequency

## Claim

When an options position is delta-hedged at fixed intervals (daily vs. weekly vs. at-threshold), the P&L variance increases significantly with longer hedging intervals even when realised vol is correctly estimated. Specifically, weekly delta-hedging produces at least 2× the P&L standard deviation of daily hedging, even when the average P&L is similar. This path dependency makes the hedging interval a critical risk variable independent of the vol forecast.

## Rationale

Sinclair's Volatility Trading derives the discrete-hedging P&L formula explicitly: residual variance from discrete hedging is proportional to sigma × sqrt(pi / 2N), where N is the number of hedges. As N decreases (less frequent hedging), residual variance grows — meaning weekly hedging (N=4 per month) has roughly sqrt(21/4) ≈ 2.3× the residual vol of daily hedging (N=21). Natenberg and other sources confirm that gamma scalping P&L is path-dependent: the same final realised vol produces different P&L depending on when vol is realised relative to the hedge times. This is not a model assumption but a mathematical consequence of discrete rebalancing.

## How to Test

Using SPX daily returns and ATM option pricing (ORATS 2010-2023): for each month, simulate delta-hedging a short straddle at 3 frequencies (daily, weekly, threshold-based at 0.10 delta). Measure P&L mean and standard deviation across 100+ months per frequency. Falsified if weekly P&L standard deviation is not significantly higher than daily, or if the ratio is below 1.5×. Secondary test: does threshold-based hedging at 0.10 delta achieve similar mean P&L with lower variance than calendar-based weekly?

**Data required:** SPX daily prices 2010-2023, ATM option prices from ORATS or similar for delta calculation

### Variables Needed

- `delta`
- `gamma`
- `realized_volatility`
- `hedging_pnl`
- `pnl_variance`

### What Would Support It

P&L standard deviation ratio weekly/daily > 1.5; statistically significant at 95% confidence; consistent across vol regimes

### What Would Falsify It

P&L standard deviation ratio weekly/daily < 1.2; or threshold hedging producing higher variance than calendar daily

## Source Themes

- [[Delta-Neutral Trading and Gamma Scalping]]
- [[Gamma and Theta: The Core Greeks Tradeoff]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `1c32b3c0d846`
