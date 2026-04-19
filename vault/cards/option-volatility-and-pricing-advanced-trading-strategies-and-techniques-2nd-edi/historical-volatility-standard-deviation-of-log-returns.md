---
card_id: 4da03e1b-0708-489d-a6d0-7cd9794813bf
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 2706-2712"
page_start: 2706
page_end: 2712
tags:
  - historical-volatility
  - calculation
  - log-returns
  - standard-deviation
  - annualization
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Historical Volatility: Standard Deviation of Log Returns

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 2706-2712

## Summary

Calculation: (1) Compute log returns: r_i = ln(P_i / P_{i-1}); (2) Find mean: r̄ = (1/n) × Σr_i; (3) Compute sample std dev: σ_daily = √[Σ(r_i − r̄)² / (n−1)]; (4) Annualize: σ_annual = σ_daily × √252. Using (n−1) divisor gives unbiased estimate. Log returns are preferred over percentage returns because: they are additive over time, symmetric for equal up/down moves, and naturally bounded (avoiding negative prices). Daily settlement-to-settlement returns are standard for exchange-traded options. Increasing the lookback N improves stability but reduces responsiveness to recent vol changes.

## Tags

#historical-volatility #calculation #log-returns #standard-deviation #annualization

## Notes

<!-- Personal notes here -->
