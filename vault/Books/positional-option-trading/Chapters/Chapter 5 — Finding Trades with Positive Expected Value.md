# Chapter 5: Finding Trades with Positive Expected Value
*Positional Option Trading, Euan Sinclair — pp. 88–115*

---

## Chapter Summary

Chapter 5 provides a structured catalog of 11 distinct trading edges in options markets, organized by confidence level. Sinclair distinguishes edges from rules: an edge is an observable phenomenon; a rule is a specific way to monetize it. Rules decay; edges persist. The chapter also analyzes the XIV/VIX ETN collapse of February 2018 as a case study in how crowding and leverage can amplify vol-premium strategies into disasters.

---

## Core Framework: Edges vs Rules

- **Rule**: "Sell front-month SPX straddles on Mondays" — specific, brittle, decays
- **Edge**: "Implied volatility has a variance premium over realized vol" — structural, durable
- Study edges, not rules. Monetize edges with structures adapted to the current regime.

---

## The February 2018 VIX Explosion: A Warning

- S&P 500 fell 4.2% on Feb 5, 2018. VIX rallied **115.6%** — nearly 9× the regression-predicted 12.8%
- **Why**: XIV (short-VIX ETN) had ~1300% growth in short interest from 2013–2017. At rebalance time, concentrated forced buying of VIX futures spiked the market
- XIV was not an ETF — it was an ETN (a note). No direct arbitrage possible. XIV only dropped 15% by equity close while VIX futures +45%, creating massive dislocation, then acceleration clause triggered
- **Key lesson**: Crowding in divergent (momentum) strategies creates destabilizing feedback loops. Leverage amplifies this — LTCM convergence strategy failed not because the edge was wrong but because leverage turned a stable trade unstable.

---

## The 11 Tradeable Effects

### Confidence Level 3 — Form the core of a trading operation

**1. Variance Premium (IV > Realized Vol)**
- Best-documented effect in vol trading. SPX premium: mean 4.08 pts, positive 85% of the time over 1990–2018.
- Exists in equity indices, VIX, bonds, commodities, and currencies
- Persistent structural risk premium — insurance demand and jump risk
- Strategy: sell straddles/strangles/condors with delta hedge; scale by VIX quintile

**2. Earnings Implied Volatility Overpricing (Short Side)**
- Front-expiration IV rises significantly in weeks before earnings, then collapses after release
- Selling straddle as close as possible before earnings: 64% win rate in Sinclair's study
- Caution: naked short straddle has large tail risk from earnings surprise. Use spreads.
- Strategy: sell front-month ATM straddle/strangle immediately before earnings; benefit from IV collapse

**3. VIX Term Structure Contango**
- VIX futures in contango 81% of the time (2006–2019)
- Cash VIX is a better predictor of future VIX levels than futures are (Simon and Campasano 2014)
- Strategy: sell front-month VIX futures when term structure in contango (Fig 4.3 showed ~$80K P/L 2015–2019 with filter)

**4. Options and Fundamental Factors (Smart Beta → Smart Vol)**
- Factors that predict stock returns also predict option variance premia: value, size, momentum, quality, low-beta
- Options on small stocks and value stocks have larger variance premia
- By industry: Utilities highest (+31.25%), Technology negative (−7.66%)
- Strategy: prefer selling options on value, small-cap, low-growth, non-tech stocks

### Confidence Level 2 — Reasonable confidence; use with appropriate position sizing

**5. Earnings Straddle: Buy Before, Sell After**
- Long ATM straddle starting 10 days before earnings: 43% win rate, win/loss = 1.70, skewness +5.4 (Sinclair's 73-stock study)
- Fig 5.1 shows steady upward equity curve: ~$40,000 cumulative on $10K notional
- After earnings: IV collapse → profit from short side. Net: buy 10 days out, sell on release day
- Strategy: long straddle long-vol before earnings; flip to short post-announcement

**6. Post-Earnings Announcement Drift (PEAD)**
- Stocks with positive earnings surprises continue to drift upward over 60–75 days
- Effect documented since 1968 (Ball and Brown). Larger for: retail-heavy stocks, less institutional ownership, Fridays, high transaction-cost stocks
- Interpretation: investor underreaction to earnings news, not a risk premium
- Strategies:
  - Positive surprise: long 40Δ/10Δ call spread (cheap post-earnings IV)
  - Negative surprise: sell covered call or 50Δ/20Δ put spread

**7. FOMC Volatility Overpricing**
- IV rises before FOMC meetings and collapses afterward
- Similar to earnings effect but calendar-driven
- Strategy: sell straddles the day before FOMC meeting

**8. VIX Mean Reversion**
- VIX mean-reverts to its long-run average (usually 18–20%)
- When VIX spikes far above long-run average: strong pull to revert
- Most useful as a filter overlaying other strategies: reduce size when VIX is extreme, not as standalone trade

### Confidence Level 1 — Smaller allocation; useful for disciplined "gambling" in small size

**9. Earnings-Induced Reversals**
- Stocks that drifted strongly into earnings tend to reverse when the news breaks
- 145 bps return (vs 22 bps in non-earnings periods) from long-short momentum reversal strategy (So and Wang 2014, 1996–2011)
- Strategy: shade straddle delta in direction of expected reversal when selling earnings straddle

**10. Pre-Earnings Announcement Drift (PEAD Across Industry Peers)**
- Stocks drift in the direction of earnings-related moves in earlier-reporting sector peers
- Very limited edge from this alone; useful as a confirmation signal

**11. Week-of-Expiration Variance Premium**
- In the final week before expiration, short vol strategies tend to have extra edge
- Related to gamma and theta ratio dynamics near expiry

---

## Crowding Considerations

- **Convergence strategies** (short vol, value investing): crowding is stabilizing — more players push toward fair value, helping returns
- **Divergence strategies** (trend following, momentum): crowding is destabilizing — more players push further from fair value, creating bubbles
- Short vol is a convergence strategy in theory, but if structured with leverage products (XIV, VXX) it can be destabilized

---

## Key Lessons

1. **Edges, not rules.** Study why a premium exists; then choose the structure. Don't backfit a specific rule.
2. **Level 3 = core portfolio.** The variance premium, earnings IV overpricing, and VIX contango are well-proven, structural, persistent. Size them appropriately.
3. **Level 1 = controlled speculation.** Use small positions to satisfy the need to be active without destroying the core portfolio.
4. **Post-earnings drift uses cheap IV.** After earnings, IV collapses — directional call/put spreads become cheap. This is the right time to buy, not before.
5. **Don't crowd into momentum products.** The XIV event shows how structural leverage vehicles can amplify beyond any reasonable risk model.

---

## Source Pages

- XIV collapse case study: pp. 88–96
- Confidence Level 3 effects (variance premium, IV term structure, fundamental factors): pp. 88–100
- Earnings strategies (long before/short after, PEAD): pp. 100–110
- Level 2 effects (FOMC, mean reversion): pp. 107–112
- Level 1 effects (reversals, pre-earnings drift): pp. 112–115
