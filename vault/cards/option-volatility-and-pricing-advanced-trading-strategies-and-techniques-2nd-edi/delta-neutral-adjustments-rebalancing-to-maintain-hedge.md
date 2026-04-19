---
card_id: e68d2d62-3d9e-4751-adaf-465b85264a67
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 949-957"
page_start: 949
page_end: 957
tags:
  - delta-neutral
  - rebalancing
  - gamma-scalping
  - adjustments
  - p&l
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Delta-Neutral Adjustments: Rebalancing to Maintain Hedge

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 949-957

## Summary

After initiating a delta-neutral hedge (buying options + shorting underlying), the delta drifts as the underlying moves (due to gamma). To restore neutrality: if the underlying rises and delta becomes positive, sell more underlying; if the underlying falls and delta becomes negative, buy more underlying. These rebalancing trades are adjustments — they don't affect theoretical edge because the underlying has no theoretical value in an options framework. The cumulative profit from all adjustment trades is the gamma scalp P/L. Total position P/L = theoretical edge at initiation + gamma scalp P/L + theta paid + vega P/L.

## Tags

#delta-neutral #rebalancing #gamma-scalping #adjustments #p&l

## Notes

<!-- Personal notes here -->
