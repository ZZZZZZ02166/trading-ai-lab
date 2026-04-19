---
card_id: 2e45c610-0807-4f11-a153-88578716c4ec
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: caution
page_ref: "pp. 3285-3292"
page_start: 3285
page_end: 3292
tags:
  - margin
  - black-scholes
  - assumption-violation
  - caution
  - forced-liquidation
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Margin Calls: Black-Scholes Frictionless Assumption Fails

**Type:** caution
**Source:** Option Volatility and Pricing — pp. 3285-3292

## Summary

Black-Scholes assumes unlimited frictionless borrowing and lending. In practice, margin calls can force position liquidation at the worst time — when a position is deeply against the trader. If additional capital is unavailable, the model's theoretical hedge cannot be maintained. This creates forced selling into adverse markets, amplifying losses. The practical implication: strategy capital requirements must account for worst-case margin demands, not just initial margin. Deep OTM short options that appear safe based on delta may require substantial additional margin if vol spikes and the underlying moves toward the strike.

## Tags

#margin #black-scholes #assumption-violation #caution #forced-liquidation

## Notes

<!-- Personal notes here -->
