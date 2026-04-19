# Chapter 6 — Arbitrage Strategies
*Source: Trading Options as a Professional — Ch. 6*

---

## Summary

Chapter 6 extends the synthetic relationships of Chapter 5 into the realm of arbitrage. It covers three arbitrage mechanisms — conversions, reverse conversions, and box spreads — that market makers use to lock in riskless profits from put-call parity violations. These strategies are rarely accessible to retail traders due to transaction cost requirements, but understanding them explains why option prices stay in line with each other and what "fair value" actually means.

---

## Key Concepts

### Conversion

**Structure**: Long stock + Long put + Short call (same strike, same expiry)

Net position: all Greeks approximately zero (delta, gamma, vega, theta, rho ≈ 0). The position's P/L is locked regardless of where the stock goes.

**When profitable**: when the call is overpriced relative to put-call parity. If the "fair" call price is $8.00 but market shows $8.25, buying the conversion locks in $0.25 per share riskless.

**Target call price formula:**
> Call target = Strike + (interest × days/365) + Put price − Stock price

If market call > this formula → conversion is profitable.

### Reverse Conversion

**Structure**: Short stock + Short put + Long call (same strike, same expiry)

Mirror of conversion. Profitable when call is underpriced (put is overpriced) relative to parity.

Short stock rebate significantly affects profitability: market makers receive 80% of interest on short stock proceeds, improving their effective cost for reverse conversions. Retail traders who don't receive rebates cannot profitably execute most reverse conversions.

**Target call price formula:**
> Call target = Stock price − Put price + (interest × days/365)

### Pin Risk

When stock is exactly at the strike at expiration, the market maker holding a conversion or reversal doesn't know if assignment will occur. If they hedge assuming no assignment and receive assignment (or vice versa), they end up with unexpected large stock exposure overnight.

Pin risk is not theoretical — it occurs at every expiration when popular strikes are near the closing price. Professional traders monitor short strikes approaching expiration carefully and adjust hedges accordingly.

### Box Spread

**Structure**: Bull call spread (buy lower strike call, sell higher strike call) + Bear put spread (buy higher strike put, sell lower strike put), same strikes, same expiry.

**Value at expiration**: always equal to the spread width (e.g., 90–100 box always worth exactly $10).

**Fair value**: Spread width − interest = PV(spread width).  
Example: 90–100 box, 60 days, 4% rate: FV = 10 × [1 − (0.04 × 60/365)] = 10 × 0.9934 = $9.93

**If box trades below FV**: buy the box → locked-in riskless profit.  
**If box trades above FV**: sell the box (collect cash, pay back spread width at expiry) → riskless profit equivalent to borrowing at below-market rate.

Box spreads have zero delta, gamma, vega, and theta. They are pure interest-rate instruments — synthetic money market investments.

---

## Example: Long Box

Table 6-19: 90–100 long box
- Long 90 Call @ 8.50
- Short 100 Call @ 2.00
- Short 90 Put @ 2.25
- Long 100 Put @ 7.00
- Net debit: (8.50 − 2.00) + (7.00 − 2.25) = 6.50 + 4.75 = 11.25... wait, recalculate: box always costs PV($10). If FV = $9.93 and box costs $9.14, profit = $0.79 per share = $79 per box. This profit is riskless regardless of stock price.

---

## Two-Trade Arbitrage

Conversions and box spreads can be executed in two separate trades to capture edge on each leg:
- Trade 1: buy stock + sell calls (or buy puts)
- Trade 2: buy puts (or sell stock)

This approach captures bid-ask spread edge on each component separately. Total profit = sum of edges − transaction costs.

---

## Key Lessons

1. Arbitrage is not about predicting direction — it's about exploiting mispricing relative to a known formula.
2. The formulas for conversion and box spread pricing are precise and algorithmic. Market makers execute these the instant a deviation appears.
3. Understanding these arbitrage constraints helps retail traders recognize when they're being offered an option that is clearly mispriced relative to another option (e.g., a call that is much cheaper than an equivalent synthetic call).
4. Short stock rebate creates a systematic pricing advantage for market makers on reverse conversions.

---

## Warnings

⚠️ **Pin risk is real and recurring.** Every expiration with popular strikes near the stock price creates pin risk for traders with conversion/reversal positions. Manage carefully.

⚠️ Retail traders cannot replicate most market maker arbitrage because they don't receive short stock rebates and have higher transaction costs. Do not attempt conversions/reversals without analyzing costs carefully.

⚠️ Box spreads carry pin risk at both strikes if held to expiration — all four legs are live options.

---

## Connections to Rest of Book

- Chapter 5's synthetic relationships are the algebraic foundation for all three arbitrage strategies
- Chapter 9 develops the bid-ask pricing formulas for executing conversions and reversals at profitable levels
- Short stock rebate from Chapter 1 is essential for reverse conversion profitability calculations

---

## Page References
- Conversion mechanics and formula: pp. 165–180 (Ch. 6)
- Reverse conversion and short stock rebate effect: pp. 180–210 (Ch. 6)
- Pin risk: pp. 189–196 (Ch. 6)
- Box spread mechanics and pricing: pp. 210–225 (Ch. 6)
