---
hypothesis_id: d7a4665f-9e2d-4297-8263-e487a2c9073e
status: candidate
confidence: 0.75
tags: ['intraday', '0dte', 'straddle', 'mean-reversion', 'entry-filter', 'variance-premium']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# 0DTE Straddle P&L Variance Is Lower When Sold After a Large Morning Move Has Partially Reverted

**Status:** candidate | **Confidence:** ███████░░░ 75%

#intraday #0dte #straddle #mean_reversion #entry_filter #variance_premium

## Claim

A 0DTE SPX ATM straddle sold after the following condition is met — SPX has moved > 0.6% from open by 10:00 ET and then retraced at least 30% of that move by 10:30 ET — exhibits lower P&L variance and higher Sharpe than a 0DTE straddle sold at a fixed time (10:30 ET) without the reversion filter. The reversion-entry filter identifies sessions where the initial vol burst has dissipated, leaving residual IV premium without the underlying directional pressure.

## Rationale

The combination of the first-hour vol and intraday mean-reversion themes in this knowledge base implies that the 10:00–11:00 window after a large open move has two characteristics useful to a short-vol trader: (1) IV remains elevated from the opening burst, and (2) directional pressure has partially resolved. Selling straddles into this configuration — high IV, reduced directionality — captures the variance premium at a moment when the realised-vol-to-come is likely lower than the still-elevated IV. This is an intraday analogue of the overnight to 10:30 vol mean reversion.

## How to Test

Using SPX 5-minute data and ORATS intraday IV from 2022–2023 (0DTE era): identify days where SPX moves > 0.6% from open by 10:00 ET AND retraces > 30% of that move by 10:30 ET. Sell ATM 0DTE straddle at 10:30 ET on qualifying days. Benchmark: sell ATM 0DTE straddle at 10:30 ET on all days. Compare P&L mean, standard deviation, Sharpe across 100+ qualifying days vs. all days. Falsified if conditional-entry Sharpe is not significantly higher than unconditional entry, or if P&L variance is not lower.

**Data required:** SPX 5-minute prices and ORATS 0DTE ATM IV intraday snapshots 2022–2023

### Variables Needed

- `straddle_pnl`
- `pnl_variance`
- `sharpe`
- `0dte`
- `intraday_returns`
- `reversion_filter`

### What Would Support It

Conditional-entry Sharpe > unconditional-entry Sharpe by > 20%; P&L standard deviation lower by > 15% in conditional-entry group

### What Would Falsify It

No significant Sharpe or variance difference between conditional and unconditional entry, or the reversion filter produces fewer trades without improvement

## Source Themes

- [[Straddle Strategies: Long and Short Volatility Expressions]]
- [[Delta-Neutral Trading and Gamma Scalping]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `1c32b3c0d846`
