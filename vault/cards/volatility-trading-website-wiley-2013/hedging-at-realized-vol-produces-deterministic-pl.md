---
card_id: 02adc68d-0768-47e2-a171-ce7613f8ec84
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: principle
page_ref: "pp. 138-138"
page_start: 138
page_end: 138
tags:
  - delta-hedging
  - realized-vol
  - pnl
  - deterministic
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Hedging at Realized Vol Produces Deterministic P/L

**Type:** principle
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 138-138

## Summary

Equation 7.15: dC(σr) − Δ(σᵢ)dS − r(C(σᵢ) − Δ(σᵢ)S)dt = ½(σ²r − σ²ᵢ)S²Γ(σᵢ)dt. If the trader hedges using BSM delta computed at the actual realized vol (σr = hedging vol), the stochastic dS terms cancel and the P/L per time step is purely deterministic: ½(σ²r − σ²ᵢ)S²Γ(σᵢ)dt. Total P/L = ½(σ²ᵢ − σ²r) × ∫e^(−rt)S²Γ(σᵢ)dt — a locked-in profit if σᵢ > σr. Figure 7.8 shows P/L accumulating smoothly over time under this scheme. Practical issue: σr is unknown in advance. This scheme is a theoretical ideal that motivates trading when IV is significantly above forecast realized vol.

## Tags

#delta-hedging #realized-vol #pnl #deterministic

## Notes

<!-- Personal notes here -->
