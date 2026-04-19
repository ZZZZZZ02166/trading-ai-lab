# Trading Option Greeks 2e — Detailed Summary
*Dan Passarelli, 2012 (Second Edition)*

---

## Part I: The Basics of Option Greeks (Ch. 1–8)

### Chapter 1: The Basics (pp. 18–37)

The book opens by establishing the vocabulary. An option is a contract that gives the holder the *right but not the obligation* to buy (call) or sell (put) a fixed quantity of an underlying asset at a specified strike price. Standard equity option contracts represent 100 shares. For every long contract in existence there is a corresponding short contract—they are created in pairs and are equally common.

Passarelli introduces the mechanics of opening and closing positions, the role of the Options Clearing Corporation (OCC) as counterparty guarantor, and the distinction between intrinsic value (how far an option is ITM) and time value (the remainder). He defines moneyness: for calls, ITM = stock > strike; ATM = stock ≈ strike; OTM = stock < strike. Puts reverse the relationship.

The chapter walks through the four basic option positions using Target (TGT) and S&P ETF (SPY) examples:
- **Long call**: hockey-stick payoff, defined max loss (premium), unlimited upside above the break-even (strike + premium).
- **Short call**: limited reward (premium), unlimited risk if the underlying rises. Covered call = long stock + short call: caps upside at the strike but eliminates the unlimited-risk problem.
- **Short put**: collects premium but obligates the seller to buy stock at the strike. Break-even = strike − premium. Equivalent to a covered call in economic exposure.
- **Long put**: bearish directional bet or protective hedge (married put = long stock + long put = portfolio insurance).

Spreads are introduced as combinations of the four basic positions. The at-expiration diagram is established as the standard visual tool.

---

### Chapter 2: Greek Philosophy (pp. 39–69)

Chapter 2 is the heart of Part I. Option pricing was revolutionised in 1973 by Black, Scholes, and Merton. The Black-Scholes model uses six inputs: stock price, strike price, time to expiration, risk-free interest rate, dividends, and volatility. The greeks—delta, gamma, theta, vega, rho—are the partial derivatives of this model with respect to each input.

