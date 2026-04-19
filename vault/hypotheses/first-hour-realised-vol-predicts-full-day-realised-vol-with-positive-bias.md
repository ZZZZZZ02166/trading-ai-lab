---
hypothesis_id: 814304fb-a5be-410f-a56a-b8a1b8a3bd19
status: candidate
confidence: 0.74
tags: ['intraday', 'realized-volatility', 'first-hour', 'mean-reversion', 'delta-hedging', 'entry-timing']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# First-Hour Realised Vol Predicts Full-Day Realised Vol With Positive Bias

**Status:** candidate | **Confidence:** ███████░░░ 74%

#intraday #realized_volatility #first_hour #mean_reversion #delta_hedging #entry_timing

## Claim

The annualised realised volatility of SPX computed from the first 60 minutes of trading (9:30–10:30 ET) overestimates full-day realised volatility on average. When first-hour vol exceeds the prior day's ATM IV by more than 2 percentage points, delta-hedging a short straddle sold at 10:30 ET using the first-hour vol as the hedge ratio generates lower residual P&L variance than using overnight IV.

## Rationale

The opening auction resolves overnight information, creating a burst of realised vol that often does not persist through the full session. Sinclair's work on vol estimators shows that intraday vol is highly autocorrelated at short horizons but mean-reverts at longer horizons. If the first hour vol is a biased-upward predictor of full-day vol, then entering a short straddle after the open burst — when the opening vol has dissipated but the IV has not yet repriced — captures the mean reversion in realised vol. Yang-Zhang handles the overnight gap separately, which is relevant here because the first-hour excess vol often traces to the gap open rather than sustained directional pressure.

## How to Test

Using SPX 1-minute data 2010–2023: compute first-hour annualised realised vol (9:30–10:30) and full-day realised vol daily. Regress full-day vol on first-hour vol — measure the coefficient and R². Test whether first-hour vol systematically overestimates full-day vol. Secondary: for days where first-hour vol > prior ATM IV by > 2pp, enter short ATM straddle at 10:30 ET and hold to close — measure P&L distribution. Falsified if first-hour vol is an unbiased predictor of full-day vol, or if the 10:30 entry has negative expected P&L.

**Data required:** SPX 1-minute OHLC 2010–2023; ORATS ATM IV at open and 10:30 ET

### Variables Needed

- `first_hour_realized_vol`
- `full_day_realized_vol`
- `implied_volatility`
- `straddle_pnl`

### What Would Support It

First-hour vol > full-day vol on > 55% of days; regression coefficient < 1.0; 10:30 entry generates positive average P&L

### What Would Falsify It

First-hour vol is an unbiased predictor (coefficient ≈ 1.0, intercept ≈ 0), or 10:30 entry has no edge

## Source Themes

- [[Delta-Neutral Trading and Gamma Scalping]]
- [[High-Efficiency Volatility Estimators: Parkinson, Garman-Klass, Rogers-Satchell]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
