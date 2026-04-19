# Concept: The Variance Premium
*From: Positional Option Trading, Euan Sinclair*

---

## Definition

The **variance premium** (also called the volatility premium) is the persistent empirical tendency for implied volatility to be higher than subsequently realized volatility. In practical terms: if you sell options and continuously delta-hedge, you will collect more premium than you pay out in gamma P/L — on average, over many trades.

---

## The Evidence

- Documented in S&P 500 options from the earliest available data to the present
- Exists in individual equity options, though with higher variance trade-to-trade
- Exists in commodity options (oil, gas, grains, copper), currency options, VIX options, bond options
- A 1906 book on London Stock Exchange options already documented this tendency
- Average premium: 2–5 IV points in SPX depending on measurement period and method
- Statistically significant at very high levels across all major markets tested

---

## Why It Exists (All Reasons Matter)

1. **Insurance demand:** Investors with long portfolios buy put options for downside protection. They pay above fair value for this insurance — just as homeowners pay above actuarial value for fire insurance. This demand is structural and expected to persist.

2. **Behavioral path-dependency:** Investors dislike drawdowns disproportionately (loss aversion). They pay extra for instruments that prevent painful wealth paths, even if terminal wealth is the same. This makes options worth more than their pure expected payout.

3. **Uncertainty premium:** Options provide insurance against model failure — the possibility that volatility is much higher than anyone estimates. In a world with parameter uncertainty, this uncertainty premium is rational.

4. **Volatility risk premium:** Short-vol positions have negative correlation with economic downturns (large losses occur when stocks crash). This systematic risk deserves compensation.

---

## How to Capture It

**Index options (most reliable):**
- Sell front-month ATM straddles or strangles on SPX/SPY
- Delta-hedge daily after selling
- Monitor VIX term structure — steeper contango = higher expected roll yield
- Close position before expiration if vol has collapsed

**VIX futures:**
- Sell front-month VIX futures when term structure is in contango
- Roll before expiration
- No delta hedging needed (no underlying to hedge)
- XIV/SVXY provide packaged exposure but with mechanical termination risks

**Single stocks:**
- Higher variance trade-to-trade than index
- Earnings events create concentrated risk — either exclude or manage separately
- Skew premium is larger for individual stocks

---

## Important Caveats

- **The premium is not always present.** In some market regimes (typically crash events), realized vol massively exceeds implied vol. These are the periods of maximum short-vol losses.
- **Higher premium = higher risk.** The premium is largest when VIX is high — precisely when the risk of further vol escalation is also highest.
- **Crowding risk.** As more capital chases the premium (VXX short sellers, variance swap sellers), the premium may compress and the gap-down risk concentrates.
- **The premium does NOT disappear when volatility is low.** In low-vol regimes, the premium is smaller in absolute terms but still positive. The problem is that low-vol regimes have high gamma (require frequent hedging) and thin premium.

---

## Optimal Environment for Short-Vol Strategies

| VIX Level | Premium | Risk Profile | Assessment |
|-----------|---------|-------------|------------|
| < 13% | Small | Low gamma, low risk | Poor risk/reward |
| 13–20% | Medium | Moderate | Best environment |
| 20–25% | Large | Elevated | Acceptable with sizing |
| > 25% | Very large | Tail risk high | Reduce size significantly |

---

## Source Page References

- Definition and historical context: pp. 67–68
- Cross-asset evidence: pp. 73–77
- VIX term structure: pp. 69–73
- Why it exists: pp. 82–86
- Summary: p. 86
