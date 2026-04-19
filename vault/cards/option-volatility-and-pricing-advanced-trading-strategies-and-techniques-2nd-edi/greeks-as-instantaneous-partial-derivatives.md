---
card_id: 3824b0c5-444c-4c82-a14d-29fb885f23eb
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: concept
page_ref: "pp. 800-807"
page_start: 800
page_end: 807
tags:
  - greeks
  - partial-derivatives
  - delta
  - gamma
  - instantaneous
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Greeks as Instantaneous Partial Derivatives

**Type:** concept
**Source:** Option Volatility and Pricing — pp. 800-807

## Summary

The five standard Greeks are all partial derivatives of the option pricing function: delta = ∂V/∂S, gamma = ∂²V/∂S², theta = ∂V/∂t (time), vega = ∂V/∂σ, rho = ∂V/∂r. Each measures sensitivity while holding other variables constant. As partial derivatives, they are valid only for infinitesimally small changes — approximations for any finite move. For large moves: use delta + ½ × gamma × ΔS² for better accuracy. Greeks must be recalculated continuously as market conditions change — a snapshot from the morning is not valid after a significant price move.

## Tags

#greeks #partial-derivatives #delta #gamma #instantaneous

## Notes

<!-- Personal notes here -->
