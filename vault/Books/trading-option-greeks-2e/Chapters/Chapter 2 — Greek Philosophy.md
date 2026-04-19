# Chapter 2: Greek Philosophy
*Trading Option Greeks 2e — pp. 39–69*

---

## Chapter Summary

This is the foundational chapter. Passarelli introduces the five greeks as the risk measurement tools every option trader must develop fluency in. The chapter uses the Black-Scholes model as the frame: the greeks are the partial derivatives of that model — each one answers the question "how does this option's value change when one input changes?"

---

## Delta (Δ)

Delta has four equivalent definitions (all useful, each illuminating a different aspect):

1. **Rate of change**: how much the option price changes per $1 move in the underlying
2. **Derivative/slope**: the slope of the option price vs. stock price curve at any given point
3. **Equivalent shares**: the number of underlying shares the option position replicates (delta × 100 for equity options)
4. **Probability proxy**: approximate probability of expiring ITM (simplified, not mathematically exact — uses risk-neutral probability without risk-neutral adjustment)

Call deltas range from 0 (deep OTM) to +1.00 (deep ITM). Put deltas range from −1.00 to 0. For a given strike, the absolute values of the call delta and put delta sum to approximately 1.00 (put-call parity).

**How delta changes with conditions:**
- As stock price rises through a call's strike: delta rises from near 0 toward 1.00
- Higher volatility: ITM deltas decrease, OTM deltas increase (the distribution spreads out)
- More time to expiration: OTM options have higher deltas (more chance to move ITM)
- At expiration: delta is binary — 0 (OTM) or 1.00 (ITM)

---

## Gamma (Γ)

Gamma is the rate of change of delta per $1 move in the underlying. It is the "second derivative" of option value with respect to the underlying price.

- **Long options have positive gamma**: when the underlying moves in your favor, delta increases (convexity works for you); when it moves against you, delta decreases (convexity buffers the pain).
- **Short options have negative gamma**: the opposite — the underlying's moves always hurt more than initial delta suggests.

Gamma is highest for ATM options near expiration — this is where delta is most sensitive to small moves. Deep ITM and OTM options have very low gamma (their delta doesn't change much with small moves). Gamma is the mathematical source of the concept "options gain value on big moves."

---

## Theta (Θ)

Theta is the rate of daily time decay — how much option value is lost (long options) or gained (short options) with each passing day.

- Long options: negative theta (pay daily toll)
- Short options: positive theta (collect daily toll)
- ATM options have the highest absolute theta
- Theta is not linear — it accelerates near expiration, steepening especially in the final 2–3 weeks
- Higher volatility → higher option prices → higher absolute theta

The theta for a 32-day 80-strike call is 0.03/day. A short position collects $3/day. By expiration, all time value reaches zero regardless of where it started.

---

## Vega (Υ)

Vega measures sensitivity to a 1 percentage-point change in implied volatility.

- Long options: positive vega (benefit from rising IV)
- Short options: negative vega (hurt by rising IV)
- ATM options have the highest vega (most time value to be affected)
- LEAPS have much higher vega than short-dated options
- Vega operates in parallel with theta: a higher-vega option also decays faster

The 30-strike ATM call/put in the chapter's table has vega = 0.085. A 1-point IV rise = +$8.50 per contract for the long holder. A 10-point IV rise = +$85 per contract.

---

## Rho (ρ)

Rho measures sensitivity to a 1 percentage-point change in the risk-free interest rate.

- Calls: positive rho (higher rates → higher call prices)
- Puts: negative rho (higher rates → lower put prices)
- Negligible for short-dated options (22-day rho ≈ 0.015)
- Significant for LEAPS (2-year LEAPS rho ≈ 0.858)

The direction: higher rates increase the cost of carrying stock (the opportunity cost embedded in put-call parity), raising call prices and lowering put prices.

---

## Put-Call Parity

c + PV(strike) = p + S

Algebraically equivalent: **call = put + stock − strike + interest − dividends**

This equation mathematically locks all calls and puts of the same strike and expiration together. If any of the six inputs changes, parity adjustments happen across all linked securities. If IV rises, both the call and put rise together. If rates rise, calls rise and puts fall by equal rho amounts.

The equation is the foundation of all synthetic positions (Chapter 6).

---

## Key Lessons

1. **Greek fluency is non-negotiable.** Options are multi-dimensional instruments. Delta alone is insufficient; you must track gamma (how delta is changing), theta (daily cost), vega (IV sensitivity), and rho (rate sensitivity) simultaneously.
2. **The four delta definitions are all useful.** When sizing a position, definition 3 (equivalent shares) is most practical. When estimating probability of profit, definition 4 applies. When estimating P/L from a move, definition 1 applies.
3. **Gamma and theta are always paired.** High gamma = high theta. There is no free option position.
4. **Higher volatility changes everything.** Higher vol means higher option prices, higher gamma, higher theta, higher vega. All greeks get amplified by vol.
5. **Put-call parity is the backbone.** When you don't understand why an option is priced a certain way, check what parity implies.

---

## Connections to the Rest of the Book

- Gamma and theta tradeoff is the main topic of Ch. 5 (volatility-selling)
- Vega and term structure are developed in Ch. 3 and Ch. 11 (calendars)
- Put-call parity is applied in Ch. 6 (synthetics) and Ch. 9 (vertical spreads)
- Delta-neutral trading (Ch. 12, 13) uses delta as the variable to neutralise
