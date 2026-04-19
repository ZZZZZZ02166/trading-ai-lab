---
card_id: 2d1540c5-202b-4d90-a194-c360ebcbffd6
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 2527-2538"
page_start: 2527
page_end: 2538
tags:
  - black-scholes
  - delta
  - N(d1)
  - probability
  - risk-neutral
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Black-Scholes Delta: N(d1) and Normal Distribution

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 2527-2538

## Summary

In Black-Scholes, call delta = N(d₁) = cumulative standard normal at d₁. For an option with 1% vol (1/100 of a standard deviation), the peak of the standard normal is ≈ 0.399/100 = 0.00399 per delta unit. Delta ranges 0→1 for calls and 0→−1 for puts. ATM call delta ≈ 0.50 (not exactly, due to forward price adjustment). For European options: the call delta also approximates the risk-neutral probability of expiring ITM. This interpretation is useful: a 30-delta option has approximately a 30% probability of expiring in-the-money under the risk-neutral measure.

## Tags

#black-scholes #delta #N(d1) #probability #risk-neutral

## Notes

<!-- Personal notes here -->
