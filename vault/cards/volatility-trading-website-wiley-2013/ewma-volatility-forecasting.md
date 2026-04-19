---
card_id: 1b1b7612-c3d2-4c96-a6c9-673b545ad42f
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 66-66"
page_start: 66
page_end: 66
tags:
  - ewma
  - volatility-forecasting
  - decay-factor
  - igarch
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# EWMA Volatility Forecasting

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 66-66

## Summary

Exponentially Weighted Moving Average forecasts volatility by giving more weight to recent observations: σ²_t = λσ²_{t-1} + (1-λ)r²_{t-1}. λ (decay factor) controls the speed of updating: λ=0.94 (RiskMetrics default) gives half-life of ~12 days (slow adaptation); λ=0.86 gives half-life of ~5 days. Advantage: simple, requires only one parameter. Weakness: EWMA is an IGARCH(1,1) model with no mean reversion — it treats vol shocks as permanent. GARCH(1,1) is strictly better because it includes mean reversion (long-run variance term). Choose λ by minimizing squared forecast error on historical data.

## Tags

#ewma #volatility-forecasting #decay-factor #igarch

## Notes

<!-- Personal notes here -->
