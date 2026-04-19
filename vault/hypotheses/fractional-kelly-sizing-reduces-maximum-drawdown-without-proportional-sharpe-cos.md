---
hypothesis_id: 3723c67b-b512-4c24-8859-d843f1e2d2b7
status: candidate
confidence: 0.83
tags: ['kelly-criterion', 'position-sizing', 'drawdown', 'sharpe', 'risk-management']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Fractional Kelly Sizing Reduces Maximum Drawdown Without Proportional Sharpe Cost

**Status:** candidate | **Confidence:** ████████░░ 83%

#kelly_criterion #position_sizing #drawdown #sharpe #risk_management

## Claim

When options strategies are sized at half-Kelly versus full-Kelly, maximum drawdown decreases by approximately 50% while the Sharpe ratio decreases by less than 25%. This asymmetry — where risk reduction is not proportional to return reduction — makes half-Kelly the dominant sizing strategy for vol sellers facing fat-tail return distributions.

## Rationale

Sinclair's Volatility Trading derives the Kelly criterion analytically and shows that at half-Kelly, an investor achieves approximately 75% of maximum long-run growth while variance falls to 25% of the full-Kelly variance — a 4:1 ratio of variance reduction to growth reduction. For options strategies with non-Gaussian returns (fat tails, skewness), the practical argument is even stronger: full Kelly sizing calibrated to a Gaussian estimate will be over-Kelly in reality, meaning it can destroy capital. Natenberg reinforces this from a risk-management perspective, stressing that survival (not maximisation) is the primary goal for options sellers. The Kelly theme in this knowledge base captures both the theoretical derivation and the practical caution.

## How to Test

Using a simulated options strategy (short SPX straddle, monthly, 2005-2023, ORATS data): size positions at full-Kelly, half-Kelly, quarter-Kelly, and fixed 1% risk. Measure Sharpe, maximum drawdown, and terminal wealth for each sizing rule. Falsified if half-Kelly maximum drawdown is not significantly below full-Kelly, or if Sharpe ratio degrades proportionally with sizing reduction. Also test whether fat-tail adjustment (using realised kurtosis instead of Gaussian assumption) changes the optimal fraction.

**Data required:** SPX monthly straddle returns from ORATS 2005-2023; Monte Carlo simulation of fat-tailed return distribution

### Variables Needed

- `kelly_fraction`
- `position_size`
- `returns`
- `drawdown`
- `sharpe`

### What Would Support It

Half-Kelly maximum drawdown < 60% of full-Kelly drawdown; half-Kelly Sharpe > 75% of full-Kelly Sharpe

### What Would Falsify It

Half-Kelly drawdown within 20% of full-Kelly, or half-Kelly Sharpe below 75% of full-Kelly Sharpe (proportional degradation)

## Source Themes

- [[Kelly Criterion and Fractional Position Sizing]]
- [[Multi-Leg Volatility Strategies: Straddles, Strangles, Butterflies, and Condors]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `1c32b3c0d846`
