# Volatility Trading — Detailed Summary
*Euan Sinclair, Wiley (2013), 2nd Edition*

---

## Chapter 1: Option Pricing (pp. 8–32)

### BSM as Language, Not Truth
Sinclair opens with a provocative framing: the Black-Scholes-Merton model is wrong — but it is the best shared language we have for discussing options. Every market participant quotes implied volatilities, not option prices, precisely because IV is a BSM-derived quantity that strips out moneyness and time. This means you can compare options across strikes and expirations with a single number.

The model is not used because it is true. It is used because consistency is more valuable than accuracy when trading relative value.

### Derivation from Taylor Expansion
The BSM PDE follows naturally from a Taylor expansion of option value dC:

```
dC = (∂C/∂S)dS + (∂C/∂t)dt + ½(∂²C/∂S²)(dS)²
```

Under Ito's lemma, (dS)² = σ²S²dt for a geometric Brownian motion. Setting up a delta-neutral portfolio eliminates the dS term, and requiring the portfolio to earn the risk-free rate gives the BSM PDE.

The key consequence: **the drift μ of the underlying cancels completely**. Option pricing is drift-independent — two traders who disagree on where a stock is headed will agree on option value if they agree on volatility. This is among the most important and counterintuitive results in finance.

### Greeks from the Expansion
Each Greek is a coefficient in the Taylor expansion:
- Delta (δ) = ∂C/∂S — rate of change with underlying price
- Gamma (γ) = ∂²C/∂S² — rate of delta change; the "curvature profit"
- Theta (θ) = ∂C/∂t — time decay per day
- Vega (ν) = ∂C/∂σ — sensitivity to implied vol change

The one-step P/L from delta-hedging: P/L = ½γS²(σ²_realized − σ²_implied)dt. This is the engine of volatility trading: positive when realized vol exceeds the IV you sold.

---

## Chapter 2: Volatility Measurement (pp. 33–53)

### Five Estimators
Sinclair presents five OHLC-based historical vol estimators:

| Estimator | Data Used | Efficiency vs CC |
|-----------|-----------|------------------|
| Close-to-Close (CC) | Closing prices only | 1× (baseline) |
| Parkinson (1980) | H, L | 4.9× |
| Garman-Klass (1980) | O, H, L, C | 7.4× |
| Rogers-Satchell (1991) | O, H, L, C (drift-independent) | ~5× |
| Yang-Zhang (2000) | O, H, L, C + overnight | 14× |

Yang-Zhang is the most comprehensive: it captures overnight gaps (missed by Parkinson/GK/RS) and handles drift (missed by CC and GK). It is the recommended primary estimator.

**Bias correction**: Sample standard deviation underestimates true vol. Correction factor c₄(N):
- N=10: 0.973; N=20: 0.988; N=100: 0.998

**Diagnostic use**: Compare estimators. If Parkinson >> CC, intraday price action dominates. If CC >> Parkinson, overnight gaps dominate (e.g., around earnings).

### Barrier / First Exit Time Method
An alternative estimator using hitting times: measure how long log-prices take to exit ±b boundaries. More efficient than CC (std dev of estimates: 0.028 vs 0.048). Requires tick data.

### Intraday Seasonality
Vol is U-shaped intraday (Figure 2.8/2.9): highest at open and close, lowest at midday. Estimators using intraday data should account for this.

### Principle: No Single Best Estimator
Use all five. The differences between them are diagnostic signals about the nature of the vol you are trying to measure.

---

## Chapter 3: Stylized Facts About Returns and Volatility (pp. 53–65)

Six universally observed properties:

1. **Volatility clusters** — autocorrelation in |r|² and |r| is positive and slow-decaying (Figures 3.2/3.3). GARCH was built to capture this.

2. **Volatility mean-reverts** — VIX has half-lives on the order of weeks to months. The mean itself drifts across regimes (Figures 3.5/3.6).

3. **Fat tails** — excess kurtosis > 0 universally. Empirical values: Hang Seng 32.7, Nasdaq 9.9, FTSE 100 6.4, Nikkei 6.7, WTI 3.0, IBM 4.4, Google 2.0. BSM assumes kurtosis = 0.

