---
card_id: 1c97a33b-e04f-4cba-922b-0294d775749f
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 150–152"
page_start: 150
page_end: 152
tags:
  - boness_model
  - subjective_pricing
  - drift
  - directional_trading
  - bsm
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Boness model: subjective option pricing with drift

**Type:** concept
**Source:** Positional Option Trading (Wiley Trading) — pp. 150–152

## Summary

BSM is correct for market makers who hedge. For speculators with directional views, the Boness model (1962) uses the trader's actual drift forecast μ: Call: C = S·exp(μT)·N(d₃) − X·N(d₄) where d₃ = [ln(S/X) + (μ + σ²/2)·T] / (σ√T) and d₄ = [ln(S/X) + (μ − σ²/2)·T] / (σ√T). If Boness value > market price, the option is underpriced relative to your forecast. Even a modest directional forecast (μ = 3% above risk-free) meaningfully changes option value. Partial derivative ∂C/∂μ = T·S·exp(μT)·N(d₃) — larger for longer-dated options.

## Tags

#boness_model #subjective_pricing #drift #directional_trading #bsm

## Notes

<!-- Personal notes here -->
