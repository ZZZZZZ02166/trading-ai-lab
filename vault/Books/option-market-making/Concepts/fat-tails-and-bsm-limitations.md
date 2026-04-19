# Concept: Fat Tails and BSM Limitations
*From: Option Market Making, Allen Jan Baird*

---

## Definition

**Fat tails** (leptokurtosis) describe the empirical finding that financial asset returns have more extreme observations than a normal (log-normal) distribution predicts. The tails of the real distribution are "fatter" — extreme events occur far more frequently than BSM assumes.

This is not a modeling detail — it is a persistent, structural feature of all major financial markets tested.

---

## The Evidence (From Chapter 2)

- **Figure 2.4:** Empirical returns vs normal curve — taller peak AND fatter tails than normal
- **Figure 2.5:** September wheat futures across multiple years consistently show fat tails
- **Figure 2.6:** S&P 500 five-day returns (1928-1988): positive excess in tails beyond ±3 SD, negative excess in ±1 to ±2 SD range
- **Figure 2.7:** Cauchy distribution fits wheat price changes better than normal curve
- Long-term stock/commodity records show price moves 5–6 standard deviations from the mean that should be virtually impossible under normality

---

## Why It Matters

1. **BSM underprices deep OTM options.** Since the normal distribution underestimates tail probability, BSM will systematically underprice deep out-of-the-money puts and calls (the wings). Real prices should reflect a fat-tail premium.

2. **Market-implied skew reflects fat-tail reality.** The widespread positive volatility skew (wings trading at higher IV than ATM) partially compensates for fat tails — the market has learned to price this empirically.

3. **Catastrophic risk is larger than model risk.** Maximum loss estimates based on BSM (±3 or ±4 SD events) dramatically understate actual catastrophic risk. Market makers need capital reserves for events that the model says "can't happen."

4. **Alternative distributions (Cauchy, Paretian) fit better.** These distributions have heavier tails and sometimes infinite variance. While not used in standard pricing models, their fit to data confirms that normal distribution-based risk management is systematically underprepared for extreme events.

---

## Common Misunderstandings

- **"Fat tails are rare — most of the time BSM is fine."** True for typical market conditions. But market makers don't go bankrupt during typical conditions. They go bankrupt during the fat-tail events BSM said were impossible.

- **"The volatility smile compensates for fat tails."** Partially, but imperfectly. The smile is derived from market prices, not from explicit fat-tail modeling. During extreme events, even the smile may underprice realized tail risk.

---

## Practical Implications

- Always add a fat-tail buffer when pricing deep OTM options
- Capital reserves should be based on fat-tail scenarios, not 3-SD BSM scenarios
- Be especially cautious selling naked OTM options — BSM suggests they are safe; fat-tail reality disagrees

---

## Source Page References

- Fat-tail evidence and figures: pp. 20–24
- S&P 500 error curve (Figure 2.6): p. 22
- Cauchy distribution (Figure 2.7): pp. 23–24
- Practical implications for market makers: p. 24
