---
card_id: c9ff1022-51f9-402e-84a2-14359abbd1ce
doc_id: 9e3a85506c46
book_title: "Option Volatility and Pricing"
author: "Sheldon Natenberg"
card_type: mechanism
page_ref: "pp. 1582-1583"
page_start: 1582
page_end: 1583
tags:
  - vertical-spread
  - bull-spread
  - bear-spread
  - defined-risk
  - payoff-bounded
created_at: 2026-04-15
model_used: claude-sonnet-4-6
---

# Vertical Spread Payoff: Bounded Between 0 and Spread Width

**Type:** mechanism
**Source:** Option Volatility and Pricing — pp. 1582-1583

## Summary

A vertical spread (long lower strike / short upper strike call, or long upper / short lower put) always expires between 0 and the spread width. A 100/105 call vertical: expires at $0 if underlying < 100, at $5 if underlying > 105. A 95/105 put vertical: worth $0 if market > 105, $10 if market < 95. The bounded payoff defines maximum profit and maximum loss — both are known at entry. Trading range: always within [0, spread width]. This makes verticals ideal for expressing directional views with defined risk.

## Tags

#vertical-spread #bull-spread #bear-spread #defined-risk #payoff-bounded

## Notes

<!-- Personal notes here -->
