---
card_id: 53e23780-cd1f-4fb9-8d02-8c4112df2934
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: definition
page_ref: "pp. 3908-3926"
page_start: 3908
page_end: 3926
tags:
  - tau
  - time-to-expiration
  - day-count
  - black-scholes
  - convention
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Tau (τ): Time to Expiration in Option Formulas

**Type:** definition
**Source:** Option Volatility and Pricing — pp. 3908-3926

## Summary

Tau (τ) is standard notation for time to expiration in years. For 30 calendar days: τ = 30/365 ≈ 0.082. For 63 trading days: τ = 63/252 = 0.25. Tau appears throughout Black-Scholes: in the forward price, in d₁ and d₂, and in all Greeks. √τ scales volatility to the holding period: 30-day vol = annual vol × √(30/252). Practitioners must confirm the day-count convention used (365 calendar days vs. 252 trading days) — the two conventions produce different tau values and slightly different Greeks. For options with less than a week to expiry, the correct day count convention matters significantly for theta calculations.

## Tags

#tau #time-to-expiration #day-count #black-scholes #convention

## Notes

<!-- Personal notes here -->
