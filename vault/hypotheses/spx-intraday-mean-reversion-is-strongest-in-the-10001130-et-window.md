---
hypothesis_id: 3b6be4ae-86f3-4aac-9495-39adc4a8e25b
status: candidate
confidence: 0.73
tags: ['intraday', 'mean-reversion', 'delta-hedging', 'hedge-timing', 'microstructure']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# SPX Intraday Mean Reversion Is Strongest in the 10:00–11:30 ET Window

**Status:** candidate | **Confidence:** ███████░░░ 73%

#intraday #mean_reversion #delta_hedging #hedge_timing #microstructure

## Claim

SPX exhibits statistically significant intraday mean reversion in the 10:00–11:30 ET window: when the index moves more than 0.5% from the open by 10:00 ET, it reverses on average by 30–50% of that move by 11:30 ET. This mean reversion creates a predictable intraday delta pattern for options positions — short delta positions entered after the open surge are profitable more often than not, and delta-hedging at 10:30 ET rather than at open reduces hedge cost by capturing this reversion.

## Rationale

Market microstructure research consistently documents that the opening period resolves overnight information imbalances, creating price overshoots that partially revert as liquidity returns. For options traders, this matters because BSM delta is computed using spot price, and hedging into an opening spike locks in an overstated delta relative to the equilibrium level the market reaches at midday. Sinclair notes that discrete hedging cost depends on when you hedge relative to vol clustering. If the first 30 minutes are disproportionately noisy, delaying the first hedge by 30–60 minutes reduces spurious hedge costs without significantly increasing gamma exposure.

## How to Test

Using SPX 5-minute data 2010–2023: identify days where SPX moves > 0.5% from prior close by 10:00 ET. Measure return from 10:00 to 11:30 ET separately for up and down opening moves. Compute reversal percentage (retracement as fraction of opening move). Separately: compare delta-hedge cost for an ATM straddle hedged at open vs. hedged at 10:30 ET across all days. Falsified if there is no systematic reversion tendency, or if 10:30 hedge timing increases rather than decreases total hedge cost.

**Data required:** SPX 5-minute OHLC 2010–2023; BSM delta from ORATS open IV snapshot

### Variables Needed

- `intraday_returns`
- `delta`
- `hedge_cost`
- `mean_reversion`

### What Would Support It

Average reversion of > 25% of opening move by 11:30 ET on days with > 0.5% opening gap; 10:30 hedge timing reduces transaction costs vs. open timing

### What Would Falsify It

No significant reversion tendency in 10:00–11:30 window, or momentum rather than reversion dominates (further move in same direction)

## Source Themes

- [[Delta-Neutral Trading and Gamma Scalping]]
- [[Delta and Moneyness: Directional Sensitivity]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
