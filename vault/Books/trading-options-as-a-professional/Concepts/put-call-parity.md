# Put-Call Parity
*Source: Trading Options as a Professional — Ch. 5, 6*

---

## Definition

The fundamental relationship linking calls, puts, and stock with the same strike and expiry:

> **+Call − Put = +Stock** (simplified, zero interest/dividends)

More precisely:
> **Call = Put + Stock − Strike + (interest on strike × time) − dividends**

This equation states that a call is always equivalent to a put plus the underlying minus the present value of the strike. Any mispricing between the two sides creates riskless arbitrage.

---

## All Six Synthetic Positions

Rearranging put-call parity yields every possible synthetic:

| Want | Build with |
|------|-----------|
| Long stock | Long call + Short put |
| Short stock | Short call + Long put |
| Long call | Long stock + Long put |
| Long put | Short stock + Long call |
| Short call | Short stock + Short put |
| Short put | Long stock + Short call (**covered call**) |

---

## Why It Matters

1. **Covered call = short put** — same P/L, same risk. Traders who sell covered calls "for safety" are running the same downside exposure as naked short put sellers.
2. **Pricing check**: if you're offered a call at a price that doesn't line up with the put and stock, one of them is mispriced. Market makers will immediately arbitrage it.
3. **Strategy selection**: knowing the synthetic tells you whether the real or synthetic form of a position is cheaper after transaction costs.
4. **Arbitrage enforcement**: conversions and reverse conversions only work because parity is enforced by market participants. The parity relationship is maintained in real time.

---

## Common Misunderstandings

- **"Put-call parity only applies to European options."** Approximately true for American options too, with an early-exercise premium adjustment.
- **"The covered call is a conservative strategy."** Only directionally — it has the same downside exposure as a short put. It eliminates upside beyond the short strike.
- **"Synthetics are identical to real positions."** In theory, yes. In practice, transaction costs, margin requirements, and dividend/interest effects create small differences.

---

## Interest and Dividend Effects

With non-zero interest rates: call time value > put time value by the interest on the strike (carry cost).
- Stock 100, strike 100, 5% rate, 30 days: call 3.08, put 2.70. Difference ≈ $0.38 = interest on $100 for 30 days at 5% ($0.41).

With dividends: dividend amount reduces call value and increases put value by approximately the dividend PV.

---

## Page References
- Definition and synthetic table: pp. 136–142 (Ch. 5)
- Time value equality: pp. 152–157 (Ch. 5)
- Arbitrage application (conversions, reversals, boxes): pp. 165–225 (Ch. 6)
