---
doc_id: "3605e0c990fe"
book_title: "Order Flow Trading Setups"
author: "Trader Dale"
file_path: "books/Order-Flow-Trading-Setups-1.pdf"
page_start: 1
page_end: 161
---

# Cheat Sheet

*Order Flow Trading Setups by Trader Dale*

## Read the footprint

- **Bid** records sell-initiated execution. **Ask** records buy-initiated execution. Every execution also has a passive counterparty.
- **Bar delta** equals summed ask volume minus summed bid volume. **CVD** accumulates bar delta from the declared reset.
- **Bar node** is the price row with the largest combined bid and ask total. **Multiple nodes** repeat at the same price across consecutive bars.
- **Diagonal imbalance** compares opposite sides at neighboring prices. Dale shows a configurable 3-to-1 ratio and an adjacent stack convention.
- **Unfinished high or low** leaves volume on both sides of the extreme in Dale's definition. A distant or untested reference can remain open.

## Replay sequence

1. Mark a trend cluster, rejection cluster, repeated node, large execution, or stacked band from completed data.
2. Record when price clearly separates and when the first retest starts. Dale's multiple-node example calls for two fully separated footprints.
3. At a preselected zone, record large passive-interest clues, a heavy-volume stall, initiative away from the level, or a matched price/CVD divergence.
4. Mark the next heavy-volume area and structural invalidation while the information is still available.
5. Record the failed examples alongside the successful ones.

## Read together

Use the detailed study note for PDF pages. Pair with Forthmann's notes on prior value, initial balance, and the distinction between TPO POC and VPOC.
