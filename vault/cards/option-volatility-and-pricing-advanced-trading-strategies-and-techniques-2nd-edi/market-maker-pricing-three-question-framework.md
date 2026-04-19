---
card_id: ebb50e07-6795-4437-b8c3-6cd1690ddc32
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 3014-3022"
page_start: 3014
page_end: 3022
tags:
  - market-making
  - pricing-framework
  - theoretical-value
  - inventory
  - edge
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Market Maker Pricing: Three-Question Framework

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 3014-3022

## Summary

A market maker prices options using three sequential questions: (1) What does the marketplace think the option is worth? (current market mid-price → market IV); (2) What do I think it's worth? (my theoretical value from my vol forecast); (3) What positions am I carrying? (inventory). If I think value > market: I want to buy → bid below my theoretical value to capture edge. If I already hold too many long options: shade the bid lower to avoid adding more. These three questions determine both the level of bid/ask and the width of the spread. Market makers are not predicting direction — they are capturing edge in a vol view vs. market IV.

## Tags

#market-making #pricing-framework #theoretical-value #inventory #edge

## Notes

<!-- Personal notes here -->
