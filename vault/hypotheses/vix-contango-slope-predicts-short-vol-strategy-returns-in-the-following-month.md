---
hypothesis_id: 5c8f6f43-6607-47f4-9fd5-403e592d15a6
status: candidate
confidence: 0.82
tags: ['vix', 'contango', 'term-structure', 'short-vol', 'variance-premium']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# VIX Contango Slope Predicts Short-Vol Strategy Returns in the Following Month

**Status:** candidate | **Confidence:** ████████░░ 82%

#vix #contango #term_structure #short_vol #variance_premium

## Claim

When the VIX futures term structure is in contango (front-month VIX futures below second-month), short volatility strategies earn higher returns in the following 21 days compared to periods of backwardation. The steepness of the contango slope — measured as (M2 VIX - M1 VIX) / M1 VIX — correlates positively with subsequent short-vol P&L.

## Rationale

Sinclair's analysis of VIX term structure shows that contango is the normal regime, reflecting the market's tendency to over-price future uncertainty. Natenberg's treatment of calendar spreads explains why front-month premium decays faster than back-month in contango. Multiple books in this knowledge base — including those on VIX futures mechanics and term structure trading — agree that contango encodes a structural roll yield that accrues to short near-term vol positions. The meta-theme on Volatility Regime Dynamics synthesises these views: IV mean reversion is faster and more reliable in contango regimes because the structural selling pressure from VIX ETP rebalancers reinforces the premium decay.

## How to Test

Using CBOE VIX futures daily settlement data (2004-2023), measure contango slope each Monday as (VX2 - VX1) / VX1. Run 21-day short VIX futures position (short front-month, roll before expiry). Separate returns into contango vs. backwardation periods. Falsified if average 21-day return in contango periods is not significantly higher than in backwardation. Use OLS regression of contango slope on next-21d return to test the dose-response relationship.

**Data required:** CBOE VIX futures daily settlement data 2004-2023, monthly expiration calendar

### Variables Needed

- `vix_futures_term_structure`
- `contango_slope`
- `short_vol_returns`

### What Would Support It

Statistically significant positive correlation (r > 0.2) between contango slope and next-21d short-VIX returns; higher Sharpe in contango regime

### What Would Falsify It

No significant difference in returns between contango and backwardation periods, or negative returns even in steep contango

## Source Themes

- [[Volatility Term Structure: Contango, Backwardation, and Calendar Spreads]]
- [[Implied Volatility Mean Reversion and Variance Swaps]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
- `9e3a85506c46`
- `1c32b3c0d846`
