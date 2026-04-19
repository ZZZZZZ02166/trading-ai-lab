---
card_id: 6dbe1ee7-90aa-47c1-8b14-e207ea14d1f0
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: concept
page_ref: "pp. 2236-2248"
page_start: 2236
page_end: 2248
tags:
  - american-options
  - barone-adesi-whaley
  - binomial-model
  - computational-speed
  - pricing-model
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Barone-Adesi/Whaley: Faster American Option Pricing

**Type:** concept
**Source:** Option Volatility and Pricing — pp. 2236-2248

## Summary

The Cox-Ross-Rubinstein binomial model prices American options accurately but is computationally slow (many lattice steps). Barone-Adesi and Whaley (1987) introduced a quadratic approximation that runs significantly faster while maintaining good accuracy. Used widely for real-time American option pricing and risk management. The BAW model is particularly accurate for equity options where early exercise is driven primarily by dividends (calls) or interest rates (puts). Less accurate for very long-dated options where the quadratic approximation breaks down.

## Tags

#american-options #barone-adesi-whaley #binomial-model #computational-speed #pricing-model

## Notes

<!-- Personal notes here -->
