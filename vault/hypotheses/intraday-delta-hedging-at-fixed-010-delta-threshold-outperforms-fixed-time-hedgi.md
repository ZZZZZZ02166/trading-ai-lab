---
hypothesis_id: 474c2a14-7788-4938-b014-5188f368d8ee
status: candidate
confidence: 0.8
tags: ['intraday', 'delta-hedging', 'threshold-hedging', 'transaction-costs', 'gamma', 'whalley-wilmott']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Intraday Delta Hedging at Fixed 0.10-Delta Threshold Outperforms Fixed-Time Hedging for Short Straddles

**Status:** candidate | **Confidence:** ████████░░ 80%

#intraday #delta_hedging #threshold_hedging #transaction_costs #gamma #whalley_wilmott

## Claim

For a short ATM straddle on SPX, delta-hedging when the position delta exceeds ±0.10 (threshold-based) produces lower P&L variance than hedging at fixed 30-minute intervals, while achieving similar average P&L. The threshold approach concentrates hedges at the moments of maximum gamma exposure, whereas calendar-based hedging wastes transaction costs on quiet periods when delta is near zero.

## Rationale

Sinclair derives the optimal hedging bandwidth in the presence of transaction costs (Whalley-Wilmott model): hedge only when the delta deviation exceeds a threshold proportional to transaction cost / (gamma × vol). For short straddles with high gamma near ATM, the optimal hedge threshold is small (meaning hedge frequently when near ATM) but grows when gamma is lower. Fixed 30-minute hedging ignores the position's current gamma, spending transaction costs during quiet periods and potentially hedging too infrequently during high-vol bursts. The key hypothesis is that the threshold approach achieves most of the delta-neutrality benefit with fewer, better-timed hedges.

## How to Test

Simulate short SPX ATM straddle daily from 2015–2023 using 5-minute prices. Strategy A: hedge every 30 minutes. Strategy B: hedge when |position delta| > 0.10 (measured continuously from 5-min updates). Measure for each strategy: total number of hedges, P&L mean, P&L standard deviation, Sharpe, and hedge cost (assume 0.005% per hedge notional). Falsified if Strategy A has lower P&L variance than Strategy B, or if the Sharpe ratio improvement from threshold hedging is less than 10%.

**Data required:** SPX 5-minute prices 2015–2023; BSM delta computed from ORATS daily open IV

### Variables Needed

- `delta`
- `gamma`
- `hedge_cost`
- `pnl_variance`
- `sharpe`

### What Would Support It

Threshold hedging Sharpe > calendar hedging Sharpe by > 10%; threshold approach makes > 20% fewer total hedges with < 10% higher P&L variance

### What Would Falsify It

Calendar hedging achieves lower P&L variance, or threshold approach requires more total hedges

## Source Themes

- [[Delta-Neutral Trading and Gamma Scalping]]
- [[Market Maker Edge and Theoretical Value]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
- `b1f5afe25863`
