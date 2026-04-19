---
hypothesis_id: 79c1efe0-14d5-41fe-ae60-2a68dff73f8c
status: candidate
confidence: 0.83
tags: ['intraday', 'leverage-effect', 'implied-volatility', 'asymmetry', 'microstructure', 'vol-sensitivity']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Intraday Leverage Effect: IV Responds Asymmetrically to Up vs. Down SPX Moves Within 5 Minutes

**Status:** candidate | **Confidence:** ████████░░ 83%

#intraday #leverage_effect #implied_volatility #asymmetry #microstructure #vol_sensitivity

## Claim

For SPX moves of equal magnitude, a 1% downward move causes a larger increase in ATM implied volatility (on average 1.2–1.8 vol points) than the IV decrease caused by a 1% upward move (on average 0.6–0.9 vol points). This asymmetry is measurable at the 5-minute level and is larger during the first and last hour of trading, when vol sensitivity to price is highest.

## Rationale

The BSM assumptions and leverage effect theme in this knowledge base documents the well-established negative correlation between equity returns and implied volatility. At intraday timescales, this relationship is sharper and more immediate: market makers adjust their IV quotes within minutes of a move because their delta-neutral books become directionally exposed on down-moves (they are typically net long delta from selling puts). The asymmetry — IV rises more on down-moves than it falls on up-moves of equal size — is a direct consequence of convex demand for downside protection. Sinclair quantifies the leverage effect empirically across multiple markets.

## How to Test

Using SPX 5-minute returns and matched 5-minute IV snapshots (ORATS or LiveVol) 2015–2023: regress 5-minute ATM IV change on 5-minute SPX return separately for positive and negative returns. Compute the coefficient for down-moves and up-moves and test whether they are significantly different (asymmetry test). Separately estimate the coefficients in first-hour (9:30–10:30) and last-hour (15:00–16:00) vs. midday. Falsified if the coefficient magnitudes for up and down moves are statistically indistinguishable, or if the asymmetry is not larger in the first/last hour.

**Data required:** SPX 5-minute returns and ATM IV snapshots from ORATS or LiveVol 2015–2023

### Variables Needed

- `implied_volatility`
- `intraday_returns`
- `leverage_effect`
- `vol_sensitivity`

### What Would Support It

Down-move IV coefficient significantly larger in magnitude than up-move IV coefficient (p < 0.05); asymmetry ratio > 1.5; effect stronger at open/close

### What Would Falsify It

Symmetric IV response to up and down moves of equal magnitude, or reversal (IV rises more on up-moves)

## Source Themes

- [[Black-Scholes-Merton Assumptions and Their Violations]]
- [[Delta and Moneyness: Directional Sensitivity]]
- [[Volatility Skew and Structural OTM Put Premium]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `1c32b3c0d846`
