---
card_id: 65e8946d-620a-45e2-bc98-f2b330dc0fe7
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 241–243"
page_start: 241
page_end: 243
tags:
  - statistics
  - rare_events
  - rule_of_three
  - drawdown
  - sample_size
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Rule of Three: Estimating Probability of Rare Events from No-Occurrence Samples

**Type:** concept
**Source:** Positional Option Trading (Wiley Trading) — pp. 241–243

## Summary

If an event has not occurred in n observations, a 95% upper bound on its true probability is 3/n. Example: if a strategy has not had a 15% drawdown in 30 observations, the 95% upper bound on the probability of a 15%+ drawdown per period is 3/30 = 10%. Derived from: solving (1−p)^n < 0.05 for p, giving p_upper ≈ 3/n. Caution: this assumes IID observations. Non-IID returns (correlated losses in crises) make the true probability of rare events higher than this estimate suggests.

## Tags

#statistics #rare_events #rule_of_three #drawdown #sample_size

## Notes

<!-- Personal notes here -->
