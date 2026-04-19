---
hypothesis_id: 1284f9b6-16e5-494a-8a21-24c433bb6470
status: candidate
confidence: 0.72
tags: ['market-making', 'bid-ask-spread', 'gamma', 'dealer-positioning', 'transaction-costs']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Market Maker Bid-Ask Spread Widens When Gamma Exposure Exceeds Inventory Tolerance

**Status:** candidate | **Confidence:** ███████░░░ 72%

#market_making #bid_ask_spread #gamma #dealer_positioning #transaction_costs

## Claim

When options market makers accumulate net short-gamma inventory (measured as delta-adjusted notional gamma exposure), the bid-ask spread on ATM options widens by a measurable and predictable amount. Specifically, each additional 1% increase in dealer gamma exposure (as a fraction of normal inventory) correlates with a 0.1–0.3 volatility-point widening of the bid-ask spread. This predicts that transaction costs for delta-hedging increase precisely when hedging is most needed.

## Rationale

The market maker edge theme in this knowledge base documents that bid-ask spreads are not random but reflect compensation for the market maker's gamma risk. When dealers are short gamma (typically from selling puts to institutional buyers), they need to delta-hedge more frequently, and their inventory tolerance shrinks — leading to wider spreads. This relationship is documented across multiple books: Natenberg links spread width to theoretical value uncertainty and hedge cost; other sources note that dealer positioning drives option pricing dynamics beyond simple BSM inputs. The testable hypothesis is that dealer gamma exposure (proxied by net options positioning data) predicts subsequent spread widening.

## How to Test

Using CBOE options positioning data (ISEE, SKEW index, or dealer positioning from OCC) and ORATS bid-ask spread data 2015-2023: regress weekly change in ATM bid-ask spread on weekly change in dealer net gamma position (as percentage of open interest). Control for VIX level and volume. Falsified if the gamma-exposure coefficient is not statistically significant (p < 0.05) and positive. Secondary test: does dealer gamma exposure on Mondays predict hedging cost (slippage + spread) for weekly options entered that day?

**Data required:** ORATS bid-ask spread data, CBOE OCC options positioning data or ISEE sentiment data 2015-2023

### Variables Needed

- `bid_ask_spread`
- `gamma`
- `dealer_positioning`
- `volatility`

### What Would Support It

Statistically significant positive coefficient (p < 0.05) between dealer gamma exposure and subsequent spread widening; R² > 0.10

### What Would Falsify It

No significant relationship between dealer gamma proxy and spread changes, or negative relationship

## Source Themes

- [[Market Maker Edge and Theoretical Value]]
- [[Gamma and Theta: The Core Greeks Tradeoff]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
