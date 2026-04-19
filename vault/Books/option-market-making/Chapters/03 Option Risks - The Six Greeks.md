# Chapter 3: Option Risks — The Six Greeks
*pp. 37–52 | Option Market Making, Allen Jan Baird*

---

## Summary

This chapter defines and explains the six quantifiable market risks of option positions. Every option responds to six independent variables: underlying price change (delta), rate of price change (gamma), time passage (theta), implied volatility change (kappa/vega), interest rate change (rho), and implied volatility differences across strikes (skew). Calendar spread positions also carry time delta and time kappa risks.

The chapter is notable for its emphasis on *dollar risk* — always multiply Greek risk values by the actual contract dollar value to know your real exposure.

---

## The Six Greeks

### Delta (Δ) — Price Sensitivity
- **Definition:** Dollar change in option price per $1 change in underlying
- **Range:** 0 to +1.00 for calls; 0 to −1.00 for puts
- **ATM delta:** ≈ ±0.50 (roughly 50% probability of expiring ITM)
- **Deep ITM:** delta → ±1.00 (moves with underlying)
- **Far OTM:** delta → 0 (nearly insensitive to price)
- **Delta drift:** As price moves, delta changes (this change is gamma). Near expiration, ATM delta becomes nearly binary.
- **Delta neutral:** Net portfolio delta = 0. Requires continuous rebalancing because price moves change delta.

### Gamma (Γ) — Curvature / Delta Sensitivity
- **Definition:** Change in delta per $1 change in underlying
- **Long options:** Always positive gamma — delta increases toward +1 as call moves ITM
- **Short options:** Always negative gamma
- **Highest gamma:** ATM; near zero for deep ITM or OTM
- **Expiration effect:** Near expiration, ATM gamma spikes dramatically (pin risk)
- **Lambda (Λ):** Percentage change in option value per 1% change in underlying. Always >1 (leverage). High for OTM options.

### Theta (Θ) — Time Decay
- **Definition:** Daily change in option value due to time passage alone
- **Long options:** Negative theta (lose value each day)
- **Short options:** Positive theta (gain value each day)
- **Largest theta:** ATM options
- **Theta-gamma relationship:** For long options, theta is the daily cost of holding gamma. Large gamma = large theta. The price move needed to overcome theta = the "break-even move."

### Kappa/Vega (K) — Implied Volatility Sensitivity
- **Definition:** Dollar change per 1-point change in implied volatility
- **Long options:** Positive kappa (benefit from rising IV)
- **Short options:** Negative kappa (benefit from falling IV)
- **Highest kappa:** ATM, longer-dated options
- **Critical importance:** Often the LARGEST risk. A 10-point IV move can create $800+ P&L swings per contract in major futures. Must be managed separately from delta.
- **Key trap:** Long call + rising underlying + falling IV = potentially net loss despite "being right" directionally

### Rho (ρ) — Interest Rate Sensitivity
- **Definition:** Dollar change per 1-percentage-point change in risk-free rate
- **Futures options:** Small rho (futures price already incorporates carry)
- **Stock/bond options:** More significant; affects present value of exercise price
- **Direction:** Higher rates → higher call values, lower put values (for non-futures options)

### Skew Risk — Differential IV Across Strikes
- **Definition:** Change in option value from changes in the shape/slope of the IV smile
- **Positive skew:** OTM wings trade at higher IV than ATM center (most common)
- **Negative skew:** Wings below ATM (rare, usually temporary)
- **Skew shift:** Large price moves shift the entire skew curve, affecting spread traders

---

## Time Spread Risks (Calendar Spreads)

- **Time delta:** Risk from differential underlying price sensitivity across expiration months (basis risk)
- **Time kappa:** Risk from divergent IV changes between front and back months
- Both can cause large P&L swings even when single-month positions appear risk-neutral

---

## Key Lessons

1. **Always translate Greeks to dollars.** A 0.10 gamma on one option is $50 risk for a $500/point contract. A 10-option position = $500 gamma risk. Never think in cents per option for risk assessment.

2. **Kappa is often the most important risk.** More market makers are hurt by unexpected IV moves than by delta or theta. Build a kappa budget into every strategy.

3. **Gamma and theta are inseparable for long options.** Being long gamma means being short theta. You pay time decay for the right to benefit from large moves. The position only profits if realized vol exceeds the theta cost.

4. **Delta neutrality requires active management.** A position that is delta-neutral at price 100 becomes delta-positive if price rises to 105 (for a long call portfolio). You must rehedge.

---

## Warnings

- Near expiration, gamma concentrates sharply at the money — pin risk is real. A $0.50 move through a strike near expiration can cause huge delta changes for short options.
- Time kappa/vega risk in calendar spreads is NOT captured by standard single-month Greek measures. Model it separately.
- Skew shift can turn a profitable vertical spread into a losing position independent of any directional move.

---

## Connection to the Rest of the Book

The Greeks defined here are used throughout the book. Chapter 4 shows how Greek risk profiles differ across the 22 core position types. Chapter 6 extends to calendar spread risks. Chapter 8 covers the practical management of kappa (skew risk, tracking implied vs historical vol).
