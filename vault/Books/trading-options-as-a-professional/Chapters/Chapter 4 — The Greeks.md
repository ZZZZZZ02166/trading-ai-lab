# Chapter 4 — The Greeks
*Source: Trading Options as a Professional — Ch. 4*

---

## Summary

Chapter 4 is the central chapter of the book and the most technically dense. Bittman covers all five Greeks in systematic detail: how each one varies with stock price, time, and volatility, including graphs showing all three relationships. He then extends this to position Greeks — how individual Greeks scale to a full portfolio position.

The chapter is notable for its comprehensive visual treatment. For each Greek, Bittman provides:
- Greek vs. stock price (bell-shaped or S-curve)
- Greek vs. time to expiry (how it changes as time passes)
- Greek vs. volatility (how IV level affects the Greek)

---

## Delta: Directional Exposure

### S-Curve Behavior
- Deep OTM call: delta ≈ 0
- ATM call: delta ≈ 0.50
- Deep ITM call: delta ≈ 1.00
- For puts: mirror S-curve from 0 to −1.00

### Delta and Time
Time has minimal effect on delta away from the strike. Only ATM options maintain ~0.50 delta across all time horizons. ITM stays near 1.00; OTM stays near 0.

### Delta and Volatility
Higher vol compresses all deltas toward 0.50. In a high-vol environment, any option has a meaningful chance of ending up anywhere — ITM deltas fall toward 0.50, OTM deltas rise toward 0.50. This means high-IV environments reduce the directional differentiation between strikes.

### Position Delta
Position delta = option delta × contracts × 100.  
Long 4 XYZ 80 Calls, delta 0.55 → position delta = +220.  
Position behaves like being long 220 shares: $1 stock rise ≈ +$220.

---

## Gamma: Rate of Delta Change

### Bell-Shaped Profile
Gamma peaks at the ATM strike. Deep ITM and OTM options have near-zero gamma. The bell is centered on the strike.

### Gamma Near Expiration
ATM gamma accelerates exponentially as expiration approaches. In the final 20 days, gamma can become very large. OTM and ITM gamma remain low.

### Gamma and Volatility
Higher vol reduces gamma for all options. The broader return distribution means delta changes more gradually per dollar move.

### Position Gamma
Long options: positive position gamma (delta moves in your favor on moves).  
Short options: negative position gamma (delta moves against you on moves).  
Example: long 4 XYZ 80 Calls, gamma 0.04 → position gamma = +0.16. $1 stock rise increases position delta by +16 (from 220 to 236).

---

## Vega: Volatility Sensitivity

### Bell-Shaped Profile
Vega is highest for ATM options, falling toward zero for deep ITM and OTM.

### Vega and Time
Vega increases with time to expiry. LEAPS have the most vega exposure. Near expiration, vega approaches zero for all options.

### Vega and Volatility: Concave Relationship
Vega rises from zero, peaks at moderate volatility (~30–50%), then declines at extreme vol levels. A 1% IV change produces different dollar impacts at different IV starting levels.

### Position Vega
Long options: positive position vega (IV rise = gain).  
Short options: negative position vega (IV rise = loss).  
Example: long 4 XYZ 80 Calls, vega 0.13 → position vega = +0.52. 1% IV rise → +$52 gain.

---

## Theta: Daily Time Decay

### Inverted Bell-Shaped Profile
Theta is most negative (largest decay) for ATM options. Deep ITM and OTM have smaller absolute theta.

### Theta Acceleration Near Expiration
ATM theta starts small for long-dated options, then accelerates in the final weeks. The last 3–6 weeks of an ATM option's life see the most rapid dollar decay. This is the "theta harvest" for short-option traders.

### Theta and Volatility
Higher vol increases dollar theta. The gamma-theta linkage is confirmed: both increase together with higher vol, ATM, and near expiration.

### Position Theta
Long options: negative position theta (pay daily decay).  
Short options: positive position theta (collect daily decay).  
Example: short 4 XYZ 80 Calls, theta 0.04 → position theta = +0.16 ($16/day income).  
Over 30 days: +$480 from theta alone (if all else equal).

---

## Rho: Interest Rate Sensitivity

### S-Curve for Calls, Inverted for Puts
Call rho is positive and largest for deep ITM options.  
Put rho is negative and most negative for deep ITM puts.

### Rho and Time
Rho increases with time to expiry. LEAPS have the most rho exposure. OTM short-dated options have near-zero rho.

### Rho and Volatility
Higher vol decreases rho. At extreme vol, time premium dominates and the carry component becomes a small fraction of total value.

### Position Rho
Example: long 4 XYZ 80 Calls, rho 0.07 → position rho = +0.28. 1% rate rise → +$28 gain (calls benefit from higher rates; puts are hurt).

---

## Summary Table: Greek Behaviors

| Greek | ATM vs. OTM/ITM | Effect of Time | Effect of Higher Vol | Long Position Sign |
|-------|----------------|----------------|---------------------|-------------------|
| Delta | ~0.50 at ATM | Minimal away from ATM | Compresses toward 0.50 | + (calls), − (puts) |
| Gamma | Peak at ATM | Rises exponentially near expiry (ATM) | Falls | + |
| Vega | Peak at ATM | Rises with more time | Peaks at moderate vol | + |
| Theta | Most negative ATM | Accelerates near expiry (ATM) | Rises | − |
| Rho | Most positive ITM (calls) | Rises with more time | Falls | + (calls) |

---

## Warnings

⚠️ Negative position gamma means the position's directional bias works against you on every adverse move. Short-gamma positions in volatile markets can accumulate losses faster than the position's theta recovers them.

⚠️ Vega and theta are both largest near expiration for ATM options. Short-option traders in the final 3 weeks face both maximum theta income AND maximum gamma/vega risk simultaneously.

⚠️ Greeks change as market conditions change. A delta calculation today is not valid if the stock moves $5. Always re-evaluate Greeks dynamically.

---

## Page References
- Delta: pp. 78–99 (Ch. 4)
- Gamma: pp. 99–104 (Ch. 4)
- Vega: pp. 104–108 (Ch. 4)
- Theta: pp. 108–113 (Ch. 4)
- Rho: pp. 113–117 (Ch. 4)
- Position Greeks: pp. 126–134 (Ch. 4) / pp. 143–155 (Ch. 4)
