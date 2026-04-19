---
card_id: 0fc38ef1-8027-49f3-a8d8-86d49e3eb837
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 154–156"
page_start: 154
page_end: 156
tags:
  - itm_probability
  - boness_model
  - directional_trading
  - options_pricing
  - drift
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# True ITM probability N(d₄) vs risk-neutral N(d₂)

**Type:** concept
**Source:** Positional Option Trading (Wiley Trading) — pp. 154–156

## Summary

BSM's N(d₂) is the risk-neutral probability (correct for hedging and replication). The true physical-measure probability of expiring ITM is N(d₄) from the Boness model. Example: 1-year 110-call, S=$100, σ=30%, r=0%, μ=10%: N(d₂) = 32% (risk-neutral), N(d₄) = 45% (physical). Difference = 13 percentage points. For a speculative buyer with a 10% drift forecast, the option has a 45% chance of paying off, not 32%. Using N(d₂) = 32% to evaluate 'is this worth buying?' gives the wrong answer. Speculators should always evaluate options using N(d₄) with their own drift forecast.

## Tags

#itm_probability #boness_model #directional_trading #options_pricing #drift

## Notes

<!-- Personal notes here -->
