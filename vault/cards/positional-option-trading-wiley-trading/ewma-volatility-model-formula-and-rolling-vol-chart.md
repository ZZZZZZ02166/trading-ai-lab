---
card_id: cbc0c6ff-c93f-4680-b100-8e16e67bec1f
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 61–63"
page_start: 61
page_end: 63
tags:
  - ewma
  - volatility_forecasting
  - garch
  - vol_clustering
  - realized_volatility
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# EWMA volatility model: formula and rolling vol chart

**Type:** mechanism
**Source:** Positional Option Trading (Wiley Trading) — pp. 61–63

## Summary

Figure 3.1: Maximus Inc. 30-day rolling vol shows clustering and mean reversion — the motivation for EWMA. Equation 3.2: σ²_t = λ·σ²_{t-1} + (1−λ)·r²_{t-1}. λ (decay factor) typically 0.9–0.95. λ=0.94 is the RiskMetrics standard. EWMA weights recent returns more heavily than older ones, adapting faster to regime changes than equal-weighted rolling windows. Avoids the 'ghost effect' where a large return suddenly drops out of the lookback window and causes an artificial vol spike.

## Tags

#ewma #volatility_forecasting #garch #vol_clustering #realized_volatility

## Notes

<!-- Personal notes here -->
