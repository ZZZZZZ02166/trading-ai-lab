---
card_id: 1da1c19f-1c32-4e44-87c9-f5d32efa3c79
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 120-120"
page_start: 120
page_end: 120
tags:
  - transaction-costs
  - market-impact
  - bid-ask
  - square-root
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Transaction Cost Estimation for Options Hedging

**Type:** mechanism
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 120-120

## Summary

Transaction costs have two components: (1) bid-ask spread — typically dominant for retail/semi-professional traders; (2) market impact. Market impact scales with the square root of trade size (Hasbrouck 1991, BARRA 1997): f(s) = k√s, where s = shares traded and k is a constant. Total expected transaction cost per rebalance: C ≈ k₁ × |ΔShares| × S + k₂ × √(|ΔShares|) × S. For small trades, bid-ask dominates; for large trades, market impact dominates. Retail traders: primarily bid-ask cost. Institutional: primarily market impact. Sinclair suggests estimating k from historical transaction data before trading.

## Tags

#transaction-costs #market-impact #bid-ask #square-root

## Notes

<!-- Personal notes here -->
