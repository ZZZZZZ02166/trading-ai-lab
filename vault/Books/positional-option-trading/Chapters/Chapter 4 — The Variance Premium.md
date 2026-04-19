# Chapter 4: The Variance Premium
*Positional Option Trading, Euan Sinclair — pp. 67–87*

---

## Chapter Summary

Chapter 4 is the empirical core of the book. The variance premium — the persistent tendency for implied volatility to exceed subsequent realized volatility — is documented exhaustively across equity indices, the VIX, commodities, bonds, and currencies. Sinclair presents the statistics with detail, shows how the premium varies with VIX regime, and gives multiple structural reasons why it should persist. He also names the "peso problem" — the only serious argument against the premium — and explains why it is unlikely to invalidate the historical record.

---

## The Core Fact

**Implied volatility has been an upward-biased estimator of future realized volatility for as long as data exists.**

For the S&P 500 (1990–2018):
- VIX averaged 4.08 points above subsequent 30-day realized volatility
- Premium is positive 85% of the time
- Distribution is right-skewed (bell-shaped but with severe left tail during crises)

---

## Key Data (Table 4.1 — S&P 500 Variance Premium)

| Statistic | Value |
|-----------|-------|
| Mean | +4.08 vol pts |
| Median | +4.63 vol pts |
| Standard deviation | 5.96 |
| Skewness | −2.33 |
| Maximum | +31.21 |
| Minimum | −53.34 (2008/crisis) |
| 90th percentile | +9.62 |
| 10th percentile | −1.45 |

Other major equity indices show similar premia: Dow Jones (+3.5), NASDAQ 100 (+3.4), Russell 2000 (+3.2).

---

## Variance Premium by VIX Quintile (Table 4.3)

| VIX Range | Mean Premium | SD | Comment |
|-----------|-------------|-----|---------|
| < 13.0 | 2.61 | 3.54 | Low premium, poor risk/reward |
| 13.0–15.9 | 3.37 | 3.60 | Good balance |
| 15.9–19.4 | 4.35 | 4.58 | **Optimal zone** |
| 19.4–24.2 | 4.19 | 6.53 | Good return, elevated risk |
| > 24.2 | 5.87 | 9.06 | Highest premium, worst risk profile |

**Practical implication**: Mid-level VIX (15–20) is the best environment for systematic short-vol. High VIX gives highest premium but worst distribution. Low VIX gives too little return for the gamma risk.

---

## VIX Futures and Term Structure

- Short front-month VIX futures has been profitable (Fig 4.1: ~$80,000 P/L over 4 years with one $30,000 drawdown in Feb 2018)
- VIX term structure has been in contango 81% of the time since 2006
- **Contango filter** (Fig 4.3): only shorting when curve is in contango significantly smooths the equity curve
- This is a term-structure effect, not the same as the equity variance premium — VIX itself doesn't decay (Fig 4.2)

---

## Cross-Asset Variance Premia

### Commodities (Table 4.4 — 21 markets, 1989–2011)
- 18 of 21 commodity markets have statistically significant variance premia
- Notable: Natural gas +10.2%, Oats +6.2%, Lumber +3.5%, Crude oil +3.4%
- Within-sector correlations are moderate (Grains 24.2%, Energy 33.4%)
- **Cross-sector correlations to S&P 500 variance premium are LOW** (2–30%), making commodities useful diversifiers (Table 4.6)
- Exception: T-bonds have moderate positive correlation to equity premium (39.3%)

### Bonds
- 1-month variance swaps on US Treasuries overpriced by ~20% (5-year: 18.7%, 10-year: 27.6%, 30-year: 21.2%), Sharpe ~2
- Most bond variance premium is clustered around macroeconomic data releases

### VIX Options
- Variance premium in VIX options comparable in size to equity index premium

### Currencies
- Significant premia in USD/GBP, USD/JPY, USD/CHF, USD/EUR
- Some currencies (NZD, AUD) show negative premia — linked to safe-haven status

### Equity Single Names (Table 4.7)
- Utilities: +31.25% (strongest), Tech: −7.66% (negative — growth stocks)
- Small stocks and value stocks have larger premia than large/growth stocks

---

## The CNDR and BFLY Indexes (Figs 4.7–4.8)
- CBOE's CNDR (condor) index has returned ~12× in 30 years; BFLY ~8×
- Both underperformed after 2008: not because premium disappeared (median stayed at 4.61 pts) but because VIX dropped (from median 18.3 to 16.3), increasing gamma and path dependency, and SKEW index rose from 116.2 to 125.7 (OTM puts became more expensive relative to ATM)

---

## Why the Variance Premium Persists: Five Reasons

1. **Insurance demand**: Long equity holders buy puts for downside protection. This demand persists structurally — the customer sets the price.
2. **Jump risk**: Options uniquely protect against discontinuous price jumps that dynamic hedging cannot replicate. This non-redundancy commands a premium.
3. **Trading restrictions**: Retail brokers often prohibit naked option selling, structurally forcing an entire class of participants to be net long vol.
4. **Market-maker inventory**: Market-makers are systematically net long teeny options as business insurance. This consistent demand supports OTM option prices.
5. **Path dependency** (Figs 4.9–4.12): People care about HOW returns are realized, not just terminal value. They prefer "recover from adversity" paths → willingness to overpay for the gamma convexity of long options.

---

## Path Dependency: The Peso Problem (Figs 4.11–4.12)

- Short put: steady theta collection, looks great for 20 days, then a jump — P/L path is smooth then spikes
- Long call: bleeds theta daily, but gets convex payoff if a jump occurs — "snatching victory from jaws of defeat"
- People prefer the long call's path (loss then recovery), even though terminal P/L may be identical
- **Peso problem**: perhaps options are fairly priced, and the crashes we haven't seen yet will eventually wipe out all short-vol profits. "Just you wait."
  - Hard to refute, but history shows the premium has persisted across all observed crises
  - Same logic would apply to every risk premium — the real question is whether the evidence is strong enough to trade

---

## Implied Skew Premium
- Half of the excess return from selling OTM puts is due to realized skewness premium (not just variance)
- Option markets predict "nine out of the past five market corrections" — implied skew is reactive, steepest after crashes
- The skew can be captured via skew swaps (model-free) or by selling OTM puts spreads

---

## Key Warnings

- **High VIX does NOT mean safe.** Highest premium comes with worst risk profile and most negative skewness
- **Low VIX is not a free lunch.** Higher gamma → more path dependency → smaller edge per unit of risk
- **Don't sell volatility after a spike without reducing size.** The premium is highest when risk is also highest
- **CNDR/BFLY performance degraded post-2008** despite constant premium — structure matters, not just premium existence

---

## Source Pages

- VIX short strategy and term structure (Figs 4.1–4.3): pp. 67–70
- SPX variance premium stats (Figs 4.4–4.6, Table 4.1): pp. 69–73
- CNDR/BFLY indexes (Figs 4.7–4.8): pp. 74–76
- Commodity premia (Tables 4.4–4.6): pp. 78–82
- Reasons for premium persistence: pp. 80–84
- Path dependency / peso problem (Figs 4.9–4.12): pp. 83–87
