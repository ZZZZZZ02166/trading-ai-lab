---
card_id: 405500b4-c983-48b8-89ca-e5d80126bf6f
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: concept
page_ref: "pp. 15-15"
page_start: 15
page_end: 15
tags:
  - greeks
  - delta
  - gamma
  - theta
  - vega
  - pnl
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Greeks as Sensitivities from the Taylor Expansion

**Type:** concept
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 15-15

## Summary

Each Greek is a coefficient in the Taylor expansion of option value change: Delta (δ) = ∂C/∂S — first-order price sensitivity; Gamma (γ) = ∂²C/∂S² — second-order, captures convexity; Theta (θ) = ∂C/∂t — time decay; Vega (ν) = ∂C/∂σ — sensitivity to volatility; Rho (ρ) = ∂C/∂r — interest rate sensitivity. In continuous delta-hedging, the P/L from one time step is: P/L = ½γ(dS)² + θdt = ½γσ²_realized S²dt − ½γσ²_implied S²dt = ½γS²(σ²_r − σ²_i)dt. The trader profits when realized vol exceeds implied vol.

## Tags

#greeks #delta #gamma #theta #vega #pnl

## Notes

<!-- Personal notes here -->
