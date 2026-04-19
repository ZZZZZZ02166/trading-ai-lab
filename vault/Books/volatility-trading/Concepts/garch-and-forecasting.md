# GARCH and Volatility Forecasting
*Source: Volatility Trading — Ch. 4*

---

## Definition
GARCH(1,1) is the standard model for forecasting time-varying volatility, capturing both clustering (persistence) and mean reversion.

---

## Model
σ²_t = ω + αr²_{t-1} + βσ²_{t-1}

| Parameter | Role |
|-----------|------|
| ω | Long-run variance floor |
| α | Shock reaction (ARCH) |
| β | Persistence (GARCH) |

Long-run variance: V_L = ω/(1−α−β)

Term structure: E[σ²_{t+T}] = V_L + (σ²_t − V_L)(α+β)^T

---

## MSFT Example (May 2007)
ω=0.00000505, α=0.053, β=0.884 → V_L = 11%, current vol = 16% → decays exponentially to 11% over ~120 days.

---

## EWMA Comparison
EWMA = IGARCH with no mean reversion (ω=0). GARCH strictly dominates because it includes the mean-reversion floor.

---

## Practical Use
1. Fit to 2+ years daily returns
2. Generate term structure forecast
3. Compare to market ATM term structure
4. Implied steeper than GARCH → front-month rich vs back → calendar spread opportunity

---

## Common Mistakes
- Overfitting (out-of-sample performance degrades)
- Not re-fitting after regime changes
- Using GARCH in isolation

## Page Reference
Ch. 4, pp. 66–83
