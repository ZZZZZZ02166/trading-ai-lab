---
hypothesis_id: "5330eeb2-73db-556b-960c-5d04e66bd236"
title: "Diagonal Imbalance Stacks at Reclaimed Levels"
status: "proposed"
tags: ["stacked_imbalance", "liquidity_sweep", "trade_confirmation"]
source_doc_ids: ["3605e0c990fe", "885b985763be"]
source_card_ids: ["4434cf17-fe0e-5a0d-8dec-202cc3c2be59", "b2edec64-1969-59b9-989f-1cbd6af20908", "33d4232d-f7af-5d77-9725-37362509ac63"]
source_refs: [{"card_id": "4434cf17-fe0e-5a0d-8dec-202cc3c2be59", "chunk_id": "c39f1e3a-118a-4ccb-9d27-b27375e5b03a", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 36, "page_end": 37}, {"card_id": "b2edec64-1969-59b9-989f-1cbd6af20908", "chunk_id": "c39f1e3a-118a-4ccb-9d27-b27375e5b03a", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 37, "page_end": 38}, {"card_id": "33d4232d-f7af-5d77-9725-37362509ac63", "chunk_id": "0fcaba3b-7b9e-4394-9ecb-f22c9869b4b0", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 113, "page_end": 117}]
---

# Diagonal Imbalance Stacks at Reclaimed Levels

## Claim

At a reclaimed prior-session or opening-range extreme, a same-side diagonal footprint stack in the reclaim direction predicts more continuation over the next 15 minutes than a reclaimed level with comparable price and volume but no stack.

## Rationale

Dale specifies how the comparison is calculated, and Forthmann places stacks after failed breaks and tests them in the context of next-bar follow-through. Matching price-only reclaims isolates whether the footprint adds signal.

## Data needed

Exchange-level executions by price and aggressor side, prior-session reference levels and opening bars.

## Test design

Freeze the stack ratio, adjacency, zero-denominator handling and minimum size before testing. Determine the reclaim and stack using only completed bars, then start measuring the outcome at the next observable price. Use identical candidate selection for both groups.

## Decision criteria

- **Support** Positive held-out improvement with a plausible range of fixed stack definitions.
- **Reject** No improvement over price-only reclaims, or a result that depends on retrospectively choosing the stack threshold.

## Sources

- Order Flow Trading Setups, PDF pp. 36–37
- Order Flow Trading Setups, PDF pp. 37–38
- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 113–117
