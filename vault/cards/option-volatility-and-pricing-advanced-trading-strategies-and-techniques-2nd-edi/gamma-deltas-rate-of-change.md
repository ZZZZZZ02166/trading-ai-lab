---
card_id: 60f77e5f-8f2b-426a-9be8-45f22501a1d5
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 843-845"
page_start: 843
page_end: 845
tags:
  - gamma
  - delta
  - rate-of-change
  - long-gamma
  - short-gamma
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Gamma: Delta's Rate of Change

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 843-845

## Summary

Gamma = how much delta changes per one-point move in the underlying. All long options (calls and puts) have positive gamma. Rule: when underlying rises, add gamma to old delta; when underlying falls, subtract gamma from old delta. Example: call with delta 40, gamma 4, underlying at 97.50. If underlying rises to 101.50 (+4 points): average delta = (40 + 56)/2 = 48; new option value ≈ old value + 4 × 0.48. Long gamma means delta accelerates in your favor as the underlying moves. Short gamma means delta moves adversely. Gamma is the primary risk measure for dynamic hedgers.

## Tags

#gamma #delta #rate-of-change #long-gamma #short-gamma

## Notes

<!-- Personal notes here -->
