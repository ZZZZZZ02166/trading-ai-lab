---
card_id: 19a334e6-3b49-46d6-9a1c-119916970524
doc_id: ddc2a298cd88
book_title: "Option Market Making"
author: "Allen Jan Baird"
card_type: caution
page_ref: "pp. 187–188"
page_start: 187
page_end: 188
tags:
  - delta_hedging
  - market_making
  - common_mistakes
  - hedge_ratio
  - futures
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Hedge at Actual Traded Prices, Not Stale Board Prices

**Type:** caution
**Source:** Option Market Making — pp. 187–188

## Summary

Poor delta hedging occurs when a market maker uses posted board prices or lagged quotes instead of actual traded futures prices to calculate and execute delta hedges. If options are priced at a futures level of 100 but actual futures are trading at 101, hedging delta using 100 gives an incorrect hedge ratio and leaves residual directional exposure. Always base delta calculations on the actual current futures market, not stale board quotes.

## Tags

#delta_hedging #market_making #common_mistakes #hedge_ratio #futures

## Notes

<!-- Personal notes here -->
