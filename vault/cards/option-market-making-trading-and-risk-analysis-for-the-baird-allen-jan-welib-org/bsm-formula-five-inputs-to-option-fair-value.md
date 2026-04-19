---
card_id: 4dda20fa-8101-4b4d-a617-4873fe282d6c
doc_id: ddc2a298cd88
book_title: "Option Market Making"
author: "Allen Jan Baird"
card_type: mechanism
page_ref: "pp. 28–28"
page_start: 28
page_end: 28
tags:
  - bsm_model
  - options_pricing
  - black_formula
  - volatility
  - fair_value
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# BSM Formula: Five Inputs to Option Fair Value

**Type:** mechanism
**Source:** Option Market Making — pp. 28–28

## Summary

The Fischer Black futures options model requires five inputs: (1) current futures price X, (2) strike price K, (3) time to expiration t (annualized), (4) risk-free interest rate r, (5) volatility S (standard deviation of log price change). The call fair value formula is C = e^(-rt)[XN(d1) − KN(d2)], where d1 = [ln(X/K) + (S²/2)t] / (S√t) and d2 = d1 − S√t. N(d) is the cumulative normal probability integral.

## Tags

#bsm_model #options_pricing #black_formula #volatility #fair_value

## Notes

<!-- Personal notes here -->
