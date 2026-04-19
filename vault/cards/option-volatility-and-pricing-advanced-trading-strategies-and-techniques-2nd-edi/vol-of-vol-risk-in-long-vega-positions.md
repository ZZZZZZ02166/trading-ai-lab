---
card_id: 1fc5ba76-c035-4d01-9c1d-506d77f547fe
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: volatility_insight
page_ref: "pp. 4017-4024"
page_start: 4017
page_end: 4024
tags:
  - vol-of-vol
  - vega
  - volga
  - implied-volatility
  - risk-management
  - long-vol
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Vol-of-Vol: Risk in Long Vega Positions

**Type:** volatility_insight
**Source:** Option Volatility and Pricing — pp. 4017-4024

## Summary

Long vega positions (long options, long straddles) profit if IV rises. But IV itself is volatile — it can spike and crash unpredictably. The risk of a long vega position is not just from realized vol failing to meet IV; it also includes the risk that IV falls before the position is closed. This vol-of-vol risk is captured by volga (second derivative of option value to vol). Deep OTM options have high volga — their vega increases significantly if vol rises. In stressed markets, IV can mean-revert quickly after a spike, turning a profitable long-vega position negative within days. Long vol positions require active management of IV exposure.

## Tags

#vol-of-vol #vega #volga #implied-volatility #risk-management #long-vol

## Notes

<!-- Personal notes here -->
