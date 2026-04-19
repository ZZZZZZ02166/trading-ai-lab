# Detailed Summary: Option Market Making

---

## Chapter 1: Economics of Option Market Making

The book opens by defining the market maker's role: a professional who stands ready to buy at a bid and sell at an offer at all times, providing the service of *immediacy*. Without market makers, buy and sell order flows would rarely be evenly matched, causing prices to be more volatile and erratic. Market makers earn the bid/offer spread as gross income — this is called "getting the edge."

The supply/demand analysis shows that a market maker enters the market when prices deviate from long-run equilibrium: selling when prices rise above equilibrium (P1) and buying when they fall below (P2). The spread between P1 and P2 is the market maker's compensation for providing price stability.

Importantly, options/futures trading is a zero-sum game — every dollar one trader makes, another loses. This does not make market making socially harmful; rather, it provides risk-shifting services (analogous to insurance) that allow commercial firms to hedge and concentrate on productive activity.

**The market maker's cost structure is more demanding than it appears.** While exchange members pay minimal brokerage, they still face overhead costs (membership fees, data services, office costs) and must often give up edge on some trades to maintain order flow. Empirical studies show net profit per trade is well below the full bid/offer spread.

The key distinction between option market making and other forms of dealing: option market makers accumulate *carryover positions* across multiple strikes and expirations that cannot be quickly liquidated. Managing this complex ongoing exposure — not just the daily trading — is the central challenge of the business.

**The perspective of this book is pure market making** — income from providing liquidity, not from speculative directional bets. The goal is risk-neutral profit. Market makers who take directional shots are speculating, and speculation in options can lead to catastrophic losses if not managed carefully.

---

## Chapter 2: Options

### What is an Option?

A call option gives the holder the right to buy the underlying at the strike price. A put gives the right to sell. The seller (writer) of the option is obligated to fulfill this right if the buyer exercises. Options can be on spot assets (cash options) or futures contracts (futures options). Futures options deliver a futures position when exercised.

**Payoff at expiration:**
- Long 100 call (premium $1.70): loss of $1.70 below $100, breakeven at $101.70, unlimited gain above
- Long 100 put (premium $1.70): loss of $1.70 above $100, breakeven at $98.30, increasing gain below
- Short positions are the mirror images

**Intrinsic value** is the immediate exercise value. For a call: max(asset price − strike, 0). For a put: max(strike − asset price, 0). Options with intrinsic value are *in the money* (ITM); those without are *out of the money* (OTM). The value above intrinsic is *time premium* (extrinsic value) — the market's price for uncertainty about future moves. At expiration, all time premium vanishes.

### Option Fair Value

An option is fairly valued when trading at that price produces neither gain nor loss for either side over the long run. Fair value is the probability-weighted average of all possible payoffs:

**V = Σ (probability × payoff)**

Modern fair-value models use the Black-Scholes-Merton (BSM) framework, which links the log-normal probability distribution of future price changes to expected payoffs. The BSM model for futures options requires five inputs: (1) current futures price, (2) strike price, (3) time to expiration (annualized), (4) risk-free interest rate, (5) volatility.

**BSM formulas (Fischer Black futures version):**
- C = e^(-rt) × [X × N(d1) − K × N(d2)]
- P = e^(-rt) × [K × N(−d2) − X × N(−d1)]
- d1 = [ln(X/K) + (S²/2)t] / (S√t)
- d2 = d1 − S√t

Where N(d) is the cumulative normal distribution, X = futures price, K = strike, S = volatility, t = time to expiration, r = risk-free rate.

### Volatility

Volatility in the BSM model is the standard deviation of annualized log percentage price changes. It converts to a daily standard deviation in points as: SDP = P × (V / √250), where P is the current price and V is annualized volatility. The square-root-of-time rule governs scaling across time intervals.

