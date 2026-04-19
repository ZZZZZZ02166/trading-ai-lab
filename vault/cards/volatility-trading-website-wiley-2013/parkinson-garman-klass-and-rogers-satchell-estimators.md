---
card_id: 1770c813-ab44-42b6-9267-a142745d1c71
doc_id: 1c32b3c0d846
book_title: "Volatility Trading, + Website Wiley (2013)"
author: "Euan Sinclair"
card_type: definition
page_ref: "pp. 38-38"
page_start: 38
page_end: 38
tags:
  - parkinson
  - garman-klass
  - rogers-satchell
  - volatility-estimator
  - efficiency
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Parkinson, Garman-Klass, and Rogers-Satchell Estimators

**Type:** definition
**Source:** Volatility Trading, + Website Wiley (2013) — pp. 38-38

## Summary

Parkinson (1980): σ²_P = [1/(4n ln2)] Σ(ln(Hᵢ/Lᵢ))² Uses only daily high-low range. 4.9× more efficient than CC. Weakness: ignores overnight gaps; underestimates vol when gaps are large. Garman-Klass (1980): σ²_GK = 0.5[ln(H/L)]² − [2ln2−1][ln(C/O)]² Uses O, H, L, C. 7.4× more efficient than CC. Assumes zero drift. Rogers-Satchell (1991): σ²_RS = ln(H/C)ln(H/O) + ln(L/C)ln(L/O) Drift-independent — correct estimator when stock has known trend. Weakness: ignores overnight gap. Compare Parkinson vs CC: if Parkinson >> CC, intraday vol dominates; if CC >> Parkinson, overnight gaps dominate.

## Tags

#parkinson #garman-klass #rogers-satchell #volatility-estimator #efficiency

## Notes

<!-- Personal notes here -->
