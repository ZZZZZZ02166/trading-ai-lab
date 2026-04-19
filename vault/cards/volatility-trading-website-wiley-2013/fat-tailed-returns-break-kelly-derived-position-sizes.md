---
card_id: 88c27885-780a-442c-87f4-98bbdf2e276a
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: caution
page_ref: "pp. 165-165"
page_start: 165
page_end: 165
tags:
  - kelly-criterion
  - fat-tails
  - kurtosis
  - position-sizing
  - caution
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Fat-Tailed Returns Break Kelly-Derived Position Sizes

**Type:** caution
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 165-165

## Summary

Kelly theory assumes returns are normally distributed. Real financial returns have fat tails — excess kurtosis causes more frequent extreme moves. Figure 8.17 shows: when the return distribution is logistic (kurtosis 9 vs normal 3), the Kelly-optimal position size destroys the bankroll in simulation (wealth collapses to near zero) versus the smooth growth of the normal-distribution example (Figure 8.15). This is not a theoretical curiosity — equity returns routinely have kurtosis 5-15. Practical fix: use half-Kelly or less; run simulations with fat-tailed return distributions to stress-test any position sizing rule before deploying capital.

## Tags

#kelly-criterion #fat-tails #kurtosis #position-sizing #caution

## Notes

<!-- Personal notes here -->
