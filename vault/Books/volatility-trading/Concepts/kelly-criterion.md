# Kelly Criterion
*Source: Volatility Trading — Ch. 8*

---

## Definition
Position sizing formula that maximizes expected geometric growth rate of wealth. Specifies optimal fraction f* of bankroll to bet per trade.

---

## Formula
Binary bet (win prob p, loss prob q=1-p, payoff b): **f* = (pb−q)/b = p − q/b**

Continuous: maximize E[ln(1 + f×G)] over f.

General: f* = edge/odds

---

## Key Property: Geometric Mean
Kelly maximizes geometric mean growth, not arithmetic mean. Above f*, arithmetic mean grows but geometric mean shrinks → eventual ruin.

---

## Good Points
1. Maximizes long-run log wealth
2. Zero risk of ruin
3. Asymptotically optimal

## Bad Points
1. Requires true p (never known exactly)
2. Severe drawdowns at full Kelly
3. Non-ergodic path (loss+win < starting)
4. Constant position size recalculation

---

## Practical Default: Half-Kelly
f*/2: growth = 75% of Kelly, variance = 25%. Recommended for vol traders.

## For Vol Trading
f* ≈ (IV − forecast realized vol) / expected loss per unit vega if wrong.

## Page Reference
Ch. 8, pp. 144–162
