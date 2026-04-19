---
hypothesis_id: 71152e2e-cfa4-4650-9b56-126c1f4b3884
status: candidate
confidence: 0.81
tags: ['intraday', 'bid-ask-spread', 'market-making', 'transaction-costs', 'time-of-day', 'microstructure']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# SPX Options Bid-Ask Spread Is Widest in the First 15 Minutes and Narrows Monotonically to Midday

**Status:** candidate | **Confidence:** ████████░░ 81%

#intraday #bid_ask_spread #market_making #transaction_costs #time_of_day #microstructure

## Claim

The bid-ask spread (in implied vol terms) for SPX ATM options is widest in the first 15 minutes of trading (9:30–9:45 ET) and narrows monotonically until approximately 11:30 ET, after which it stabilises. Trading costs for options strategies executed at the open are systematically higher than those executed at midday, with the vol-point spread approximately 30–50% wider at open vs. midday across normal vol regimes (VIX 15–25).

## Rationale

Market maker edge and bid-ask spread theory in this knowledge base establishes that spreads compensate market makers for adverse selection risk and inventory gamma risk. Both are elevated at the open: adverse selection is highest when information is most asymmetric (post-overnight), and market makers have not yet established their intraday inventory position. As the session progresses, information is resolved, inventories adjust, and competition among market makers tightens spreads. This is analogous to the earnings vol crush: just as post-earnings IV falls as uncertainty resolves, post-open spreads fall as information resolves. The hypothesis is directly testable from bid-ask quote data.

## How to Test

Using CBOE LiveVol or ORATS intraday bid-ask quotes for SPX ATM options (nearest DTE ≥ 5) from 2015–2023: compute mid-IV from bid and ask at 5-minute intervals throughout the day. Compute spread = (ask_IV - bid_IV) / 2. Average spread by 30-minute time bucket. Regress spread on time-of-day controlling for VIX level and daily vol regime. Falsified if spread is not significantly higher in the first 15 minutes vs. midday, or if the pattern is non-monotonic with higher midday spreads.

**Data required:** CBOE LiveVol or ORATS intraday bid-ask quotes for SPX ATM options 2015–2023

### Variables Needed

- `bid_ask_spread`
- `implied_volatility`
- `time_of_day`
- `market_maker_edge`

### What Would Support It

First-15-minute average spread > midday average spread by > 25%; monotonic intraday decline confirmed by regression; pattern consistent across VIX regimes

### What Would Falsify It

No significant time-of-day pattern in spreads, or spreads wider at midday due to low liquidity

## Source Themes

- [[Market Maker Edge and Theoretical Value]]
- [[Gamma and Theta: The Core Greeks Tradeoff]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
