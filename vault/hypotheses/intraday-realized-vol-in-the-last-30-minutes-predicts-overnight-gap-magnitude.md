---
hypothesis_id: cad085ea-ad74-489b-b4e6-9bba3d8d08a6
status: candidate
confidence: 0.72
tags: ['intraday', 'realized-volatility', 'overnight-gap', 'yang-zhang', 'close-vol', 'forecasting']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Intraday Realized Vol in the Last 30 Minutes Predicts Overnight Gap Magnitude

**Status:** candidate | **Confidence:** ███████░░░ 72%

#intraday #realized_volatility #overnight_gap #yang_zhang #close_vol #forecasting

## Claim

The annualised realised volatility of SPX computed from the last 30 minutes of the trading session (15:30–16:00 ET) is a better predictor of the subsequent overnight gap (|next open - prior close| / prior close) than either the full-day realised vol or the ATM implied volatility. When last-30-min vol exceeds the daily average 30-min vol by more than 2×, the overnight gap is on average 40% larger than the base rate.

## Rationale

The final 30 minutes of trading concentration large institutional portfolio rebalancing flows (mutual fund end-of-day pricing, index rebalancing, options expiration pinning). These flows often represent information about upcoming overnight developments — hedge funds positioning for overnight news, institutions reducing risk before close. Sinclair's Yang-Zhang estimator explicitly separates overnight and intraday vol components because they are driven by different processes. If the close-period vol reflects genuine information rather than noise, it should predict the overnight gap better than a full-day average that dilutes this signal.

## How to Test

Using SPX 5-minute data 2010–2023: compute last-30-minute annualised vol and full-day average 30-min vol for each trading day. Compute next-day overnight gap = |open(t+1) - close(t)| / close(t). Regress overnight gap on last-30-min vol, full-day average vol, and ATM IV (from ORATS close-of-day). Compare R² and coefficient significance across the three predictors. Falsified if last-30-min vol is not a significantly better predictor than full-day vol, or has no significant positive relationship with overnight gap.

**Data required:** SPX 5-minute OHLC 2010–2023; ORATS end-of-day ATM IV

### Variables Needed

- `last_30min_realized_vol`
- `overnight_gap`
- `full_day_realized_vol`
- `implied_volatility`

### What Would Support It

Last-30-min vol has higher R² for predicting overnight gap than full-day vol or ATM IV; when last-30-min vol > 2× daily average, overnight gap is > 40% larger than base rate

### What Would Falsify It

ATM IV or full-day vol outperforms last-30-min vol in predicting overnight gap, or no significant relationship

## Source Themes

- [[High-Efficiency Volatility Estimators: Parkinson, Garman-Klass, Rogers-Satchell]]
- [[Delta-Neutral Trading and Gamma Scalping]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
