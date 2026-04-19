# Concept: Implied Volatility
*From: Option Market Making, Allen Jan Baird*

---

## Definition

**Implied volatility (IV)** is the volatility value that, when plugged into the BSM pricing formula, produces the option's observed market price. It is derived by inverting the BSM formula:

> Given: market price, strike, time, rate → solve for volatility

IV represents the market's *current consensus estimate of future volatility* for that option's expiration period. It is forward-looking.

---

## Why It Matters

1. **IV is the market's volatility price.** When IV is high, the market believes future price moves will be large. When IV is low, it expects calm. Market makers buy options when IV is low (cheap) and sell when IV is high (expensive) — relative to their volatility forecast.

2. **IV diverges from historical volatility.** Figure 2.8 (October cotton) shows IV and 20-day historical vol frequently diverging by 10+ percentage points. Neither reliably predicts future realized volatility. Both must be tracked.

3. **IV drives kappa risk.** The dollar P&L impact of a 1-point IV change equals the position's net kappa. A 10-point IV spike on a large position can create enormous gains or losses completely independent of price direction.

4. **IV skew reveals market preferences.** The shape of IV across strikes (the smile) reflects market participants' demand for specific payoff profiles. Positive skew = demand for OTM options. Understanding the current skew level is essential for pricing spreads.

---

## Common Misunderstandings

- **"High IV means the option is overpriced."** Not necessarily — if realized vol ends up being higher than IV implied, the option was actually cheap. IV is forward-looking; whether it's "right" is only known in hindsight.

- **"IV predicts future volatility reliably."** It doesn't. IV often overshoots or undershoots actual future vol. The relationship is noisy and unstable (heteroscedasticity).

- **"You can lose on a long call even when the market rises."** True, and IV is why. If IV falls sharply when the underlying rises (common in strong rallies), the kappa loss can exceed the delta gain.

---

## Source Page References

- Definition and BSM inversion: pp. 28–30
- IV vs historical vol divergence (Figure 2.8): p. 30
- Kappa/vega as IV sensitivity: pp. 43–46
- Skew: pp. 48–49
- Skew revisited with spread pricing: pp. 175–176
