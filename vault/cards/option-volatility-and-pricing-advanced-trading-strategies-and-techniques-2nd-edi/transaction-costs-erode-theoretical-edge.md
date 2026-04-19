---
card_id: 9973bcee-cb0b-4529-b9ee-715b48508b6e
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: caution
page_ref: "pp. 3292-3301"
page_start: 3292
page_end: 3301
tags:
  - transaction-costs
  - black-scholes
  - gamma-scalping
  - caution
  - friction
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Transaction Costs Erode Theoretical Edge

**Type:** caution
**Source:** Option Volatility and Pricing — pp. 3292-3301

## Summary

Black-Scholes assumes zero transaction costs. In practice, every gamma-neutral rebalancing trade incurs commissions and bid-ask spread costs. For high-gamma strategies requiring frequent adjustments, these costs can eliminate or reverse the theoretical edge. The number of rebalancing trades multiplied by cost per trade = total friction cost. Strategies that require 20+ adjustments per week at $2/contract each may pay $40+ per contract in friction alone — exceeding the initial theoretical edge. Retail traders with high per-trade costs must use much larger edges than market makers to achieve profitability net of transaction costs.

## Tags

#transaction-costs #black-scholes #gamma-scalping #caution #friction

## Notes

<!-- Personal notes here -->
