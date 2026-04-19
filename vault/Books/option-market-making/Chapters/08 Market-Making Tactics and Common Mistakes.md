# Chapter 8: Market-Making Tactics and Common Mistakes
*pp. 151–184 | Option Market Making, Allen Jan Baird*

---

## Summary

This is the most operationally practical chapter — it covers the daily mechanics of running a market-making operation: how to price spreads given current skew, how to track P&L to attribute profits correctly, and the four most common mistakes that turn market-making edge into loss.

---

## Skew Risk Revisited

At high positive implied volatility skew, OTM wing options are expensive relative to ATM. This affects spread pricing directly:

**100-105 Call Spread values by skew level** (Table 8.7):
| Skew | 1×1 spread | 1×2 ratio |
|------|-----------|-----------|
| Flat | $1.66 | $0.92 |
| Low positive | $1.54 | $0.68 |
| High positive | $1.42 | $0.44 |

**Strategic implication:** When skew is flat or negative, wing options are cheap — buy ratio spreads (long 1×1, short additional OTM). When skew is high positive, wing options are expensive — sell ratio spreads or buy butterflies.

**Skew shift (Figure 8.4):** A large upward price move shifts the entire skew curve — what was an OTM call becomes near-ATM, changing the IV relationship between strikes. This can hurt vertical spread traders even with no change in the underlying's position relative to original strikes.

---

## Tracking Trading Results

**The two-account system:**

| Account | What it tracks |
|---------|----------------|
| Carryover account | Daily mark-to-market of existing positions (before new trades) |
| Daily trading account | P&L from new trades executed today |

**Why it matters:** Net total P&L = carryover P&L + daily trade P&L. If most profit comes from carryover (positions moving in your favor), you may be speculating more than market making. A genuine market maker shows positive daily trading P&L consistently across many cycles.

**Calculation method:**
- Carryover P&L: value all existing positions at Day 1 settlement, then at Day 2 settlement (no new trades) — the difference is carryover P&L
- Daily trade P&L: for each trade, (settlement Day 2 − trade price) × quantity for buys; reverse for sells

---

## The Four Most Common Market Maker Mistakes

### 1. Failure to Hedge Delta
The most costly mistake. After completing a non-spread option trade, deciding NOT to hedge delta immediately — hoping the market will move favorably first. This is speculation dressed as market making.

**The cardinal rule: Hedge when you should, not when it's most convenient.**

Even if the hedge costs a small loss, take it immediately. Waiting to hedge at a better level is a directional bet. Small hedging losses are the cost of doing business; large speculative losses from unhedged deltas are potentially business-ending.

### 2. Incorrect Delta Hedging
Hedging at stale posted board prices or lagged quotes instead of actual traded futures prices. If options were priced at futures = 100 but actual futures are at 101, your delta calculation is wrong and the hedge leaves residual directional exposure.

**Solution:** Always base delta calculations on actual current traded futures price, not posted board prices. Physically position yourself to hear actual trades or have a clerk relay prices.

### 3. Overtrading
Trading more contracts than you can monitor and hedge accurately. When position volume exceeds your capacity to manage it, errors accumulate, hedges get delayed, and edge evaporates. Impatience is a significant cause — trading for the sake of activity rather than waiting for genuinely edged opportunities.

**Rule:** Only trade at your price, in quantities you can fully manage. Patient waiting for genuine edge opportunities is a competitive advantage.

### 4. Poor Kappa/Vega Risk Adjustment
Allowing net kappa/vega to drift significantly long or short through accumulated trades without adjustment. If one side of the market consistently buys options from you, you become net short kappa — exposed to large losses from any IV spike. The reverse creates exposure to IV declines.

**Rule:** Stay net kappa-neutral or at most slightly long. Correct large kappa imbalances by adjusting spread ratios even at a small concession. Never let kappa concentration become the dominant risk in your book.

---

## Key Lessons

1. **Price spreads with current skew in mind.** Pricing a vertical spread using flat-skew assumptions when skew is actually highly positive will cause you to systematically underprice the short OTM wing.

2. **Track carryover P&L and daily trading P&L separately.** Total profits can look good while daily trading P&L is negative — meaning the market is actually subsidizing bad market making through lucky directional bets.

3. **The single most important habit: immediate delta hedging.** Every delay is speculation. Build the habit of hedging reflexively.

4. **Overtrading is the market maker's equivalent of forcing trades.** The edge per trade shrinks with each additional position you cannot monitor properly.

---

## Warnings

- Skew wobble — random day-to-day fluctuations in skew level — creates daily P&L noise for spread traders even with no directional move. Accept this as part of the business; do not overtrade to "correct" it.
- Trading last in a large "string" (large lot order executed by multiple traders sequentially) means the first traders' hedges have already moved futures prices against you. Avoid being last in strings whenever possible.
