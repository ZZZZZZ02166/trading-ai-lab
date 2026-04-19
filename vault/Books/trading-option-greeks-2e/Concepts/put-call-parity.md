# Put-Call Parity and Synthetics
*Source: Trading Option Greeks 2e — Ch. 2, 6, 9*

---

## The Equation

> **c + PV(strike) = p + S**

Where:
- c = call value
- PV(strike) = present value of the strike price (= strike − interest)
- p = put value  
- S = stock price

In pricing-model form (useful for practice):
> **call = put + stock − strike + interest − dividends**

This equation mathematically locks every call and put of the same strike and expiration together. If any component is mispriced, arbitrage is possible.

---

## Why This Matters

Put-call parity is not just a theoretical relationship — it is the foundation of:
1. All synthetic positions
2. Conversion/reversal arbitrage
3. Box spread pricing
4. Understanding how dividends and interest rates affect relative call/put prices
5. Identifying when one leg of a position is over/underpriced relative to its synthetic equivalent

Passarelli on the trading floor: "That's 500. A put is a call; a call is a put." This was his introduction to the most important structural truth in options.

---

## Synthetic Positions

Rearranging the parity equation creates all synthetic positions:

| Position | Equivalent | Notes |
|----------|-----------|-------|
| Long call | Long put + long stock | Same payoff at expiration |
| Long put | Long call + short stock | |
| Long stock | Long call + short put | "Synthetic long stock" |
| Short stock | Short call + long put | |
| Short call | Short put + short stock | |
| Short put | Short call + long stock | |

These equivalences allow professional traders to create positions in whichever form is most liquid or capital-efficient at the time.

---

## Conversions and Reversals

**Conversion** = long stock + long put + short call (same strike, same expiry).
Net delta ≈ 0. P/L = put-call parity discrepancy.

**Reversal** = short stock + short put + long call (same strike, same expiry).
Mirror image of conversion.

Market makers use these to lock in mispricings. The P/L is the difference between the actual market prices and what parity says they should be. Both positions are near-riskless — all greeks approximately zero.

---

## Box Spreads

**Box** = bull call spread + bear put spread (same strikes, same expiration).

A 60–70 box is always worth exactly $10 at expiration. Present value = $10 − interest (e.g., $9.85 for 90-day box at 6% rates). If the box trades at $9.70, buying it locks in a riskless profit of $0.15 — equivalent to a risk-free interest rate return.

Box spreads are pure arbitrage instruments: fixed future value, no directional or vol exposure.

---

## Interest and Dividend Effects via Parity

From the parity equation:
- **Higher interest rates**: PV(strike) falls → call price rises, put price falls
- **Higher dividends**: dividend term increases → call price falls, put price rises

These effects are the mechanical basis of rho (Chapter 7) and the dividend pricing chapter (Chapter 8). They are not independent — they all flow from the same put-call parity equation.

---

## Pin Risk (Conversion/Reversal Risk)

For market makers holding conversion or reversal positions near expiration, **pin risk** arises when the stock is exactly at the strike. The market maker doesn't know if the option will be assigned. If they hedge assuming no assignment and then get assigned (or vice versa), they end up with an unexpected large stock position overnight.

This is not theoretical — it is a real, recurring problem at each options expiration.

---

## Common Misunderstandings

- **"Put-call parity only applies to European options."** In practice, it applies approximately to American options too, with adjustments for early exercise value.
- **"Synthetics are the same in all situations."** Cost of carry (interest) and dividends create small differences between a position and its synthetic — these matter for LEAPS and for positions held through ex-dividend dates.

---

## Page References

- Parity equation: pp. 62–63 (Ch. 2)
- Synthetic positions: pp. 131–138 (Ch. 6)
- Conversions, reversals, pin risk: pp. 139–144 (Ch. 6)
- Box spreads: pp. 144–147 (Ch. 6), pp. 193 (Ch. 9)
- Interest and parity: pp. 148–152 (Ch. 7)
