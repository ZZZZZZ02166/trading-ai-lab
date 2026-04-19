---
card_id: 274e5606-27d4-4c15-b1f0-063db5526021
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: principle
page_ref: "pp. 48-48"
page_start: 48
page_end: 48
tags:
  - volatility-estimator
  - best-practice
  - diagnosis
  - high-frequency
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Use Multiple Vol Estimators and Compare — No Single Best

**Type:** principle
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 48-48

## Summary

No single historical volatility estimator dominates all market conditions. The correct approach: calculate all five (CC, Parkinson, GK, RS, YZ) and compare. Diagnostic use: if Parkinson >> CC, intraday moves dominate. If CC >> Parkinson, overnight gaps dominate (important around earnings/events). If YZ >> GK, overnight gaps contribute significantly. Sinclair also recommends high-frequency data when available — it provides the most accurate realized vol estimates with negligible microstructure noise above 5-minute bars.

## Tags

#volatility-estimator #best-practice #diagnosis #high-frequency

## Notes

<!-- Personal notes here -->
