---
card_id: fee2047b-140b-4703-8ac2-2fcc0b23fd97
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 235-235"
page_start: 235
page_end: 235
tags:
  - vix
  - variance-swap
  - model-free
  - implied-volatility
  - cboe
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# VIX: Model-Free Implied Volatility via Variance Swap Replication

**Type:** concept
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 235-235

## Summary

The CBOE VIX (post-2003 methodology) is a model-free measure of S&P 500 30-day implied volatility, derived from Carr and Madan's variance swap framework. VIX² = (2/T) × Σ [ΔKᵢ/Kᵢ²] × e^(rT) × Q(Kᵢ) − (1/T)[F/K₀ − 1]² where Q(Kᵢ) are market prices of OTM options at strike Kᵢ. Key: unlike BSM IV which solves for σ at one strike, VIX integrates across the entire option strip — it is a model-free measure. VIX = annualized (×√12 from 30-day) measure. Cannot be directly traded — VIX futures and options exist for indirect access.

## Tags

#vix #variance-swap #model-free #implied-volatility #cboe

## Notes

<!-- Personal notes here -->
