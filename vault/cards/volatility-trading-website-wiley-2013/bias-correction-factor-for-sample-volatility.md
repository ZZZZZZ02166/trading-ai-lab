---
card_id: 690fa7f3-d485-4b05-a789-6c7875dd01b5
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 40-40"
page_start: 40
page_end: 40
tags:
  - bias-correction
  - sample-variance
  - statistics
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Bias Correction Factor for Sample Volatility

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 40-40

## Summary

Sample standard deviation is a biased estimator of population std dev. The bias correction factor c₄(N) comes from the chi distribution: c₄ = √(2/(N-1)) × Γ(N/2) / Γ((N-1)/2). Key values: N=5: 0.940, N=10: 0.973, N=20: 0.988, N=50: 0.996, N=100: 0.998. Correction: σ_unbiased = σ_sample / c₄(N). Figure 2.2 shows variance converges rapidly — sample variance is within 3% of true variance by N=20. For most practical purposes, bias is negligible above N=30.

## Tags

#bias-correction #sample-variance #statistics

## Notes

<!-- Personal notes here -->
