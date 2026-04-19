# Chapter 4: Position Risk Profiles
*pp. 53–60 | Option Market Making, Allen Jan Baird*

---

## Summary

This chapter categorizes all single-month option strategies into 22 core position types and introduces the concept of *risk sign modality* — the number of times a position's Greek risk (gamma, theta, kappa) changes sign across the full price range. This framework lets a market maker quickly classify any position and predict how its risk will evolve as the underlying moves.

The key insight: no matter how large or complex a market maker's carryover position becomes, it will always resemble one of these 22 archetypes in terms of risk character.

---

## The 22 Core Position Types

| # | Position | Risk Modality |
|---|----------|---------------|
| 1 | Long call | Unimodal (+) |
| 2 | Short call | Unimodal (−) |
| 3 | Long put | Unimodal (+) |
| 4 | Short put | Unimodal (−) |
| 5 | Long straddle/strangle | Unimodal (+) |
| 6 | Short straddle/strangle | Unimodal (−) |
| 7 | Bull spread | Bimodal |
| 8 | Bear spread | Bimodal |
| 9 | Long fence | Bimodal |
| 10 | Short fence | Bimodal |
| 11 | Ratio spread long calls (tail = backspread) | Bimodal |
| 12 | Ratio spread long puts (tail) | Bimodal |
| 13 | Ratio spread short calls | Bimodal |
| 14 | Ratio spread short puts | Bimodal |
| 15 | Long cartwheel | Bimodal |
| 16 | Short cartwheel | Bimodal |
| 17 | Long wrangle | Trimodal |
| 18 | Short wrangle | Trimodal |
| 19 | Long butterfly/condor | Trimodal |
| 20 | Short butterfly/condor | Trimodal |
| 21 | Conversion/reversal/box | Near-zero risk |
| 22 | Time spread | Time-based risk |

---

## Risk Sign Modality

**Figure 4.2** illustrates the three types:

- **Unimodal (a):** Single peak, one sign across all prices. Examples: long/short call, straddle. Simple, predictable.
- **Bimodal (b):** Changes sign once across the price range. Examples: vertical spreads, fences. The sign change occurs near the short strike.
- **Trimodal (c):** Changes sign twice. Examples: butterflies, condors, wrangles. Two sign changes, near both short strikes.

For spreads, **gamma peaks are always nearest the short strikes.** Understanding this tells you exactly where the position's sensitivity concentrates.

---

## Key Definitions

**Straddle:** Long (or short) same-strike call + put. Unimodal: always positive gamma (long), always negative theta. Benefits from any large move; suffers from time decay.

**Strangle:** Long (or short) different-strike call + put. Similar to straddle but the positive gamma range is narrower near expiration.

**Vertical spread:** Long and short options at different strikes, same type, same expiration. Bimodal gamma — positive below the short strike, negative above.

**Butterfly:** Long one lower-strike, short two center-strikes, long one upper-strike. Trimodal. Maximum profit at expiration when price = center strike. Benefits from low realized volatility.

**Condor:** Long two outer strikes, short two inner strikes. Wider profitable zone than butterfly. Trimodal.

**Ratio spread:** Long one, short more at a different strike. Can have unlimited risk if the short options are not fully hedged. Used when IV is high.

**Conversion/Reversal:** Near-zero market risk. Pure arbitrage exploiting put-call parity. Conversion = long underlying + long put + short call. Reversal = short underlying + short put + long call.

---

## Quirkiness

**Figure 4.1** shows an irregular carryover position payoff — a jagged, multi-peaked line that bears no resemblance to any standard position type. This is the practical reality for active market makers: accumulated trades across many strikes create an irregular payoff that can spike dramatically near expiration at specific strikes.

Key lesson: **Positions acquire quirkiness near expiration** — they take on the risk character of the nearest standard position type as expiration approaches and standard deviations shrink.

---

## Key Lessons

1. **Memorize the 22 archetypes.** Any position encountered in practice is a variant of one of these. Knowing the archetype immediately tells you the risk character.

2. **Risk sign modality determines how risk evolves with price.** A bimodal position has positive gamma on one side and negative on the other. Knowing which side you're on tells you whether a price move helps or hurts.

3. **Butterflies and condors are short gamma, long theta near center.** They earn time decay when the market is quiet and lose when markets are volatile. They are essentially volatility-selling instruments.

4. **Conversions/reversals define fair value bounds.** If options deviate from put-call parity by more than transaction costs, arbitrage capital immediately corrects them.

---

## Warnings

- Complex carryover positions can have hidden risk concentrations at specific strikes that are not visible from simple Greek totals. Always compute the full expiration P&L profile across all strikes.
- Ratio spreads carry unlimited risk on the short side. Always know the maximum loss before entering any ratio position.

---

## Connection to the Rest of the Book

The appendix to this chapter contains detailed Greek profiles (delta, gamma, theta, kappa at 30 days and at expiration) for all 22 positions — the single most useful reference in the book. Chapter 8 revisits position sizing and tactical adjustments based on current market conditions.
