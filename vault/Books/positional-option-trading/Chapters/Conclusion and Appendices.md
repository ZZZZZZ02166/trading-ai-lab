# Conclusion and Appendices
*Positional Option Trading, Euan Sinclair — pp. 226–252*

---

## Conclusion (pp. 226–227)

> "Football is like chess, but with dice." — Peter Krawietz, Liverpool FC

Option trading is the same. Skill matters enormously — but randomness is irreducible. You can correctly forecast realized volatility, direction, and IV regime, and still lose money on an individual trade because of path dependency, interest rate changes, or dividend adjustments. The skill is in making the right decisions repeatedly, not in achieving the right outcome every time.

**Core message**: We operate under deep uncertainty — not just "unknown probabilities" but genuinely unknowable, time-varying distributions. This is not a reason to stop looking for edge. It is a reason to look very hard, test rigorously, and demand robustness across markets, time periods, and parameter settings.

**Key principles from the conclusion:**
1. Focus on phenomena, not parameterizations. Volatility matters because it measures uncertainty, not because it's a standard deviation.
2. A good trading strategy is robust to implementation details. If small parameter changes destroy the backtest, the edge isn't real.
3. Test across multiple markets. Real edges appear everywhere the conditions apply, not just in the specific sample you studied.

---

## Appendix 1: BSM Extensions (pp. 228–240)

The main text used the simplest form of BSM. In practice, several extensions are needed.

### Interest Rate and Dividend Adjustments
- **Cost-of-carry model**: replaces the underlying price with a forward price F = S·e^(r-q)T where q is the continuous dividend yield
- **American options**: early exercise changes pricing — calls on dividend-paying stocks may be exercised early; puts always have some early exercise value
- **Discrete dividends**: cannot be handled cleanly within BSM — requires numerical methods or approximations

### Imperfect Hedging (Fig A1.3)
- BSM assumes perfect continuous hedging; in practice hedges are imperfect
- **Fig A1.3**: Shows residual risk from imperfect correlation between the hedge instrument and the option underlying. Scatter plot of hedge P/L vs option P/L — the slope is the hedge ratio but there's significant scatter around the line
- This residual basis risk is unavoidable and must be included in position sizing
- **Key practical point**: Use historical realized correlation to estimate hedge effectiveness; don't assume correlation = 1

### Mixture-of-Normals Model (p. 237–238)
- A simple way to model fat tails without GARCH: assume returns come from a mixture of two (or more) normal distributions with different means and variances
- Example: 90% of the time volatility = 15% (normal market), 10% of the time volatility = 40% (crisis market)
- This produces a distribution with fat tails and possibly negative skew — matching observed option prices better than a single normal
- Does not add much predictive power vs GARCH but provides intuition for why the volatility surface exists

---

## Appendix 2: Statistical Rules of Thumb (pp. 240–244)

### Rule of Five
- If you observe an event N times with zero occurrences of a particular outcome, the 95% upper confidence bound on the probability of that outcome is approximately 3/N
- Example: 1,000 trades with no catastrophic loss → upper bound on probability ≈ 3/1000 = 0.3% per trade

### Rule of Three
- **Eq A2.3–A2.4 (Rule of Three)**: When you have observed n trials with zero events:
  > Upper 95% CI on p ≈ 3/n
- More generally, if you've observed k events in n trials:
  > 95% CI: p ∈ [(k/n) − 2√(p(1-p)/n), (k/n) + 2√(p(1-p)/n)]
- **When the rule applies**: p must be constant across observations; trials must be independent
- Useful for: estimating tail event probabilities from limited data (e.g., "We've run this strategy 100 times without a 50% drawdown — what's the probability of that drawdown?")
- **Limitations**: Does not apply when the probability is time-varying (aging processes, trend-following) or when observations are correlated

---

## Appendix 3: Market Microstructure (pp. 245–252)

### Bid-Ask Spread and Effective Costs
- The posted bid-ask spread understates actual transaction costs for large orders
- **Effective spread**: For a large market order, the average fill price will be worse than the best available price because earlier orders move the market against you
- Fig A3.1 / Table A3.1 (order book structure): shows how liquidity thins rapidly as you move away from the best bid/offer
- **Key concept**: A trader who provides liquidity (limit orders) earns the spread; a trader who takes liquidity (market orders) pays it
- For positional traders executing large option orders: work the order over time using limit orders to minimize impact cost

### Market Impact
- Large orders move prices adversely during execution
- Impact is proportional to order size relative to average daily volume
- In options: open interest and volume vary enormously across strikes and expirations — liquidity drops sharply for far-OTM or far-dated options
- **Practical rule**: Size positions so they can be exited in 1–3 days of normal volume without significant market impact

---

## Source Pages

- Conclusion: pp. 226–227
- BSM extensions (interest rates, dividends): pp. 228–234
- Imperfect hedging Fig A1.3: pp. 234–237
- Mixture-of-normals: pp. 237–240
- Rule of Five / Rule of Three (Eqs A2.3–A2.4): pp. 240–244
- Order book / effective spread (Table A3.1): pp. 245–252
