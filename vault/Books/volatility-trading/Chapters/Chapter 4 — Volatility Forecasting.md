# Chapter 4 — Volatility Forecasting
*Volatility Trading — Euan Sinclair, pp. 66–83*

---

## Summary
EWMA, GARCH(1,1), volatility cones. Introduces the variance premium as the theoretical source of edge in option selling.

---

## EWMA
σ²_t = λσ²_{t-1} + (1-λ)r²_{t-1}

λ=0.94 (RiskMetrics): half-life ~12 days. No mean reversion — GARCH strictly dominates.

## GARCH(1,1)
σ²_t = ω + αr²_{t-1} + βσ²_{t-1}

| Parameter | Role |
|-----------|------|
| ω | Long-run variance floor |
| α | Reaction to recent shocks |
| β | Persistence of past variance |

Long-run variance: V_L = ω/(1−α−β)
Term structure: E[σ²_{t+T}] = V_L + (σ²_t − V_L)(α+β)^T

**MSFT example** (May 2007): ω=0.00000505, α=0.053, β=0.884 → long-run vol 11%, current 16%, decays over ~120 days (Figure 4.2).

Compare GARCH term structure vs market implied → calendar spread opportunities.

## Volatility Cone (Figure 4.3)
Plot max/median/mean/min of rolling realized vol for each horizon.

**MSFT Table 4.1**: 30-day (max 0.843, median 0.317, min 0.058); 60-day (median 0.287); 240-day (median 0.170).

If current ATM IV > historical max cone → historically expensive.

## Variance Premium
IV exceeds subsequent realized vol by ~30% on average for equity indices. Necessary but not sufficient for selling vol — premium varies and can be negative for months.

## Forecasting Failure Modes
- Lookback bias in GARCH parameters
- Regime shifts: calm-market model underestimates crisis vol
- Structural breaks: permanent vol changes

**Best practice**: blend GARCH + cone + implied vol + fundamental forecast
