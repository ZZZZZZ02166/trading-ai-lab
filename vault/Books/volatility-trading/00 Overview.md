# Volatility Trading — Overview
*Euan Sinclair, Wiley (2013), 2nd Edition*

---

## What This Book Is

Sinclair's *Volatility Trading* is the most comprehensive practitioner-level treatment of the complete workflow for trading implied vs realized volatility. Where Natenberg (*Option Volatility and Pricing*) teaches the theory of options and Greeks, and Cottle (*Trading Option Greeks*) focuses on position management, Sinclair's book focuses on the quantitative process: how to measure volatility, forecast it, size a position, hedge it efficiently, and evaluate whether the strategy actually worked.

The book is written by a physicist turned options trader and shows: every claim is empirically grounded, formulas are derived not just stated, and the discussion of what can go wrong is as thorough as the discussion of what should go right.

---

## Core Themes

1. **BSM as a language, not the truth** — the model is a communication framework, not a price oracle
2. **Volatility measurement requires multiple estimators** — no single estimator is best; use all five and compare
3. **The variance premium is real but not free** — IV systematically exceeds realized vol for equity indices, but the premium varies and can be negative for months
4. **Hedging is a cost-benefit trade-off** — continuous rehedging is impossible; utility-based bands (Zakamouline) are the right framework
5. **Position sizing is as important as edge** — Kelly criterion, fractional Kelly, and goal-based (Browne) sizing
6. **Psychology destroys more edges than bad models** — 10 identified cognitive biases with practical counters

---

## Book Structure (15 Chapters)

| Ch | Topic | Key Contribution |
|----|-------|-----------------|
| 1 | Option Pricing | BSM as language; Taylor expansion derivation; drift irrelevance |
| 2 | Volatility Measurement | Five estimators + barrier method; intraday seasonality |
| 3 | Stylized Facts | Clustering, fat tails (kurtosis table), leverage effect, vol-volume |
| 4 | Forecasting | EWMA, GARCH(1,1), volatility cones, variance premium |
| 5 | IV Dynamics | Vol surface, sticky strike/delta, Corrado-Su smile model |
| 6 | Hedging | HN, Whalley-Wilmott, Zakamouline bands; market impact |
| 7 | P/L Distribution | Path dependency; dispersion formula; hedging at realized vs implied |
| 8 | Money Management | Kelly, fractional Kelly, Browne goal-reaching, optimal entry |
| 9 | Trade Evaluation | Sharpe, Sortino, Omega, K ratio, goal-setting |
| 10 | Psychology | 10 biases; practical debiasing rules |
| 11 | Variance Premium | QQQ empirical results; straddle Sharpe 1.37; individual vs index |
| 12 | The VIX | Model-free calculation; VIX futures contango; VXX decay |
| 13 | Leveraged ETFs | Vol decay formula; compound option structure |
| 14 | Trade Lifecycle | Full AAPL example: estimation → entry → hedging → exit |
| 15 | Conclusion | Consistent process as competitive advantage |

---

## Key Formulas at a Glance

| Formula | Description |
|---------|-------------|
| σ²_t = ω + αr²_{t-1} + βσ²_{t-1} | GARCH(1,1) |
| P/L ≈ Vega × (σ_implied − σ_realized) | Central vol trading result |
| σ_residual = σ × √(π/2N) | Discrete hedging dispersion |
| f* = p/L − q/W | Kelly criterion (general) |
| S_max = 0.75σ | Optimal entry for mean-reverting asset |
| f(s) = k√s | Market impact square root law |
| VIX² = (2/T)Σ[ΔKᵢ/Kᵢ²]e^(rT)Q(Kᵢ) | Model-free variance (VIX formula) |
| dL/L = λdS/S − ½λ(λ−1)σ²dt | Leveraged ETF vol decay |

---

## How This Book Relates to Others in the Vault

| Book | Focus | Relationship |
|------|-------|-------------|
| Option Volatility and Pricing (Natenberg) | Theory, Greeks, intuition | Prerequisite — Sinclair builds on Natenberg's foundations |
| Trading Option Greeks (Cottle) | Position Greeks, trade management | Complementary — Cottle is about managing what Sinclair helps you enter |
| Volatility Trading (Sinclair) | Quantitative process end-to-end | The most complete practitioner workflow book |

---

## Who Should Read This Book

- Options traders wanting to move beyond intuition to quantitative process
- Quants building vol-forecasting models for options books
- Risk managers understanding realized vs implied vol dynamics
- Anyone who has read Natenberg and wants the "how do you actually trade this" answer

---

## Page Reference
- Full text: 298 pages (incl. references, index, appendices)
- Content chapters: pp. 8–262
