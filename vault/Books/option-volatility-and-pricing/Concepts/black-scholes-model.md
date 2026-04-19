# Black-Scholes Model
*Source: Option Volatility and Pricing — Ch. 5, 18*

---

## Definition

The Black-Scholes model (1973) is a closed-form mathematical formula for pricing European options on non-dividend-paying stocks. It assumes underlying prices follow a lognormal distribution and derives theoretical option values through risk-neutral pricing (dynamic replication).

---

## The Six Assumptions

1. **Frictionless markets**: no transaction costs, no taxes, unlimited borrowing/lending at the risk-free rate
2. **Continuous trading**: positions can be adjusted at any time
3. **Constant interest rates** over the option's life
4. **Constant volatility** over the option's life
5. **Volatility is independent of the underlying price**
6. **Small price changes are normally distributed**, implying lognormal distribution of prices at expiration

**All six are violated in real markets.** This does not make the model useless — it makes it a starting point that practitioners adjust for.

---

## The Formula

For a European call on a non-dividend-paying stock:
```
C = S × N(d₁) − K × e^(−rT) × N(d₂)

d₁ = [ln(S/K) + (r + σ²/2) × T] / (σ × √T)
d₂ = d₁ − σ × √T
```

Where:
- S = current stock price
- K = exercise price
- r = risk-free interest rate (continuous compounding)
- T = time to expiration (years)
- σ = volatility (annualized std dev of log returns)
- N(x) = cumulative standard normal distribution

Put formula (from put-call parity):
```
P = K × e^(−rT) × N(−d₂) − S × N(−d₁)
```

---

## Implied Volatility

IV is the back-solved input. Given: S, K, r, T, and market option price, solve for σ. This is done numerically (no closed-form solution). IV is the market's forward-looking consensus estimate of future realized vol.

**Practical calculation**: pricing software (Op-Eval, Bloomberg, etc.) handles this automatically. Enter market price; receive IV.

---

## Greeks from Black-Scholes

| Greek | Formula | Interpretation |
|-------|---------|---------------|
| Delta (call) | N(d₁) | Risk-neutral probability of expiring ITM |
| Gamma | N'(d₁) / (S × σ × √T) | Curvature; rate of delta change |
| Theta | Multiple components (see below) | Daily time decay |
| Vega | S × N'(d₁) × √T | $ per 1% vol change |
| Rho (call) | K × T × e^(−rT) × N(d₂) | $ per 1% rate change |

**Theta decomposition**:
1. Volatility value decay: always negative for long options
2. Interest-rate component: can be positive or negative depending on settlement type

The decay component almost always dominates. Both calls and puts have the same sign for the vol decay component.

---

## Model Extensions

| Extension | Purpose |
|-----------|---------|
| Black model (1976) | Futures options (no cost of carry on futures) |
| Garman-Kohlhagen (1983) | Currency options (two interest rates) |
| Merton (1973) | Continuous dividend yield |
| Binomial (CRR, 1979) | American options (early exercise) |
| Barone-Adesi/Whaley (1987) | Faster American option approximation |

---

## Most Important Violations and Their Consequences

| Violation | Real-World Effect | Consequence |
|-----------|-----------------|------------|
| Vol not constant | Volatility smile/skew | Different IVs for different strikes; surface management needed |
| Fat tails | Large moves occur more than model predicts | Short gamma positions face larger-than-expected losses |
| Jumps in price | Gaps on earnings, news | Delta hedge gaps before rebalancing |
| Transaction costs | Each rebalancing costs money | Edge must cover costs; less frequent rebalancing needed |
| Discrete trading | Cannot rebalance continuously | Gamma scalp profits are slightly less than theoretical |

---

## When the Model Works Well

- European options on liquid underlyings without jumps
- Short-dated ATM options (where all assumptions are closest to valid)
- As a framework for thinking about relative value (IV comparison across strikes)
- When used consistently (same model for both pricing and Greek calculation)

---

## Common Misunderstandings

- **"The model is wrong, so I shouldn't use it."** All models are wrong; the question is whether they are useful. Black-Scholes is the universal pricing benchmark — everyone uses it, even when they know its limitations.
- **"Black-Scholes gives you the true option value."** No — it gives you the value consistent with its assumptions. The market price may deviate because real-world risk premiums exceed model-implied values.
- **"IV from Black-Scholes is the market's forecast of realized vol."** Not exactly — IV includes risk premiums (structural demand, liquidity) that cause IV to systematically exceed expected realized vol (the variance premium).

---

## Page References
- Formula derivation and inputs: Ch. 5, pp. 476-560
- Black-Scholes model in depth (Ch. 18): pp. 2527-2650
- Black-Scholes assumptions and violations: Ch. 21, pp. 3276-3433
- Implied volatility calculation: Ch. 5
