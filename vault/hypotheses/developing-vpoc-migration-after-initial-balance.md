---
hypothesis_id: "290073ae-a424-54eb-9361-25b59c9e8a12"
title: "Developing VPOC Migration After Initial Balance"
status: "proposed"
tags: ["initial_balance", "point_of_control", "trend_continuation"]
source_doc_ids: ["885b985763be"]
source_card_ids: ["a7be728c-0070-5581-b396-ce4821dd80c5", "3ec9fe7d-f1e8-5412-b1ae-995bb35577ae"]
source_refs: [{"card_id": "a7be728c-0070-5581-b396-ce4821dd80c5", "chunk_id": "2d81898a-432c-4b97-b766-2e40ac41a16f", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 20, "page_end": 21}, {"card_id": "3ec9fe7d-f1e8-5412-b1ae-995bb35577ae", "chunk_id": "968de1f7-12e8-4378-b234-69fab54d571d", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 45, "page_end": 50}]
---

# Developing VPOC Migration After Initial Balance

## Claim

Following an initial-balance range extension, a developing VPOC shift in the direction of the break predicts wider post-shift range extension than a comparable break with no shift.

## Rationale

Forthmann treats moving acceptance after fresh directional initiative differently from a POC change inside rotation. Freezing every developing snapshot makes the sequence testable.

## Data needed

Historical futures volume at price or raw trade prints with timestamps to recreate developing profiles and opening ranges.

## Test design

Use a fixed initial-balance definition and live-equivalent profile updates and tie rules. Compare candidates with the same elapsed session time and comparable extension size. Start the outcome at the confirmed shift or matched comparison time.

## Decision criteria

- **Support** Higher post-decision favorable excursion for migration cases in held-out sessions.
- **Reject** No incremental effect over initial extension, contemporaneous price and elapsed trading time.

## Sources

- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 20–21
- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 45–50
