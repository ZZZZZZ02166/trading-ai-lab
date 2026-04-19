---
card_id: 5ad80ff6-3b24-4121-af29-a29986cb11e6
doc_id: a24baf7c9499
book_title: "Positional Option Trading (Wiley Trading)"
author: "Euan Sinclair"
card_type: mechanism
page_ref: "pp. 229–231"
page_start: 229
page_end: 231
tags:
  - dividends
  - bsm_assumptions
  - american_options
  - option_pricing
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Dividend Handling in BSM: Discrete Dividend Adjustment

**Type:** mechanism
**Source:** Positional Option Trading (Wiley Trading) — pp. 229–231

## Summary

For options on dividend-paying stocks, BSM must be adjusted because dividends reduce the stock price. Standard approach: replace spot price S with S − PV(dividends) where PV is discounted present value of known dividends during option life. For a single dividend D paid at time t_D: S_adjusted = S − D·exp(−r·t_D). Error from ignoring dividends grows with dividend yield and option maturity. American options on dividend-paying stocks may be early-exercised just before ex-dividend — European BSM underprices these relative to American pricing models.

## Tags

#dividends #bsm_assumptions #american_options #option_pricing

## Notes

<!-- Personal notes here -->
