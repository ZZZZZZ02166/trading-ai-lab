# Chapter 5 — Synthetic Relationships
*Source: Trading Options as a Professional — Ch. 5*

---

## Summary

Chapter 5 establishes that every option position is algebraically equivalent to a two-component combination of the other two instruments (stock, calls, puts). This equivalence — rooted in put-call parity — is the structural foundation of option pricing and arbitrage. Understanding synthetics allows traders to: (1) identify the cheapest form of any position, (2) check whether an option is fairly priced, (3) understand why the covered call has the same risk profile as a short put.

---

## Key Concepts

### Put-Call Parity

**Fundamental equation:** +Call − Put = +Stock (same strike, same expiry, assuming zero interest and dividends)

Rearranged into all six synthetic positions:

| Real Position | Synthetic Equivalent | Notes |
|--------------|---------------------|-------|
| Long stock | Long call + Short put | Same strike, same expiry |
| Short stock | Short call + Long put | Same strike, same expiry |
| Long call | Long stock + Long put | The protective put |
| Long put | Short stock + Long call | |
| Short call | Short stock + Short put | |
| **Short put** | **Long stock + Short call** | = **Covered call** |

The last row is the most practically important for most traders: the covered call strategy (long stock, sell call) is **identical** to a naked short put. Same P/L profile. Same risk. Same dollars.

### Tables 5-1 through 5-8

Each table in Chapter 5 verifies the synthetic equivalence numerically at specific stock prices. For example, Table 5-1 (Synthetic Long Stock):
- Long 100 Call at 3.00, Short 100 Put at 3.00
- At stock = 90: call loses 3, put loses 7, combined: −10 = long stock loss
- At stock = 100: combined P/L = 0 = long stock P/L
- At stock = 110: combined = +10 = long stock gain

### Time Value Equality

With zero interest rates and no dividends: **time value of call = time value of put** (same strike). With non-zero rates: call time value = put time value + (interest on strike × time fraction). Example from Op-Eval Pro: stock 100, strike 100, 5% rate, 30 days: call 3.08, put 2.70. Difference of $0.38 ≈ interest on $100 for 30 days at 5% ($0.41).

### Effective Stock Price

The "effective stock price" of a synthetic position accounts for the net premium paid/received. If you create a synthetic long stock (long call at 3, short put at 3, net zero), the effective stock price is the strike. If net premium is non-zero, effective price adjusts accordingly.

---

## Key Lessons

1. **The covered call = short put**. If you sell covered calls "for income," you are exactly as exposed to downside as a naked short put seller. The stock you own provides no additional protection — the call you sold removes the upside.
2. Synthetic positions can be more or less expensive than real positions depending on bid-ask spreads, margin, and capital efficiency. Professional traders always ask: "is it cheaper to trade the real or the synthetic?"
3. Put-call parity is not theoretical — it holds because market makers actively arbitrage away violations (Chapter 6 explains this in detail).

---

## Example: Op-Eval Pro Verification

Figure 5-10 (stock 100, strike 100, vol 25%, rate 5%, 30 days):
- Call value: 3.08 / Put value: 2.70
- Time value of call: 3.08 (all time value, no intrinsic)
- Time value of put: 2.70 (all time value)
- Difference: 0.38 ≈ interest on $100 strike for 30 days at 5%

Figure 5-11 (stock 88, strike 85, vol 30%, rate 4%, 90 days):
- Call value: 7.27 (3.00 intrinsic + 4.27 time value)
- Put value: 3.48 (all time value)
- Time value of call − time value of put: 4.27 − 3.48 = 0.79 ≈ interest on $85 at 4% × 90/365 = $0.84

---

## Warnings

⚠️ Transaction costs matter when choosing between a real position and its synthetic. The cheapest form varies by market conditions and by trader type (retail vs. professional with rebates).

⚠️ When interest rates are non-zero or dividends are paid, synthetics and real positions are not perfectly equivalent. The difference is small for short-dated options but matters significantly for LEAPS and dividend-paying stocks.

---

## Connections to Rest of Book

- Chapter 6 uses synthetic relationships to construct conversions, reverse conversions, and box spreads
- The covered call = short put equivalence is a recurring theme in position risk management (Chapter 10)
- Chapter 9 uses synthetic pricing to determine bid-ask pricing formulas for arbitrage strategies

---

## Page References
- Put-call parity and all six synthetics: pp. 136–155 (Ch. 5)
- Time value equality: pp. 152–156 (Ch. 5)
- Op-Eval Pro examples: pp. 157–162 (Ch. 5)
