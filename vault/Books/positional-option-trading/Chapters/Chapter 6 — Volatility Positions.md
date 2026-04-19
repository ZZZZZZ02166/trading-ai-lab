# Chapter 6: Volatility Positions
*Positional Option Trading, Euan Sinclair — pp. 116–148*

---

## Chapter Summary

Chapter 6 is a comprehensive, simulation-driven comparison of short-volatility structures. Using 10,000 GBM paths and historical S&P 500 data, Sinclair shows how straddles, strangles, butterflies, condors, straddle spreads, calendar spreads, and delta-hedged positions differ in P/L distribution shape — not in average return (which depends only on IV mismatch), but in variance, skewness, and downside risk. The central theme: **structure determines distribution shape, not expected value**.

---

## Core Insight

For any vol-selling structure, the expected P/L is:

> **E[P/L] ≈ vega × (IV − RV)**

This is the same regardless of structure. What changes with structure is:
- **Distribution shape**: skewness, kurtosis, win rate
- **Worst-case outcomes**: minimum P/L under adverse paths
- **Sensitivity to drift**: how badly do you lose if the underlying moves directionally?

---

## Simulation Parameters (baseline throughout chapter)

- 1-year ATM straddle on $100 stock
- IV = 30%, RV = 30% (fairly priced, zero edge case)
- Drift = 0%, rates = 0%
- 10,000 GBM paths

---

## Structure Comparisons

### Short Straddle vs Short Strangle (Fairly Priced)

| Statistic | Short Straddle | Short Strangle (9Δ/23Δ) |
|-----------|---------------|--------------------------|
| Average | $8 | −$6 |
| St Dev | $1,882 | $2,140 |
| Skewness | −1.83 | **−4.8** |
| Excess Kurtosis | 6.41 | 24.2 |
| Median | $384 | **$841** |
| 10th pct | −$2,274 | −$1,994 |
| Minimum | −$15,321 | −$27,683 |
| % Profitable | 57% | **78%** |

**Key takeaways**:
- Strangle wins more often (78% vs 57%) but has much worse tail risk (min −$27K vs −$15K)
- Strangle's return distribution has fat tails and extreme negative skewness (−4.8 vs −1.83)
- Both have ~zero average P/L (fairly priced, as expected)

### Mispriced Structures (realized vol = 70%, sold at 30% IV)

| Statistic | Mispriced Straddle | Mispriced Strangle |
|-----------|-------------------|-------------------|
| Average | −$3,071 | −$3,230 |
| St Dev | $5,425 | $9,190 |
| Skewness | −4.31 | −4.2 |
| Median | −$2,143 | −$1,650 |
| 10th pct | −$7,069 | −$10,085 |
| Minimum | −$94,084 | **−$197,526** |
| % Profitable | 25% | 36% |

Straddle loses less badly than strangle when vol is severely underestimated — strangle's tail is catastrophic.

### Effect of Unexpected 20% Drift (vol correct, direction wrong)

- Straddle: avg −$800, 50% win rate — less harmed
- Strangle: avg −$1,106, 65% win rate — more harmed (wings far from ATM, doesn't benefit from directional movement)
- **Short straddle is more robust to directional errors than short strangle**

---

## Butterfly and Condor

### Short Butterfly: Capped Risk, Capped Reward
- Long the OTM strangle (70/130), short the ATM straddle
- Maximum loss = width of wings × 100 shares
- P/L distribution: approximately uniform between max profit and max loss

### Short Condor: More Conservative
- Long wider strangle (70/130), short tighter strangle (80/120)
- Even more capped — smaller maximum profit and smaller maximum loss
- Better for traders who want predictable, bounded outcomes

**Fig 6.12 (poorly-priced butterfly)**: Butterfly: Average −$25, SD $2,460, Skewness +0.4, 10th Pct −$2,756, Win Rate 46%
**Fig 6.13 (condor)**: Similar shape, tighter bounds

---

## Delta-Hedged Positions

- Daily hedging dramatically narrows the P/L distribution (Fig 6.7 vs Fig 6.1)
- Hedged straddle: near-normal distribution, much lower variance
- Caveat: transaction costs eat into average return (Table 1.1 showed ~$115 drag per year per $100 stock at $0.10/share)
- **For positional traders (not market makers): hedge rarely or not at all**

---

## Straddle Spread (Calendar-like Risk Reduction)

Sell front-month straddle, buy same-strike back-month straddle:

| Statistic | Short Straddle | Straddle Spread |
|-----------|---------------|-----------------|
| Average | $261 | $265 |
| St Dev | $597 | **$210** |
| Skewness | −1.4 | **0.0** |
| Median | $411 | $260 |
| 10th pct | −$574 | **−$18** |
| Min | **−$3,753** | **−$66** |
| % Profitable | 72% | **87%** |

The straddle spread achieves **similar average P/L** with dramatically lower variance, near-zero skewness, and a minimum loss of only −$66 vs −$3,753. The back-month option acts as a near-perfect hedge against extreme moves.

**Fig 6.14**: At expiry, straddle spread P/L is a tent shape — maximum profit when underlying ends exactly at the strike, zero P/L when far away. Can't lose more than the spread between the two option prices.

---

## Calendar Spread

- Sell 30-day ATM straddle (IV=40%), buy 60-day ATM straddle (IV=30%)
- Capture extra variance premium in the shorter-dated option
- Distribution similar to short 1-month straddle but with lower dispersion
- Calendar provides "partial hedge": if underlying moves far, back-month gains partially offset front-month loss

---

## Skew and OTM Puts

- Chapter documents: S&P 500 drops faster (larger) than it rises — but only marginally so (Table 6.13)
- Average upside daily move: 0.73%; average downside: 0.76% — very small asymmetry
- Before 1987: almost no index option skew. After 1987 crash: skew became permanent (overcompensation for crash risk)
- **OTM puts are the most overpriced options** on equity indices — most of the skew premium comes from them
- Selling OTM puts: highest premium per option, but also highest relative skewness

---

## Key Lessons

1. **Structure doesn't change expected value, only distribution shape.** Choose structure based on your risk tolerance, not because you think it has higher edge.
2. **Higher win rate always means worse tail risk.** Strangle: 78% wins, but −$27K minimum. There is no free lunch in vol selling.
3. **Straddle spread dramatically reduces skewness and downside risk** at virtually no cost to average P/L. This is the closest thing to a free lunch in structure selection.
4. **Short straddle is more robust to drift errors than short strangle.** If you're wrong directionally, straddle loses less.
5. **Delta hedging converts negatively-skewed P/L into near-normal distribution** — but costs money in transaction costs.
6. **OTM puts are the most overpriced.** But selling them raw (naked put or strangle) creates extreme negative skewness. Use spreads to manage the tail.

---

## Warning

"Repair" of a losing position is a dangerous concept. The loss is already realized. Ignore the original trade and ask: "Given what I know now, what position do I want?" This is psychologically hard but correct.

---

## Source Pages

- Straddle vs strangle simulation (Tables 6.1–6.6, Figs 6.1–6.4): pp. 117–127
- Effect of drift on structures: pp. 127–131
- Butterfly and condor (Tables 6.9–6.10, Figs 6.12–6.13): pp. 128–135
- Straddle spread (Table in text, Fig 6.14): pp. 133–137
- Delta-hedged positions: pp. 137–140
- Calendar spread: pp. 140–144
- Skew and OTM puts (Table 6.13): pp. 144–148
