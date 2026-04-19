# Option Volatility and Pricing — Detailed Summary
*Sheldon Natenberg — Second Edition*

---

## Part I: Financial Contracts (Chapters 1-3)

### Chapter 1: Financial Contracts
Natenberg begins with the building blocks: forwards, futures, and options. A key foundational principle: in derivatives markets, you can sell first and buy later — unlike conventional markets where you must own before selling. This short-selling capability is foundational to every option strategy.

The notional value of a derivative (quantity × price) represents total exposure, but initial capital required (margin) is only a fraction. Futures require mark-to-market daily settlement — gains are credited, losses debited, margin calls issued when accounts fall below maintenance. Understanding the settlement mechanics prevents costly surprises.

### Chapter 2: Forward Pricing
The forward price of any underlying is determined by the spot price plus cost of carry:
- **Stocks**: F = S × e^(rT) − PV(dividends)
- **Futures**: F = S × e^(r−q)T where q is the continuous dividend yield
- **Currency**: F = S × e^(r_domestic − r_foreign)T

The critical concept of **implied values**: any unknown variable (spot price, interest rate, dividend) can be back-solved if all other inputs plus the forward price are known. This same back-solving concept directly underlies implied volatility.

### Chapter 3: Contract Specifications and Settlement
Options differ by: settlement style (European vs. American), underlying type (stock, futures, index, currency), settlement type (cash vs. physical), and strike/expiry conventions. Eurodollar options invert convention: a 93 call = a 7% put in interest-rate terms. Always verify quoting conventions before trading interest-rate derivatives.

---

## Part II: Pricing Theory (Chapters 4-6)

### Chapter 4: Expiration P/L and Parity Graphs
At expiration, options have simple payoffs: calls = max(0, S−K), puts = max(0, K−S). Parity graphs show these payoffs as straight-line hockey-stick shapes. For any complex strategy, the expiration P/L is the sum of all individual option payoffs plus the breakeven adjustment from premium paid/received. The parity graph is the simplest tool for understanding a strategy's expiration behavior — no Greeks needed.

### Chapter 5: Theoretical Pricing Models
**The central insight**: option theoretical value = expected value of payoff at expiration, discounted to present value. This requires a probability distribution for the underlying at expiration. The Black-Scholes model assumes a lognormal distribution of future prices (equivalently: normally distributed log returns).

Why lognormal? Stock prices cannot go below zero but can rise without bound — this asymmetry matches the lognormal distribution. Log returns (ln(P_t/P_{t-1})) are normally distributed; price levels are lognormally distributed.

Theoretical value is only half the problem. Because the model is probability-based, outcomes are only reliable in the long run — any single trade can deviate from expected value. A trader must also manage variance.

### Chapter 6: Volatility
**The most important chapter in the book.**

Volatility = the annualized standard deviation of logarithmic price returns. It is the single input to option pricing models that cannot be directly observed — every other input (price, strike, expiry, rate, dividend) is known. This makes volatility the central variable of all options analysis.

**Calculating historical volatility**: (1) log returns r_i = ln(P_i/P_{i-1}); (2) sample standard deviation using n−1 divisor; (3) annualize by multiplying by √252. Lookback window choice is a tradeoff: 20-day is responsive but noisy; 60-day is balanced; 252-day is stable but slow.

**Alternative estimators**: Parkinson (high-low) and Garman-Klass (open-high-low-close) are more statistically efficient than close-to-close but understate vol for assets with overnight gaps.

**The lognormal distribution**: Its asymmetry (bounded below at zero, unbounded above) means the mean of the future price distribution exceeds the current forward price. The right tail is longer than the left tail.

---

## Part III: Dynamic Hedging and the Greeks (Chapters 7-13)

### Chapter 7: Dynamic Hedging
**Proof of concept**: An option's theoretical value can be replicated by dynamically hedging a delta-neutral position in the underlying throughout the option's life. The cost of this replication = the sum of all cash flows from the hedging process = the option's theoretical value.

