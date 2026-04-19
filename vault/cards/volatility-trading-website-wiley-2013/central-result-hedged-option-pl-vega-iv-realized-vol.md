---
card_id: 2d210981-52b8-445c-b412-55d2bd9ce24f
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: principle
page_ref: "pp. 131-131"
page_start: 131
page_end: 131
tags:
  - pnl
  - vega
  - implied-volatility
  - realized-volatility
  - central-result
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Central Result: Hedged Option P/L ≈ Vega × (IV − Realized Vol)

**Type:** principle
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 131-131

## Summary

From BSM theory, the total P/L of a continuously delta-hedged option position is: P/L = ½ × ∫ (σ²_implied − σ²_realized) × S²Γ(σᵢ) × e^(−rt) dt. Simplified: P/L ≈ Vega × (σ_implied − σ_realized). This is the central result for volatility trading: the edge in selling options comes entirely from the gap between the IV you sold and the realized vol that follows. If IV = 25% and realized = 20%, the P/L per $1 vega ≈ +$5 per vol point. Critical caveat: this is the expected P/L. The actual P/L has wide dispersion around this expectation due to path dependency and discrete hedging.

## Tags

#pnl #vega #implied-volatility #realized-volatility #central-result

## Notes

<!-- Personal notes here -->
