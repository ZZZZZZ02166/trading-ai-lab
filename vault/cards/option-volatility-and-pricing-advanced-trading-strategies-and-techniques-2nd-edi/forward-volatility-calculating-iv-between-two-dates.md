---
card_id: e1486be6-8f58-4e48-8f39-5fc149251c07
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 2873-2879"
page_start: 2873
page_end: 2879
tags:
  - forward-volatility
  - term-structure
  - calendar-spread
  - calculation
  - relative-value
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Forward Volatility: Calculating IV Between Two Dates

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 2873-2879

## Summary

Forward vol for the period t₁ → t₂ given term structure: σ_forward = √[(σ₂² × t₂ − σ₁² × t₁) / (t₂ − t₁)]. This is the break-even realized vol implied by a calendar spread between t₁ and t₂. If the actual calendar spread trades below this forward vol, the spread is cheap; if above, it is expensive. Example: 30-day IV = 25%, 60-day IV = 22%. Forward vol for days 30-60 = √[(0.22² × 60 − 0.25² × 30) / 30] = √[0.03... ] ≈ 18.7%. A calendar spread at 18% IV is cheap vs. this forward.

## Tags

#forward-volatility #term-structure #calendar-spread #calculation #relative-value

## Notes

<!-- Personal notes here -->