**Two types:**
- **Historical (statistical) volatility:** Calculated from actual past price changes. Always looking backward. Formula: SDV = √[Σ(Ri − R̄)² / (N−1)] × √PY
- **Implied volatility:** Derived by solving BSM backward from the market option price. Forward-looking — the market's current consensus estimate of future volatility.

**Critical problem:** Real financial asset returns are NOT log-normally distributed. Multiple empirical studies show:
1. **Fat tails** — extreme events occur far more frequently than normal distribution predicts (Figure 2.5: wheat futures; Figure 2.6: S&P 500 error curve)
2. **Leptokurtosis** — higher central peaks than normal (Figure 2.4)
3. Cauchy and Paretian distributions fit better than log-normal (Figure 2.7)

**Heteroscedasticity** — volatility is not constant over time. It clusters and shifts. This makes historical volatility an unreliable predictor of future volatility. Figure 2.8 (October cotton futures) shows implied and 20-day historical vol frequently diverging by 10+ percentage points with no consistent predictive relationship.

### Financial and Futures Options

Futures markets can be in **contango** (distant months above near months, normal when storage costs are positive) or **backwardation** (near months above distant, usually supply shortage). Income-earning assets (stocks, bonds) typically have backward futures term structure because futures are discounted by the income yield. Understanding term structure matters for option fair value across expiration cycles.

---

## Chapter 3: Option Risks

Six quantifiable market-based risks for any option position:

### Delta (Δ)
Dollar change in option price per $1 change in underlying price. The *hedge ratio*. Ranges from 0 to +1.0 for calls (0 to −1.0 for puts). Deep ITM delta → ±1.0; far OTM delta → 0; ATM delta ≈ ±0.50. Delta also approximates the probability of expiring in-the-money.

Delta changes as price and time change (this change is gamma). A delta-neutral position has net delta of zero — no short-term price sensitivity. But delta neutrality requires continuous rebalancing because price moves change delta.

### Gamma (Γ)
Rate of change of delta per $1 change in price. Measures curvature. Long options always have positive gamma. Short options have negative gamma. ATM gamma is highest; deep ITM or OTM gamma → 0. Near expiration, ATM gamma spikes dramatically — creating "pin risk" where a small price move near a strike can cause enormous delta changes. Lambda (elasticity) is the percentage change in option value per 1% change in underlying; always >1.

### Theta (Θ)
Daily time decay. Long options have negative theta (lose value daily). Short options have positive theta (gain value daily). ATM theta is largest; deep ITM/OTM theta is smallest. Theta and gamma have opposite signs for long options — the gamma benefit from large moves must exceed the daily theta cost for a long position to profit.

### Kappa/Vega (K)
Dollar change per 1-point change in implied volatility. Long options are positive kappa (benefit from rising IV). Short options are negative kappa. ATM long-dated options have highest kappa. Kappa risk is often the LARGEST risk for market makers — a 10-point IV move can cause $800+ swings per contract in major futures, dwarfing delta or theta effects. Kappa must be managed separately from delta.

**Key paradox:** A long call position can lose money even when the underlying rises, if implied volatility falls sharply at the same time. This is a common source of confusion for traders who don't understand kappa.

### Rho (ρ)
Sensitivity to risk-free interest rate changes. Small for futures options (futures price already reflects carry). Significant for long-dated stock or bond options.

### Skew Risk
Different strikes in the same expiration trade at different implied volatility levels — the *implied volatility skew* (or smile). Positive skew means OTM wings trade at higher IV than ATM center — the most common pattern in most markets. Skew risk arises when this shape changes. A skew shift from a large price move (Figure 8.4) can hurt vertical spread traders independent of any directional move.

---

## Chapter 4: Position Risk Profiles

Every option trading strategy for a single expiration can be classified as one of 22 core positions. The risk character of any position is described by its *risk sign modality*:
- **Unimodal** — risk has one sign (positive or negative) across all prices. Characteristic of single options and straddles.
- **Bimodal** — risk changes sign once across the price range. Characteristic of vertical spreads.
- **Trimodal** — risk changes sign twice. Characteristic of butterflies and condors.

