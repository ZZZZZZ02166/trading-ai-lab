---
card_id: a6dd2cb3-b350-4e74-8cd0-839db4b3bc7a
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 61–63"
page_start: 61
page_end: 63
tags:
  - garch
  - volatility_forecasting
  - vol_clustering
  - mean_reversion
  - vol_term_structure
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# GARCH(1,1): captures vol clustering and mean reversion

**Type:** mechanism
**Source:** Positional Option Trading (Wiley Trading) — pp. 61–63

## Summary

GARCH(1,1): σ²_t = ω + α·r²_{t-1} + β·σ²_{t-1}. α captures vol clustering (high vol follows high vol — today's large return increases tomorrow's vol). β captures persistence (yesterday's vol forecast influences today). ω/(1−α−β) = long-run unconditional variance. Figure 3.2: GARCH term structure of forecast vol for SPY — both GARCH(1,1) (solid) and GJR-GARCH (dashed) start at ~20% and decay to ~10% over 120 days. At long horizons, reversion to the long-run mean dominates — forecasting mean reversion is the primary contribution of GARCH for long-horizon estimates.

## Tags

#garch #volatility_forecasting #vol_clustering #mean_reversion #vol_term_structure

## Notes

<!-- Personal notes here -->
