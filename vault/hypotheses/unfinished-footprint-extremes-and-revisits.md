---
hypothesis_id: "ce9d7537-4b8a-5c5c-9302-57c819fe0b36"
title: "Unfinished Footprint Extremes and Revisits"
status: "proposed"
tags: ["unfinished_auction", "footprints", "first_retest"]
source_doc_ids: ["3605e0c990fe", "885b985763be"]
source_card_ids: ["6a657962-ff00-5945-85c5-42263a4a0e41", "3a70bba7-1617-5dfb-b14e-ee5adafafeec", "0af8600a-8e89-5823-93c4-a297cfa7ce96"]
source_refs: [{"card_id": "6a657962-ff00-5945-85c5-42263a4a0e41", "chunk_id": "8353efce-cff6-43c9-b254-81a820153f75", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 38, "page_end": 41}, {"card_id": "3a70bba7-1617-5dfb-b14e-ee5adafafeec", "chunk_id": "045c9368-78bd-4754-a9b6-8e0e4a8ae1a7", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 71, "page_end": 74}, {"card_id": "0af8600a-8e89-5823-93c4-a297cfa7ce96", "chunk_id": "39a74462-e82b-47a9-a835-25b79cd363fd", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 58, "page_end": 60}]
---

# Unfinished Footprint Extremes and Revisits

## Claim

Among equally distant footprint highs or lows, an extreme that still has executions on both sides predicts a higher chance of being revisited within 60 minutes than an extreme with the expected zero side.

## Rationale

Dale provides a print-level definition and examples of revisits, as well as cases where price first travels away. Forthmann's weak-extreme concept supplies context but has a different operational definition.

## Data needed

Historical futures footprints reconstructed from trade prints by side and price, with consistent completed bar boundaries.

## Test design

Label finished and unfinished extremes on bar close. Predeclare treatment of missing observations and zero quantities, and match by distance, swing type, price direction and session time. Count the first future touch and handle session-end censoring.

## Decision criteria

- **Support** A higher matched revisit rate in later periods with the same footprint construction.
- **Reject** The difference disappears after matching distance and bar range, or reverses across sessions.

## Sources

- Order Flow Trading Setups, PDF pp. 38–41
- Order Flow Trading Setups, PDF pp. 71–74
- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 58–60
