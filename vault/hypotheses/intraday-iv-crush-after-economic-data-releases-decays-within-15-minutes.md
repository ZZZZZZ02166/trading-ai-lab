---
hypothesis_id: 730f4110-d823-4f5a-9f7d-8321ed58e66b
status: candidate
confidence: 0.77
tags: ['intraday', 'vol-crush', 'macro-release', 'implied-volatility', 'vega', 'event-vol']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Intraday IV Crush After Economic Data Releases Decays Within 15 Minutes

**Status:** candidate | **Confidence:** ███████░░░ 77%

#intraday #vol_crush #macro_release #implied_volatility #vega #event_vol

## Claim

Following a scheduled macroeconomic release (CPI, NFP, FOMC minutes) that does not exceed consensus expectations by more than 1 standard deviation, implied volatility for SPX ATM options decreases by an average of 2–5 vol points within 15 minutes of the release, and this IV crush is largely complete within 30 minutes. Selling ATM straddles 5 minutes after the release and holding for 25 minutes captures positive premium decay in non-surprise releases.

## Rationale

The earnings vol crush theme in this knowledge base applies at a micro-level to any uncertainty-resolution event: options embed a premium for the upcoming information event, and when the release is in-line with expectations, the uncertainty resolves and IV collapses. The vega theme establishes that IV crush is proportional to vega and the magnitude of the pre-release premium. For macro releases specifically, the IV premium is front-loaded into the minutes before the release, and its decay is rapid. Sinclair's volatility trading framework implies that any event-driven IV premium is systematically overpriced relative to realised post-event vol in non-surprise scenarios.

## How to Test

Using ORATS intraday IV snapshots on CPI and NFP release days 2015–2023: measure ATM IV 5 minutes before release, 5 minutes after, 15 minutes after, and 30 minutes after. Classify releases as 'surprise' (|actual - consensus| > 1 SD) or 'in-line'. Compute IV change separately for each group. For in-line releases: backtest selling ATM straddle 5 minutes post-release, closing 25 minutes post-release. Falsified if IV crush in in-line releases is not significantly larger than on non-release days, or if post-release straddle P&L is negative.

**Data required:** ORATS or LiveVol intraday IV snapshots on CPI/NFP dates 2015–2023; Bloomberg consensus vs. actual data

### Variables Needed

- `implied_volatility`
- `iv_crush`
- `straddle_pnl`
- `macro_release_surprise`

### What Would Support It

Average IV drop > 2 vol points within 15 minutes of in-line release; post-release straddle P&L positive on > 60% of in-line days

### What Would Falsify It

No significant IV drop after in-line releases, or IV drops equally on non-release days of similar magnitude

## Source Themes

- [[Vega and Implied Volatility: The Earnings Vol Crush]]
- [[Implied Volatility Mean Reversion and Variance Swaps]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
