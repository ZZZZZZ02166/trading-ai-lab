# Positional Option Trading: An Advanced Guide
*Euan Sinclair — Overview*

---

## What This Book Is About

Positional Option Trading is a rigorous, quantitative guide for traders who want to use options to express both volatility and directional views. Unlike pure market-making books (which aim for delta-neutral, risk-free edge), this book is for speculative traders — people who have a view on volatility levels, direction, or both, and want to translate that view into the most appropriate option structure.

The core argument: **implied volatility persistently overstates subsequent realized volatility** (the variance premium), and this is the most reliable source of edge in options. Everything else — directional forecasts, skew plays, earnings effects — is layered on top of this foundation.

---

## Who This Book Is For

- Traders with a basic understanding of options (BSM, Greeks) who want to trade them as a speculative vehicle
- Anyone transitioning from index/ETF options to single-stock or commodity options
- Quantitatively-minded traders who want their option strategies grounded in empirical evidence
- Not for market makers seeking risk-free spread income — this is a book about taking informed positions

---

## Main Themes

1. **The Variance Premium is the primary edge.** Implied vol is higher than realized vol most of the time, across most assets. Short-vol strategies systematically capture this premium.

2. **Quantitative forecasting beats intuition.** Every trade should be backed by a specific, testable forecast — not a vague feeling. Models are imperfect but more reliable than gut instinct.

3. **Structure selection follows edge identification.** First identify WHY there is edge (variance premium, skew premium, earnings effect). Then choose the option structure that most efficiently captures it.

4. **Size using Kelly, adjusted for negative skew.** Short-vol strategies have negatively skewed returns. Kelly sizing must account for this, and parameter estimation uncertainty means trading well below raw Kelly estimates.

5. **Meta risks matter.** Counterparty risk, fraud, regulatory changes, and liquidity crises kill more traders than market risk does.

---

## Key Takeaways

- **Implied volatility is usually overpriced** — the variance premium is the most robust empirical fact in options.
- **BSM is a parameterization tool** (converting prices to IV), not a valuation oracle. Use it as a measuring stick.
- **Drift matters for speculators** — use the Boness model (real-world probability) rather than risk-neutral BSM when expressing directional views.
- **Kelly criterion with negative-skew adjustment** is the right sizing framework for short-vol positions.
- **Fractional Kelly** (25–50% of estimated Kelly) is almost always the right choice given finite data and parameter uncertainty.
- **Stops change the shape of the return distribution** — they don't simply prevent losses, they eliminate recovering winners.
- **Discipline without edge is just faster failure** — good risk management cannot rescue a strategy with no positive expectation.

---

## How This Book Relates to Others

| Book | Emphasis |
|------|----------|
| *Option Market Making* (Baird) | Risk-neutral pricing, pure spread income, delta neutrality |
| **Positional Option Trading** (Sinclair) | Speculative positions, variance premium, Kelly sizing |
| *Option Volatility and Pricing* (Natenberg) | Comprehensive Greeks, pricing theory, market making |
| *Volatility Trading* (Sinclair, earlier) | More technical vol trading framework, predecessor to this book |
| *Trading Option Greeks* (Passarelli) | Practical Greeks application for retail traders |

---

## Chapter Structure

1. **Options: A Summary** — BSM review, delta hedging mechanics, hedging costs
2. **EMH and Its Limitations** — What edge is, risk premium vs behavioral anomaly, data mining risks
3. **Forecasting Volatility** — Historical vol, EWMA, GARCH, VIX, forecast comparison
4. **The Variance Premium** — Empirical evidence across assets, term structure, VIX
5. **Finding Trades with Positive Expected Value** — 11 specific tradeable phenomena
6. **Volatility Positions** — Straddles, strangles, butterflies, condors, calendars
7. **Directional Option Trading** — Boness model, subjective pricing, ITM probability
8. **Directional Option Strategy Selection** — Long call, covered call, put spread, risk reversal
9. **Trade Sizing** — Kelly criterion, estimation uncertainty, fractional Kelly, stops
10. **Meta Risks** — Counterparty, crypto, fraud, operational risks
- **Appendices** — BSM adjustments, statistical rules of thumb, execution
