---
card_id: 886718e0-bab2-47b3-8dde-1b969fff5a61
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 93-93"
page_start: 93
page_end: 93
tags:
  - corrado-su
  - skewness
  - kurtosis
  - smile
  - gram-charlier
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Corrado-Su Model: Implied Skewness and Kurtosis in the Smile

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 93-93

## Summary

Corrado and Su (1996) extend BSM to incorporate the third (skewness μ₃) and fourth (kurtosis μ₄) moments of the return distribution via Gram-Charlier expansion: σ_implied(K) = σ_ATM + f(μ₃, μ₄, S, K, T). Figure 5.14 shows: with σ=0.30, μ₃=−0.70 (negative skew), μ₄=11 (excess kurtosis), the model produces a pronounced downward-sloping smile matching equity market structure. Key insight: negative skewness is the primary driver of equity IV slope; excess kurtosis adds to smile curvature (wings up on both sides). QQQQ test: μ₃=0.08, μ₄=50 (Figure 5.13) — fitting the smile reveals fat-tailed implied return distribution. Weakness: skewness/kurtosis are not independent — Figure 5.15 shows the valid parameter space is constrained.

## Tags

#corrado-su #skewness #kurtosis #smile #gram-charlier

## Notes

<!-- Personal notes here -->
