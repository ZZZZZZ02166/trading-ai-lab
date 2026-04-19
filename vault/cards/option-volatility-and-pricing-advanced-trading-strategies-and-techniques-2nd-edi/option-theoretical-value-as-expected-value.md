---
card_id: 8494e54a-4e7f-4069-8db0-b46cf7af2d56
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 438-447"
page_start: 438
page_end: 447
tags:
  - theoretical-value
  - expected-value
  - probability
  - pricing-model
  - present-value
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Option Theoretical Value as Expected Value

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 438-447

## Summary

The theoretical value of an option equals the expected value of its payoff at expiration, discounted to the present. If an option can expire worth $0, $2, $12, or $22 with probabilities 40%, 30%, 20%, 10%: E[payoff] = $0.60 + $2.40 + $2.20 = $5.20. The present value accounts for interest: if rates are 12%/year and expiration is 2 months, theoretical value = $5.20 / (1 + 0.12 × 2/12) = $5.10. A pricing model is a formalized, continuous version of this expected-value calculation using a probability distribution for the underlying at expiration. Black-Scholes uses the lognormal distribution.

## Tags

#theoretical-value #expected-value #probability #pricing-model #present-value

## Notes

<!-- Personal notes here -->
