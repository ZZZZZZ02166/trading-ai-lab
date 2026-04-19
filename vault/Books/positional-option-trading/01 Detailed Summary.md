# Positional Option Trading — Detailed Summary
*Euan Sinclair*

---

## The Central Argument

Sinclair's thesis is deceptively simple: implied volatility is almost always overpriced relative to subsequently realized volatility. This *variance premium* is the most robust empirical fact in options markets, documented across equity indices, individual stocks, commodities, currencies, and volatility products for decades. Building a trading strategy around this premium — understanding when it exists, how to capture it efficiently, how to size positions correctly, and what structural risks to avoid — is what this book teaches.

This is not a theoretical textbook. Every claim is backed by empirical evidence. Every strategy recommendation is grounded in historical data. The tone is skeptical and quantitative throughout.

---

## Chapter 1: Options — A Summary

The book opens by reframing BSM. Conventional wisdom treats BSM as a pricing model that tells you what an option is worth. Sinclair argues it's better understood as a *parameterization tool*: the market prices options via supply and demand, and BSM converts those prices into a single comparable parameter — implied volatility. This is why traders speak in IV terms rather than dollar terms. If BSM were perfect, a single constant IV would describe all options on the same underlying. The existence of the volatility smile/skew is simply evidence that BSM is an imperfect model.

The second important use of BSM is calculating delta for hedging. When a delta-hedged position is held, the remaining P/L over a small interval is:

> **Profit = ½Γ·S²·(σ_realized² − σ_implied²)·dt**

This single equation is the foundation of volatility trading. It says the delta-hedged option profits when realized vol exceeds implied vol and loses when it falls short. The magnitude depends on gamma (highest ATM) and the squared vol differential.

BSM's assumptions — constant volatility, continuous trading, no transaction costs, normally distributed returns — are all violated in practice. But the model's value as a measurement standard persists because everyone uses it, making IV a shared language for option markets.

**Hedging frequency tradeoff:** Continuous hedging eliminates directional risk but incurs continuous transaction costs. Practitioners hedge less frequently, accepting wider P/L variance in exchange for lower costs. The correct frequency depends on position gamma and individual transaction cost structure.

---

## Chapter 2: The Efficient Market Hypothesis and Its Limitations

**Discipline without edge is just faster failure.** A trader with no real edge who applies strict discipline and position sizing will lose money faster than a sloppy trader with the same bad strategy. The first task is identifying genuine edge — not managing a strategy without it.

The chapter distinguishes two sources of trading profit:

1. **Risk premia:** Structural payments from parties seeking insurance. The variance premium is the premier example — investors buy options for protection and accept paying above fair value. Risk premia are expected to persist because the structural demand for insurance doesn't disappear.

2. **Behavioral inefficiencies:** Temporary mispricings from cognitive biases. These erode once discovered and widely traded. Post-earnings drift is an example.

Sinclair is deeply skeptical of behavioral explanations: there are 50+ catalogued biases, so any market anomaly can be explained post-hoc by some bias. Behavioral stories are unfalsifiable and thus scientifically weak. Require that any proposed inefficiency have: (1) strong statistical evidence across multiple periods and markets, (2) a specific, predictive mechanism (not a vague bias), (3) survival after controlling for known risk factors.

**Data mining:** The White Reality Check and Hansen's SPA test detect whether apparent outperformance in backtests results from overfitting to historical data. Every strategy discovered through large-scale parameter search should be tested with these methods. Without such tests, most "edges" are artifacts.

---

## Chapter 3: Forecasting Volatility

Every option trade is an implicit volatility forecast. Even the choice to sell options "because vol is high" is a forecast that realized vol will be lower. The relevant question is not whether to forecast but how.

**Methods compared:**
- **Historical vol (rolling window):** Simple, interpretable. Suffers from ghost effects (a large return falls out of the window suddenly).
- **EWMA (λ=0.9–0.95):** Exponentially weights recent data more heavily. Adapts faster to vol changes. RiskMetrics uses λ=0.94.
- **GARCH(1,1):** σ²_t = ω + α·r²_{t-1} + β·σ²_{t-1}. Captures both vol clustering (high vol follows high vol) and mean reversion to long-run level. The term structure of GARCH forecasts decays toward long-run vol over longer horizons.
- **VIX:** Market-implied 30-day forward IV for SPX. Has predictive advantage for SPX but only available for index options.

