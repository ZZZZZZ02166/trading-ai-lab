# Chapter 13: Delta-Neutral Trading — Trading Realized Volatility
*Trading Option Greeks 2e — pp. 259–274*

---

## Chapter Summary

Chapter 13 is the practical mechanics chapter for gamma scalping — the active process of rebalancing a delta-neutral option position as the underlying moves. While Chapter 12 focused on IV trading (vega plays), this chapter focuses on trading *realized volatility*: profiting from actual stock movements through continuous delta rebalancing.

---

## What Is Gamma Scalping?

A long gamma position has positive convexity: when the underlying moves up, delta increases (making you more long); when it moves down, delta becomes negative (making you short). By continuously selling when positive delta grows and buying when negative delta grows, the trader "locks in" each move as a small profit.

The cumulative effect: the trader systematically **buys low and sells high** in the underlying, with each rebalance capturing a small profit. If the stock moves enough (realized vol > implied vol), these scalps more than pay for the daily theta cost.

---

## Long Gamma Example: Harry

**Setup**: Harry buys 20 40-strike calls at $1.20 each (50 delta) and short 1,000 shares at $40 (delta-neutral).

| Day | Stock Move | Action | Scalp P/L | Theta Cost |
|-----|------------|--------|-----------|------------|
| 1 | +$3 to $43 | Sell 112 shares at $43 | +$168 | −$50 |
| 2 | −$3 to $40 | Buy back 112 shares at $40 | +$168 | −$50 |
| 3 | −$2 to $38 | Buy shares at $38 | +$112 | −$50 |
| 4 | +$2 to $40 | Sell shares at $40 | +$112 | −$50 |
| 5–6 | Weekend | None | 0 | −$100 |
| 7 | +$0.25 | Sell 70 shares | +$9 | −$50 |

After 7 days: stock scalps ≈ +$569, theta cost ≈ −$400, net gain ≈ +$169 for a relatively active week.

**The key**: The theta cost is a fixed drag ($50/day in this example). The scalp income depends on actual stock movement. If the stock makes large daily moves, scalps exceed theta. If the stock barely moves, theta wins.

---

## Short Gamma Example: Mary

**Setup**: Mary sells 20 40-strike calls and buys 1,000 shares (delta-neutral). This is the mirror image of Harry.

When stock rises: delta goes negative (the short call's delta increases in absolute terms, overwhelming the long stock). Mary must **buy shares at rising prices** to re-neutralize. When stock falls: must **sell shares at falling prices** to re-neutralize.

Short gamma systematically forces the trader to buy high and sell low in the underlying. Theta income compensates. Mary's position is profitable if the stock moves *less* than implied vol predicts.

---

## The Breakeven Condition

Gamma scalping is profitable when:
> Realized daily stock σ > Implied daily σ (= IV / √256)

For IV = 25%: implied 1-day σ = 25/16 = 1.56%. If the stock actually moves 2%+ per day on average, long gamma wins. If it moves 1% per day, theta wins.

This is the fundamental question when deciding whether to buy or sell vol: what is your expectation of realized vol vs. what the market is pricing in (IV)?

---

## Hedge Frequency and Judgment

How often should you rebalance? Passarelli notes this is not mechanical:
- Professional traders use the 1σ price levels derived from IV as trigger points for hedging
- Market feel and technical indicators also come into play
- Covering too frequently (at every tick) creates excessive transaction costs
- Covering too infrequently misses scalp opportunities and leaves you with large unhedged delta positions

Each trader must develop their own rhythm based on their trading style, transaction cost structure, and market conditions.

---

## P/L Decomposition at End of Week

After 7 days, breaking down the full P/L:
- **Gamma scalp profits**: sum of all stock hedge profits
- **Theta cost**: −$50/day × 7 = −$350
- **Vega P/L**: if IV moved during the week, this additional term appears
- **Net**: scalps − theta ± vega

This decomposition is how professional traders evaluate whether their gamma-scalping thesis was correct, regardless of the net P/L.

---

## Key Lessons

1. **Gamma scalping converts stock price oscillations into realized P/L.** Each hedge rebalance locks in a small gain proportional to the size of the move.
2. **Theta is the "rent" for being long gamma.** Every day the stock doesn't move enough to cover theta is a losing day for the long gamma trader.
3. **Short gamma forces buy-high/sell-low.** Understanding this makes clear why short gamma is dangerous in volatile markets — and why theta income compensates.
4. **The breakeven is IV vs. expected realized vol.** If you believe the stock will be more volatile than IV implies, buy gamma. If you believe it will be quieter, sell gamma.
5. **Hedge frequency involves judgment, not rules.** The professional's edge is often in *when* and *how much* to hedge, not just *whether* to hedge.

---

## Connection to the Rest of the Book

- Ch. 12 covers the vega (IV) side of delta-neutral trading
- Ch. 14 (vol charts) provides the analytical framework for knowing when realized vol > implied vol
- Ch. 15 (straddles) is the most natural structure for gamma scalping (maximum gamma per dollar)
