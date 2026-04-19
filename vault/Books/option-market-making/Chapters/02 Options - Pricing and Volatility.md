# Chapter 2: Options — Pricing and Volatility
*pp. 9–36 | Option Market Making, Allen Jan Baird*

---

## Summary

This is the longest chapter and the technical foundation of the book. It covers option definitions and payoffs, the concept of fair value, the Black-Scholes-Merton pricing model, and — most importantly — volatility in all its dimensions.

The chapter builds from first principles: an option's value is the probability-weighted sum of all possible payoffs. BSM provides the standard formula for computing this, given five inputs. Of those inputs, only volatility must be estimated — making volatility the central uncertainty of options pricing.

The chapter then critically examines the log-normal assumption underpinning BSM, presenting extensive empirical evidence that real financial returns are leptokurtic (fat-tailed) rather than normal. This has profound implications for option pricing, especially for deep OTM options and tail risk.

---

## Key Concepts

- **Intrinsic value:** Immediate exercise value — max(S − K, 0) for calls, max(K − S, 0) for puts
- **Time premium:** Value above intrinsic value; vanishes at expiration
- **Fair value:** Price at which trading produces neither gain nor loss over the long run; equals expected value
- **BSM model:** Theoretical fair value based on log-normal price distribution
- **Historical volatility (HV):** Backward-looking standard deviation of log price changes
- **Implied volatility (IV):** Forward-looking — derived by inverting BSM from market prices
- **Leptokurtosis:** Fat tails and high center peak in real return distributions
- **Heteroscedasticity:** Volatility that changes over time — makes HV a poor predictor of future vol

---

## Key Lessons

1. **The BSM model is a relative pricing tool, not an absolute one.** Market makers use it to identify when one option is mispriced relative to another. Fair value in absolute terms is unknowable because future volatility is unknowable.

2. **Volatility is the only BSM input you must estimate.** Current price, strike, time to expiration, and interest rate are all observable. Volatility estimation is where all the pricing skill lies.

3. **Real returns have fat tails.** The empirical evidence is overwhelming: financial asset returns show more extreme events than log-normal predicts. BSM therefore systematically underprices deep OTM options (wings). Market makers should price wings with a fat-tail premium.

4. **Implied and historical volatility frequently diverge.** Figure 2.8 (cotton futures) shows this clearly. There is no stable predictive relationship. Neither is reliably "right." Using only historical vol to price options exposes you to mispricing relative to where the market is actually trading.

5. **Volatility scales with √time.** Daily vol = annual vol / √250. Weekly vol = annual vol / √52. This square-root-of-time rule governs how to translate any volatility estimate across time horizons.

6. **Contango vs backwardation matters for options pricing.** Forward prices (which options are priced off) differ from spot prices due to cost of carry. For income-earning assets, futures trade below spot (backwardation). For commodity assets with positive carry costs, futures trade above spot (contango). Always use the correct forward price when pricing options.

---

## Important Examples

- **Figure 2.1/2.2:** Payoff diagrams for 100 strike call and put (premium $1.70). Breakevens at $101.70 (call) and $98.30 (put).
- **Figure 2.3:** Discrete probability histogram showing fair value calculation: Σ(P × $) = $0.88 for a 100 call over a 95–105 outcome range.
- **Figure 2.4:** Normal distribution vs empirical returns — empirical is taller at center AND has fatter tails.
- **Figure 2.5:** Wheat futures price changes show fat-tail behavior across multiple years.
- **Figure 2.6:** S&P 500 error curve — excess frequency in tails and deficit in ±1-2 SD zone.
- **Figure 2.7:** Cauchy distribution fits wheat price changes better than normal.
- **Figure 2.8:** October cotton futures — implied and historical vol diverge frequently.
- **Figure 2.9:** Contango vs backwardation diagram for futures term structure.

---

## Key Formulas

**BSM (Fischer Black futures version):**
- C = e^(−rt) × [X × N(d1) − K × N(d2)]
- d1 = [ln(X/K) + (S²/2)t] / (S√t) ;  d2 = d1 − S√t

**Standard Deviation in Points:**
- SDP_t = P × (V / √PY) where PY = number of periods per year

**Volatility scaling:**
- Vol_daily = Vol_annual / √250 ;  Vol_weekly = Vol_annual / √52

---

## Warnings

- Do not assume BSM gives the "true" fair value — it gives a model price. Model error (especially from the normality assumption) is real and significant.
- Heteroscedasticity means 20-day historical vol today is a poor predictor of vol 20 days from now. Use implied vol as a sanity check, not a confirmation.
- Long-dated options (>1 year) require interest rate term structure adjustments not in simple BSM.

---

## Connection to the Rest of the Book

This chapter provides the pricing foundation used throughout. Chapter 3 builds on it to define the six Greeks. Chapter 5 uses put-call parity (derived from BSM no-arbitrage conditions) for synthetic trading. The volatility concepts introduced here are revisited in Chapter 8 (skew risk) and in the market-making tactics sections.
