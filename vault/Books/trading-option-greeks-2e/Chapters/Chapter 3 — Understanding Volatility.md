# Chapter 3: Understanding Volatility
*Trading Option Greeks 2e — pp. 70–87*

---

## Chapter Summary

Volatility is the central variable in option pricing — the only input that is not directly observable. This chapter defines the two types of volatility, explains how implied volatility is derived and what drives it, and introduces the analytical tools (vol charts, term structure, skew) that option traders use daily.

---

## Historical Volatility (HV)

HV = annualized standard deviation of close-to-close log returns.

**Formula**: 
- Calculate the log return for each day: ln(close_t / close_t-1)
- Calculate the standard deviation of these returns over the chosen lookback period
- Annualize: multiply by √(trading days per year)

**Convention**: 252 trading days per year (or 256, since √256 = 16, a computational convenience).

HV is backward-looking — it tells you how volatile the stock *has been*, not how volatile it *will be*. Common lookback windows: 10-day, 20-day, 30-day, 60-day. Different windows give different readings for the same stock.

---

## Implied Volatility (IV)

IV is the volatility value that, when plugged into the pricing model with all other inputs (stock price, strike, time, interest, dividends), produces the observed market option price.

**Intuition**: If a $100 stock has a 60-day 100-strike call trading at $4.50, and all other inputs are known, the only missing variable is volatility. The IV is whatever volatility makes the model output $4.50.

**IV is forward-looking** — it represents the market's consensus expectation of future realized volatility.

**1-day standard deviation from IV**:
> 1-day expected σ = IV / √256

For a $100 stock at 32% IV: 32 / 16 = 2%. The market implies ~68% probability the stock moves less than $2/day.

---

## What Drives IV

- **Fear and uncertainty** → IV rises. Before earnings, mergers, FDA decisions, economic data.
- **Complacency** → IV falls. When nothing is anticipated, investors use options to squeeze out extra profit (greed), not protection.
- **Post-event vol crush**: After the event, uncertainty resolves. IV collapses regardless of whether the move was large or small. "Buy the rumor, sell the news."
- **Market makers as IV dampeners**: Delta-neutral market makers arb away excessive premium, preventing IV from deviating too far from fair value.

---

## Mean Reversion of IV

IV for most stocks and indices trades within a characteristic range. When IV deviates significantly from the mean:
- IV elevated above the mean → vol-selling opportunity
- IV depressed below the mean → vol-buying opportunity

VIX demonstrates this property at the index level — it consistently mean-reverts. The "range" must be assessed relative to the stock's own historical IV, not absolute levels.

---

## VIX

The CBOE's index measuring the IV of a hypothetical 30-day SPX option. Not a traded option itself but a calculated index. VIX of 20 implies ~1.25% expected daily S&P 500 moves. Used as a fear indicator and as a benchmark for market-wide vol regime assessment.

---

## IV Term Structure

IV varies across expiration dates:
- **Contango (normal)**: longer-dated options have higher IV than shorter-dated
- **Backwardation (inverted)**: front-month IV spikes above back-months, typically before anticipated events

Passarelli's GM example (p. 84): in a quiet period, GM February 32.5 call at 32% IV, March at 33%, April at 34% — gentle upward slope. In volatile or pre-event conditions, front-month can be 10+ points above back-months.

This term structure creates the foundation for calendar spread strategies (Chapter 11).

---

## Volatility Skew

In equity markets, OTM puts consistently trade at higher IV than ATM options, which trade higher than OTM calls. The distribution looks like a "smirk" rather than a symmetric smile.

**Why skew exists**:
- Persistent demand for downside protection (portfolio insurance)
- Fear of market crashes is asymmetric — downside crashes are more feared than upside rips

**Practical impact**: OTM puts at the same dollar distance from ATM as OTM calls trade at 10+ vol points higher IV. This is a structural feature of equity option markets that creates persistent arbitrage-like opportunities for risk reversals and put spread strategies (discussed in Chapters 8 and 16).

---

## Key Lessons

1. **IV, not HV, is what you trade.** HV tells you what happened; IV tells you what the market expects. The gap between them is the edge.
2. **The 1-day standard deviation is a practical tool.** Use it daily to calibrate whether stock moves are "normal" or "extreme" relative to options pricing.
3. **Mean reversion of IV is the foundation of vol-selling.** Without this property, there would be no systematic edge in short-vol strategies.
4. **Term structure matters for calendar spreads.** The shape of the IV curve across expirations determines which months are "cheap" or "rich" relative to each other.
5. **Skew is not noise — it's structural.** Understanding why puts are persistently overpriced relative to calls opens up risk-reversal and skew-arbitrage strategies.

---

## Connections to the Rest of the Book

- Vol charts (Ch. 14) visualize the relationship between HV and IV over time
- Calendar spreads (Ch. 11) exploit the IV term structure
- Straddles/strangles (Ch. 15) are pure IV trades
- Delta-neutral vol selling and buying (Ch. 12) is grounded in IV mean reversion
- Skew trading (Ch. 16) exploits the persistent vol skew
