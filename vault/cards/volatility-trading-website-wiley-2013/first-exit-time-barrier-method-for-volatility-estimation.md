---
card_id: 44ac344c-4087-4ed7-86e7-400bf00554cb
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 40-40"
page_start: 40
page_end: 40
tags:
  - first-exit-time
  - barrier-method
  - volatility-estimator
  - efficiency
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# First Exit Time / Barrier Method for Volatility Estimation

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 40-40

## Summary

An alternative to OHLC estimators: measure how long a random walk takes to exit a symmetric boundary ±b. For a Brownian motion with vol σ, the expected first exit time is T = b²/σ². Back-solve σ from observed exit times. Figure 2.4 shows this method produces standard deviation of vol estimates of 0.028 vs 0.048 for close-to-close — 1.7× more efficient. Weakness: requires tick/intraday data to observe crossing times; not applicable to daily OHLC data. Best for high-frequency practitioners.

## Tags

#first-exit-time #barrier-method #volatility-estimator #efficiency

## Notes

<!-- Personal notes here -->