**Empirical finding:** When tested on S&P 500, all methods perform similarly with differences of ~0.5 vol points in average error. No single model dominates. This means model selection matters less than having a process at all.

**Forecast horizon:** Short-term forecasts (days to weeks) are far more accurate than long-term. At month+ horizons, reversion to long-run average is often the best forecast.

---

## Chapter 4: The Variance Premium

This is the empirical heart of the book. The variance premium — the persistent tendency for IV to exceed realized vol — is documented across:
- S&P 500 index options (most studied, most robust)
- Individual US stocks
- Commodity options (oil, natural gas, grains, copper)
- Currency options (major pairs)
- VIX options
- Bond options

The premium has existed since options data has been collected. In the SPX, it has averaged 2–5 IV points depending on the period and measurement method, and is statistically significant at very high levels.

**VIX term structure and contango:** VIX futures are normally in contango (longer-dated > spot). This creates a persistent roll yield for short VIX positions — futures converge toward spot as expiration approaches. Cash VIX is a better predictor of future VIX than the futures price. Selling front-month VIX futures when the term structure is steep captures both the roll yield and variance premium.

**Premium scales with vol level:** Both the size and variability of the variance premium increase with the VIX level. Mid-VIX environments (15–20) offer the best risk-adjusted opportunity. Low vol: premium is small, gamma is high (requires frequent hedging). High vol: premium is large but so is variance of outcomes.

**Why the premium exists (and will persist):**
1. *Insurance demand:* Investors with long stock portfolios buy puts for protection, paying above fair value. This creates structural demand that persists regardless of who knows about the premium.
2. *Path dependency:* Investors care not just about final wealth but about avoiding painful drawdowns along the way. They rationally pay extra for options that protect against path-dependent losses.
3. *Uncertainty premium:* Options provide insurance against model uncertainty itself — the possibility that vol will be much higher than anyone expects.

**Implied skewness premium:** A large portion of the variance premium comes specifically from OTM puts being overpriced. The skew (IV increases for lower strikes) reflects this overpricing. Selling OTM puts collects both the variance premium and the skew premium.

---

## Chapter 5: Finding Trades with Positive Expected Value

Sinclair catalogs 11 specific tradeable phenomena with empirical support. The most important:

**1. Variance Premium (Confidence Level 3 — highest)**
Sell options (straddles, strangles, variance swaps) on indices and stocks where IV persistently exceeds realized vol. Use term structure contango as a timing filter.

**2. Earnings Volatility Overpricing (Confidence Level 3)**
IV of options expiring shortly after earnings overstates the subsequent move by ~30% on average. Selling straddles or strangles before earnings has positive expected value. Best results with smaller, less-followed stocks. Must manage fat-tail risk of occasional huge moves.

**3. Post-Earnings Announcement Drift / PEAD (Confidence Level 2)**
Stocks continue moving in the direction of the earnings surprise for 60+ days. Effect is strongest for small caps. Directional plays: buy calls/puts in the direction of the surprise after the announcement.

**4. Earnings-Induced Reversals (Confidence Level 2)**
Some stocks overshoot on earnings day and partially reverse over the next week. Fade very large moves (>10% on high volume).

**5. FOMC/Macro Event Vol (Confidence Level 2)**
Implied vol around FOMC announcements overstates subsequent moves. Short straddles into FOMC dates have historically positive expected value.

**Caution on leveraged short-vol products:** XIV's collapse in February 2018 illustrated how short-vol ETFs can have mechanical termination risks independent of the strategy's fundamental validity. The product's rebalancing mechanism (buying VIX futures as they go up to maintain target leverage) created a feedback loop during the vol spike.

---

## Chapter 6: Volatility Positions

