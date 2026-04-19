# Chapter 2 — Volatility Measurement
*Volatility Trading — Euan Sinclair, pp. 33–53*

---

## Summary
Five historical volatility estimators. No single estimator is best — use all five and treat differences as diagnostic signals.

---

## Five Estimators

| Estimator | Data | Efficiency vs CC | Notes |
|-----------|------|-----------------|-------|
| Close-to-Close | C | 1× | Misses intraday |
| Parkinson | H,L | 4.9× | Misses overnight gaps |
| Garman-Klass | O,H,L,C | 7.4× | Zero-drift assumption |
| Rogers-Satchell | O,H,L,C | ~5× | Drift-independent |
| Yang-Zhang | O,H,L,C+overnight | 14× | Recommended primary |

Yang-Zhang: σ²_YZ = σ²_overnight + k×σ²_RS, k = 0.34/(1.34 + (n+1)/(n-1))

**Bias correction c₄(N)**: N=10: 0.973; N=20: 0.988; N=100: 0.998. Apply: σ_unbiased = σ_sample/c₄

## Barrier / First Exit Time Method
Efficiency: std dev of estimates 0.028 vs 0.048 for CC (1.7× better). Requires tick data.

## Intraday Seasonality (Figures 2.8/2.9)
U-shaped: highest at open and close, lowest midday. Accounts for 20-40% of daily variance.

## Diagnostic Usage
- Parkinson >> CC → intraday dominates
- CC >> Parkinson → overnight gaps dominate (earnings/events)
- Use all five; compare before trading

## Key Lessons
1. Never use only CC in production
2. Yang-Zhang is the general-purpose recommendation
3. High-frequency data (5-min bars) > OHLC when available
