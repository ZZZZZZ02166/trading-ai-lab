---
card_id: cb78d30f-1c91-41bf-a18e-d9c2cdc9cb7f
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: concept
page_ref: "pp. 2724-2734"
page_start: 2724
page_end: 2734
tags:
  - historical-volatility
  - parkinson
  - garman-klass
  - high-low
  - efficiency
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Parkinson and Garman-Klass: High-Low Volatility Estimators

**Type:** concept
**Source:** Option Volatility and Pricing — pp. 2724-2734

## Summary

Two efficiency-improving HV estimators using intraday data: (1) Parkinson (1980): uses daily high and low prices; requires fewer data points to achieve same accuracy as close-to-close. Formula uses the squared range: σ² ∝ Σ(ln(H/L))². (2) Garman-Klass (1980): uses open, high, low, close; further improves efficiency. Both produce consistently lower volatility estimates than close-to-close because they exclude overnight gaps. Applicable only during continuous trading hours. For assets with significant overnight price gaps (earnings, gaps on news), these estimators understate true volatility. Use close-to-close for assets with frequent gaps.

## Tags

#historical-volatility #parkinson #garman-klass #high-low #efficiency

## Notes

<!-- Personal notes here -->
