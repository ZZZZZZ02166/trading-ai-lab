# Chapter 5: An Introduction to Volatility-Selling Strategies
*Trading Option Greeks 2e — pp. 109–127*

---

## Chapter Summary

While Chapter 4 dealt with long options (time working against you), Chapter 5 flips to short options where time works in your favor. The defining feature of every strategy here is **positive theta** — you collect daily time decay — in exchange for **negative gamma** — you accept loss if the stock moves too far. Passarelli walks through three traders with three levels of directional bias, using the same underlying (Johnson & Johnson and Harley-Davidson) across multiple examples.

---

## The Gamma-Theta Relationship

This is the chapter's central idea and applies to every short-vol strategy:

- **Short options = positive theta + negative gamma**
- Positive theta: you collect daily decay as time passes
- Negative gamma: stock movement hurts you — and the hurt accelerates as the position gains delta exposure

These two forces are not separable. You cannot harvest theta without accepting gamma. The more theta you collect (ATM options, options near expiration), the more gamma risk you are accepting simultaneously.

---

## Example 1: Naked Short Call (Brendan)

Setup: JNJ is in a $60–$65 channel. Brendan sells the 65-strike call at $0.66 premium.

Position greeks (per contract):
- Delta: −0.34 (slightly bearish/neutral)
- Gamma: −0.15 (negative)
- Theta: +0.003 ($0.30/day per contract)

Maximum profit: $660 if stock stays below $65. Unlimited loss above $65.66 (break-even).

**The stop-loss gamma acceleration effect**: Brendan's stop-loss is at 1.10 (if the call value rises to 1.10, he covers). With delta = 0.34 and gamma = 0.15, if JNJ rises $1: new delta = 0.34 + 0.15 = 0.49. The stop-loss at 1.10 is reached when JNJ rises just **$1.01** — not the $1.32 a pure delta calculation would suggest. Gamma makes losses arrive faster than expected.

**Over time**: if the stock stays in range and time passes, theta rises (more daily reward). But as theta rises near expiration, so does gamma (more risk). The short-vol trader's dilemma intensifies as expiration approaches.

---

## Example 2: Short Put (Stacie)

Setup: JNJ at $62. Stacie sells the 62.50-strike put (slightly ITM) at $1.28 premium. She is bullish.

Why short put instead of naked call? Higher delta (bullish bias) and higher premium. But:
- **Higher delta = larger directional move required for break-even**
- **IV risk is more symmetric**: a JNJ decline will likely come with rising IV, which amplifies losses via vega

**Whipsaw risk**: In volatile environments, Stacie's stop-loss can be triggered by random oscillation. The stock might drop to her stop, she exits for a loss, then the market reverses and she would have been profitable. Higher IV → more whipsaw potential → need for wider stops → larger potential loss.

---

## Example 3: Term Structure and Month Selection (Bill)

Setup: Harley-Davidson short put. Term structure: March 19.2% IV, April 23.3% IV, May 23%.

March is cheapest by IV — less premium collected per day of decay. April/May have elevated IV, suggesting the market anticipates something (news, earnings, uncertainty). Bill must decide: sell March for less premium but in a "quiet" environment, or sell a higher-IV month for more premium but in a period of more anticipated movement?

This is the practical application of Chapter 3's term structure analysis to actual trade selection.

---

## Additional Example: Covered Put vs. Short Put (Libby)

Libby is short 1,000 shares of Harley-Davidson and considers turning her short into a covered put (short stock + short put). This illustrates that covered puts and naked puts have similar P/L shapes — the same "curious similarity" as covered calls and naked calls.

---

## Practical Rules from This Chapter

1. **Sell options when the stock is near a resistance level** (for calls) or support level (for puts). The channel analysis provides a technical rationale.
2. **Gamma amplifies losses faster than delta predicts.** Always calculate stop-loss distances using gamma too, not just delta.
3. **As expiration approaches, both theta and gamma increase.** Reward and risk grow simultaneously. Plan for this.
4. **Higher IV = higher potential whipsaw.** Adjust stop-loss levels wider in high-IV environments, but accept that the larger stop means a larger potential loss.
5. **Stop orders must be pre-defined.** "If material news is announced, sometimes traders need to think on their feet" — but the default plan is a predetermined stop, not improvisation.

---

## Warnings

- Naked calls have unlimited risk. Never forget this when the trade goes against you.
- Rising IV while a position moves against you compounds losses. The vega (negative for short options) hurts you at the same time as delta and gamma.
- The covered call and naked call have the same at-expiration P/L shape. The difference is capital requirement and unlimited-risk treatment, not economic exposure.

---

## Connection to the Rest of the Book

- Ch. 10 (wing spreads) and Ch. 15 (straddles) build on vol-selling with defined risk
- Ch. 12–13 develops the delta-neutral approach to vol selling (pure IV/gamma trading)
- Ch. 14 (vol charts) provides the analytical tool for deciding *when* to sell vol
- Ch. 9 (vertical spreads) shows how to define and cap the losses from a short option
