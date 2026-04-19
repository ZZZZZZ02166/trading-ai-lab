# Concept: Subjective Option Pricing (Boness Model)
*From: Positional Option Trading, Euan Sinclair*

---

## Definition

**Subjective option pricing** uses the trader's actual directional forecast (drift μ) to calculate the personal value of an option, as opposed to the risk-neutral BSM approach which assumes drift is irrelevant. The Boness model (1962, predating BSM) is the mathematical framework.

---

## Why BSM Ignores Drift (And When That's Wrong)

BSM removes drift from option pricing via the replication argument: a market maker who can continuously buy/sell the underlying to replicate the option can guarantee a profit regardless of where the underlying goes. Drift is irrelevant to the replication cost, so it doesn't appear in the pricing formula.

This is correct for **market makers who hedge**. But for **speculators who buy options for directional exposure**, they are NOT replicating — they want the underlying to go up (for calls) or down (for puts). For them, drift matters enormously, and BSM gives the wrong value.

---

## The Boness Formula

**Call:**
> C = S·exp(μT)·N(d₃) − X·N(d₄)

**Where:**
- d₃ = [ln(S/X) + (μ + σ²/2)·T] / (σ√T)
- d₄ = [ln(S/X) + (μ − σ²/2)·T] / (σ√T)
- μ = trader's actual drift forecast (e.g., 10% annual)

**Generalized form with discounting:**
> C = S·exp(μT)·N(d₃) − exp(−rT)·X·N(d₄)

---

## True ITM Probability vs Risk-Neutral Probability

| Measure | Formula | What It Means |
|---------|---------|---------------|
| Risk-neutral (BSM) | N(d₂) | Used for hedging and replication |
| Physical (Boness) | N(d₄) | True probability under your drift forecast |

**Example:** 1-year 110 call, S=$100, σ=30%, r=0%, μ=10%:
- Risk-neutral probability = 32%
- Physical probability = 45%
- Difference = 13 percentage points

The physical probability is what matters for a speculative buyer. Using N(d₂) = 32% and asking "is this option worth buying?" gives the wrong answer if you have a 10% drift forecast.

---

## Drift Greek (Sensitivity to Forecast)

The partial derivative of the call price with respect to drift:
> ∂C/∂μ = T·S·exp(μT)·N(d₃)

This measures how much the subjective value changes for a 1% change in drift estimate. Errors in the drift forecast flow directly into the option valuation. For long-dated options (large T) or large positions (large S), small drift errors produce large valuation errors.

---

## Practical Use

1. **Forecast the drift** μ for the underlying using your fundamental/quantitative analysis
2. **Calculate Boness value** using the formula above
3. **Compare to market price** (BSM value with market IV)
4. If Boness value > market price for calls (or puts): your directional view implies the option is underpriced relative to your forecast
5. **Choose the appropriate structure:** long call, covered call, put spread, or risk reversal depending on the size and confidence of your directional forecast

---

## Common Misunderstandings

- **"I should only use Boness if I'm sure about direction."** False — Boness is more informative than BSM for *any* speculative position. Even a modest directional forecast (μ = 3% above risk-free rate) meaningfully changes option value.

- **"The difference is small."** Not for far-OTM options or long-dated options. A 10% drift forecast can change ITM probability from 32% to 45% — a 40% relative increase.

- **"The market already prices in drift."** The market prices in the risk-neutral drift (approximately 0 after adjustment). If you have information that the actual drift is higher, Boness quantifies your edge.

---

## Source Page References

- Why drift doesn't matter for market makers: pp. 149–151
- Boness model and formulas: pp. 151–153
- True vs risk-neutral ITM probability: pp. 154–155
- Drift greek (∂C/∂μ): p. 153
- Practical option selection tables: pp. 160–163
