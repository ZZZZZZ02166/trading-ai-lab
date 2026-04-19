---
card_id: 13e59419-4f98-4363-86ab-bfd7d00f9121
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: caution
page_ref: "pp. 2550-2554"
page_start: 2550
page_end: 2554
tags:
  - vega
  - time
  - leaps
  - forward-price
  - caution
  - assumption-violation
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Vega Decreases with Time for Some Stock Options

**Type:** caution
**Source:** Option Volatility and Pricing — pp. 2550-2554

## Summary

Increasing time to expiration raises vega for most options, but not all. For stock options, the forward price = S × e^(rT). As time increases, the forward price rises (positive interest rates), which can move the option away from ATM. Since ATM options have maximum vega, becoming less ATM reduces vega. A deep ITM stock call may have lower vega for longer expiries than shorter ones — counterintuitive. This matters for: LEAPS pricing, long-dated collar analysis, and any strategy where the vega assumption is 'longer = higher vega.' Always verify using a pricing model rather than assuming.

## Tags

#vega #time #leaps #forward-price #caution #assumption-violation

## Notes

<!-- Personal notes here -->
