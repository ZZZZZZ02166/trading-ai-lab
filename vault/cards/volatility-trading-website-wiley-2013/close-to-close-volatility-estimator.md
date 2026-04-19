---
card_id: 77cdeaf3-8d7a-4719-8f50-71df1f234992
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: definition
page_ref: "pp. 33-33"
page_start: 33
page_end: 33
tags:
  - close-to-close
  - volatility-estimator
  - bias-correction
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Close-to-Close Volatility Estimator

**Type:** definition
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 33-33

## Summary

The simplest historical volatility estimator: σ² = [1/(n-1)] Σ(rᵢ)² where rᵢ = ln(Cᵢ/Cᵢ₋₁). Only uses closing prices. Easy to implement and verify. Weaknesses: ignores intraday price action; if price moves intraday but closes unchanged, the estimator records zero variance for that day. Misses 20–40% of total daily variance. Bias correction: multiply by 1/c₄ where c₄ depends on sample size N (N=10: c₄=0.973, N=20: c₄=0.988, N=100: c₄=0.998). Best for: liquid markets where only closing prices are available.

## Tags

#close-to-close #volatility-estimator #bias-correction

## Notes

<!-- Personal notes here -->
