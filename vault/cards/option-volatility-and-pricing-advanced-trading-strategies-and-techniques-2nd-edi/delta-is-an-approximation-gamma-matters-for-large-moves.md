---
card_id: 1a32d011-0958-4130-bbfa-6a98cc090ebc
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: caution
page_ref: "pp. 848-854"
page_start: 848
page_end: 854
tags:
  - delta
  - gamma
  - approximation
  - large-moves
  - caution
  - p&l-estimation
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Delta Is an Approximation: Gamma Matters for Large Moves

**Type:** caution
**Source:** Option Volatility and Pricing — pp. 848-854

## Summary

Delta gives the rate of change of option value for a small move. For large moves, delta-only estimates are increasingly inaccurate because delta itself changes (gamma). Better approximation: ΔV ≈ delta × ΔS + ½ × gamma × ΔS². For a short-gamma position, this second term is negative — losses are larger than delta alone predicts. Example: short a straddle, delta = 0 but gamma = −20. A 5-point move causes delta-estimated loss of 0, but actual loss ≈ ½ × 20 × 25 = 250 points. Always consider gamma when estimating P/L for large underlying moves.

## Tags

#delta #gamma #approximation #large-moves #caution #p&l-estimation

## Notes

<!-- Personal notes here -->
