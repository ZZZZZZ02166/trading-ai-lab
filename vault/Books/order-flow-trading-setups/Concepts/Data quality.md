---
doc_id: "3605e0c990fe"
book_title: "Order Flow Trading Setups"
author: "Trader Dale"
file_path: "books/Order-Flow-Trading-Setups-1.pdf"
page_start: 17
page_end: 61
tag: "data_quality"
---

# Data quality

- **Footprints Need Venue-Level Executed Volume**. Centralized futures data lets the analyst observe executed size by price and side for that contract. Spot FX is decentralized, so a feed from one broker gives only a partial view of spot activity. Dale uses currency futures for analysis and maps the levels separately when executing in spot. [PDF pp. 17–19](../../../../books/Order-Flow-Trading-Setups-1.pdf#page=17)
- **Map Currency Futures Levels Before Spot Execution**. Currency futures and spot pairs can use different quotation directions and price scales. Dale compares them side-by-side and uses an inverse display where appropriate. A corresponding swing or zone must be mapped to the execution instrument. [PDF pp. 19–20](../../../../books/Order-Flow-Trading-Setups-1.pdf#page=19)
- **A Large-Trade Filter Misses Split Execution**. The filter highlights single executions above a configurable size. Dale's 25-lot illustration is calibrated to his currency-futures example, and activity varies by instrument and session. Small clips and iceberg replenishment can be missed by a large-print cutoff. [PDF pp. 60–61](../../../../books/Order-Flow-Trading-Setups-1.pdf#page=60)
