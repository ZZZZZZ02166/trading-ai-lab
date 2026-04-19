---
card_id: 300ea189-9c21-475c-89c5-805c3cc9facb
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 186-186"
page_start: 186
page_end: 186
tags:
  - hurst-exponent
  - performance-persistence
  - statistics
  - edge
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Hurst Exponent: Testing Persistence of Performance

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 186-186

## Summary

The Hurst exponent H measures whether a time series is trending (H > 0.5), random (H = 0.5), or mean-reverting (H < 0.5). Applied to strategy P/L series: H > 0.5: returns exhibit momentum — past good months predict future good months (strategy has true persistence, not luck); H = 0.5: returns are random — no predictability; H < 0.5: returns mean-revert — good months followed by bad (overfitting/mean-reversion). For a volatility selling strategy with genuine edge, H should be > 0.5. Estimate using rescaled range analysis: H = log(R/S) / log(N).

## Tags

#hurst-exponent #performance-persistence #statistics #edge

## Notes

<!-- Personal notes here -->
