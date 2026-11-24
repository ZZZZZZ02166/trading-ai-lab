---
hypothesis_id: "ced3e6cb-c536-596d-8b74-55868fbd21e3"
title: "Stalled Aggression With Later Initiative"
status: "proposed"
tags: ["absorption", "delta", "trade_confirmation"]
source_doc_ids: ["3605e0c990fe", "885b985763be"]
source_card_ids: ["d6151b03-c9d8-53e2-9e0c-008dde797e63", "7556814f-177a-5eb7-a5f5-f1669ef0f0f0", "7d98e1c4-2333-5d50-b6ae-7e6a79d43ba2"]
source_refs: [{"card_id": "d6151b03-c9d8-53e2-9e0c-008dde797e63", "chunk_id": "09de14ff-9942-4f52-bf97-2b28570f2db2", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 95, "page_end": 98}, {"card_id": "7556814f-177a-5eb7-a5f5-f1669ef0f0f0", "chunk_id": "c5578610-5946-4af7-9128-c261ae35659e", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 87, "page_end": 91}, {"card_id": "7d98e1c4-2333-5d50-b6ae-7e6a79d43ba2", "chunk_id": "eada4243-9c07-4f3c-9b60-18ee73260311", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 78, "page_end": 81}]
---

# Stalled Aggression With Later Initiative

## Claim

At a predeclared price reference, heavy executed volume with limited price progress followed by opposite-side initiative predicts a larger favorable post-confirmation excursion than a comparable stall without a directional response.

## Rationale

Both authors read passive absorption and subsequent initiative as distinct observations. This candidate tests whether the second stage carries incremental information at a mapped level.

## Data needed

Exchange-aligned futures trade timestamps, aggressor classifications or a validated quote-based reconstruction, and completed bars.

## Test design

Register each stall with a trailing activity baseline and a small price-progress limit. Compare both groups after the same elapsed confirmation window. Report a price-only reclaim baseline and sensitivity to classification error and costs.

## Decision criteria

- **Support** Incremental held-out improvement over stalled-volume and price-only baselines.
- **Reject** The apparent advantage disappears after the same decision clock and price-response baseline are applied.

## Sources

- Order Flow Trading Setups, PDF pp. 95–98
- Order Flow Trading Setups, PDF pp. 87–91
- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 78–81