4. **Leverage effect** — vol increases as price declines. Figure 3.4 shows negative autocorrelation of signed returns at lag 1. Two mechanisms: (i) financial leverage rises as equity value falls; (ii) volatility feedback (demand for puts increases after a decline).

5. **Volume-volatility correlation** — SPY daily range vs volume: r = 0.81; absolute returns vs volume: r = 0.68 (Figures 3.8/3.9). High-volume days are high-vol days.

6. **Log-normal distribution of vol** — Figure 3.10 shows right-skewed distribution of 30-day S&P 500 vol. Bull market (above 200-day MA): median vol = 12.1%; bear market: 21.6%.

---

## Chapter 4: Volatility Forecasting (pp. 66–83)

### EWMA
Simplest adaptive model: σ²_t = λσ²_{t-1} + (1-λ)r²_{t-1}. Default λ=0.94 (RiskMetrics). Problem: no mean reversion. GARCH strictly dominates.

### GARCH(1,1)
σ²_t = ω + αr²_{t-1} + βσ²_{t-1}

Long-run variance: V_L = ω/(1-α-β). Mean reversion speed: (1-α-β).

MSFT parameters (May 2007): ω=0.00000505, α=0.053, β=0.884.
Long-run vol ≈ 11%. Current vol ≈ 16%. Term structure decays exponentially to 11% over ~120 days (Figure 4.2).

**Use**: GARCH-predicted term structure = theoretical forward vol curve. Compare to market implied term structure to identify calendar spread value.

### Volatility Cone
Figure 4.3: for each horizon (30/60/120/240 days), plot max/median/mean/min of historical realized vol over rolling windows. Table 4.1 (MSFT): 30-day max 0.843, median 0.317, min 0.058; 240-day median 0.170.

**Use**: if current ATM IV plots above the historical max at that horizon, vol is historically expensive. Combine with GARCH forecast for a complete view.

### Variance Premium
IV systematically exceeds subsequent realized vol by ~30% for equity indices. This is the fundamental source of edge for vol sellers. But it varies — it can be near zero or negative for months. High IV is necessary but not sufficient to expect profit from selling.

---

## Chapter 5: Implied Volatility Dynamics (pp. 83–108)

### Vol Surface
Figure 5.1 (QQQQ, August 1, 2007): 3D surface — IV as function of strike and expiry. Two key dimensions: skew (IV vs strike) and term structure (IV vs expiry). Level shifts dominate slope changes.

### Term Structure Dynamics (Stein Result)
Stein (1989): σ_long = σ_LR + 0.85×(σ_front − σ_LR). The proportionality constant ≈ 0.85.
Figure 5.3 shows QQQQ ATM term structure slightly upward-sloping (0.219 to 0.228).

### Smile Dynamics: Sticky Strike vs Sticky Delta
- **Sticky Strike**: IV at each absolute strike is fixed as underlying moves
- **Sticky Delta**: IV at each delta is fixed as underlying moves
Figure 5.12 shows the backbone (sticky strike) vs actual smile. In practice: reality lies between these two conventions.

### Corrado-Su: Skewness and Kurtosis in the Smile
Extends BSM to incorporate third (μ₃) and fourth (μ₄) moments via Gram-Charlier expansion. Figure 5.14: with σ=0.30, μ₃=−0.70, μ₄=11, produces a pronounced downward equity smile. Negative skewness is the dominant driver of IV slope; excess kurtosis drives smile curvature.

### Earnings IV and Event Volatility
Figure 5.8 (AAPL, Q2 2007): IV rises ~10 days before earnings, collapses day of announcement. 73-stock pre-earnings long straddle test: 43% win rate, win/loss = 1.70, skewness = 5.4 (extreme right tail from large surprise outcomes).

---

## Chapter 6: Hedging (pp. 108–131)

### Utility-Based Framework
Hedging is a cost-benefit problem, not a continuous obligation. Minimize expected hedging cost while maintaining acceptable risk.

### Three Methods, Increasing Accuracy
1. **Hodges-Neuberger (HN)**: exact solution, computationally intensive PDE. Reveals asymmetric bands for long vs short gamma.
2. **Whalley-Wilmott (WW)**: analytic approximation: band ∝ [k×|Γ|/γ]^(1/3). Figure 6.5 shows straight diagonal bands vs delta. Good for small costs.
3. **Zakamouline**: improved approximation, preserves long/short gamma asymmetry (Figures 6.8). Currently recommended.

