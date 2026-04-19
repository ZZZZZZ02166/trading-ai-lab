---
card_id: 6b829831-5c5c-4763-b2f5-3e99874dd969
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: caution
page_ref: "pp. 44–45"
page_start: 44
page_end: 45
tags:
  - data_mining
  - backtesting
  - statistical_testing
  - edge
  - overfitting
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# White's Reality Check: Testing for Data Mining

**Type:** caution
**Source:** Positional Option Trading (Wiley Trading) — pp. 44–45

## Summary

The White Reality Check (WRC) and related tests (Hansen's SPA) detect whether the best strategy in a large historical search outperforms purely by chance. The algorithm: (1) collect returns of all strategies tested; (2) use bootstrap resampling to build a null distribution of best-strategy returns; (3) test if observed best performance exceeds the null. This is the only rigorous way to validate a strategy discovered through large-scale backtesting. Without such a test, apparent 'edges' from parameter searches are likely overfitting artifacts.

## Tags

#data_mining #backtesting #statistical_testing #edge #overfitting

## Notes

<!-- Personal notes here -->
