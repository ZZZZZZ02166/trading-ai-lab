# Delta-Neutral Trading
*Source: Trading Options as a Professional — Ch. 8, 9*

---

## Definition

Delta-neutral trading establishes a position with approximately zero net delta by offsetting option delta with an opposite stock position. The result: directional exposure is neutralized, leaving the position primarily exposed to volatility (both implied and realized) and time decay.

---

## Establishing Delta Neutrality

1. Open option position → creates positive or negative delta
2. Calculate total position delta: option delta × contracts × 100
3. Trade stock in opposite direction to offset

Example: long 20 calls at delta 0.50 → position delta = +1,000. Short 1,000 shares → net delta = 0. Remaining exposures: gamma (+), vega (+), theta (−).

---

## Long vs. Short Delta-Neutral

| Feature | Long Delta-Neutral | Short Delta-Neutral |
|---------|-------------------|---------------------|
| Option position | Long options | Short options |
| Stock position | Short stock | Long stock |
| Gamma | Positive | Negative |
| Vega | Positive | Negative |
| Theta | Negative (pay daily) | Positive (collect daily) |
| Profits when | Realized vol > IV, or IV rises | Realized vol < IV, and IV falls |
| Risk | Theta erodes if stock doesn't move | Large moves create gamma losses |

---

## Gamma Scalping (Long Gamma)

The profit mechanism for long gamma positions:
- Stock rises → delta becomes positive → sell stock to re-neutralize → lock in gain
- Stock falls → delta becomes negative → buy stock to re-neutralize → lock in gain
- Net: each round-trip captures a small profit
- Total gamma P/L = sum of all stock scalps

**Breakeven**: total gamma scalp profits ≥ total theta paid over holding period.

---

## Rebalancing Frequency

- Too frequent → transaction costs exceed scalp profits
- Too rare → large directional exposure defeats the purpose
- Professional rule: rebalance when delta drifts by ~1 standard deviation of expected daily move

---

## Two Types of Delta-Neutral Traders

**Speculators**: hold for days to weeks; profit from IV forecast vs. actual realized vol; accept the risk their forecast is wrong.

**Market makers**: hold for minutes to hours; goal is to close position at bid or ask before IV changes adversely; use delta-neutral as short-term insurance while seeking to transact at the spread.

---

## P/L Attribution

Always decompose total P/L into:
- Theta P/L (position theta × days)
- Gamma P/L (sum of all stock scalps)
- Vega P/L (IV change × position vega)

Without attribution, you don't know which part of your strategy is working.

---

## Common Misunderstandings

- **"Delta-neutral means no risk."** No — it replaces directional risk with volatility risk (gamma + vega).
- **"Gamma scalping is free money."** No — transaction costs and theta are real costs that offset scalp profits.
- **"Market makers are delta-neutral all the time."** No — they use it as a temporary hedge while seeking to close positions at a profit.

---

## Page References
- Concept and establishment: pp. 242–252 (Ch. 8)
- Long vs. short delta-neutral: pp. 252–268 (Ch. 8)
- Gamma scalping mechanics: pp. 260–270 (Ch. 8)
- Market maker use of delta-neutral: pp. 278–280 (Ch. 8), pp. 280–290 (Ch. 9)
