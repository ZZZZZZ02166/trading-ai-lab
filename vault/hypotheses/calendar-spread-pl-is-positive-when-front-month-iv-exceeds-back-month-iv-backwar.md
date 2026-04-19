---
hypothesis_id: 53db34b5-9a5c-459b-a69a-a05cec4f85b4
status: candidate
confidence: 0.76
tags: ['calendar-spread', 'term-structure', 'backwardation', 'implied-volatility', 'mean-reversion']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Calendar Spread P&L Is Positive When Front-Month IV Exceeds Back-Month IV (Backwardation Entry)

**Status:** candidate | **Confidence:** ███████░░░ 76%

#calendar_spread #term_structure #backwardation #implied_volatility #mean_reversion

## Claim

When the VIX term structure is in backwardation (front-month IV > back-month IV), buying a calendar spread — long back-month, short front-month — generates positive average returns as the term structure mean-reverts to contango. The calendar spread profits from both the roll yield and the relative IV convergence, with Sharpe above 0.5 in the month following backwardation entry.

## Rationale

The volatility term structure theme documents that contango is the normal state and backwardation is a crisis-driven dislocation that reliably reverts. Sinclair's GARCH term structure analysis shows that GARCH forecasts mean reversion in volatility: when front-month IV spikes above back-month, GARCH predicts front-month will decay while back-month stays anchored — exactly the dynamic that benefits a calendar spread. Natenberg's calendar spread mechanics confirm that the position profits when short-maturity vol falls relative to long-maturity vol. The combination of mean reversion bias and contango structural pull creates a predictable convergence trade in backwardation.

## How to Test

Using ORATS or CBOE monthly SPX options data 2005-2023: identify months where 1-month ATM IV > 2-month ATM IV (backwardation). Enter long 2-month, short 1-month ATM calendar spread. Hold for 21 days, measuring P&L as the spread narrows. Compare to control periods of contango (normal). Falsified if calendar spread P&L in backwardation entry periods is not positive on average, or if the Sharpe is below 0.0. Test whether steeper backwardation (larger front-month premium) predicts larger subsequent P&L.

**Data required:** ORATS or CBOE SPX options with 1-month and 2-month ATM IV series 2005-2023

### Variables Needed

- `term_structure`
- `implied_volatility`
- `calendar_spread_pnl`
- `backwardation_slope`

### What Would Support It

Positive average calendar spread P&L in backwardation entries; Sharpe > 0.5; steepness of backwardation positively correlated with P&L

### What Would Falsify It

Negative or zero average P&L in backwardation entries, or no significant difference vs. contango-entry baseline

## Source Themes

- [[Volatility Term Structure: Contango, Backwardation, and Calendar Spreads]]
- [[Implied Volatility Mean Reversion and Variance Swaps]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `1c32b3c0d846`
- `ddc2a298cd88`
