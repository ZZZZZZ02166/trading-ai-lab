---
card_id: 7586be0e-8dd8-4c2e-b335-4f920a41e873
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 193–196"
page_start: 193
page_end: 196
tags:
  - kelly_criterion
  - estimation_uncertainty
  - position_sizing
  - fractional_kelly
  - statistics
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Kelly estimation uncertainty: full Kelly almost always means over-betting

**Type:** mechanism
**Source:** Positional Option Trading (Wiley Trading) — pp. 193–196

## Summary

The Kelly fraction is estimated from historical data with finite sample size. With n=1,000 trades: sd(f̂) ≈ 0.03–0.10 depending on strategy. There is a meaningful probability that estimated f* > 0 while the true f* ≤ 0. Equations 9.26–9.32: Variance of Kelly estimate via delta method: Var(f̂) = (1/σ² + 2μ²/σ⁴)/n. Equations 9.33–9.37: With skewness correction: sd(f̂) = √(1/σ² + 2μ²/σ⁴)/(n−1). Fractional Kelly tables: to keep over-betting probability below 10% with skew adjustment, scale Kelly by 0.205×; below 20%: scale by 0.478×. Practical default: trade at 25–50% of estimated Kelly.

## Tags

#kelly_criterion #estimation_uncertainty #position_sizing #fractional_kelly #statistics

## Notes

<!-- Personal notes here -->
