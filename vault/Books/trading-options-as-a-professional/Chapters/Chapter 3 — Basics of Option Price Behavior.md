# Chapter 3 — Basics of Option Price Behavior
*Source: Trading Options as a Professional — Ch. 3*

---

## Summary

Chapter 3 explains how option prices respond to changes in market conditions. This is the first of two chapters on price behavior — Chapter 3 covers the inputs (what drives prices), while Chapter 4 covers the Greeks (how fast each input drives prices). Together they form the analytical foundation for evaluating any option position.

The chapter's most important contribution is the three-part forecast framework: any option trade requires simultaneous views on direction, timing, and volatility. Getting one right and two wrong loses money.

---

## Key Concepts

### Five Pricing Components

| Component | Effect on Call | Effect on Put |
|-----------|---------------|---------------|
| Stock price rises | Value rises | Value falls |
| Strike price rises | Value falls | Value rises |
| Time to expiry increases | Value rises | Value rises |
| Volatility increases | Value rises | Value rises |
| Interest rate rises | Value rises | Value falls |
| Dividend increases | Value falls | Value rises |

### Time Decay: Non-Linear Acceleration

A 100 Call (30% vol) at 90 days = 6.53. At 45 days = 5.25. At 7 days ≈ 2.50. At expiration: hockey-stick.

The decay curve is concave: the final 15 days can cost as much as the preceding 75 days combined. This is why short-option strategies maximize theta collection in the last 3–6 weeks — but also why long-option positions near expiration decay fastest.

### OTM Time Decay and Volatility

Higher volatility slows the percentage rate of decay for OTM options in the early period:
- 110 Call at 20% vol: 79% of total decay in first half of life
- 110 Call at 40% vol: 54% of total decay in first half

High-vol OTM options stay "alive" longer. For option sellers: lower vol environments decay OTM options faster in percentage terms.

### Call and Put Values vs. Stock Price

Call values rise as stock rises — but the slope (delta) is not constant. Near ATM, delta ≈ 0.50 and changes fastest. Deep ITM: delta → 1.00 (moves one-for-one). Deep OTM: delta → 0 (barely moves). This curvature is gamma — the second derivative of value with respect to stock price.

### Interest Rates and Dividends

- Higher interest rates: calls more expensive (you avoid financing the stock), puts cheaper (you delay receiving sale proceeds)
- Higher dividends: calls cheaper (stock price drops on ex-div, reducing call value), puts more expensive
- Effects are most significant for deep ITM options and LEAPS

---

## Three-Part Forecast

Option trading requires three simultaneous forecasts:
1. **Direction**: up, down, or sideways?
2. **Timing**: before expiration?
3. **Volatility**: IV rising, falling, or stable?

### Example — Jumpco April 75 Calls

| Scenario | Stock Direction | IV Direction | P/L |
|----------|----------------|--------------|-----|
| A | +10% in 7 days | Unchanged | +$X (win on direction) |
| B | +10% in 7 days | Falls 5 vol pts | ±0 (direction wins, vol crushes) |
| C | Unchanged | Falls 5 vol pts | −large (lost on both timing and vol) |

Scenario B shows that being correct on direction but wrong on vol can produce near-zero profit. This is the key insight: option buyers often win on direction but still lose because they paid too much for IV.

---

## Key Lessons

1. Options are priced like insurance — all pricing components can be thought of as risk factors. Higher risk = higher premium.
2. Time decay is not a straight line. Sellers who wait until the final week collect the most theta per day — but also accept the most gamma risk.
3. Multiple-scenario analysis (best case, most likely, worst case) is mandatory before entering any option position.
4. Delta is introduced here as the first Greek but covered fully in Chapter 4.

---

## Warnings

⚠️ A trader who only analyzes direction and timing (ignoring volatility) will be repeatedly surprised when correct directional bets lose money due to IV compression.

⚠️ The three-part forecast makes options inherently harder to trade than stocks — more dimensions of right/wrong. The flip side: it also means more edges are available to those who understand all three.

---

## Connections to Rest of Book

- Chapter 4 introduces the Greeks, which measure each of the five pricing components precisely
- Chapter 7 expands on volatility (HV, IV, distribution, skew)
- Chapter 8 (delta-neutral trading) operationalizes the volatility dimension of the three-part forecast

---

## Page References
- Five pricing components: pp. 50–57 (Ch. 3)
- Time decay: pp. 62–68 (Ch. 3)
- Call/put values vs. stock price: pp. 55–62 (Ch. 3)
- Interest rates and dividends: pp. 67–71 (Ch. 3)
- Three-part forecast: pp. 72–76 (Ch. 3)
