---
card_id: 1563f02b-a236-4317-8c1e-09dcb5d8cdaa
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: definition
page_ref: "pp. 38-38"
page_start: 38
page_end: 38
tags:
  - yang-zhang
  - volatility-estimator
  - overnight-gap
  - efficiency
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Yang-Zhang Estimator: Best General-Purpose Estimator

**Type:** definition
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 38-38

## Summary

Yang-Zhang (2000): σ²_YZ = σ²_overnight + k × σ²_open-to-close + (1−k) × σ²_RS where k = 0.34 / (1.34 + (n+1)/(n-1)). Combines overnight return variance + intraday (Rogers-Satchell) variance. Handles both drift and overnight gaps. 14× more efficient than CC. This is the most comprehensive of the standard five estimators. Weakness: requires full OHLC data including reliable open prices. Sinclair recommends it as the primary estimator for daily data.

## Tags

#yang-zhang #volatility-estimator #overnight-gap #efficiency

## Notes

<!-- Personal notes here -->