**Delta (Δ)** has four equivalent definitions:
1. Rate of change of option value per $1 move in the underlying
2. Slope of the option price vs. stock price graph
3. Equivalent shares represented (delta × 100 for equity options)
4. Approximate probability of expiring ITM (trader's rule of thumb, not exact)

Call deltas range 0 to +1; put deltas range −1 to 0. The table on p. 44 shows RMBS options with stock at $21.30: the 17.5 call (0.81 delta) vs. the 30 call (0.89 delta) — deep ITM options have deltas near 1. Higher volatility pushes ITM deltas down and OTM deltas up, expanding the delta distribution away from extremes.

**Gamma (Γ)** is the rate of change of delta per $1 move in the underlying. Highest for ATM options near expiration; lowest for deep ITM/OTM. Gamma is what makes long options convex: large moves benefit holders more than initial delta implies. Short options have negative gamma—a dangerous, concave risk profile.

**Theta (Θ)** is daily time decay. Long options have negative theta; short options have positive theta. ATM options have the most time value and the highest absolute theta. Theta is not linear—it accelerates as expiration approaches and becomes especially steep in the final two to three weeks. Higher volatility inputs create higher option prices, which means faster absolute dollar decay.

**Vega (Υ)** measures sensitivity to a 1 percentage-point change in IV. Long options have positive vega. ATM options have the highest vega; LEAPS have much higher vega than short-dated options. The p. 60 table shows the ATM 30-strike call with vega = 0.085, compared to far-OTM options with vega near zero.

**Rho (ρ)** measures sensitivity to a 1 percentage-point change in the risk-free rate. Calls have positive rho; puts have negative rho. For short-dated options (22 days), rho ≈ 0.015—nearly irrelevant. For LEAPS (2 years), rho ≈ 0.858—significant.

**Put-Call Parity**: c + PV(strike) = p + S. This equation mathematically links every call and put of the same strike and expiration. Rearranged: call = put + stock − strike + interest − dividends. This underpins all synthetic positions and is the basis for arbitrage when prices deviate. Passarelli's mentorship story on the floor: "A put is a call; a call is a put."

---

### Chapter 3: Understanding Volatility (pp. 70–87)

**Historical Volatility (HV)** = annualized standard deviation of close-to-close log returns. Convention: 252 trading days per year (or 256, since √256 = 16, a computational convenience). HV is backward-looking.

**Implied Volatility (IV)** is the volatility input that makes a pricing model match the observed market option price. It is the market's forward-looking consensus on future realized volatility. A $100 stock with 32% IV implies ~68% probability of staying within $68–$132 over one year. The 1-day expected σ = IV / √256 = 2% for a 32% IV stock.

IV responds to market psychology: it rises with fear and anticipated events, falls with complacency and post-event vol crush. "Buy the rumor, sell the news" manifests in IV rising into earnings and collapsing after. Market makers act as natural dampeners by arbing away extreme premium.

**IV term structure**: Normally, longer-dated options have higher IV (contango). Before events, the front month can spike into backwardation. Passarelli shows GM 32.5 calls at different expirations: February at 32%, March at 33%, April at 34%—a gentle upward slope in quiet conditions.

**Volatility skew**: OTM puts trade at higher IV than ATM options, which trade higher than OTM calls. In the Citigroup example (p. 86), the 31-strike puts have IV more than 10 points above the 38-strike calls at the same distance from ATM. This reflects the persistent demand for downside protection.

**VIX** = the CBOE's measure of a hypothetical 30-day SPX option's IV. The "fear index." Passarelli notes that VIX levels provide insight into expected market-wide vol and mean-revert strongly over time.

---

### Chapter 4: Option-Specific Risk and Opportunity (pp. 87–109)

This chapter uses Disney call examples to show how greeks interact for a directional option buyer. Kim buys the Disney March 37.5 call (OTM). Her greek priorities:
1. **Delta**: most important—her entire rationale is directional.
2. **Theta**: working against her daily at −$0.70 per contract.
3. **Vega**: secondary risk; IV can rise or fall.
4. **Gamma**: helpful if the stock moves strongly through the strike.

The three-way strike comparison (ITM 32.5 vs. ATM 35 vs. OTM 37.5 calls) shows the trade-offs: ITM calls behave most like stock (high delta, low gamma/vega). ATM calls have maximum gamma and vega. OTM calls offer maximum leverage relative to premium spent but have the lowest win probability.

The "teenie" discussion (pp. 107–108) illustrates the asymmetry of OTM options: teenie buyers paid minimal amounts for occasional huge payoffs; teenie sellers collected tiny credits with occasional catastrophic losses. Neither edge is inherent—options are fairly priced in aggregate. Edge must come from superior forecasting.

---

### Chapter 5: An Introduction to Volatility-Selling Strategies (pp. 109–127)

While Chapter 4 discussed long options (time working against the trader), Chapter 5 flips to short options. **The gamma-theta relationship is the central theme**: short-option strategies collect theta (positive daily income) but accept gamma risk (losses from stock movement).

Passarelli walks through three examples:
- **Naked call (Brendan)**: Sells JNJ 65-strike call at $0.66 when stock is at $62 in a channel. Delta=0.34, Gamma=0.15. If JNJ rises just $1.01, the stop-loss at $1.10 is triggered—gamma made the loss accelerate faster than delta alone predicted. Key: as theta rises near expiration, so does gamma.
- **Short put (Stacie)**: Bullish-neutral sell of the JNJ 62.5-strike put. Higher delta (0.45 vs. Brendan's 0.34), so a larger premium and higher risk. Rising IV that typically accompanies a stock decline can accelerate losses before the stop is hit.
- **Short put with term structure awareness (Bill)**: Harley-Davidson example comparing March (19.2% IV) vs. April (23.3% IV). March is cheapest by IV but may not offer enough premium. Bill must decide whether the higher-IV month's extra premium compensates for the added uncertainty.

A practical observation closes the chapter: the naked call and covered call have essentially the same P/L shape at expiration—the difference is in capital requirement, unlimited-risk treatment, and psychological framing.

---

### Chapter 6: Put-Call Parity and Synthetics (pp. 128–148)

This is the synthetic positions chapter. Put-call parity: c + PV(strike) = p + S (or in pricing-model form: call = put + stock − strike + interest − dividends). Rearranging this equation creates all synthetic positions:

| Synthetic | Components |
|-----------|------------|
| Synthetic long call | Long put + long stock |
| Synthetic short call | Short put + short stock |
| Synthetic long put | Long call + short stock |
| Synthetic short put | Short call + long stock |
| Synthetic long stock | Long call + short put (same strike) |
| Synthetic short stock | Short call + long put (same strike) |

**Conversions** (long stock + long put + short call) and **reversals** (short stock + short put + long call) are near-riskless positions used by market makers to lock in pricing discrepancies. The P/L is the put-call parity discrepancy.

**Pin risk** (pp. 143–144): at expiration when the stock is right at the strike, the market maker doesn't know if the option will be assigned. This creates a ±100 delta uncertainty that must be managed carefully.

**Box spreads**: bull call spread + bear put spread (same strikes, same expiration) = fixed-value instrument. A 60–70 box is always worth $10 at expiration. It should trade at PV($10) = $10 − interest. If it trades below fair value, it's a riskless arbitrage opportunity.

---

### Chapter 7: Rho (pp. 148–157)

Rho = sensitivity to the interest rate. From put-call parity: higher rates raise call prices and lower put prices. The relationship: as rates rise, the forward price (cost of carrying the underlying) increases, which benefits calls.

For a 2-year LEAPS call with a $70 strike at 8% interest: rho = +0.793. A 1% rate increase immediately adds $0.79 to the call's value. Rate changes affect LEAPS much more than short-dated options—a 22-day call with rho = 0.015 barely registers a rate move. In environments of interest rate uncertainty, LEAPS traders must model rho scenarios.

---

### Chapter 8: Dividends and Option Pricing (pp. 157–172)

Dividends affect option prices through put-call parity: call = put + stock − strike + interest − **dividends**. Higher dividends reduce call prices and raise put prices. The four key dates: declaration date, ex-dividend date, record date, payable date. The ex-date is what matters for option pricing—the stock price drops by approximately the dividend amount on this date.

**Early exercise of ITM calls before ex-dates**: If the time value of an ITM call is less than the upcoming dividend, it is economically rational to exercise early to receive the dividend. This reduces call prices just before ex-dates and creates early-assignment risk for short call holders.

**Dividend surprise risk**: The GE example shows that when a company changes its dividend significantly, traders using historical estimates price options incorrectly. The "wrong dividend" error on a $76 stock with a surprise dividend: call value drops from $1.65 to $1.35—a $0.30 miss. Always use declared (not estimated) dividend amounts when pricing options.

---

## Part II: Spreads (Ch. 9–11)

### Chapter 9: Vertical Spreads (pp. 173–193)

Vertical spreads = buy and sell options of the same type (call or put), same underlying, same expiration, different strikes. The defining feature: both maximum profit and maximum loss are defined.

**Bull call spread (AAPL 395–405)**:
- Buy 395 call @ $14.60; sell 405 call @ $10.20. Net debit: $4.40.
- Max profit: $5.60 (difference in strikes − debit). Max loss: $4.40. Break-even: $399.40.
- Greek comparison vs. outright 395 call: gamma reduced from 0.0097 to 0.0001 (−99%); vega reduced from 0.513 to 0.020 (−96%). Theta reduced from 0.208 to 0.014. Delta = 0.100 vs. 0.484.

The spread trades enormous gamma and vega reduction for a lower net debit. This makes timing less critical—a trader who is right on direction but off on timing is more likely to profit from the spread than from the outright call.

**Bear put spread**: Buy higher-strike put, sell lower-strike put. For modest bearish moves (stock drifting down to the short strike). The bull put spread (credit version) = sell higher-strike put, buy lower-strike put. Both bull call and bull put spreads have the same at-expiration payoff for the same strikes—they are economically equivalent.

**Box spread as two vertical spreads**: a bull (bear) call spread + a bear (bull) put spread at the same strikes is a fixed-value position worth exactly the spread width at expiration.

---

### Chapter 10: Wing Spreads — Condors and Butterflies (pp. 193–217)

Wing spreads profit from limited stock movement. All are combinations of two vertical spreads.

**Condor**: sell inner vertical, buy outer vertical (four different strikes). Short condor = net credit, profits if stock stays inside inner strikes.

**Iron condor**: short OTM put spread + short OTM call spread. Example: QQQ at $55.95 with 31 DTE: sell 55 put/buy 54 put + sell 57 call/buy 58 call. Net credit $0.63. Max risk $0.37. Strike selection using the 1σ rule: 1σ = 55.95 × 0.232 × √(35/252) ≈ $4.05. Short strikes at ±1σ places them at the boundary of the expected price range.

**Butterfly**: sell two options at the same middle strike, buy one each of a lower and higher strike. The profit peak is at expiration exactly at the middle strike.

**Iron butterfly**: short ATM straddle (short call + short put at same strike) + long OTM strangle for protection. Often more capital-efficient than a regular butterfly because OTM options may have tighter bid-ask spreads.

Wing spreads have two break-even prices. Managing the position when one leg is threatened requires judgment: close entirely, close only the threatened side, or roll to wider strikes.

---

### Chapter 11: Calendar and Diagonal Spreads (pp. 217–242)

Calendar spreads = buy far-month option + sell near-month option (same strike). The primary motivation is the theta differential: the near-month option decays faster. The P/L is tent-shaped at near-month expiration: maximum profit if stock is at the short strike; losses increase as the stock moves away.

Calendar spreads are also vega plays: a long calendar benefits from back-month IV rising relative to front-month IV. Passarelli's term-structure trade (p. 228–229): July IV at 45% vs. September at 38%. Buy the calendar to capture the 7-point IV differential. If July IV converges to 38%, profit ≈ $1,283.

**Rolling calendars**: systematically sell front-month calls against a LEAPS each month, reducing the LEAPS cost basis over time. After several rolls, the LEAPS can be effectively "free."

**Diagonal spreads**: buy far-month at one strike, sell near-month at a different strike. Combines the calendar's time-spread characteristics with a vertical spread's directional bias. Bullish diagonal: buy lower-strike back-month, sell higher-strike front-month.

**Double calendars**: long call calendar + long put calendar at different strikes, bracketing the stock price. Benefits from range-bound trading and/or rising IV.

---

## Part III: Volatility (Ch. 12–17)

### Chapter 12: Delta-Neutral Trading — Trading Implied Volatility (pp. 243–258)

Delta-neutral trading neutralises directional exposure by hedging delta with the underlying stock, leaving the position exposed primarily to changes in IV (vega) and realized vol (gamma/theta). This is how professionals "trade volatility."

**Volatility selling (Susie Seller)**: Sell delta-neutral options when IV is elevated before an earnings event. If IV crushes after the announcement, the vega gain profits. Example: sold 20 fifty-strike calls at 28% IV just before earnings. IV collapsed from 28% to 25% post-announcement. Decomposition: vega P/L (+$3,000) − theta cost ($75) − gamma/delta loss ($225) = net $800 profit.

**Volatility buying (Bobby Buyer)**: Buy delta-neutral options when IV is low. Profit from IV expansion and/or gamma scalping. Bobby bought options at 24% IV before the same event. IV rose, but the stock also moved, creating gamma scalp profits. Less theta risk than vol selling.

Portfolio margining is discussed as enabling more capital-efficient option strategies than strategy-based margining, as it assesses risk across the full position.

---

### Chapter 13: Delta-Neutral Trading — Trading Realized Volatility (pp. 259–274)

This chapter focuses on **gamma scalping**: the dynamic process of rebalancing the delta hedge as the underlying moves.

**Long gamma trader (Harry)**: Buys 20 ATM calls + short 1,000 shares at $40 (delta-neutral). When the stock falls $2: gamma causes delta to go negative; Harry buys shares to re-neutralize (buying the dip). When stock rallies $3: delta goes positive; Harry sells shares (selling the rally). Each hedge cycle locks in a realized profit. Net result: profitable if realized vol > implied vol priced into the options.

Over 7 days, Harry's stock scalp profits total $750, while theta costs $350, for a net gain of $400. When realized vol is high (lots of daily moves), gamma scalping is profitable.

**Short gamma trader (Mary)**: Sells 20 ATM calls + buys 1,000 shares (delta-neutral short gamma). When stock rises, must buy at rising prices (bad). When stock falls, must sell at falling prices (bad). Theta income compensates—profitable if stock moves *less* than implied vol predicted.

The breakeven daily move: the stock's actual realized daily σ must exceed the option's implied 1-day σ for long gamma to be profitable. Gamma scalping is not just a mechanical process—experienced traders adjust hedge frequency based on market feel and the 1σ price levels derived from IV.

---

### Chapter 14: Studying Volatility Charts (pp. 276–289)

Volatility charts plot IV and 30-day realized vol on the same graph over time. Passarelli presents **nine patterns** — all combinations of IV and realized vol rising, staying constant, or falling. Each pattern implies a different strategy:

| Pattern | IV | Realized | Implication |
|---------|-----|----------|-------------|
| 1 | Rises | Rises | Caution: if IV rises faster, options overpriced—sell |
| 2 | Constant | Rises | Realized exceeds IV: buy vol (gamma) |
| 3 | Falls | Rises | Post-earnings crush: options cheap, stock moving—buy gamma |
| 4 | Rises | Constant | Classic pre-earnings IV rush: buy straddles early |
| 5 | Constant | Constant | Quiet/neutral: income strategies (condors, calendars) |
| 6 | Falls | Constant | Vol premium compressing: short vol opportunity |
| 7 | Rises | Falls | The classic pre-earnings setup: buy straddle before event |
| 8 | Constant | Falls | Realized falling below IV: short-vol opportunity |
| 9 | Falls | Falls | Post-crisis normalization: return to short-vol strategies |

These nine patterns are the practitioner's framework for deciding *what kind* of trade to put on.

---

### Chapter 15: Straddles and Strangles (pp. 289–312)

**Long straddle** = buy ATM call + buy ATM put. Profits from large moves in either direction. Break-even = strike ± total premium. Example: 70-strike straddle at $4.25/side = $8.50 total; break-evens at $65.75 and $74.25. The straddle is the simplest pure vol trade: maximum vega per dollar spent (both sides positive vega), maximum theta cost (both sides negative theta).

Susan's straddle trade (p. 296–298): bought ATM straddle at 36% IV when realized vol was 36% and options were cheap. Over two weeks, she scalped $5,200 from gamma scalping while the stock oscillated. This more than covered the theta decay.

**Short straddle** = sell ATM call + put. Passarelli: "one of the riskiest positions one can trade." Maximum profit = premium if stock is exactly at strike at expiration. Unlimited losses in both directions. John's short straddle example (p. 301–303): stock moved $2.75 against him; gamma/delta hurt, theta helped slightly. Key lesson: define max loss threshold before entry.

**Long strangle** = buy OTM call + OTM put. Lower cost but wider break-evens. Less vega per dollar spent. Better when you expect a large move but want to reduce premium at risk.

**Short strangle** = sell OTM call + OTM put. More wiggle room than a short straddle. Still unlimited risk. Best in high-IV environments. Mark (p. 309–310): sells 100–110 strangle when the 105 straddle is at $5.40. The extra room between strikes makes management easier.

---

### Chapter 16: Ratio Spreads and Complex Spreads (pp. 312–329)

**Ratio spreads**: buy fewer options, sell more at a different strike. The extra short option creates a net credit but introduces potentially unlimited risk beyond the short strikes. Requires accurate predictions of both direction AND a limited range—"generally best avoided" unless there is a specific edge in both.

**Backspreads**: sell fewer, buy more (the opposite). A call backspread (sell 1, buy 2 at higher strike) has positive gamma and positive vega initially. Benefits from large moves AND rising IV. But: if the stock falls far below the short strike, vega and gamma flip negative—the position transforms from "long vol" to "short vol."

**Market maker complex position management**: Passarelli describes how market makers accumulate positions across many strikes/expirations and manage the combined net greek profile. Key skills: lower bids when long gamma/vega (don't want more exposure); raise bids when short gamma/vega (need to hedge). The net position is treated as a unified portfolio.

**Skew trading** (p. 325–326): equity vol skew makes OTM puts trade 4+ vol points above equidistant OTM calls. A risk reversal (sell OTM put, buy OTM call) profits if skew normalizes. **Delta lean** = intentional slight directional bias in an otherwise neutral position when the trader has a mild directional view.

---

### Chapter 17: Putting the Greeks Into Action (pp. 329–344)

The synthesis chapter. Passarelli presents two case studies:

- **Arlo (vol buying)**: Agilent Tech stock is in an uptrend with rising intraday moves but flat close-to-close HV. IV is at mid-range. Conclusion: buy delta-neutral options with slight bullish bias to exploit the divergence between intraday and close-to-close realized vol.
- **Luke (directional spread)**: Different stock, mild bullish view, not willing to pay for full vol exposure. Conclusion: bull call spread—reduce vega and theta, keep most of the delta.

**Key rules** summarised in the final chapter:
1. Always plan for worst-case outcomes before entering a trade. "You can plan for it. And as an option trader, you have to."
2. **Would I Do It Now? Rule**: at any time during a trade, ask "would I enter this position fresh at current prices?" If no, close it. This eliminates sunk-cost bias.
3. Greeks help at every stage: finding trades, sizing, managing, exiting. Without greek fluency, option trading is guesswork.

---

*Source: pp. 18–344, Trading Option Greeks 2e*