### Transaction Costs
Bid-ask spread (fixed) + market impact (proportional to √trade size). f(s) = k√s (square root law). Retail: bid-ask dominates. Institutional: market impact dominates.

### Aggregation
Portfolio vega = Σ(νᵢ × Sᵢ × λᵢ) using correlation matrix or PCA factor loadings.

### Practical Hedging Rules
1. Buy wings to inoculate against jump risk
2. Diversify across underlyings
3. Size positions to limit catastrophic loss
4. Don't use worst historical scenario as the benchmark (fat tails mean worse is always possible)

---

## Chapter 7: Distribution of Hedged Positions (pp. 131–144)

### Central Result
P/L of a continuously delta-hedged position:
```
P/L = ½(σ²_implied − σ²_realized) × ∫ e^(−rt) S²Γ(σᵢ) dt
    ≈ Vega × (σ_implied − σ_realized)
```

This is the engine. Sell straddles when IV > forecast realized vol.

### The Bad News: Wide Dispersion
Figure 7.1: 100 simulations of 1-year option hedged at 30% vol, 30% realized — portfolio value at expiry ranges from −$200,000 to +$50,000. Even with a positive edge, you lose frequently.

Table 7.1: daily hedging → mean P/L ≈ −$97, P10 = $7,612, kurtosis = 4.40. Returns are fat-tailed.

### Path Dependency
Figures 7.2/7.3: same annualized vol (23.44%) but different paths — jump on Day 1 vs jump before expiry — produce very different P/L outcomes. The timing of large moves within the option life matters.

### Hedging Dispersion Formula
σ_residual = σ_option × √(π/(2N)). Doubling hedging frequency reduces dispersion by 1/√2 ≈ 30%. Figure 7.6 shows the relationship.

### Hedging at Realized vs Implied Vol
- **Hedge at realized vol**: P/L per step = ½(σ²_r − σ²_i)S²Γdt — deterministic. Locks in edge. Unknown σ_r in advance.
- **Hedge at implied vol**: P/L is stochastic per step but unbiased. Minimizes P/L variance (Figure 7.10). Standard practice.

---

## Chapter 8: Money Management (pp. 144–176)

### Kelly Criterion
Maximize E[log(1 + f×G)]. For binary bet: f* = p − q/b.
Figure 8.4: expected bankroll peaks at Kelly fraction (~0.17 for typical trade). Betting > Kelly → bankroll depletes (geometric mean turns negative).

Good: maximizes long-run growth; zero ruin risk; optimal in long run.
Bad: requires knowing true probability; brutal drawdowns; not ergodic for finite-horizon traders.

### Fractional Kelly
Half-Kelly: reduces expected growth to 75% of full-Kelly but variance to 25%. Practically recommended for most vol traders. Figures 8.6/8.7/8.8 show PDF evolution at Kelly, half-Kelly, double-Kelly.

### Browne Goal-Reaching
α* = μW / (σ²(G−W)). Optimal for reaching a target G before ruin. Table 8.1: Browne beats Kelly by 10-40% in expected time to reach a goal.

### Mean-Reverting Sizing
For a mean-reverting process: optimal entry at S_max = 0.75σ from the mean (Figure 8.18). Applied to VIX: wait for VIX to trade 0.75 standard deviations above its rolling mean before shorting vol.

### Caution: Fat Tails
Figure 8.17: with logistic distribution (kurtosis = 9), Kelly-optimal position size destroys the bankroll. Always run fat-tail simulations before deploying position sizing rules.

---

## Chapter 9: Trade Evaluation (pp. 176–200)

### Performance Metrics
- **Sharpe**: (R_p − R_f) / σ_p. Standard benchmark. Weakness: treats upside and downside equally.
- **Sortino**: (R_p − MAR) / σ_downside. Better for skewed returns.
- **Omega**: E[gain above L] / E[loss below L]. Uses full distribution.
- **K Ratio**: linearity of log equity curve. Measures consistency, not just level.

### Goal Setting
Pre-define three levels: Success (Sharpe > 1.5), Respectability (0.8–1.5), Failure (< 0.5). Set before trading. Don't adjust post-hoc.

