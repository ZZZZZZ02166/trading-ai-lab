---
hypothesis_id: 788cee78-6708-473e-b5d8-9837b7ed9433
status: candidate
confidence: 0.76
tags: ['0dte', 'intraday', 'straddle', 'theta', 'gamma', 'entry-timing']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# 0DTE Straddle Sold at Market Open Has Higher Expected P&L Than One Sold at Noon

**Status:** candidate | **Confidence:** ███████░░░ 76%

#0dte #intraday #straddle #theta #gamma #entry_timing

## Claim

A zero-days-to-expiration (0DTE) SPX ATM straddle sold at 9:45 ET generates higher average P&L than the same structure sold at 12:00 ET, because the morning IV premium embeds a larger variance risk premium relative to the realised intraday vol that follows. The open-sold 0DTE also benefits from the full day's theta decay, whereas the noon-sold position captures only afternoon decay.

## Rationale

0DTE options have become the dominant volume driver in SPX options. Their gamma profile is extreme near ATM — a position sold ATM at open has maximum theta and maximum gamma exposure, but also maximum IV premium if the open IV overestimates actual intraday movement. The U-shaped intraday IV hypothesis supports this: if IV is systematically elevated at the open, the variance risk premium is highest then. Furthermore, a noon-entry 0DTE has already experienced much of the day's vol resolution, so the remaining premium is smaller. The gamma-theta theme in this knowledge base establishes the tradeoff: at 0DTE, theta is enormous, and if realised vol stays below the implied move, the seller wins rapidly.

## How to Test

Using SPX 0DTE options data (ORATS or CBOE LiveVol) from 2022–2023 (since 0DTE daily expirations began in earnest in 2022): for each trading day, record ATM straddle price at 9:45 ET and at 12:00 ET. Simulate selling at each time and closing at 15:45 ET. Compute P&L for each entry time across 200+ days. Falsified if noon-entry P&L is not significantly lower than open-entry P&L, or if open-entry has negative expected P&L. Control for VIX regime and days with large macro events.

**Data required:** SPX 0DTE options intraday snapshots 2022–2023 from ORATS or CBOE LiveVol; SPX 1-minute prices

### Variables Needed

- `implied_volatility`
- `straddle_price`
- `0dte_pnl`
- `theta`
- `intraday_realized_vol`

### What Would Support It

Open-entry average P&L > noon-entry average P&L by > 20%; statistically significant; consistent across VIX regimes

### What Would Falsify It

No significant difference in P&L by entry time, or noon-entry outperforms open-entry

## Source Themes

- [[Gamma and Theta: The Core Greeks Tradeoff]]
- [[Multi-Leg Volatility Strategies: Straddles, Strangles, Butterflies, and Condors]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `1c32b3c0d846`
