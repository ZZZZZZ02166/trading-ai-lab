# Concept: Kelly Criterion for Options Trading
*From: Positional Option Trading, Euan Sinclair*

---

## Definition

The **Kelly criterion** is a mathematical formula for the optimal fraction of capital to bet in a series of trades to maximize the long-run geometric growth rate of wealth. It was originally developed for simple binary bets but extends to continuous return distributions.

For a strategy with mean return μ and standard deviation σ (approximately normally distributed):

> **f* ≈ μ/σ²** (or equivalently, the Sharpe ratio × σ)

This is the fraction of total capital that should be deployed in each trade.

---

## Extensions for Options (Non-Normal Returns)

Options strategies typically have **negative skew** (many small wins, rare large losses — for short-vol positions). The Kelly fraction must be adjusted:

> **f* ≈ μ/(μ²+σ²) + λ₃μ²/(μ²+σ²)³**

Where λ₃ is the third central moment (skewness × σ³). **Negative skewness reduces the optimal Kelly fraction** compared to the naive symmetric estimate.

---

## The Estimation Uncertainty Problem

The Kelly fraction is estimated from historical data, which always has finite sample size. Key results:

- **Var(f̂) = (1/σ² + 2μ²/σ⁴)/n** — variance of the Kelly estimate declines with more data
- With n=1000 trades: sd(f̂) ≈ 0.03–0.10 for typical strategies
- There is a meaningful probability that estimated f* > 0 while the true f* ≤ 0

**Consequence: Full Kelly on an estimated fraction almost always means over-betting.**

---

## Fractional Kelly: The Practical Solution

To keep the probability of over-betting below a target threshold:

| Chance of Over-Betting | Normal Returns (Kelly Scale) | Skew-Adjusted (Kelly Scale) |
|------------------------|------------------------------|-----------------------------|
| 10% | 0.048 × Kelly | 0.205 × Kelly |
| 15% | 0.230 × Kelly | 0.357 × Kelly |
| 20% | 0.375 × Kelly | 0.478 × Kelly |

**Practical default: trade at 25–50% of estimated Kelly.** This is the right answer before you have large sample sizes, which in options means almost always.

---

## Growth Rate vs Drawdown

Growth rate as function of Kelly fraction f:

> **GR(f) = (f − f²/2) · μ²/σ²**

- GR is maximized at f = 1 (full Kelly)
- GR = 0 at f = 2 (double Kelly)
- GR < 0 for f > 2 (over-betting destroys wealth)

The **growth rate to drawdown ratio** peaks at f = 0.5 (half-Kelly). This is why **half-Kelly maximizes risk-adjusted returns** — it gives the most growth per unit of drawdown.

---

## Ruin Probability

Probability of reaching wealth level B (e.g., 200%) before ruin level A (e.g., 0%):

> **P(A, B) = (1 − A^(1−2/f)) / (B^(1−2/f) − A^(1−2/f))**

Counterintuitively:
- At very low f (0.1× Kelly): ruin probability ≈ 90% of reaching goal
- At full Kelly: ruin probability ≈ 45% of reaching goal
- At 2× Kelly: worse than full Kelly

**More aggressive betting does NOT improve survival odds.** Trading at 25–50% Kelly gives the best combination of growth and survival probability.

---

## Stops and Kelly: An Important Interaction

Adding a stop loss does not simply truncate the left tail. It:
1. Eliminates some trades that would have recovered above the stop
2. Changes the return distribution from unimodal to bimodal
3. **Reduces average return** even for strategies with positive expected value
4. Trailing stops are worse than fixed stops

Stops should be used only when position monitoring is impossible or the drawdown would be genuinely existential.

---

## Common Misunderstandings

- **"Kelly is reckless."** At full Kelly, yes. At quarter or half Kelly, no. The Kelly framework explicitly accounts for risk — it's designed to prevent ruin while maximizing growth.

- **"Kelly guarantees I won't go broke."** Kelly maximizes geometric growth and minimizes time to a goal, but does not guarantee anything with finite data. Fractional Kelly adds a safety margin.

- **"I can calculate Kelly precisely."** No — the estimate has substantial uncertainty, especially with short-vol strategies where the skewness parameter is hard to estimate. This is why fractional Kelly is not just a conservative preference but a mathematically justified correction.

---

## Source Page References

- Kelly for continuous distributions: pp. 191–202
- Skewness adjustment: pp. 192–195
- Estimation uncertainty: pp. 196–200
- Fractional Kelly tables: pp. 200–201
- Growth rate / drawdown: pp. 201–202
- Ruin probability: pp. 203–204
- Stops: pp. 204–209
