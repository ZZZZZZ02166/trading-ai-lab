---
title: "Volume Profile and Order Flow"
type: synthesis
source_doc_ids: ["3605e0c990fe", "885b985763be"]
sources:
  - doc_id: "3605e0c990fe"
    file_path: "books/Order-Flow-Trading-Setups-1.pdf"
    page_start: 20
    page_end: 145
  - doc_id: "885b985763be"
    file_path: "books/Volume Profile & Market Profile Order Flow for Next Gen Daytrading.pdf"
    page_start: 19
    page_end: 203
---

# Volume Profile and Order Flow

Both books first locate a reference in the auction, then read what price and executed volume do at that reference. Forthmann spends more time on the prior auction, the opening, value, and the developing point of control. Dale gives more explicit footprint rules for defining a potential retest and evaluating the local reaction.

## Terms that need distinct labels

| Term | Measurement | Source |
|---|---|---|
| TPO POC | Price with the most visits across time brackets in a declared range. | Forthmann, PDF pp. 19–21 |
| VPOC | Price with the most total executed volume in the declared range. | Forthmann, PDF pp. 22–26 |
| Footprint node | Highest combined bid and ask volume at a price within one bar. Consecutive bars can share it. | Dale, PDF pp. 26–27, 35–36, 55–59 |
| Thin profile or single print | Thin volume reflects sparse execution. A TPO single print reflects a visit in only one time bracket. | Forthmann, PDF pp. 20–21, 27 |
| Diagonal imbalance | Relative executed volumes at neighboring prices. Dale illustrates a configurable 3-to-1 ratio. Forthmann illustrates a different setting and reads sequences with more discretion. | Dale, PDF pp. 36–38, 65–70. Forthmann, PDF pp. 70–77 |
| Unfinished business or weak auction | Dale checks for bid and ask prints at a footprint extreme. Forthmann discusses nearly equal highs or lows as a chart-level weak extreme. | Dale, PDF pp. 38–41, 71–79. Forthmann, PDF pp. 59–60 |

## What to record in a replay

1. Freeze the instrument and session, prior high and low, overnight extremes, prior value area and control prices before the setup begins.
2. Record the first sweep, reclaim, or separation from a marked zone with an observable timestamp. Keep developing profile values at the time they were visible.
3. Record whether aggression extends price, stalls at the reference, or flips afterward. Keep executed delta and resting depth as separate fields.
4. If evaluating the repository's discretionary setup, also record the confirmed break of structure, the pullback, and the time of invalidation. That makes it possible to compare the price-only setup with the same setup plus order-flow evidence.
5. Measure subsequent response from the first tradable time after confirmation. Record unsuccessful candidates and check the effect in later sessions.

Large prints and a stall can support an absorption interpretation. They identify neither the trader nor its net position. Accurate footprint or CVD work needs trades by price and aggressor side, or a separately validated reconstruction. Standard OHLCV bars and option-contract caches cannot recreate that measurement by themselves.

## Study notes

- [[Books/order-flow-trading-setups/00 Overview|Order Flow Trading Setups]]
- [[Books/volume-profile-market-profile-order-flow-next-generation-of-daytrading/00 Overview|Volume Profile, Market Profile, Order Flow]]

Six source-linked hypotheses are in [the experiment file](../../experiments/hypotheses_order_flow_profiles.json). Each defines a comparison and an outcome for a future test.
