---
card_id: d77b93c7-f464-4b72-beb8-41a7656641c5
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 60–62"
page_start: 60
page_end: 62
tags:
  - garch
  - volatility_forecasting
  - volatility_clustering
  - mean_reversion
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# GARCH(1,1): Volatility Mean-Reversion with Recent-Data Weighting

**Type:** mechanism
**Source:** Positional Option Trading (Wiley Trading) — pp. 60–62

## Summary

GARCH(1,1) models conditional variance as: σ²_t = ω + α·r²_{t-1} + β·σ²_{t-1}, where α+β+γ=1 and γV is the long-run variance target. It captures: (1) volatility clustering — high vol tends to follow high vol; (2) mean reversion toward long-run level γV; (3) heavier weight on recent squared returns. The GARCH forecast decays toward long-run vol over time, producing a term structure of expected vol that flattens with horizon.

## Tags

#garch #volatility_forecasting #volatility_clustering #mean_reversion

## Notes

<!-- Personal notes here -->
