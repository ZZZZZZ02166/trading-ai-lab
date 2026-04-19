---
card_id: e03a1c05-f039-461b-b540-e9e57585a0e0
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 233–234"
page_start: 233
page_end: 234
tags:
  - stochastic_volatility
  - fat_tails
  - volatility_regimes
  - kurtosis
  - bsm_limitations
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Non-Constant Volatility: Stochastic Vol Models vs Mixing Normals

**Type:** concept
**Source:** Positional Option Trading (Wiley Trading) — pp. 233–234

## Summary

Real volatility is not constant — it clusters in regimes and shows mean reversion. Two modeling approaches: (1) Stochastic vol models (Heston, SABR) explicitly model vol as a random process, reproducing the implied vol smile. (2) Mixture-of-normals: returns drawn from multiple normal distributions with different volatilities produces fat tails and kurtosis. Key formula: Kurtosis = 3·(p₁σ₁² + p₂σ₂²)²/(p₁σ₁² + p₂σ₂²)² for a two-regime mixture. S&P 500 vol regularly switches between low-vol (10–15%) and high-vol (30–80%) regimes, which mechanically produces the observed leptokurtosis in stock returns.

## Tags

#stochastic_volatility #fat_tails #volatility_regimes #kurtosis #bsm_limitations

## Notes

<!-- Personal notes here -->
