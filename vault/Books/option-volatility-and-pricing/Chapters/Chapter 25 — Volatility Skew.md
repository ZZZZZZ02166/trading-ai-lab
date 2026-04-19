# Chapter 25 — Volatility Skew and Volatility Contracts
*Option Volatility and Pricing — Natenberg*

---

## Summary

The volatility smile and skew represent the empirical failure of the Black-Scholes constant-volatility assumption. This chapter explains why IV varies across strikes, what structural forces create and maintain equity skew, how to trade skew, and the mechanics of volatility derivatives.

---

## The Volatility Smile: IV Across Strikes

Black-Scholes assumes IV is constant across all strikes for the same expiration. In reality, if you back-solve IV from market prices at each strike and plot IV vs. strike, you get a curve — not a flat line.

**Names for the IV vs. strike curve**:
- "Volatility smile": symmetric, higher IV at both ends (common in FX)
- "Volatility skew": asymmetric (common in equities — downward sloping)
- "Vol surface": the full 2D surface of IV vs. strike vs. expiration

The existence of the smile/skew proves that real-world price distributions have different shapes than the lognormal distribution assumed by Black-Scholes. Fat tails and jump risk are not captured by the constant-volatility lognormal model.

---

## Equity Skew: Structure and Causes

For equity index and individual stock options: **OTM puts have higher IV than OTM calls** (downward-sloping skew).

**Two structural causes that reinforce each other**:

1. **Institutional insurance demand**: large investors buy OTM puts continuously to protect long equity portfolios. Persistent buying pressure inflates OTM put IV.

2. **Covered call writing**: retail investors who own stock systematically sell OTM calls to generate income. Persistent selling pressure depresses OTM call IV.

Both forces operate simultaneously, creating a persistent structural gap between OTM put IV and OTM call IV. This gap is larger for index options than individual stocks because: (1) large institutions primarily hedge via index options; (2) index options have more consistent coverage across the entire market.

**Result**: OTM puts are structurally expensive. Sellers of OTM puts earn a structural premium above the basic variance premium. Buyers of OTM puts systematically overpay.

---

## Skew Shapes by Asset Class

| Asset Class | Skew Shape | Dominant Risk |
|------------|-----------|--------------|
| Equity indexes | Steep downward | Crash risk (downside gaps) |
| Individual stocks | Moderate downward | Earnings gaps, buyouts |
| Agricultural commodities | Often upward | Supply disruption (drought, disease) |
| Energy commodities | Mixed/upward | Supply disruption spikes |
| Currencies | Symmetric smile | Bidirectional crash risk |
| Interest rates | Context-dependent | Depends on product |

Never apply equity skew intuitions to other asset classes without verification.

---

## Trading the Skew

**Long skew (buying OTM puts relative to OTM calls)**:
- Buy OTM puts / sell OTM calls (short risk reversal or long put spread)
- Benefits if: crash occurs, skew steepens (OTM put IV rises relative to call IV)
- Costs: paying structural premium built into OTM puts

**Short skew (selling OTM puts relative to OTM calls)**:
- Sell OTM puts / buy OTM calls (long risk reversal)
- Benefits from collecting structural premium; profitable if market stays calm
- Risk: large downside move causes large losses (short OTM put)

**Risk reversal as a skew instrument**:
- Short risk reversal (sell put / buy call): bullish + short skew
- Long risk reversal (buy put / sell call): bearish + long skew
- A vega-neutral risk reversal isolates the skew exposure from the absolute vol exposure

---

## Risk Reversals: Measuring and Trading Skew

Risk reversal = price of OTM call minus price of OTM put (same delta, same expiry). A negative risk reversal (puts > calls in IV) indicates downward skew. A more negative risk reversal means steeper skew.

**Vega neutral risk reversal**: adjust quantities of puts and calls so net vega = 0. Isolates the skew trade from absolute vol direction.

Note: a vega-neutral risk reversal tends to be gamma-neutral as well, but not always. The trader may need to choose between vega neutrality and gamma neutrality depending on market conditions.

---

## Volatility Derivatives

Before VIX futures and variance swaps, there was no way to trade pure volatility without also taking on delta risk.

### VIX Futures
- VIX = implied 30-day vol of S&P 500 calculated from options prices
- VIX futures: trade on expected VIX level 30 days into the future
- Typically trade in contango (futures > spot VIX) because of uncertainty premium about future vol
- VIX futures have mean-reverting behavior but can stay elevated for extended periods during crises

### Variance Swaps
- Pay: realized variance − fixed variance strike (variance = vol²)
- Settled at expiration based on actual price returns over the contract life
- Key property: **variance is additive** — total variance over two periods = sum of period variances
- Enables static replication via a portfolio of options (the log-contract)
- Most common form of pure vol trading among institutional traders

### Volatility Swaps
- Pay: realized volatility (standard deviation) − fixed vol strike
- Not as common as variance swaps because volatility is not additive (√(var1 + var2) ≠ √var1 + √var2)
- Harder to replicate statically; requires dynamic hedging

### Why Variance Swaps Are Preferred
Variance (σ²) is additive across time periods: var_total = var₁ + var₂ + ... This property allows exact static replication using a portfolio of options, making variance swap hedging straightforward. Realized volatility (σ) is not additive, making vol swap hedging more complex.

---

## Realized Volatility Contract Settlement

At expiration: settlement value = annualized standard deviation of daily log returns over contract life. No model, no IV — just the actual measured vol from realized price movements. Settlement is unambiguous and objective.

---

## Common Misunderstandings About Skew

- **"Equity skew is caused by fear."** Partially — but the structural forces (insurance demand + covered call selling) exist even in calm markets. Skew persists in both low-fear and high-fear environments.
- **"OTM puts are always worth selling."** They offer structural premium, but selling OTM puts has crash risk. The structural premium compensates for occasional large losses — it's a risk premium, not free money.
- **"All markets have downward skew."** No — commodity and FX markets often have different skew shapes. Never assume equity behavior.
