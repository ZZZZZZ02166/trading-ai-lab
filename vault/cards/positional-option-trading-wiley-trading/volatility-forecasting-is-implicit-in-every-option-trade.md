---
card_id: 774d6552-4348-418c-b8d6-28d7d81d5ef3
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 56–57"
page_start: 56
page_end: 57
tags:
  - volatility_forecasting
  - garch
  - ewma
  - vix
  - realized_volatility
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Volatility forecasting is implicit in every option trade

**Type:** concept
**Source:** Positional Option Trading (Wiley Trading) — pp. 56–57

## Summary

Every option trade is an implicit volatility forecast. Even the choice to sell options 'because vol is high' is a forecast that realized vol will be lower than implied. The relevant question is not whether to forecast but how. Methods: historical rolling vol (simple but suffers from ghost effects), EWMA (weights recent data more heavily, adapts faster), GARCH(1,1) (captures vol clustering and mean reversion), VIX (market-implied, best for SPX). Empirical finding: all methods perform similarly — differences of ~0.5 vol points in average error. Model selection matters less than having a systematic process.

## Tags

#volatility_forecasting #garch #ewma #vix #realized_volatility

## Notes

<!-- Personal notes here -->
