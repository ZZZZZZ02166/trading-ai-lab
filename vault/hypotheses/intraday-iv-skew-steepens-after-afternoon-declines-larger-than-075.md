---
hypothesis_id: 9578cb29-dca6-4e41-8b2d-fc5dddb9f3fe
status: candidate
confidence: 0.76
tags: ['intraday', 'volatility-skew', 'otm-puts', 'leverage-effect', 'insurance-demand', 'afternoon-decline']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Intraday IV Skew Steepens After Afternoon Declines Larger Than 0.75%

**Status:** candidate | **Confidence:** ███████░░░ 76%

#intraday #volatility_skew #otm_puts #leverage_effect #insurance_demand #afternoon_decline

## Claim

When SPX declines by more than 0.75% between 13:00 and 15:00 ET, the 25-delta put IV skew (25D put IV minus ATM IV) steepens by an average of 0.8–1.5 vol points within 30 minutes of the move. This intraday skew steepening is significantly larger than what BSM predicts from a static vol surface moved along the sticky-strike model, confirming that demand for downside protection intensifies non-linearly with afternoon declines.

## Rationale

The volatility skew theme in this knowledge base documents that OTM put premium is driven by structural insurance demand. In intraday terms, afternoon declines trigger institutional hedging flows specifically in OTM puts, because portfolio managers face end-of-day mark-to-market and cannot wait until the next morning to hedge. This creates a reflexive feedback: declining prices → increased put demand → IV skew steepening → higher put prices → further cost of hedging. Sinclair and Natenberg both note that the relationship between spot moves and IV changes (the leverage effect) is steeper for OTM puts than for ATM options, making the skew a non-linear function of directional pressure.

## How to Test

Using ORATS intraday IV surface snapshots and SPX 5-minute data 2015–2023: identify sessions where SPX falls > 0.75% between 13:00 and 15:00 ET. Measure 25D put IV minus ATM IV at 13:00 and at 15:00. Compare skew change on these sessions to matched sessions where SPX is flat (< 0.2% move) in the same window. Falsified if the skew change in down-afternoon sessions is not significantly larger than in flat sessions. Secondary: measure how much of the skew change reverts by market close.

**Data required:** ORATS intraday IV surface (25D put, ATM) snapshots 2015–2023; SPX 5-minute prices

### Variables Needed

- `implied_volatility`
- `volatility_skew`
- `otm_put_iv`
- `intraday_returns`

### What Would Support It

Average 25D skew steepening > 0.8 vol points on days with afternoon decline > 0.75%; significantly larger than flat-session control group

### What Would Falsify It

No significant skew change vs. flat sessions, or skew moves symmetrically (both put and call IV rise equally)

## Source Themes

- [[Volatility Skew and Structural OTM Put Premium]]
- [[Delta and Moneyness: Directional Sensitivity]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
