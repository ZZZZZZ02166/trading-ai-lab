# Chapter 8: Directional Option Strategy Selection
*Positional Option Trading, Euan Sinclair — pp. 164–185*

---

## Chapter Summary

Chapter 8 extends Chapter 7's Boness framework from strike selection to full strategy selection. Using 10,000-path simulations, Sinclair compares six directional strategies — long stock, long call, call spread, short put, covered call, and risk reversal — by their P/L distributions. The key finding: the variance premium and skew premium dominate all directional strategy selection decisions. Whether IV is low or high matters more than which structure you choose.

---

## Baseline: Long Stock (Table 8.1)

| Statistic | Value |
|-----------|-------|
| Average | $2,640 |
| St Dev | $3,736 |
| Skewness | +1.12 |
| % Profitable | 75% |

Setup: 100 shares of $100 stock, μ=20% drift, σ=30% vol, 1 year.

---

## Strategy Comparisons (all: μ=20%, σ=30%, IV=30%, 1-year, $100 stock)

### Long ATM Call (Table 8.2)
- Option value: $11.92
- Average: $1,516 | SD: $3,198 | Skewness: +1.66 | Win Rate: 57%
- **Higher skewness** than long stock — leveraged upside, but you lose the entire premium if wrong
- Best when: IV is low (you're paying a fair price), you want leveraged upside, you have a strong directional conviction

### Long ATM Call Spread (100/135 — buy ATM, sell 20-delta call)
- Value: $9.04
- Similar average to long call but **eliminates extreme values and skewness**
- Distribution looks like: "long position with stop and profit target"
- **Psychological benefit**: no temptation to hold past the profit target; structure enforces discipline
- **Caution**: In equity indices, the short strike is often at a discount to ATM IV (skew works against spreads)
- Best when: You want a defined P/L range, you're uncertain about the magnitude of the move

### Short ATM Put (Table 8.4)
- Value: $11.92 (same as call by put-call parity)
- Average: $706 | SD: $986 | Skewness: −2.22 | Win Rate: ~80%
- **Higher win rate, lower average, worse tail** vs long call
- Same economic exposure (bullish + short vol), different psychological profile
- Best when: You prefer a higher win rate over maximizing average return; you're comfortable with occasional large losses

### Covered Call (BXM Index, June 1988–Sep 2019, Fig 8.6)

| Statistic | BXM (ATM monthly CC) | S&P 500 |
|-----------|----------------------|---------|
| Annual Return | **8.5%** | 7.7% |
| Volatility | **12.6%** | 17.3% |
| Max Drawdown | **40.1%** | 56.8% |
| Skewness | −0.67 | −0.29 |

BXM **outperforms** S&P 500 with significantly lower vol and shallower drawdowns. This is a 30-year real-world demonstration of the variance premium benefiting long-vol investors.

Variants:
- BXY (2% OTM calls): Annual 8.6%, Vol 12.6%, Drawdown 40.1% — slightly less capped upside
- BXMD (30-delta calls): Annual 10.3%, Vol 14.7% — higher return but more exposure to upside losses

**Best when**: You hold long stock, believe IV > expected RV, want to harvest the variance premium on your existing equity position.

### Risk Reversal: Short 20-Delta Put, Long 20-Delta Call (Table 8.9)
- Initial value: credit of $93
- Average: $948 | SD: $2,140 | Skewness: +2.69 | Win Rate: 85%
- Captures **skew premium** (sell overpriced put) while getting directional exposure
- **High win rate** (85%) with positive skewness — rare combination
- **Best when**: Stock has steep put skew; you're bullish AND want to harvest skew premium simultaneously
- Risk: short put has tail exposure; large downside moves create unlimited losses

### Short Put Spread (Table 8.12, skew-adjusted version)
- Safer alternative to naked short put for capturing put skew
- Average: $381 | SD: $1,780 | Skewness: −1.10 | Win Rate: 52%
- **If you want to short the skew premium**: use a put spread, not a ratio spread
- Long put acts as protection, position is net short the most overpriced strikes

---

## The Dominant Factor: Variance Premium Level

> "The most important consideration is probably whether the variance premium is low or high. This, more than risk preferences, is paramount in deciding to be long or short options."

**When IV is HIGH (variance premium is large):**
- Prefer being SHORT options: short straddle, covered call, short put
- Collect premium; the premium is working in your favor

**When IV is LOW (variance premium is small or negative):**
- Prefer being LONG options: long call, long call spread
- Avoid paying excessive premium for directional exposure

**Then, within the chosen direction (long or short options):**
- Choose structure based on win rate preference, maximum loss tolerance, and psychological profile

---

## Strategy Selection Matrix

| Situation | Preferred Structure |
|-----------|---------------------|
| Bullish, IV high | Covered call or short put |
| Bullish, IV low | Long call or call spread |
| Bullish + steep put skew | Risk reversal (short put, long call) |
| Bullish, want defined risk | Call spread |
| Want to harvest skew alone | Short put spread |
| Want to hedge portfolio, big crash | 1×2 put spread (buy 2 OTM puts, sell 1 less-OTM) |

---

## Ratio Spreads: Use With Caution

- "Long 1, short 2" ratio spreads: **generally best avoided**
  - Requires good prediction of BOTH direction AND volatility
  - Unlimited risk on the short side
  - "Financing" options by selling extras doesn't eliminate risk — it adds to it
- "Short 1, long 2" ratio spreads: useful for catastrophic hedge
  - If stock crashes slowly, you get short gamma — bad. But at least you can rebalance.
  - If crash is sudden and large, you end up long vega and net long options — exactly what you want

**Risk slide for OTM put hedge (Tables 8.13–8.14)**:
- Single 241 SPY put: P/L $4,650 at −30%, $2,070 at −20%
- 258/266 1×2 put spread: P/L $5,300 at −30%, $2,560 at −20%
- The 1×2 performs better in severe crashes, slightly worse in mild declines

---

## Key Lessons

1. **Variance premium trumps structure selection.** Get the regime right (high IV = sell, low IV = buy) before worrying about which structure to use.
2. **Covered calls deliver documented, decades-long outperformance** over raw long stock (BXM index). This is the simplest way to harvest the variance premium while being long equity.
3. **Risk reversal combines bullish view with skew premium capture** — but the short put tail risk is real.
4. **Single options have the best correlation between profit and correct prediction.** Spreads add structure but reduce sensitivity to your underlying forecast.
5. **There are no free option positions.** "Financing" a call by selling extras just shifts risk; it doesn't reduce it.

---

## Source Pages

- Long stock baseline (Fig 8.1, Table 8.1): pp. 164–166
- Long call / short put (Figs 8.2–8.4, Tables 8.2–8.4): pp. 167–172
- Covered call / BXM index (Fig 8.6, Tables 8.5–8.6): pp. 170–175
- Short put spread / risk reversal (Figs 8.9, Tables 8.9, 8.12): pp. 175–180
- Ratio spreads and tail hedging (Tables 8.13–8.14): pp. 180–185
