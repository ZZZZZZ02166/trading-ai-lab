---
hypothesis_id: 45b2f3a6-6abb-432a-a82e-c6199d811f78
status: candidate
confidence: 0.79
tags: ['earnings', 'vol-crush', 'implied-volatility', 'vega', 'iv-percentile']
created_at: 2026-04-15T17:21:21.371736Z
model_used: claude-sonnet-4-6
---

# Earnings Vol Crush Magnitude Correlates With Pre-Announcement IV Percentile Rank

**Status:** candidate | **Confidence:** ███████░░░ 79%

#earnings #vol_crush #implied_volatility #vega #iv_percentile

## Claim

The magnitude of implied volatility crush following an earnings announcement correlates positively with the pre-announcement IV expressed as a percentile rank within the stock's own 1-year IV history. Stocks in the top IV decile pre-earnings experience vol crush greater than 30% on average, making long-vega positions entered more than 5 days before earnings systematically unprofitable.

## Rationale

The vega and earnings vol crush theme in this knowledge base documents that IV inflation ahead of earnings is driven by uncertainty resolution demand, and that the crush post-announcement is mechanical — uncertainty resolves regardless of the outcome. Multiple books agree that the expected move implied by options is usually larger than the actual move, creating a systematic premium. The key testable refinement is whether the IV percentile rank (a relative measure of 'how elevated is this IV vs. history') predicts the crush magnitude better than absolute IV. This matters for position sizing: a stock normally at 30% vol trading at 70% vol pre-earnings has more to lose post-announcement than one normally at 60% vol trading at 65%.

## How to Test

Using ORATS earnings IV data 2010-2023: for each earnings event, compute pre-announcement ATM IV (5 days before) and post-announcement ATM IV (1 day after). Compute IV percentile rank within trailing 1-year IV history for each stock. Bucket into quartiles by percentile rank. Measure average vol crush (IV before - IV after) per quartile. Falsified if top-quartile IV-rank events do not show significantly larger vol crush than bottom-quartile events. Secondary test: does entering long-vega 10 days before high-IV-rank earnings produce negative expected P&L across 200+ events?

**Data required:** ORATS earnings IV surface data 2010-2023, 1-year rolling IV history per ticker

### Variables Needed

- `implied_volatility`
- `vega`
- `vol_crush`
- `iv_percentile_rank`

### What Would Support It

Top-quartile IV-rank events show > 25% average vol crush; bottom-quartile shows < 10%; statistically significant difference

### What Would Falsify It

No significant difference in vol crush across IV-rank quartiles, or inverted relationship (low-IV-rank stocks crush more)

## Source Themes

- [[Vega and Implied Volatility: The Earnings Vol Crush]]
- [[Implied Volatility Mean Reversion and Variance Swaps]]

## Source Books

- `230dde96f8a4`
- `b1f5afe25863`
- `ddc2a298cd88`
- `9e3a85506c46`
