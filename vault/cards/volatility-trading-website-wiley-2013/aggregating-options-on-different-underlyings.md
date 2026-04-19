---
card_id: b8026064-bfe8-4d41-9e13-b2857c059e53
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 125-125"
page_start: 125
page_end: 125
tags:
  - aggregation
  - portfolio
  - vega
  - delta
  - correlation
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Aggregating Options on Different Underlyings

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 125-125

## Summary

When a portfolio contains options on multiple underlyings, aggregate the vega exposure using a correlation matrix. The portfolio vega in 'generic' vol units: V_portfolio = Σ(νᵢ × Sᵢ × λᵢ), where λᵢ is the mapping weight from asset vol to a common volatility factor. For stocks vs index: use beta as the mapping. For cross-asset: use PCA factor loadings (Derman, Kamal, Kani 1997). Delta aggregation: DTS = Σ(Δᵢ × Sᵢ × λᵢ) — the dollar delta sum. Practical purpose: allows risk managers to see net exposure across a multi-product book in a single number, not just stock-by-stock.

## Tags

#aggregation #portfolio #vega #delta #correlation

## Notes

<!-- Personal notes here -->