The mechanics: (1) buy options, sell underlying delta amount; (2) as underlying moves, delta changes (gamma), creating directional drift; (3) rebalance to restore neutrality; (4) each rebalance trade is a small profit (for long gamma); (5) cumulative gamma scalp profits = theta paid → breakeven condition.

**Long gamma position**: profits from realized vol > IV. Each move — up or down — creates a scalp profit because delta shifts in the favorable direction. The cost is theta (daily time value decay).

**Short gamma position**: profits from realized vol < IV. Collects theta. Loses from large moves because delta shifts adversely.

**Rebalancing frequency**: Too frequent → transaction costs eat profits. Too rare → directional risk accumulates. Professional rule: rebalance when delta drifts by approximately one standard deviation of expected daily move.

**The fundamental relationship**: the expected realized volatility is the break-even volatility for a delta-neutral hedge. If the option was purchased at 30% IV, it breaks even when realized vol = 30%.

### Chapter 8: Greeks I — Delta
Delta = ∂V/∂S = rate of change of option value with underlying price. Ranges 0→1 for calls, 0→−1 for puts. ATM call delta ≈ 0.50 (slightly above/below due to forward price). In Black-Scholes, call delta = N(d₁) ≈ risk-neutral probability of expiring ITM.

**Volatility's effect on delta**: High volatility pulls all deltas toward 0.50 (OTM options become more ATM-like). Low volatility pushes deltas toward 0 or 1 (bimodal distribution). This means OTM options purchased at low vol will see large delta increases if vol spikes.

**Position delta**: always expressed in underlying equivalents. Position delta = sum(option delta × contracts × 100).

### Chapter 9: Greeks II — Gamma
Gamma = ∂²V/∂S² = rate of delta change per point move in underlying. All long options (calls or puts) have positive gamma. Add gamma to delta on up moves, subtract on down moves.

**Gamma across conditions**: ATM options have peak gamma. Gamma spikes near expiry for ATM options. Gamma decreases for ITM/OTM options as expiry approaches (they become more "digital" — certain to be in or out of the money).

**Position gamma management**: Net position gamma determines how fast delta drifts and how urgent rebalancing is. Large negative gamma positions risk exponential loss acceleration on big moves.

**Higher-order Greeks**: Speed = dGamma/dS. Charm = dDelta/dTime. These matter for large positions with long holding periods.

### Chapter 10: Greeks III — Theta
Theta = ∂V/∂t = time decay per unit of time. Long options pay theta (negative theta); short options earn it (positive theta).

**Key theta properties**: (1) ATM options have the highest theta; (2) ATM theta accelerates as expiration approaches (approach infinity at the last moment); (3) ITM/OTM theta slows near expiry; (4) ATM theta is proportional to IV.

**Theta-gamma tradeoff**: Theta and gamma are inescapably linked for ATM options. Maximum daily theta income comes with maximum gamma risk. No free lunch.

### Chapter 11: Greeks IV — Vega
Vega = ∂V/∂σ = dollar change in option value per 1% change in IV. Long options have positive vega; short options have negative vega.

**Key vega properties**: (1) ATM options have peak vega; (2) vega increases with time to expiry (LEAPS have highest vega); (3) for ATM options, vega is nearly constant across vol levels (linear value function); (4) vega can decrease with time for some stock options (forward price moves option away from ATM).

**Volga/vomma**: dVega/dVol. ATM options have near-zero volga. OTM/ITM options have positive volga — their vega increases as vol rises. Maximum volga at deltas of ~10 and ~90.

**Vanna**: dDelta/dVol (= dVega/dS). Measures how much delta changes if vol changes. Critical for managing delta hedges in volatile vol environments.

### Chapter 12: Greeks V — Rho and Phi
Rho = ∂V/∂r = sensitivity to interest rates. For stock options: calls have positive rho (rise with rates), puts have negative rho (fall with rates). Effect is small for short-dated options but significant for LEAPS and ITM options. Deep ITM calls have highest rho.

