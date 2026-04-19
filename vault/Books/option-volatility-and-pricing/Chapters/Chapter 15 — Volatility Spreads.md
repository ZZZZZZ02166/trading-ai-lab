# Chapter 15 — Volatility Spreads
*Option Volatility and Pricing — Natenberg*

---

## Summary

The four primary volatility spreads — straddle, strangle, butterfly, condor — are the building blocks of all vol trading strategies. This chapter explains their structure, P/L profiles, Greek characteristics, and when each is appropriate. It also covers ratio spreads and Christmas trees.

---

## The Four Core Volatility Spreads

### Straddle
**Structure**: Long ATM call + Long ATM put (same strike, same expiry)

| Greek | Sign | Interpretation |
|-------|------|---------------|
| Delta | ~0 | Directionally neutral |
| Gamma | + | Profits from large moves in either direction |
| Theta | − | Pays daily time decay |
| Vega | + | Profits from rising IV |

**Profits when**: realized vol > IV (gamma scalps > theta), or IV rises before expiry.
**Loses when**: underlying stays quiet AND IV falls.
**Breakeven at expiry**: strike ± (call premium + put premium).

**Short straddle** (sell both): inverse profile — collects premium, profits from quiet market and falling IV. Maximum risk: theoretically unlimited (if underlying makes a large move).

### Strangle
**Structure**: Long OTM call + Long OTM put (different strikes, same expiry)

Same Greek signs as straddle (+gamma, −theta, +vega) but:
- **Lower cost** (both options OTM)
- **Wider breakeven range** at expiration
- **Lower gamma and vega** per dollar invested
- Higher leverage per dollar spent

**Guts strangle**: uses ITM options instead of OTM — equivalent P/L but requires more capital and is less liquid.

### Butterfly
**Structure**: Long 1 lower call / Short 2 middle calls / Long 1 upper call

**At expiration**:
- Maximum value (spread width) if underlying = middle strike
- Zero value if underlying is outside the wings
- Value is between 0 and spread width for underlying between strikes

**Greek profile when executed delta-neutral**:
- Short gamma, short vega: profits from quiet market and falling IV
- The opposite of a straddle

**Key insight**: 300 butterflies can be less risky than 100 short straddles because butterfly risk is capped (you can only lose the premium paid), while straddle risk is not.

**Call butterfly = put butterfly** (by put-call parity). Always verify using the cheapest-to-construct combination.

### Condor
**Structure**: Long 1 lowest call / Short 1 lower-middle call / Short 1 upper-middle call / Long 1 highest call (4 legs)

Similar to butterfly but with a wider profit range. Maximum profit when underlying finishes between the two short strikes at expiry. Lower maximum profit than butterfly for same risk.

**Call condor = put condor** — same P/L profile.

---

## Comparison of the Four Spreads

| Spread | Underlying View | Vol View | Risk Profile |
|--------|----------------|---------|-------------|
| Long straddle | Any large move | Long vol (buy low IV) | Unlimited profit, limited loss |
| Short straddle | Quiet | Short vol (sell high IV) | Limited profit, large loss potential |
| Long butterfly | Near middle strike | Short vol | Limited profit AND limited loss |
| Long condor | Between inner strikes | Short vol | Limited profit AND limited loss |

---

## Ratio Spreads

**Call ratio spread**: Long N lower-strike calls / Short 2N (or more) upper-strike calls

**Typical execution**: For a credit (premium received > premium paid).

**P/L profile**:
- Profitable when underlying is between long strike and somewhere above short strikes
- Maximum profit when underlying = short strike at expiration
- Large loss if underlying rallies far above short strikes (uncapped on upside)

**Put ratio spread**: same but with puts, exposed to large losses on large downside moves.

**Why trade ratio spreads?**
- Collect upfront credit
- Profit from small to moderate directional moves
- Good when IV is elevated (sell more premium than you buy)

**Risk**: Large moves beyond the short strike create uncapped losses. Must monitor carefully and have a defined exit plan.

---

## Christmas Tree (Ladder)

**Long call Christmas tree**: +1 lower strike call / −1 middle strike call / −1 upper strike call (3 legs with asymmetric sizing)

- Executed for credit or small debit
- Profitable if underlying stays below or near the body strike
- Expiration P/L is asymmetric — looks like a ratio spread with additional protection from the long lower strike

**Volatility characteristics**: similar to a strangle or ratio spread — profits from calm, declining IV conditions. P/L graphs look similar to strangles even though structure is call-only.

---

## Choosing Among Volatility Spreads

| When | Use |
|------|-----|
| High IV, want short vol with defined risk | Butterfly or condor |
| High IV, willing to accept tail risk for credit | Short straddle or strangle |
| Low IV, want long vol with defined risk | Long butterfly |
| Low IV, willing to pay premium for large-move exposure | Long straddle or strangle |
| Moderately bearish with high IV | Ratio put spread (credit) |
| Moderately bullish with high IV | Ratio call spread (credit) |

---

## Common Misunderstandings

- **"A butterfly is always safer than a straddle."** Size matters — a 300-lot butterfly at $1 risk each = $300 total risk. A 1-lot straddle may have less dollar risk. Compare total dollars at risk, not number of legs.
- **"Strangles are cheaper than straddles."** Yes in premium terms, but strangles require larger moves to profit. Neither is universally "better."
- **"Ratio spreads are free money."** No — the credit comes at the cost of uncapped risk beyond the short strike. Always define your maximum acceptable loss before entry.
