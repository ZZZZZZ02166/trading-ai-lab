---
card_id: 6e6dbcd9-5029-46b6-b951-abbed6909d1c
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 1099-1110"
page_start: 1099
page_end: 1110
tags:
  - theta
  - volatility
  - atm
  - proportionality
  - approximation
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Theta Proportional to Volatility for ATM Options

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 1099-1110

## Summary

For ATM options, theta is essentially directly proportional to volatility. If IV doubles, theta approximately doubles. This makes intuitive sense: higher vol means more time premium, which decays faster in absolute dollar terms. The graph of ATM option value vs. time is approximately linear, with theta being the slope. For an ATM option with 26% IV, the daily theta is approximately proportional to vol/√252 × underlying price × delta. This proportionality is useful for quickly estimating theta changes when IV changes — if IV rises 10%, expect ATM theta to increase ~10%.

## Tags

#theta #volatility #atm #proportionality #approximation

## Notes

<!-- Personal notes here -->
