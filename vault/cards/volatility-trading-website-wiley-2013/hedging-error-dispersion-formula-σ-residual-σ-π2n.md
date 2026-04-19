---
card_id: d6661e9a-0573-469d-aded-8b08f0879049
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 133-133"
page_start: 133
page_end: 133
tags:
  - hedging
  - dispersion
  - discrete-hedging
  - formula
  - rebalancing
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Hedging Error Dispersion Formula: σ_residual = σ × √(π/2N)

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 133-133

## Summary

The standard deviation of the residual P/L from discrete hedging: σ_residual = σ_option × √(π/(2N)), where N = number of hedge rebalances. Figure 7.6 shows this relationship: dispersion decreases as 1/√N as N increases. Example: N=5 hedges → residual vol ≈ 56% of option vol; N=20 hedges → residual vol ≈ 28%; N=100 → 13%. Practical consequence: hedging daily (N≈252/year) is much better than weekly (N≈52) for reducing tracking error, but the marginal benefit diminishes quickly. Transaction costs set the economic limit on hedging frequency.

## Tags

#hedging #dispersion #discrete-hedging #formula #rebalancing

## Notes

<!-- Personal notes here -->
