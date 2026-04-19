# Chapter 7 — Volatility
*Source: Trading Options as a Professional — Ch. 7*

---

## Summary

Chapter 7 is the book's comprehensive treatment of volatility — the component that most distinguishes option trading from stock trading. Bittman covers historical volatility calculation, the statistics of expected price distributions, implied volatility mechanics, the IV-HV relationship, and volatility skew. The chapter culminates in the practical question that drives every vol trade: is current IV appropriate relative to what realized vol will actually be?

---

## Key Concepts

### Historical (Realized) Volatility

**Definition**: Annualized standard deviation of daily logarithmic returns over a specified observation window.

**Calculation**:
1. Compute daily returns: ln(today / yesterday)
2. Calculate standard deviation of those returns
3. Annualize: σ_annual = σ_daily × √252

Common windows: 10-day, 30-day, 90-day, 180-day, 300-day. Each window captures a different period's actual stock behavior. HV is backward-looking — it measures what the stock did, not what it will do.

### Normal Distribution and Expected Move

Stock returns are approximately normally distributed. Key statistical relationships:
- 68% of returns fall within ±1 standard deviation (±1σ)
- 95% within ±2σ
- 99% within ±3σ

**Expected move formula**: daily 1σ = IV × stock price / √252

Example: $100 stock at 32% IV: expected daily 1σ move = 32% / √252 × $100 = $2.01

One-year expected range: ±1σ = ±32% = $68–$132 with 68% probability.

**Op-Eval Pro Distribution Screen** calculates these ranges for multiple time periods simultaneously. Example: stock at $79.90, vol 15%, 28 days: 1σ range = $75.41–$84.39.

### Implied Volatility

**Definition**: The volatility value that, when plugged into a pricing model (Black-Scholes or binomial) with all other known inputs, produces the observed market option price.

IV is forward-looking — it is the market's consensus forecast of future realized vol over the option's life.

**Gary's Example** (Table 7-6 and 7-7):
- Gary estimates vol at 26%, model price = $2.57
- Market trades at $3.40
- Back-solving for IV: IV = 32.84%
- Interpretation: market participants are collectively pricing in more uncertainty than Gary assumed

### IV and Stock Prices: Inverse Relationship

Figure 7-8: stock price chart (Apr 2007 – Feb 2008) and IV chart. Stock fell from ~$115 to ~$90; IV spiked from ~18% to ~35% simultaneously. This inverse relationship is persistent across equities: fear drives both selling pressure (stock down) and option demand (IV up).

Practical implication: long puts are doubly effective in a sell-off — the stock decline drives intrinsic value, while the IV expansion drives vega gains simultaneously.

### Volatility Skew

**Definition**: Different implied volatilities for different strikes on the same underlying and expiry.

For equity options: OTM puts have higher IV than equidistant OTM calls. The IV vs. strike curve slopes downward (the "smirk" or negative skew).

**Figure 7-9** shows IV of 20%–28% as strike prices range from $122 to $144, with lower strikes having higher IV.

**Causes**:
1. Persistent demand for downside protection (investors buy puts as insurance)
2. Asymmetric fear of crashes vs. rallies (tail-risk premium)
3. Leverage effect: stock price declines increase debt/equity ratio, increasing vol

**Implications**:
- OTM puts are systematically expensive relative to fair value
- Risk reversals (sell rich OTM put, buy cheap OTM call) offer a structural edge
- Vol skew creates pricing differences between equivalent synthetic positions

---

## Key Lessons

1. **Three vol concepts are distinct**: historical vol (what happened), implied vol (what market prices in), expected vol (your personal forecast). The trade is always: your expected vol vs. IV.
2. The distribution screen converts IV into an expected price range — useful for strategy selection (will stock stay within 1σ? → iron condor; will it move 2σ? → long straddle/strangle).
3. IV is a per-year number — scale it to the actual option life using √(days/252) to get the implied move for that period.
4. Volatility skew is persistent and structural. OTM puts are rarely cheap. Factor this into any strategy that involves buying or selling OTM puts.

---

## Warnings

⚠️ IV can remain elevated or depressed for much longer than expected. Just because IV appears "too high" doesn't mean it will normalize before your position expires. Vol mean reversion is real but slow and unreliable over short horizons.

⚠️ The inverse IV-stock price relationship works in both directions: when stocks rally sharply, IV often falls, hurting long-vol positions that were also directionally correct.

⚠️ Skew creates systematic traps for traders who sell OTM puts because they look "cheap" in absolute dollar terms. In volatility terms, they are almost always expensive.

---

## Connections to Rest of Book

- Chapter 3 introduced IV as a pricing input; Chapter 7 explains its dynamics
- Chapter 8 (delta-neutral trading) operationalizes the IV vs. realized vol comparison
- The Distribution Screen from Chapter 7 is used in Chapter 8 to set rebalancing thresholds

---

## Page References
- Historical vol calculation: pp. 206–214 (Ch. 7)
- Normal distribution and expected moves: pp. 214–220 (Ch. 7)
- Implied volatility mechanics: pp. 220–228 (Ch. 7)
- IV and stock prices: pp. 226–228 (Ch. 7)
- Volatility skew: pp. 233–240 (Ch. 7)