Key position types:
- **Straddle:** Same-strike call + put. Unimodal positive gamma (benefits from any large move), negative theta (costs daily time decay)
- **Strangle:** Different-strike call + put. Similar to straddle but cheaper, smaller gamma near center
- **Vertical spread:** Long/short different strikes, same expiration. Bimodal gamma
- **Butterfly:** Long outer strikes, short two center strikes. Trimodal; profits from price staying near center
- **Condor:** Like butterfly but wider profitable zone. Long two outer, short two inner
- **Ratio spread:** Long one, short more at different strike. Can have unlimited risk on the short side
- **Conversion/Reversal:** Arbitrage using put-call parity (call − put = futures − strike + carry). Near-zero market risk

**Quirkiness:** Complex carryover positions can develop highly irregular risk profiles near expiration (Figure 4.1) — risk concentrates in unpredictable ways around specific strikes. Regular stress-testing across all strikes is essential.

---

## Chapter 5: Synthetic Option Making

Synthetic trading exploits put-call parity relationships for near-risk-free profits. A conversion combines a long underlying, long put, and short call at the same strike — the net position has nearly zero market risk. If the premium collected exceeds carrying costs, the trade earns a risk-free return. Reversals are the opposite. Box spreads combine a bull call spread with a bear put spread for an interest rate arbitrage.

These arbitrage relationships define the outer limits of how far any option can deviate from fair value — any deviation beyond transactions costs will be immediately eliminated by arbitrage capital.

---

## Chapters 6-7: Calendar Spread Risk and Strategy

Time spreads (calendar spreads) carry two additional risks beyond single-month position risks:

- **Time delta:** Risk from differential price sensitivity across contract months. If front-month futures rally more than back-month (basis change), time delta creates P&L impact
- **Time kappa/vega:** Risk from divergent IV changes between months. Implied volatility can move differently in front vs back months

Calendar spreads are not simply risk-free relative value trades — they carry meaningful time-based risks that must be modeled and monitored separately.

**Core strategy principles:**
- Trade delta-neutral — never speculate on direction
- Understand skew levels before pricing any spread
- Use technical analysis to identify support/resistance for position adjustment (not for prediction)
- Long butterflies and condors are optimal when IV is high and you expect range-bound markets
- Adjust kappa exposure by modifying spread ratios rather than adding naked positions

---

## Chapter 8: Market-Making Tactics

**Making a spread market:** The market maker sets bid and offer prices around the theoretical fair value, adjusting for current inventory position, order flow, and volatility levels. In high-liquidity markets, spreads are narrow; in illiquid markets, wider spreads compensate for added risk.

**Tracking trading results:** Separate the daily P&L into two accounts:
1. **Carryover account:** Daily mark-to-market change in existing positions (before new trades)
2. **Daily trading account:** P&L from new trades executed that day

This separation is the only way to know whether profits come from market-making edge or from lucky carryover position moves. A genuine market maker shows positive daily trading P&L across many cycles.

**The four most common market maker mistakes:**
1. **Failure to hedge delta** — taking directional shots instead of hedging immediately. The cardinal rule: *hedge when you should, not when it's most convenient.*
2. **Incorrect delta hedging** — using stale posted board prices instead of actual traded futures prices for delta calculations
3. **Overtrading** — trading more contracts than you can monitor and hedge accurately, eroding edge
4. **Poor kappa/vega adjustment** — allowing net kappa to drift too far in one direction, creating large IV-driven P&L swings

---

## Chapter 9: Observations from the Floor

Floor trading requires: strong mental arithmetic, physical stamina, self-esteem to handle the aggressive pit environment, and a cooperative style that builds long-term broker relationships. Professional options market making is now accessible both on-floor and off-floor (electronic/OTC). Capital requirements range from $25,000–$500,000+ depending on market and scale of operation.
