---
card_id: 257ab1c2-fb7d-4fd6-bdfe-1f920637dfe5
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: definition
page_ref: "pp. 3610-3612"
page_start: 3610
page_end: 3612
tags:
  - realized-volatility
  - variance-swap
  - settlement
  - log-returns
  - additivity
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Realized Volatility Contract Settlement

**Type:** definition
**Source:** Option Volatility and Pricing — pp. 3610-3612

## Summary

A realized vol contract settles at the annualized standard deviation of log returns over its life. Returns use daily settlement prices. Annualization factor = √(trading days per year). At settlement, realized vol is unambiguous — no model, no IV, just the actual measured volatility. Variance contracts (pay realized variance − strike) are more common than volatility contracts because variance is additive: total variance over two periods = sum of period variances. Volatility is not additive. This additivity makes variance swaps easier to replicate with a static portfolio of options (the log-contract replication).

## Tags

#realized-volatility #variance-swap #settlement #log-returns #additivity

## Notes

<!-- Personal notes here -->