### Performance Persistence
Hurst exponent H: H > 0.5 means returns exhibit momentum (genuine skill). H = 0.5 means random. H < 0.5 means mean-reverting returns (possible overfitting).

---

## Chapter 10: Psychology (pp. 199–225)

Ten identified biases relevant to vol trading:
1. **Self-attribution**: successes = skill, failures = luck → gradual overconfidence
2. **Overconfidence**: precision of vol forecasts is overestimated
3. **Availability heuristic**: vivid/recent events judged too probable
4. **Short-term thinking**: excessive daily P/L monitoring magnifies loss aversion
5. **Loss aversion**: losses hurt 2× more than equivalent gains
6. **Conservatism**: underreacting to new information
7. **Representativeness**: judging by prototype, not base rates
8. **Confirmation bias**: seeking evidence that supports existing positions
9. **Hindsight bias**: overestimating past forecast accuracy
10. **Anchoring**: excessive reliance on first data seen (e.g., anchoring to recent ATM vol)

Sinclair's summary: trading with a partner with different views, maintaining written forecasts, and looking for contradicting evidence are the three most actionable debiasing techniques.

---

## Chapter 11: Variance Premium Empirics (pp. 225–235)

QQQ/QQQQ data confirms structural variance premium for equity index options:

| Strategy | Avg Weekly Return | Sharpe | Max DD |
|----------|------------------|--------|--------|
| Short 50-delta straddle | 9.8% | 1.37 | 29.8% |
| Short 30-delta straddle | 9.7% | 1.13 | ~30% |
| Short ATM straddle | ~9% | 1.14 | ~30% |
| Short 30-delta risk reversal | 13.5% | 0.69 | 26.9% |

Premium is NOT reliably present for individual equities — driven by index-level correlation risk and negative skewness of the index return distribution.

Reasons for premium: insurance provision; negative skewness (investor demand for puts); vol-of-vol uncertainty premium; correlation risk hedge.

---

## Chapter 12: The VIX (pp. 235–242)

Model-free implied variance from Carr-Madan: VIX² integrates across the entire option strip, not just ATM. Cannot be directly traded.

VIX futures are typically in contango (Figure 12.1): term structure from ~22 (spot) to ~27 (8-month). VXX (short-dated futures ETN) loses from roll in contango — chronic value decay.

Three trading strategies:
1. Dynamic VXX/VXZ: Sharpe 1.5, max DD 18% in simulation
2. Calendar put spread on VIX: Sharpe 1.2, annualized return 15.2%
3. Short VIX straddles: avg premium 3.26% (Oct 2006 – Nov 2010)

All vulnerable to crisis spikes.

---

## Chapter 13: Leveraged ETFs (pp. 243–250)

Vol decay: dL/L = λ(dS/S) − ½λ(λ−1)σ²dt. For 2× ETF: drag = σ²dt/day. For 3× ETF: drag = 3σ²dt/day.

Options on leveraged ETFs are compound options (Carr-Madan). Market IV > theoretical IV for SSO (Figure 13.3). Most likely terminal price, not λ×return, is the correct comparison for options.

---

## Chapter 14: Life Cycle of a Trade (pp. 250–258)

AAPL short straddle example (June 2007, iPhone launch period):

**Pre-trade estimates** (Table 14.2):
- Yang-Zhang: 33.1%, CC: 25.1%, GK: 28.2%, GARCH: 36.1%, HF: 44.9%
- AAPL ATM IV = 41.4%
- Vol cone (Figure 14.6): IV at historical maximum for 30-day horizon

**Decision**: short straddle, Vega = $1,000.

**Execution**: daily position tables. June 28 — quiet, no hedge. June 29 — slight rally, bought 400 shares. July 2 — vol declined to 34%.

**Result**: actual realized vol = 30.1% vs 41.4% IV. Edge = 11.3 vol points. P/L ≈ positive as expected.

---

## Chapter 15: Conclusion (pp. 259–262)

Successful vol trading requires being above average across all domains:
- Model understanding (BSM as language)
- Vol measurement (multiple estimators)
- Forecasting (GARCH + cones + IV)
- Hedging (utility-based bands)
- Sizing (Kelly/Browne)
- Evaluation (multiple metrics)
- Psychology (overcome known biases)

"It is far better to be a trader in the slipstream of great traders than to grind away in a highly competitive business." — Sinclair
