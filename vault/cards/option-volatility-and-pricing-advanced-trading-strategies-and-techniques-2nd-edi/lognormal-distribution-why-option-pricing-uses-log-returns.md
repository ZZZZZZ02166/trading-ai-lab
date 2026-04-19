---
card_id: e8b4edb7-e91f-48ff-8db4-4ce706fac284
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: concept
page_ref: "pp. 682-692"
page_start: 682
page_end: 692
tags:
  - lognormal-distribution
  - log-returns
  - black-scholes
  - probability
  - volatility
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Lognormal Distribution: Why Option Pricing Uses Log Returns

**Type:** concept
**Source:** Option Volatility and Pricing — pp. 682-692

## Summary

Stock prices are bounded below by zero but have unlimited upside, creating asymmetric (lognormal) price distributions. Logarithmic returns ln(P_t/P_{t-1}) are symmetrically normally distributed even though price levels are lognormally distributed. Black-Scholes exploits this: volatility = annualized standard deviation of log returns; future prices are lognormally distributed around the forward price. Consequences: (1) the probability of any upward move is calculated using the lognormal distribution, not the normal; (2) the mean of the lognormal distribution exceeds the current forward price (Jensen's inequality); (3) options on high-price stocks have higher dollar vega than equivalent options on low-price stocks.

## Tags

#lognormal-distribution #log-returns #black-scholes #probability #volatility

## Notes

<!-- Personal notes here -->
