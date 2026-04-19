---
card_id: 24e57ded-a53f-4be9-ae35-2f68b9e2a761
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: caution
page_ref: "pp. 191–194"
page_start: 191
page_end: 194
tags:
  - kelly_criterion
  - estimation_error
  - trade_sizing
  - overfitting
  - risk_management
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Kelly Estimation Uncertainty: Over-Betting Risk from Parameter Error

**Type:** caution
**Source:** Positional Option Trading (Wiley Trading) — pp. 191–194

## Summary

The Kelly ratio f* is estimated from historical data with finite sample sizes. The uncertainty in f* depends on: n·Var(f) = 1/σ² + 2μ²/σ⁴ (for normal returns). With n=1000 trades: a typical sd(f) ≈ 0.03–0.10. There is a meaningful probability (~25%) that the estimated f* is positive while the true f* is zero. Practical implication: scale down the raw Kelly estimate by 50–80% to account for parameter uncertainty. Full Kelly betting on an estimated Kelly fraction with finite data almost always means over-betting.

## Tags

#kelly_criterion #estimation_error #trade_sizing #overfitting #risk_management

## Notes

<!-- Personal notes here -->
