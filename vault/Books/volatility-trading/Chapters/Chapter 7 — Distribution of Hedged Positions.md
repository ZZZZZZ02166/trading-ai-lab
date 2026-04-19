# Chapter 7 — Distribution of Hedged Positions
*Volatility Trading — Euan Sinclair, pp. 131–144*

---

## Summary
The central P/L result of vol trading, plus the bad news: dispersion is enormous. Path dependency and discrete hedging error quantified.

---

## Central Result
P/L = ½(σ²_implied − σ²_realized) × ∫ e^(−rt) S²Γ(σᵢ) dt ≈ Vega × (σ_implied − σ_realized)

Edge comes entirely from the gap between IV sold and realized vol.

## Reality: Wide Dispersion (Figure 7.1)
100 simulations, 1-year option, Vega=$1,000, hedged at 30%, realized=30% (zero edge): portfolio value at expiry ranges −$200,000 to +$50,000.

Table 7.1 (daily hedging, 51,000 sims): mean P/L −$97, P10=$7,612, kurtosis=4.40. Fat-tailed even with positive edge.

## Path Dependency (Figures 7.2/7.3)
Two paths with identical annualized vol (23.44%):
- Jump on Day 1 → deep ITM/OTM, gamma collapses, little hedge profit
- Jump last day → gamma maximum, discrete jump is worst case

**Same vol → very different P/L. Timing of large moves matters.**

## Hedging Dispersion Formula
σ_residual = σ_option × √(π/(2N))

- N=5: residual ≈ 56% of option vol
- N=20: ≈ 28%; N=100: ≈ 13%

Transaction costs set the economic limit on rehedging frequency.

## Hedging at Realized vs Implied Vol (Equation 7.15)
**At σ_r**: P/L per step = ½(σ²_r − σ²_i)S²Γdt — deterministic; locks in edge but σ_r unknown.
**At σ_i**: P/L stochastic per step but unbiased on average. Minimizes P/L variance (Figure 7.10). Standard practice.

## Key Lessons
- Evaluate vol strategies over 100+ trades minimum
- Path dependency is irreducible — cannot be hedged away
- Wide dispersion does not mean the strategy is wrong — evaluate with statistics not single outcomes
