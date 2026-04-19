# Position Greeks
*Source: Trading Options as a Professional — Ch. 4, 10*

---

## Definition

Position Greeks scale individual option Greeks to the full dollar exposure of a complete position:

> **Position Greek = Option Greek × Number of Contracts × 100**

Each position Greek measures the dollar P/L from a one-unit change in the corresponding input.

---

## The Five Position Greeks

| Greek | Formula | What It Measures |
|-------|---------|-----------------|
| Position delta | delta × contracts × 100 | Dollar gain/loss per $1 stock move |
| Position gamma | gamma × contracts × 100 | Delta change per $1 stock move |
| Position vega | vega × contracts × 100 | Dollar gain/loss per 1% IV change |
| Position theta | theta × contracts × 100 | Dollar gain/loss per day (time decay) |
| Position rho | rho × contracts × 100 | Dollar gain/loss per 1% rate change |

---

## Examples

**Long 4 XYZ 80 Calls** (option delta 0.55, gamma 0.04, vega 0.13, theta 0.04):
- Position delta: 4 × 0.55 × 100 = +220 (behaves like long 220 shares)
- Position gamma: 4 × 0.04 × 100 = +16 (delta increases by 16 per $1 rise)
- Position vega: 4 × 0.13 × 100 = +52 (+$52 per 1% IV rise)
- Position theta: 4 × 0.04 × 100 = −16 (−$16 per day for long position)

**Short 10 QRS 40 Puts** (gamma 0.11, vega 0.05, theta 0.01):
- Position gamma: −(10 × 0.11 × 100) = −110 (delta moves against you per $1 move)
- Position vega: −(10 × 0.05 × 100) = −50 (−$50 per 1% IV rise)
- Position theta: +(10 × 0.01 × 100) = +10 (+$10/day income)

---

## Greeks Are Additive for Multi-Leg Positions

For a bull call spread (long lower, short upper): position Greeks = sum of each leg's position Greeks.

20 long 70–75 call spreads:
- Position delta = +546 (46 net delta per spread × 100 × 20 contracts)
- Position gamma = +20
- Position vega = +42
- Position theta = +170/day income

---

## Why Greeks Change Dynamically

Position Greeks are snapshots at current market conditions. They change as:
- **Stock moves**: gamma causes delta to drift
- **Time passes**: theta accelerates; gamma and vega change
- **IV changes**: vega itself changes with vol level (non-linear)

A position's delta at stock price $70 may be very different from its delta at $80. Risk management requires re-evaluating Greeks whenever the stock moves significantly.

---

## Setting Dollar Risk Limits

Position Greeks translate directly into dollar risk limits:
- "Max acceptable loss per $1 adverse move" = position delta → determines position size
- "Max acceptable loss from a 5 vol-point IV rise" = position vega × 5 → determines IV risk
- "Daily theta income vs. weekly gamma risk" → determines minimum expected stock movement needed to maintain profitability

---

## Common Misunderstandings

- **"Greeks are constant"**: No. They change with every market condition change.
- **"Negative gamma means the position loses money"**: No. Short options with negative gamma collect theta. Negative gamma means losses from large moves; whether you come out ahead depends on whether theta income exceeds gamma losses.
- **"Delta is all that matters"**: No. A position with correct delta but wrong gamma, vega, or theta will be surprised by market moves, time, or IV changes.

---

## Page References
- Position gamma examples: pp. 143–149 (Ch. 4)
- Position vega examples: pp. 149–152 (Ch. 4)
- Position theta examples: pp. 152–154 (Ch. 4)
- Position rho examples: pp. 154–155 (Ch. 4)
- Position Greeks for 70–75 spread: pp. 340–345 (Ch. 10)
