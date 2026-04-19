# Cheat Sheet: Positional Option Trading
*Euan Sinclair — Fast Review*

---

## Core Philosophy

- **The variance premium is the primary edge.** IV almost always exceeds subsequent realized vol.
- **Quantify everything.** Every trade must have a specific, testable forecast behind it.
- **Structure follows edge.** First identify WHY there is edge, then choose the option structure to capture it.
- **Size with Kelly, adjusted for negative skew.** Short-vol returns are negatively skewed — raw Kelly overstates optimal bet size.

---

## Decision Framework

```
1. Does the variance premium exist for this underlying now?
   └─ Check: IV vs realized vol history, VIX term structure shape
2. Is there additional skew premium?
   └─ Check: put vs call IV differential vs historical norms
3. Is there a directional view?
   └─ If yes: use Boness model to find subjective value
   └─ If no: use pure vol structures (straddle/strangle)
4. Size with fractional Kelly (25–50% of estimated Kelly)
```

---

## Key Formulas

**Delta-hedged P/L:**
> Profit = ½Γ·S²·(σ_realized² − σ_implied²)·dt

**GARCH(1,1):**
> σ²_t = ω + α·r²_{t-1} + β·σ²_{t-1} — captures vol clustering + mean reversion

**Boness call price (with drift μ):**
> C = S·exp(μT)·N(d₃) − X·N(d₄)
> d₃,d₄ use μ instead of r

**True ITM probability:**
> P(ITM) = N(d₄) — use this for speculative positions, not N(d₂)

**Kelly fraction:**
> f* ≈ μ/σ² (normal) or μ/(μ²+σ²) + skew correction (non-normal)

**Kelly growth rate:**
> GR(f) = (f − f²/2)·μ²/σ² — maximized at f=1, zero at f=2

---

## Fractional Kelly Quick Reference

| Max Over-Betting Probability | Kelly Scale Factor |
|------------------------------|-------------------|
| 10% (skew-adjusted) | 0.20× Kelly |
| 20% (skew-adjusted) | 0.48× Kelly |
| **Practical default** | **25–50% of Kelly** |

---

## Structure Selection Guide

| Your View | Preferred Structure |
|-----------|---------------------|
| IV > realized vol, no direction | Short straddle + delta hedge |
| IV > realized vol, narrow range | Short strangle |
| IV > realized, want limited risk | Short butterfly or condor |
| Short-dated IV spike | Calendar (sell front, buy back) |
| Bullish + variance premium | Covered call (ATM) |
| Bullish + skew steep | Risk reversal (long call, short put) |
| Bearish + skew premium | Buy put spread (sell OTM put, buy far OTM put) |
| Earnings event | Short straddle pre-earnings; delta-hedge post |

---

## The 11 Tradeable Effects (Confidence Levels)

**Level 3 (Highest confidence):**
- Variance premium — sell IV broadly
- Earnings IV overpricing — sell straddles/strangles before earnings
- VIX term structure contango — sell front-month VIX futures

**Level 2:**
- Post-earnings announcement drift (PEAD) — directional after surprise
- Earnings-induced reversals — fade large gaps
- FOMC vol overpricing

---

## ⚠️ Critical Warnings

- **Discipline without edge = faster losses.** Good risk management cannot rescue negative-edge strategies.
- **Don't confuse risk premium with behavioral inefficiency.** Premia persist; inefficiencies erode.
- **Full Kelly is dangerous.** Estimation uncertainty means raw Kelly estimates almost always imply over-betting.
- **Stops change distribution shape.** They don't just prevent losses — they eliminate recovering winners.
- **Don't sell volatility after a spike without reducing size.** The premium is highest when the risk of further spikes is also highest.
- **Leverage + mean reversion = potential death spiral.** LTCM / XIV examples show how good strategies with excess leverage can fail mechanically.
- **Meta risks kill portfolios too.** Counterparty failure, fraud, regulatory changes. Use multiple brokers, regulated exchanges.

---

## Variance Premium Summary Statistics (SPX)

| VIX Quintile | Mean Premium | Assessment |
|-------------|-------------|------------|
| < 13% | Low | Poor risk/reward |
| 13–16% | Medium | Good |
| 16–19% | Medium-High | Best |
| 19–24% | High | Acceptable (reduce size) |
| > 24% | Very High | High risk — reduce further |

---

## EMH Checklist: Is Your Edge Real?

1. Is there strong statistical evidence across multiple markets and time periods?
2. Is the mechanism specific and predictive (not just "behavioral bias")?
3. Has it survived after controlling for known risk factors?
4. Is it a risk premium (persistent) or an inefficiency (temporary)?
5. Has it been tested with White Reality Check or similar for data mining?
