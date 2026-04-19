# Chapter 7 — Dynamic Hedging
*Option Volatility and Pricing — Natenberg*

---

## Summary

Natenberg proves that an option's theoretical value equals the cost of dynamically replicating it through continuous delta-neutral hedging. This chapter bridges pricing theory and practice: it shows exactly how gamma scalping works, what the breakeven condition is, and why transaction costs and rebalancing frequency are critical decisions.

---

## The Core Proof

**Claim**: An option's theoretical value = the expected total cost of replicating it via dynamic delta hedging.

**Proof by example**:
1. Buy 10 calls at delta 0.50 → position delta = +500
2. Short 500 shares to neutralize delta → net delta = 0
3. Underlying rises 1 point → call delta rises to 0.55 → position delta = +50 → sell 50 shares
4. Underlying falls back → delta returns to 0.50 → buy 50 shares back
5. Net result from round-trip: sold 50 at higher price, bought 50 at lower price → small profit

This process repeats throughout the option's life. The cumulative sum of all such round-trip profits = gamma scalp P/L. At expiration:

**P/L = Initial theoretical edge + Gamma scalp P/L − Theta paid − Transaction costs ± Vega P/L (from IV changes)**

If realized vol = IV, gamma scalps ≈ theta paid → total P/L ≈ initial theoretical edge.

---

## The Breakeven Condition

**Long gamma (bought options)**:
- Breakeven: realized vol ≥ IV at purchase
- If realized > IV: gamma scalps > theta paid → profitable
- If realized < IV: theta paid > gamma scalps → loss

**Short gamma (sold options)**:
- Breakeven: realized vol ≤ IV at sale
- If realized < IV: theta collected > gamma losses → profitable
- If realized > IV: gamma losses > theta collected → loss

**The critical insight**: the IV at which options are traded is approximately the breakeven realized vol for the hedging strategy.

---

## Gamma Scalping Mechanics

Each gamma scalp works because of the option's convexity (positive gamma for long positions):

- Stock rises → option delta becomes more positive → sell stock (at higher price) to restore neutrality
- Stock falls → option delta becomes more negative → buy stock (at lower price) to restore neutrality

Every round-trip captures a small profit proportional to: ½ × gamma × ΔS²

Total gamma P/L over the life of the position ≈ ½ × Σ(gamma_t × ΔS_t²) − Σ(theta_t × Δt)

This is the continuous-time formulation: Gamma P/L − Theta = 0 at breakeven.

---

## Rebalancing Frequency

**Too frequent**: transaction costs accumulate, eliminating profits.

**Too rare**: large directional exposure accumulates. The position is no longer delta-neutral and directional risk dominates.

**Professional rule**: rebalance when delta drifts by approximately 1 standard deviation of expected daily move.

Example: $100 stock at 25% IV. Daily sigma = 25% × $100 / √252 = $1.58. Rebalance when delta drifts by ~1.58 × underlying units.

---

## Two Types of Delta-Neutral Traders

| Feature | Speculator | Market Maker |
|---------|-----------|-------------|
| Holding period | Days to weeks | Minutes to hours |
| Vol bet | Realized vol vs. IV forecast | Capture bid-ask spread |
| Risk tolerance | Accepts vol forecast being wrong | Must hedge immediately |
| Transaction costs | Moderate | Very low (exchange fees) |
| Primary concern | Right vol forecast | Right inventory management |

---

## P/L Attribution

Always decompose actual P/L into components:

1. **Theta P/L** = position theta × days held
2. **Gamma P/L** = sum of all stock scalps
3. **Vega P/L** = (IV_final − IV_initial) × position vega

Without attribution, you don't know whether profit came from being right about vol or from favorable IV changes.

---

## Frictionless Assumption Violations

Black-Scholes dynamic hedging assumes:
1. Continuous trading — rebalance instantly at any price
2. Zero transaction costs
3. Unlimited borrowing

In practice:
- Discrete rebalancing causes slippage: each round-trip captures slightly less than the theoretical gamma scalp
- Transaction costs accumulate with each adjustment — may exceed edge
- Margin calls can force liquidation at adverse prices

These violations mean realized gamma P/L is always less than the theoretical prediction. A sufficient initial edge must cover these frictions.

---

## Interest on Hedge Position

When shorting underlying to hedge a long call:
- Proceeds from short sale earn interest
- Example: short 50 shares at 97.70 = $4,885 credit; at 6% for 70 days: +$56.21 interest income
- Each adjustment trade also creates a cash position earning/costing interest

This interest is part of true P/L. The theoretical option value already accounts for this cost of carry. Do not double-count.

---

## Connections to Other Concepts

- **Gamma** (Ch. 9): The higher the gamma, the more frequent and larger the scalp profits for a given vol level
- **Theta** (Ch. 10): The daily cost of holding long options; the income from holding short options
- **Volatility term structure** (Ch. 20): Delta-neutral positions held across different expirations have different breakeven vols
