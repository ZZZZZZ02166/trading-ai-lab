# Chapter 6 — Volatility
*Option Volatility and Pricing — Natenberg*

---

## Summary

The most important chapter in the book. Natenberg establishes volatility as the single unobservable input to option pricing models — every other input is known from market data. The chapter covers: the mathematical definition of volatility, how to calculate historical volatility, the lognormal distribution, and why volatility estimation is the central skill in options trading.

---

## Volatility: Definition

Volatility = the annualized standard deviation of logarithmic price returns.

**Why logarithmic returns?** Log returns ln(P_t / P_{t-1}) are:
1. Additive over time (log returns compound correctly)
2. Symmetric for equal percentage up/down moves
3. Compatible with the lognormal model (negative prices are impossible)

**Why standard deviation?** It measures the spread of the return distribution. A higher standard deviation means larger expected price swings.

**Why annualized?** Standardizes comparison across different holding periods. Multiply daily std dev by √252 to annualize.

---

## Calculating Historical Volatility

Steps:
1. Collect N daily settlement prices
2. Compute log returns: r_i = ln(P_i / P_{i-1})
3. Calculate mean: r̄ = (1/N) × Σr_i
4. Sample standard deviation: σ_daily = √[Σ(r_i − r̄)² / (N−1)]
5. Annualize: σ_annual = σ_daily × √252

**Using N−1 divisor** gives an unbiased estimate (sample vs. population). For large N, the difference is negligible.

**Lookback window tradeoffs**:
| Window | Characteristic | Best For |
|--------|---------------|----------|
| 10-20 days | Responsive, noisy | Detecting recent vol changes |
| 60 days | Balanced | General forecasting |
| 252 days | Stable, slow | Long-run average, regime detection |

---

## Alternative HV Estimators

**Parkinson (1980)**: Uses daily high and low: σ² ∝ Σln(H_i/L_i)². More efficient than close-to-close (fewer days needed for same accuracy).

**Garman-Klass (1980)**: Uses open, high, low, close. Most efficient among close-price-based methods.

**Limitation of both**: Only measure volatility during market hours. Understate true vol for assets with significant overnight gaps (earnings, news events).

---

## The Lognormal Distribution

Stock prices cannot go below zero but can rise without bound → price distributions are asymmetric (lognormally distributed).

**Key properties**:
- Left tail bounded at zero
- Right tail is open-ended (longer)
- Mean > mode (mean is to the right of the peak)
- Log returns are normally distributed even though prices are lognormally distributed

**Implication for expected value**: The expected future price under a lognormal distribution exceeds the current forward price (Jensen's inequality). This affects how option theoretical values are computed.

---

## Volatility and Expected Move

Given implied volatility IV:
- **Annual 1-sigma range**: ±IV × S (68% probability of staying within this range over 1 year)
- **Daily 1-sigma move**: IV × S / √252
- **N-day 1-sigma range**: IV × S × √(N/252)

Example: $100 stock at 30% IV:
- 1-day expected move: 30% × $100 / √252 = $1.89
- 30-day expected move: 30% × $100 × √(30/252) = $10.35

---

## Volatility Mean Reversion: Real but Slow

Historical volatility tends to revert toward its long-run average, but mean reversion is:
1. Slow relative to option lifetimes
2. Unreliable over short horizons
3. Variable — the mean itself shifts over time

Practical implication: IV that appears "too high" can stay elevated or rise further before reverting. Do not assume mean reversion will bail out a short-vol position.

---

## Why Volatility Estimation Is the Central Skill

Every option's theoretical value depends on the vol input. The same option at 25% vol vs. 30% vol has dramatically different theoretical values — and different Greeks. A trader who correctly forecasts that realized vol will be 20% when IV is 30% has a significant edge. A trader who uses an incorrect vol input generates a wrong theoretical value, leading to wrong edge calculations and potentially money-losing trades.

**The vol trader's workflow**:
1. Estimate expected realized vol (from historical data, regime analysis, event calendar)
2. Compare to current IV
3. If expected > IV: buy vol (long options, long gamma, long vega)
4. If expected < IV: sell vol (short options, short gamma, positive theta)

---

## Common Misunderstandings

- **"Vol is just a number."** No — it is a probability statement about the distribution of future prices. Changing vol changes the entire probability distribution.
- **"Realized vol tells you what IV should be."** Not directly — realized vol is backward-looking; IV is forward-looking. Past realized vol is a data point, not a forecast.
- **"High vol means sell."** Only if you believe realized vol will be lower than current IV. High IV relative to recent HV is a necessary but not sufficient condition for a short-vol trade.

---

## Connections to Other Concepts

- **Implied volatility** (Ch. 5): IV is back-solved from market price using the model. It is the vol input that makes model price = market price.
- **Delta-neutral hedging** (Ch. 7): The breakeven realized vol for a delta-neutral hedge = the IV at which options were purchased.
- **Volatility term structure** (Ch. 20): IV varies across expirations; forward vol measures expected vol between two dates.
- **Volatility skew** (Ch. 25): IV varies across strikes, reflecting non-lognormal distribution of real-world prices.
