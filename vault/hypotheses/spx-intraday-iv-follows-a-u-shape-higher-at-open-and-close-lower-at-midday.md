---
hypothesis_id: 7701237a-6f4d-4fad-9630-ddb17fe5dabe
status: candidate
confidence: 0.78
tags: ['intraday', 'implied-volatility', 'realized-volatility', 'straddle', 'microstructure', 'u-shape']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# SPX Intraday IV Follows a U-Shape: Higher at Open and Close, Lower at Midday

**Status:** candidate | **Confidence:** ███████░░░ 78%

#intraday #implied_volatility #realized_volatility #straddle #microstructure #u_shape

## Claim

When SPX ATM options are priced at the open (9:30–10:00 ET), implied volatility is elevated relative to the subsequent midday period (11:30–13:30 ET). Specifically, when opening IV exceeds midday IV by more than 1 vol point, selling an ATM straddle at the open and buying it back at midday generates positive premium capture on average. The variance risk premium is highest at open because the IV embeds uncertainty about the session's direction that dissipates as intraday information is processed.

## Rationale

Market microstructure theory predicts that information asymmetry is highest at the open (overnight news resolution) and close (portfolio rebalancing flows), driving wider bid-ask spreads and elevated IV. The midday period is characterised by lower volume, lower directional pressure, and therefore lower realised vol — which should translate into IV compression. Sinclair's discussion of intraday realised vol patterns supports the observation that hourly realised vol is non-uniform across the trading day. If IV at the open consistently overestimates subsequent intraday realised vol by a measurable margin, selling the open and buying back at midday is a systematic edge.

## How to Test

Using SPX 1-minute OHLC data and ORATS intraday IV snapshots (if available) or reconstructed from bid-ask midpoints of ATM options 2015–2023: compute 30-minute realised vol buckets (9:30–10:00, 10:00–10:30 … 15:30–16:00). Separately compute ATM IV at each 30-minute interval. Measure IV-HV gap per time bucket. Falsified if the open/close IV-HV gap is not significantly larger than midday gap. Secondary test: backtest open-sell / midday-buy ATM straddle across 200+ trading days.

**Data required:** SPX 1-minute OHLC data 2015–2023; intraday ATM IV snapshots from ORATS or CBOE LiveVol

### Variables Needed

- `implied_volatility`
- `realized_volatility`
- `intraday_vol_pattern`
- `straddle_pnl`

### What Would Support It

Open/close IV-HV gap > midday gap by > 1 vol point on average; open-sell/midday-buy straddle Sharpe > 0.3

### What Would Falsify It

No significant intraday IV pattern, or midday IV higher than open IV on average

## Source Themes

- [[Gamma and Theta: The Core Greeks Tradeoff]]
- [[Historical vs. Implied Volatility: Forecasting and the Variance Premium]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