**Straddle (ATM call + ATM put):** Pure volatility bet. Profits when realized vol > implied vol (long) or implied > realized (short). High gamma near strike — sensitive to large moves. Short straddle is the most popular vol-selling structure.

**Strangle (OTM call + OTM put):** Wider break-even range than straddle, collects less premium. With typical put skew, OTM puts contribute more skew premium. More resilient to moderate moves but equally exposed to catastrophic moves.

**Delta hedging reduces but does not eliminate risk:** Daily hedging of a short straddle dramatically reduces P/L variance vs unhedged. The hedged P/L depends on (realized vol − implied vol) × gamma × S². But large sudden moves (gap downs, crashes) can still produce extreme losses even with daily hedging.

**Butterfly (long strikes A & C, short 2× strike B):** Limits maximum loss vs straddle. Sacrifices some premium collected. Best when: vol is high, you want protection against tail moves, and skew is flat (wing protection is cheap).

**Condor (long far OTM + short near OTM, both sides):** Similar to butterfly but wings are wider. Less premium but larger protection zone. Same skew consideration.

**Volatility skew:** In equity markets, OTM puts have higher IV than ATM, and ATM has higher IV than OTM calls. This skew exists because: crash risk is real (negative skew in returns), investors pay for downside insurance, and the risk-neutral measure assigns higher probability to crashes than the physical measure. Selling OTM puts collects variance premium + skew premium — both are real, both compensate for real risks.

**Calendar spread:** Sell front-month, buy same-strike back-month. Profits from: front-month IV decaying faster than back-month, and the term structure staying steep. Most variance premium is in short-dated options. Risk: a large move makes the short option deeply loss-making while the long option provides limited offset.

---

## Chapter 7: Directional Option Trading

**The key insight:** BSM's no-drift pricing is correct for market makers who hedge. But speculators who buy options to benefit from a specific directional move should price options using their actual drift forecast, not the risk-neutral rate.

**Boness model (1962):** C = S·exp(μT)·N(d₃) − X·N(d₄), where d₃ and d₄ use real-world drift μ instead of r. This gives the "subjective value" of an option — how much it's worth to a trader with drift forecast μ.

**True ITM probability:** BSM's N(d₂) is the risk-neutral probability of expiring ITM (correct for hedging). The true physical-measure probability is N(d₄) from the Boness model. For a 1-year 110-call with S=$100, σ=30%, μ=10%, r=0%: risk-neutral = 32%, physical = 45%. Speculators should use N(d₄).

**Option return moments:** Option returns are intrinsically positively skewed even when underlying returns are symmetric. Long calls have positive skew — most expire worthless but occasional large winners. This skewness is independent of any directional forecast.

**Practical implication:** When using options to express directional views, compare the Boness subjective value to the market price. If subjective value > market price for calls (or puts in the other direction), there is a positive-edge directional trade. The excess of subjective value over BSM fair value represents the value of the drift forecast.

---

## Chapter 8: Directional Option Strategy Selection

For a given directional view, which option structure is best? Sinclair compares:

| Structure | Key Properties |
|-----------|---------------|
| Long ATM Call | Positive skew, defined loss, lower median than stock |
| Covered Call | Collect variance + skew premium, cap upside, higher Sharpe than stock |
| ATM Put Spread | Collect skew premium, limited loss, directional bet |
| Risk Reversal | Combines directional + skew views, 'true' probability bet |

**Covered call:** CBOE BuyWrite Index (BXM, monthly ATM covered calls on SPX) has returned 8.5% annually with 12.6% vol vs SPX's 7.7% return at 17.3% vol. Better Sharpe due to collecting variance premium. Cost: capped upside in strong bull markets.

**Strike selection for covered calls:** The variance premium peaks near ATM — selling too far OTM gives little premium while sacrificing meaningful upside. Sell just above current price to maximize the premium collected.

**Risk reversal as skew trade:** P/L formula: Profit = Vega_call·(σ_call_new − σ_call_old) + Vega_put·(σ_put_old − σ_put_new). If skew flattens, both legs profit. Best when: skew is unusually steep and you have a bullish directional view.

