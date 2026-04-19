---
card_id: 260ce9e8-47f4-49b9-aae4-69f6db3980a1
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: concept
page_ref: "pp. 2712-2723"
page_start: 2712
page_end: 2723
tags:
  - historical-volatility
  - lookback-window
  - 20-day
  - 60-day
  - forecasting
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Lookback Window Choice in HV Calculation

**Type:** concept
**Source:** Option Volatility and Pricing — pp. 2712-2723

## Summary

The lookback period for historical volatility represents a tradeoff: (1) Short window (20 days): responsive to recent vol changes, noisy; (2) Medium window (60 days): balanced; (3) Long window (252 days): stable, slow to react to vol regime changes. Most practitioners compare multiple lookbacks simultaneously: 20-day vs. 60-day vs. 252-day HV. When short-term HV > long-term HV, vol is elevated (backwardation-like); when short < long, vol is below its long-run average (normal conditions). The comparison informs whether current IV is elevated or depressed relative to recent realized vol.

## Tags

#historical-volatility #lookback-window #20-day #60-day #forecasting

## Notes

<!-- Personal notes here -->
