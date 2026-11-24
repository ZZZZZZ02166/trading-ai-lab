---
hypothesis_id: "09eb550f-79f5-57d9-889f-9ef8f0a02d1d"
title: "First Retests of Separated Volume Clusters"
status: "proposed"
tags: ["volume_cluster", "first_retest", "volume_profile"]
source_doc_ids: ["3605e0c990fe", "885b985763be"]
source_card_ids: ["7a897d6e-bba5-5599-a9e5-e340d159a02c", "80316233-b845-5188-863a-45ebbcc8f74c", "062b6be8-962a-5b98-843b-989629db43b3"]
source_refs: [{"card_id": "7a897d6e-bba5-5599-a9e5-e340d159a02c", "chunk_id": "045c49cc-69cd-444b-a04c-1108ce9475ff", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 46, "page_end": 50}, {"card_id": "80316233-b845-5188-863a-45ebbcc8f74c", "chunk_id": "8115476e-b8ba-4cf4-924f-d28cef15b8fb", "doc_id": "3605e0c990fe", "book_title": "Order Flow Trading Setups", "file_path": "books/Order-Flow-Trading-Setups-1.pdf", "page_start": 55, "page_end": 59}, {"card_id": "062b6be8-962a-5b98-843b-989629db43b3", "chunk_id": "44164a91-565b-47c9-b847-f70b7ab603ee", "doc_id": "885b985763be", "book_title": "Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading", "file_path": "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf", "page_start": 52, "page_end": 54}]
---

# First Retests of Separated Volume Clusters

## Claim

After a defined departure from an unusually high executed-volume band, a first retest predicts a higher probability of a favorable 15-minute excursion than a later retest of the same kind of band.

## Rationale

Dale emphasizes first revisits after clearly separated footprints. Forthmann describes reactions at and around prior auction bands. The frequency of a turn can be tested without inferring whether an institution defended its inventory.

## Data needed

Historical futures trade prints or volume at price, timestamps and OHLC for a consistent regular session.

## Test design

Define the band from completed bars, then register separation and every later retest in order. Compare first and later retests matched by instrument, direction, time of day and volatility. Use one bounded horizon and report the number of unique levels.

## Decision criteria

- **Support** Positive held-out difference in retest success and favorable excursion across matched groups.
- **Reject** An effect near zero, reversing in later periods, or explained by distance or time of day.

## Sources

- Order Flow Trading Setups, PDF pp. 46–50
- Order Flow Trading Setups, PDF pp. 55–59
- Volume Profile, Market Profile, Order Flow: Next Generation of Daytrading, PDF pp. 52–54
