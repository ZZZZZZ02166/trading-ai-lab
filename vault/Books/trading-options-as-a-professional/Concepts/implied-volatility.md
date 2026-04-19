# Implied Volatility
*Source: Trading Options as a Professional — Ch. 7*

---

## Definition

Implied volatility (IV) is the volatility value that, when input into a pricing model (Black-Scholes or binomial) along with all other known market inputs (stock price, strike, time, rate, dividends), produces a theoretical value equal to the observed market price.

IV is the market's **forward-looking consensus forecast** of future realized volatility over the option's remaining life.

---

## How to Calculate

IV is found by back-solving the pricing model: given a market option price, find the vol input that makes the model output match. Op-Eval Pro's CALL box calculates this automatically — enter the market price, press Enter, and it solves for IV.

Example: Stock 68, Strike 70, Interest 4%, Days 75. Gary's estimate: vol = 26% → theoretical call = $2.57. Market price = $3.40. Back-solve: IV = 32.84%.

---

## How to Interpret

- A $100 stock with 30% IV: market implies 68% probability the stock stays within ±$30 over one year
- **1-day expected move**: IV / √252 × stock price. At 30%: 30/15.87 × $100 = $1.89
- IV is a per-year measure — scale to actual holding period using √(days/252)

---

## IV Drivers

| Direction | Driver |
|-----------|--------|
| IV rises | Fear, uncertainty, anticipated events (earnings, FDA, macro), demand for protection |
| IV falls | Post-event resolution ("vol crush"), complacency, market maker arb normalizing extremes |

**Inverse relationship with stock price**: stock price drops tend to coincide with IV spikes. This creates double benefit for long puts in sell-offs.

---

## IV vs. Historical Vol: The Core Decision

Every vol trade is a bet on the relationship between IV (market forecast) and realized vol (what actually happens):

| IV vs. Expected Realized | Trade |
|--------------------------|-------|
| IV > expected realized | Sell vol (collect premium, accept gamma risk) |
| IV < expected realized | Buy vol (pay premium, collect gamma scalps) |

This comparison is the foundation of the delta-neutral trading strategies in Chapter 8.

---

## Volatility Skew

Equity options show persistent skew: OTM puts have higher IV than equidistant OTM calls. The IV vs. strike curve slopes downward. Causes: demand for downside protection; asymmetric crash risk premium.

Implication: OTM puts are structurally expensive in volatility terms. Traders who sell them earn a structural premium; traders who buy them systematically overpay.

---

## Common Misunderstandings

- **"IV predicts direction."** No. A 40% IV means large moves are expected — not specifically up or down.
- **"High IV means sell."** Not always. IV can stay elevated or rise further. Mean reversion is real but slow and unreliable over short horizons.
- **"IV is the same across strikes."** Not for equity options — volatility skew creates different IVs at different strikes.

---

## Page References
- IV definition and back-solving: pp. 220–228 (Ch. 7)
- IV and stock prices (inverse relationship): pp. 226–228 (Ch. 7)
- Volatility skew: pp. 233–240 (Ch. 7)
- Expected move formula: pp. 214–220 (Ch. 7)
