# Cheat Sheet: Option Market Making
*Allen Jan Baird — Fast Review*

---

## Core Philosophy

- **Income from the spread, not from direction.** Pure market making = risk-neutral profit from bid/offer edge
- **Hedge when you should, not when it's convenient.** Every delayed hedge is a directional bet
- **Know all six Greek risks.** Delta alone is insufficient; kappa can dominate everything

---

## The Six Greeks (Quick Reference)

| Greek | Symbol | Measures | Long option sign | Short option sign |
|-------|--------|----------|-----------------|------------------|
| Delta | Δ | Price sensitivity | + (call), − (put) | − (call), + (put) |
| Gamma | Γ | Delta change rate | + | − |
| Theta | Θ | Daily time decay | − | + |
| Kappa/Vega | K | IV sensitivity | + | − |
| Rho | ρ | Interest rate sensitivity | +/− (small for futures) | |
| Skew | — | IV differential across strikes | context-dependent | |

**ATM deltas:** Call ≈ +0.50, Put ≈ −0.50
**Theta and gamma have opposite signs for any position — you cannot have both positive gamma AND positive theta.**

---

## Critical Rules

1. **Translate all Greeks to dollars.** Gamma of 0.10 × $500/point contract × 10 options = $500 gamma risk — not 10 cents.

2. **Kappa is often your biggest risk.** A 10-point IV move can create $800+ P&L swings — larger than delta or theta over the same period.

3. **Volatility scales with √time.** Daily vol = Annual vol / √250. Do not scale linearly.

4. **Implied vol ≠ future realized vol.** IV is the market's estimate; historical vol is backward-looking. Neither reliably predicts future vol.

5. **Real returns have fat tails.** BSM underprices deep OTM options. Price wings with a fat-tail premium.

6. **Track two P&L accounts.** Carryover P&L (existing positions) vs daily trading P&L (new trades). Only positive daily trading P&L = genuine edge.

---

## Position Types by Risk Modality

| Modality | Examples | Gamma at ATM | Theta at ATM |
|----------|----------|-------------|-------------|
| Unimodal (+) | Long straddle, long call | + | − |
| Unimodal (−) | Short straddle, short call | − | + |
| Bimodal | Bull spread, bear spread, fence | +/− | |
| Trimodal | Long butterfly, condor | − near center | + near center |
| Near-zero | Conversion, reversal, box | ≈0 | ≈0 |

---

## ⚠️ Warnings

- **Do NOT delay delta hedges.** Any pause to "let the market come to you" is speculation. Hedge immediately after every non-spread option trade.
- **Do NOT use stale board prices for delta.** Always hedge at actual current traded futures prices.
- **Do NOT overtrade.** Trade only in quantities you can fully monitor and hedge.
- **Do NOT let kappa drift uncorrected.** Adjust spread ratios to stay net kappa-neutral.
- **Do NOT sell naked OTM wings without hedging.** BSM says they're safe; fat-tail reality disagrees.
- **Do NOT assume complex carryover positions are well-behaved near expiration.** Stress-test across all strikes.

---

## BSM Formula (Fischer Black futures version)

- **Call:** C = e^(−rt) × [X × N(d1) − K × N(d2)]
- **Put:** P = e^(−rt) × [K × N(−d2) − X × N(−d1)]
- **d1** = [ln(X/K) + (S²/2)t] / (S√t)
- **d2** = d1 − S√t
- X = futures price, K = strike, S = volatility, t = time (annual), r = rate

**Volatility scaling:** SDP = P × V / √PY  *(standard deviation in points over period PY)*

---

## Vol Skew Quick Reference

- **Positive skew (most common):** Wings (OTM puts + calls) > ATM IV
- **Flat skew:** All strikes at same IV
- **Negative skew (rare):** Wings < ATM IV
- **High positive skew → wings expensive → prefer butterflies/condors over ratio spreads**
- **Flat skew → wings cheap → prefer long ratio spreads**

---

## The Four Cardinal Sins of Market Making

1. Failure to hedge delta immediately
2. Hedging at wrong (stale) prices
3. Overtrading beyond your management capacity
4. Allowing net kappa/vega imbalance to accumulate
