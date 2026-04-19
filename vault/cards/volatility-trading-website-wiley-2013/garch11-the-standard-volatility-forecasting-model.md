---
card_id: f7ddb324-bab6-4f49-8e8a-2b14bd1a187b
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 66-66"
page_start: 66
page_end: 66
tags:
  - garch
  - volatility-forecasting
  - mean-reversion
  - parameters
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# GARCH(1,1): The Standard Volatility Forecasting Model

**Type:** concept
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 66-66

## Summary

GARCH(1,1) (Bollerslev 1986): σ²_t = ω + αr²_{t-1} + βσ²_{t-1}. Three parameters: ω = long-run variance contribution (floor); α = reaction to recent shocks (alpha); β = persistence of last period's variance (beta). Long-run variance: V_L = ω/(1-α-β). Mean reversion speed: (1-α-β) governs how fast vol returns to V_L. MSFT example (Figure 4.2): ω=0.00000505, α=0.053, β=0.884. Long-run vol ≈ 11%; after a shock, vol decays exponentially back toward 11% over approximately 30-60 days.

## Tags

#garch #volatility-forecasting #mean-reversion #parameters

## Notes

<!-- Personal notes here -->
