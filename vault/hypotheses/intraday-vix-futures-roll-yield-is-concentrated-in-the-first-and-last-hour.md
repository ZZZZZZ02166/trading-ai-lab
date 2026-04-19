---
hypothesis_id: 32b07c46-1a32-450c-bcb0-955a456f655a
status: candidate
confidence: 0.7
tags: ['intraday', 'vix', 'contango', 'roll-yield', 'term-structure', 'time-of-day']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Intraday VIX Futures Roll Yield Is Concentrated in the First and Last Hour

**Status:** candidate | **Confidence:** ███████░░░ 70%

#intraday #vix #contango #roll_yield #term_structure #time_of_day

## Claim

The daily returns from holding short VIX front-month futures (contango roll yield) are not earned uniformly throughout the trading session. When vol sensitivity is highest — during the first 60 minutes (9:30–10:30 ET) and the final 30 minutes (15:30–16:00 ET) — approximately 60–70% of the daily contango roll yield accrues. The midday implied volatility mean-reversion is slower, contributing less than 30% of total daily roll. Strategies that are short VIX futures only during opening and closing windows would capture most of the contango return with significantly lower intraday exposure.

## Rationale

The VIX term structure and contango theme in this knowledge base establishes that the roll yield is a structural feature driven by mean reversion of front-month IV to back-month levels. Intraday, this mean reversion is not uniform: institutional hedging demand is highest at open and close, causing IV to be temporarily elevated in these windows. The VIX front-month future's price relative to fair-value spot VIX should therefore be largest (most overpriced) at open and close, meaning the decay is concentrated there. If true, partial-day exposure strategies (open + close only) can extract most of the contango yield while avoiding the flat midday period where the carry is lower and bid-ask friction is proportionally larger.

## How to Test

Using VIX front-month futures 15-minute settlement data from CBOE 2010–2023: compute the returns from holding short VIX futures in each 30-minute intraday window (9:30–10:00, 10:00–10:30 … 15:30–16:00). Aggregate returns by window across contango periods only. Compare the sum of first-60-min and last-30-min returns to total daily return. Falsified if roll yield is distributed uniformly across windows (i.e., each 30-minute window contributes equally, at 1/13 of total). Test if open+close-only exposure achieves > 55% of full-day return with < 40% of full-day exposure time.

**Data required:** CBOE VIX front-month futures 15-minute or 30-minute intraday settlement data 2010–2023

### Variables Needed

- `vix_futures`
- `contango`
- `roll_yield`
- `intraday_returns`
- `time_of_day`

### What Would Support It

Open 60-min + close 30-min periods contribute > 55% of total daily roll yield in contango regimes; statistically significant concentration

### What Would Falsify It

Roll yield uniformly distributed across intraday windows; open+close-only exposure captures < 40% of full-day return

## Source Themes

- [[Volatility Term Structure: Contango, Backwardation, and Calendar Spreads]]
- [[Implied Volatility Mean Reversion and Variance Swaps]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
- `ddc2a298cd88`
