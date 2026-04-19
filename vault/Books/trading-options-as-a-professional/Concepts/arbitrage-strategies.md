# Arbitrage Strategies
*Source: Trading Options as a Professional — Ch. 6, 9*

---

## Definition

Arbitrage in options is the simultaneous trading of a position and its synthetic equivalent when they are mispriced relative to put-call parity. True arbitrage: no directional view, all Greeks ≈ zero, riskless profit locked in regardless of stock price.

---

## Three Mechanisms

### Conversion

**Structure**: Long stock + Long put + Short call (same strike, same expiry)  
**When**: call is overpriced relative to put-call parity  
**Target call price formula**: `Strike + (rate × days/365) + Put − Stock`  
**P/L**: locked-in credit if market call exceeds formula price

### Reverse Conversion

**Structure**: Short stock + Short put + Long call (same strike, same expiry)  
**When**: call is underpriced (put overpriced) relative to parity  
**Target call price formula**: `Stock − Put + (rate × days/365)`  
**Special factor**: short stock rebate (market makers receive 80% of interest on short proceeds) — significantly improves profitability vs. retail traders

### Box Spread

**Structure**: Bull call spread + Bear put spread (same strikes, same expiry)  
**Value at expiration**: always = spread width (e.g., 90–100 box = $10 exactly)  
**Fair value**: `(High − Low) × [1 − (rate × days/365)]`  
**When**: box trades below fair value → buy it (locked-in profit)  
**When**: box trades above fair value → sell it (locked-in profit, equivalent to borrowing)  
**No directional, gamma, or vega exposure**

---

## Pin Risk

When stock closes at or near a strike at expiration, conversion/reversal traders don't know if assignment will occur. Unexpected assignment creates large overnight stock exposure. This is a recurring, real risk at every expiration for traders holding these positions.

---

## Who Can Profitably Execute These

Market makers can execute because they:
1. Have low transaction costs (near-zero commissions)
2. Receive short stock rebates (reverse conversions)
3. Can execute quickly when mispricings appear
4. Can execute in two trades to capture edge on each leg separately

Retail traders generally cannot replicate market maker arbitrage profitability.

---

## Two-Trade Arbitrage

Execute each leg of a conversion or box spread in a separate trade, capturing bid-ask edge on each leg individually. Total profit = sum of edges minus transaction costs. Requires speed and precise execution.

---

## Why It Matters for Non-Market-Makers

Understanding arbitrage mechanics helps traders:
1. Recognize when an option is obviously mispriced relative to its synthetic equivalent
2. Understand why put-call parity holds in practice (active enforcement)
3. Avoid being on the wrong side of conversions/reversals executed by market makers

---

## Page References
- Conversion: pp. 165–196 (Ch. 6)
- Reverse conversion and pin risk: pp. 196–212 (Ch. 6)
- Box spreads: pp. 210–225 (Ch. 6)
- Pricing formulas in practice: pp. 300–330 (Ch. 9)
