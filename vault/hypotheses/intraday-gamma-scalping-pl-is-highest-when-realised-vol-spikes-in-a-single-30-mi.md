---
hypothesis_id: 114dd62a-157f-457e-b81d-a331b00596c6
status: candidate
confidence: 0.82
tags: ['intraday', 'gamma-scalping', 'realized-volatility', 'vol-clustering', 'path-dependency', 'long-gamma']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Intraday Gamma Scalping P&L Is Highest When Realised Vol Spikes in a Single 30-Minute Window

**Status:** candidate | **Confidence:** ████████░░ 82%

#intraday #gamma_scalping #realized_volatility #vol_clustering #path_dependency #long_gamma

## Claim

For a delta-neutral long-gamma position (long straddle) on SPX, the P&L from gamma scalping is highest on days when realised volatility is concentrated in a single 30-minute burst rather than distributed evenly across the session. A burst of 3× average-session vol in a single 30-minute window generates more gamma scalping P&L than three consecutive 30-minute windows each at average-session vol, even when total daily realised vol is equivalent.

## Rationale

Sinclair's discrete hedging P&L formula shows that gamma scalp P&L per hedge ≈ ½ × gamma × (dS)², where dS is the price move per interval. A single large move (3× average) contributes ½ × gamma × (3σΔt)² = 4.5 × gamma × σ²Δt, which is 4.5× larger than the contribution of three average moves. This convexity means that long-gamma positions benefit disproportionately from vol clustering — the same total realised vol delivers more P&L when concentrated. This is a direct, testable consequence of the gamma convexity that multiple books in this knowledge base describe as a core property of long-gamma positions.

## How to Test

Using SPX 5-minute returns 2010–2023: for each trading day, compute 30-minute realised vol buckets. Classify days as 'burst' (max 30-min vol > 2.5× daily average 30-min vol) or 'smooth' (all buckets within 1.5× average). Simulate daily gamma scalping P&L for a synthetic long ATM straddle (using BSM delta with daily ATM IV), rebalancing every 30 minutes. Compare P&L distribution for burst vs. smooth days, controlling for total daily realised vol. Falsified if burst days do not generate significantly higher gamma scalp P&L than smooth days at equal total vol.

**Data required:** SPX 5-minute returns 2010–2023; BSM delta computed from ORATS ATM IV at open

### Variables Needed

- `gamma`
- `realized_volatility`
- `intraday_vol_concentration`
- `gamma_scalp_pnl`

### What Would Support It

Burst days generate > 1.5× gamma scalp P&L vs. smooth days at matched total vol; convexity ratio consistent with theoretical prediction

### What Would Falsify It

No significant P&L difference between burst and smooth days at matched total realised vol

## Source Themes

- [[Delta-Neutral Trading and Gamma Scalping]]
- [[Gamma and Theta: The Core Greeks Tradeoff]]

## Source Books

- `230dde96f8a4`
- `1c32b3c0d846`
- `b1f5afe25863`