**General principle:** Variance and skew premia are more important to position profitability than getting the directional call right. A moderately wrong directional view with a short-vol structure can still be profitable if the vol premium is captured.

---

## Chapter 9: Trade Sizing

**Kelly criterion foundation:** Maximizes long-run geometric growth rate. For continuously distributed outcomes: f* ≈ μ/σ² (approximately the Sharpe ratio squared). For skewed returns: f* ≈ μ/(μ²+σ²) + λ₃μ²/(μ²+σ²)³ — negative skew (typical for short-vol) reduces the optimal fraction below the normal-distribution estimate.

**Parameter estimation uncertainty:** The Kelly fraction estimated from historical data has substantial uncertainty. With n=1000 trades, sd(f*) ≈ 0.03–0.10 depending on the strategy. There is a meaningful probability that the estimated f* is positive when the true f* is zero or negative. Full Kelly betting on an estimated fraction almost always means over-betting.

**Fractional Kelly tables:**
- To keep the probability of over-betting below 10%: scale Kelly by 0.048 (normal) or 0.205 (skew-adjusted)
- Below 20%: scale by 0.374 (normal) or 0.478 (skew-adjusted)
- **Practical default: 25–50% of estimated Kelly**

**Growth rate vs drawdown:** GR(f) = (f − f²/2)·μ²/σ². Maximized at f=1, falls to zero at f=2. The growth-rate-to-drawdown ratio peaks at f=0.5 (half-Kelly). This is why half-Kelly maximizes risk-adjusted returns, not just raw returns.

**Stops and their real effect:** Stops do not simply truncate the left tail. A 15% fixed stop on a normally distributed strategy: reduces average return from 10% to 9.6%, changes return distribution from symmetric to bimodal. Trailing stops are even worse — they eliminate recovering winners more aggressively. Stops should be used only when position monitoring is impossible or drawdown risk is existential.

**Kelly and ruin probability:** Probability of reaching 200% before ruin at 0%: highest (~90%) at very low f, declining to ~45% at full Kelly. Counter-intuitively, betting more does NOT improve survival probability — it worsens it. Trade at 25–50% Kelly for both maximum growth efficiency AND best survival odds.

---

## Chapter 10: Meta Risks

Market risk is well-understood. Meta risks — counterparty failure, fraud, regulatory changes, liquidity crises — are underappreciated and can cause total loss regardless of how good the strategy is.

**Historical examples:**
- MF Global (2011): customer funds misused, funds frozen
- Madoff: decades-long Ponzi scheme
- QuadrigaCX (2019): crypto exchange collapse, CEO dies with all passwords
- Sumitomo copper (1995): price manipulation by single trader

**Cryptocurrency:** Extremely high vol (60–80% annualized), poor regulatory oversight, exchange counterparty risk extreme. The variance premium likely exists but counterparty risks make it not directly comparable to regulated markets.

**Risk mitigation:** Multiple brokers, prefer regulated exchanges, maintain excess capital outside trading accounts, never concentrate with single counterparty, verify track records with audited returns.

---

## Appendices

**Appendix 1: BSM Adjustments**
- Interest rates: daily rate changes have std dev of 0.037% vs VIX daily changes of 1.7 points. Rate uncertainty is negligible relative to vol uncertainty — stochastic rate models add no practical value.
- Dividends: adjust S → S − PV(dividends). American early exercise at ex-dividend date.
- Non-constant volatility: regime-switching creates fat tails. A two-regime mixture of normals: kurtosis = 3·(p₁σ₁²+p₂σ₂²)²/(p₁σ₁²+p₂σ₂²)². S&P 500 switches between 10–15% and 30–80% vol regimes, explaining the observed leptokurtosis.

**Appendix 2: Statistical Rules of Thumb**
- Rule of Five: if 5 observations all lie above a threshold, 93.75% confidence the median is above that threshold.
- Rule of Three: if an event hasn't occurred in n observations, the 95% upper bound on its probability is 3/n.

**Appendix 3: Execution**
- True effective bid-ask spread often exceeds the posted spread for large orders.
- Value trades against the decision price (mid), not the bid or ask, to avoid being intimidated into worse fills.
