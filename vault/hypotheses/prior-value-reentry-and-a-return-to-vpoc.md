---
hypothesis_id: "93409f37-3f85-5329-b48e-54f6332ef946"
title: "Prior Value Reentry and a Return to VPOC"
status: "proposed"
tags: ["value_area", "point_of_control", "session_context"]
source_doc_ids: ["885b985763be"]
source_card_ids: ["fca43d5f-f8a0-5b20-adf9-92b85c27a79d", "f7237fab-e171-5c08-acce-aef82162f984"]
source_refs: [{"card_id": "fca43d5f-f8a0-5b20-adf9-92b85c27a79d", "chunk_id": "c2e057ec-ef53-4fdb-9dde-69f0b73b2990", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 28, "page_end": 30}, {"card_id": "f7237fab-e171-5c08-acce-aef82162f984", "chunk_id": "c2e057ec-ef53-4fdb-9dde-69f0b73b2990", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 28, "page_end": 30}]
---

# Prior Value Reentry and a Return to VPOC

## Claim

Among sessions opening outside prior regular-session value, confirmed reentry predicts a higher probability of a subsequent prior VPOC touch than sessions still outside value at the same decision time.

## Rationale

Forthmann separates outside acceptance from reentry and uses the prior control price as an interim reference. The study tests the nearer VPOC outcome before considering full value-area traversal.

## Data needed

Historical futures trade prints or reliable volume at price to construct value areas, plus regular-session intraday bars.

## Test design

Predeclare the value-area algorithm, tick binning, reentry rule and comparison clock. Use the same starting time for outcome measurement and exclude VPOC touches that occurred before confirmation. Report conditional rates, base rates and uncertainty.

## Decision criteria

- **Support** Higher held-out VPOC touch rate after reentry at the matched decision time.
- **Reject** No incremental lift once gap size, distance to VPOC and time of day are matched.

## Sources

- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 28–30
- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 28–30
