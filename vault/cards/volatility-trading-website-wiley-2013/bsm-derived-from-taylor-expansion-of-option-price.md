---
card_id: 9b3b0dce-a6ec-4cad-a277-22c6640fa4b8
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 9-11"
page_start: 9
page_end: 11
tags:
  - bsm
  - taylor-expansion
  - pde
  - delta-hedging
  - drift
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# BSM Derived from Taylor Expansion of Option Price

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 9-11

## Summary

The BSM PDE follows from expanding the option value dC using a Taylor series: dC ≈ (∂C/∂S)dS + (∂C/∂t)dt + ½(∂²C/∂S²)(dS)². Under Ito's lemma, (dS)² = σ²S²dt for a lognormal process. Setting up a delta-neutral portfolio (long option, short Δ shares) and requiring it to earn the risk-free rate gives the BSM PDE. The key insight: the drift μ cancels out entirely — option pricing is drift-independent. Only σ matters.

## Tags

#bsm #taylor-expansion #pde #delta-hedging #drift

## Notes

<!-- Personal notes here -->
