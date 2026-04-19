---
card_id: c72fe9b0-e198-416a-b9e4-d40f5a5b0424
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 108-108"
page_start: 108
page_end: 108
tags:
  - hedging-bands
  - hodges-neuberger
  - transaction-costs
  - delta-hedging
  - utility
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Hodges-Neuberger (HN): Utility-Based Hedging Bands

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 108-108

## Summary

Hodges and Neuberger (1989) solved the first utility-based hedging problem: given exponential utility and proportional transaction costs (cost = k × |ΔShares| × S), the optimal strategy is to maintain delta within a band around the BSM delta. Hedge only when delta drifts outside the band. Band width depends on: γ (risk aversion), k (transaction cost), σ (volatility), and time to expiry. Higher costs and lower risk aversion → wider bands (hedge less often). The full HN solution is computationally intensive (numerical PDE). It reveals two key insights: (1) hedging bands widen for long/short gamma asymmetrically; (2) the bands are centered on the BSM delta, not on zero.

## Tags

#hedging-bands #hodges-neuberger #transaction-costs #delta-hedging #utility

## Notes

<!-- Personal notes here -->
