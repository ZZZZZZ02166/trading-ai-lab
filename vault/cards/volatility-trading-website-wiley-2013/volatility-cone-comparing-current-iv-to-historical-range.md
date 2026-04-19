---
card_id: 5ac8f839-73fc-4255-a4e1-180ee19abd80
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: strategy_idea
page_ref: "pp. 73-73"
page_start: 73
page_end: 73
tags:
  - volatility-cone
  - implied-volatility
  - historical-vol
  - relative-value
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Volatility Cone: Comparing Current IV to Historical Range

**Type:** strategy_idea
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 73-73

## Summary

Figure 4.3 shows the MSFT volatility cone (2-year history): For each horizon (30/60/120/240 days), plot max/mean/median/min of historical realized vol over rolling windows of that length. Table 4.1 MSFT data: 30-day (max 0.843, median 0.317, min 0.058); 60-day (max 0.655, median 0.287); 120-day (median 0.258); 240-day (median 0.170). Use: If ATM IV for a given expiry plots above the historical max cone for that horizon, the option is historically expensive. If near min, it is cheap. Critical: cone only shows historical precedent — does not tell you whether current conditions justify elevated vol. Combine with GARCH forecast and IV comparison.

## Tags

#volatility-cone #implied-volatility #historical-vol #relative-value

## Notes

<!-- Personal notes here -->