Phi = sensitivity to dividend yield. Relevant for stock and index options with known dividend streams. Often modeled implicitly through forward price adjustments.

---

## Part IV: Spreads (Chapters 14-17)

### Chapter 14: Introduction to Spreads
**Four reasons to use spreads**: (1) Relative value — capture IV mispricing between two options; (2) Scenario expression — design a position that profits from a specific market outcome; (3) Variance reduction — spreading reduces outcome variance, making edge more reliable; (4) Capital efficiency — lower margin requirements than outright positions.

**Spreading increases breakeven vol range**: An outright short straddle at 25% IV breaks even only if realized vol ≈ 25%. A spread might allow profitability from 20% to 35%. Wider margin for error.

**The casino analogy**: Spreading the risk across multiple positions, like a casino spreading bets across many games, is more reliable than concentrating risk in one large trade.

### Chapter 15: Volatility Spreads
The four primary volatility spreads:
- **Straddle** (long call + long put, same strike): pure long vol. Profits from large moves in either direction. +gamma, −theta, +vega.
- **Strangle** (OTM call + OTM put): similar to straddle but cheaper, wider breakevens.
- **Butterfly** (long body, short two wings): profits from quiet market. Expiration value bounded by 0 and spread width. Opposite of straddle.
- **Condor** (four-legged butterfly with wider range): profits from range-bound market. Call condor = put condor (put-call parity).

**Ratio spreads**: asymmetric — long N options / short 2N (or more). Executed for credit. Profitable for small to moderate directional moves but exposed to large losses beyond the short strikes. Requires active management.

**Christmas tree**: long 1 lower strike / short 1 middle / short 1 upper. Hybrid between butterfly and ratio spread. Asymmetric P/L.

### Chapter 16: Calendar Spreads and Diagonal Spreads
**Calendar spread mechanics**: short near-term / long far-term, same strike. Increases in value when: (1) underlying stays near strike (near-term theta accelerates); (2) IV rises (far-term has more vega). Loses when: underlying moves far from strike; IV falls.

**Pre-event IV**: before earnings or announcements, IV rises while stock stays quiet. Long calendar spreads (long vega, long theta differential) benefit pre-event. Post-event, vol crush can hurt.

**Diagonal spreads**: same structure as calendar but different strikes as well as different expirations. Adds directional component to the vol play.

**Time boxes**: two diagonal spreads creating a four-legged position that captures IV term-structure mispricings between two expirations. Advanced market maker tool.

### Chapter 17: Synthetic Relationships
Put-call parity: C − P = F − K × e^(−rT) (for European options on futures; adjustments for dividends, settlement type).

**Six synthetic positions**:
1. Synthetic long underlying: long call + short put (same strike) = long stock
2. Synthetic short underlying: short call + long put = short stock
3. Synthetic long call: long underlying + long put
4. Synthetic short call: short underlying + short put
5. Synthetic long put: short underlying + long call
6. Synthetic short put: long underlying + short call = **covered call**

**Critical implication**: Covered call ≡ synthetic short put. Same risk profile. Same downside exposure. The stock you own does not protect you.

**Call and put delta sum**: |delta_call| + |delta_put| ≈ 100. If 100 put delta = −60, 100 call delta = +40.

---

## Part V: Advanced Option Pricing (Chapters 18-19)

### Chapter 18: The Black-Scholes Model in Depth
The six assumptions of Black-Scholes: (1) frictionless markets; (2) continuous trading; (3) constant interest rates; (4) constant volatility; (5) volatility independent of price; (6) small price changes normally distributed.

All six are violated in practice. The most impactful violation: volatility is NOT constant — it varies across strikes (smile/skew) and time (term structure). This is the most important limitation to understand.

**Greeks from Black-Scholes**:
- Delta = N(d₁)
- Gamma = N'(d₁) / (S × σ × √T)
- Theta = multiple components (vol decay + interest)
- Vega = S × N'(d₁) × √T

The theta of an ATM option is directly proportional to vol: theta_ATM ≈ S × σ × N'(d₁) / √(2πT).

