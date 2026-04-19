---
card_id: 14edea07-ae37-4c42-b5c2-568ee5c22dc0
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 70-70"
page_start: 70
page_end: 70
tags:
  - garch
  - term-structure
  - forward-vol
  - calendar-spread
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# GARCH Term Structure: Exponential Decay to Long-Run Vol

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 70-70

## Summary

Figure 4.2 shows GARCH(1,1) term structure for MSFT (May 21, 2007): front-month predicted vol ≈ 16%, decaying exponentially to long-run vol ≈ 11% over 120 days. The term structure at horizon T: E[σ²_{t+T}] = V_L + (σ²_t − V_L)(α+β)^T. Key insight: GARCH-implied term structure is the theoretical forward vol curve. When current vol is above long-run vol (elevated), GARCH predicts declining term structure. When below, predicts rising term structure. Compare this GARCH-predicted term structure to the market's implied term structure to identify relative value in calendar spreads.

## Tags

#garch #term-structure #forward-vol #calendar-spread

## Notes

<!-- Personal notes here -->
