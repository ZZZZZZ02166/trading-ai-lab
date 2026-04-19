---
card_id: e868f0ee-2900-486e-ba84-88691fd1431f
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 84-84"
page_start: 84
page_end: 84
tags:
  - term-structure
  - stein-result
  - mean-reversion
  - calendar-spread
  - atm
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Stein Result: ATM Term Structure Mean Reversion Rate

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 84-84

## Summary

Stein (1989) showed that if vol mean-reverts, the term structure of ATM IV should satisfy: σ_long = σ_LR + k(σ_front − σ_LR), where k is the mean-reversion speed proportionality constant. Empirical result: k ≈ 0.85. Example: if long-run average vol = 15% and front-month IV = 25%, the 1-year ATM IV should be: 0.15 + 0.85×(0.25 − 0.15) = 0.235 (under Stein). If the market prices it at 0.245, the term structure is too steep relative to the mean-reversion rate — a potential calendar spread opportunity. Implication: far-dated options move less than front-month in absolute terms.

## Tags

#term-structure #stein-result #mean-reversion #calendar-spread #atm

## Notes

<!-- Personal notes here -->