### Chapter 19: Binomial Option Pricing
The Cox-Ross-Rubinstein binomial model builds a lattice of future stock prices and works backward from expiration to compute theoretical value. Advantage over Black-Scholes: can price American options (early exercise) by comparing exercise value to continuation value at each node.

Limitation: computationally intensive. The Barone-Adesi/Whaley quadratic approximation provides a faster alternative for American options with good accuracy.

---

## Part VI: Volatility and Advanced Applications (Chapters 20-25)

### Chapter 20: Volatility Estimation
Multiple estimators: close-to-close (standard), Parkinson (high-low), Garman-Klass (open-high-low-close). The latter two are more efficient but understate vol for assets with overnight gaps.

Volatility term structure: plot IV against expiration dates. Months plotting above the smooth curve are overpriced; months below are underpriced. Forward volatility for a period t₁→t₂: σ_forward = √[(σ₂² × t₂ − σ₁² × t₁) / (t₂ − t₁)]. This is the break-even vol implied by a calendar spread.

### Chapter 21: Volatility Spreads in Practice
Delta-neutral volatility trading strategies require deciding: when to adjust (rebalancing frequency), how to adjust (underlying vs. options), and how much to reduce size when risk is exceeded. Adjustments that improve the position's risk-reward characteristics are preferred over mechanical adjustments.

### Chapter 22-23: Hedging with Options
Hedger decision framework: (1) Is worst-case disaster protection required? (2) How much directional risk to eliminate? (3) What additional risks are acceptable? Hedging strategies: outright put purchase, collar, ratio put spread, calendar spread overlay.

### Chapter 24-25: Volatility Skew and Volatility Contracts
**Volatility skew**: IV is not constant across strikes. Equity skew is downward-sloping (OTM puts > OTM calls) due to: insurance demand from institutional investors + covered call writing pressure from retail. This structural premium makes OTM put selling systematically profitable — but with crash risk.

**Skew by asset class**: Equity (downward), commodity (upward or mixed), currency (symmetric smile). Do not assume equity skew behavior applies to other markets.

**Volatility derivatives**: VIX futures, variance swaps, volatility swaps allow pure vol exposure without delta risk. Variance contracts are preferred because variance is additive over time (allows static option replication via the log-contract). VIX futures typically trade in contango due to future uncertainty premium.

---

## Key Quantitative Formulas

| Formula | Description |
|---------|-------------|
| F = S × e^(rT) | Forward price (continuous compounding) |
| σ_annual = σ_daily × √252 | Annualize daily vol |
| Expected daily move = σ_annual × S / √252 | 1-day 1-sigma range |
| σ_forward = √[(σ₂²t₂ − σ₁²t₁)/(t₂−t₁)] | Forward volatility between two dates |
| ΔV ≈ Δ × ΔS + ½ × Γ × ΔS² | Better P/L estimate using gamma |
| |delta_call| + |delta_put| ≈ 100 | Delta relationship for call/put pair |
| D = [S × (1 + r × t)] − F | Implied dividend from forward |

---

## Most Important Warnings

⚠️ **Covered call = synthetic short put.** The stock you own does not provide additional protection. You have the same downside risk as a naked short put.

⚠️ **Gamma compounds losses for short positions.** A $5 adverse move generates more loss than delta × $5. Always compute P/L estimates using both delta and gamma.

⚠️ **High IV does not always mean sell.** IV can stay elevated or rise further. Mean reversion is real but slow and unreliable over option holding periods.

⚠️ **American put early exercise premium.** Deep ITM puts may be worth exercising early, especially in low-vol, high-rate environments. Short put holders must monitor assignment risk.

⚠️ **Transaction costs eliminate theoretical edge for frequent rebalancers.** A delta-neutral strategy requiring 20+ weekly adjustments may pay more in commissions and spreads than the initial theoretical edge.

⚠️ **Vega of stock options can decrease with time.** Do not assume longer = more vega for all strikes and underlyings. Verify with pricing model.
