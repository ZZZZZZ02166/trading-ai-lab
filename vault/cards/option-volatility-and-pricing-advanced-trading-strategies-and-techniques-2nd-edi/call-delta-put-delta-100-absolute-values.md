---
card_id: 24528da8-8e3d-4c84-92d6-ed2c1dd8661a
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 1848-1865"
page_start: 1848
page_end: 1865
tags:
  - delta
  - put-call-parity
  - call-delta
  - put-delta
  - consistency
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Call Delta + Put Delta = 100 (Absolute Values)

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 1848-1865

## Summary

For a call and put with the same exercise price and expiration: |delta_call| + |delta_put| ≈ 100. If the 100 put has delta −60, the 100 call has delta +40. This relationship holds approximately because a synthetic long (long call + short put) replicates long stock (delta = +100). Precise equality would require delta_call − delta_put = 1 (for stock-type settlement) or adjustments for futures-type settlement. This relationship is useful for: quickly computing the call delta from the put delta, verifying consistency in option chains, and constructing delta-neutral positions.

## Tags

#delta #put-call-parity #call-delta #put-delta #consistency

## Notes

<!-- Personal notes here -->
