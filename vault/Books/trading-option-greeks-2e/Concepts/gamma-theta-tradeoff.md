# Gamma-Theta Tradeoff
*Source: Trading Option Greeks 2e — Ch. 2, 5, 12, 13*

---

## Definition

The gamma-theta tradeoff is the fundamental tension in every option position:

- **Long options** (positive gamma, negative theta): You benefit from large stock moves (gamma works for you) but pay a daily cost in time decay (theta works against you).
- **Short options** (negative gamma, positive theta): You collect daily time decay income (theta works for you) but suffer losses from large stock moves (gamma works against you).

These forces cannot be separated. You cannot get positive theta without accepting negative gamma, and vice versa. They are different faces of the same coin.

---

## Why This Matters

This is not a theoretical concept — it defines every option strategy's core risk:

| Strategy | Gamma | Theta | Core Risk |
|----------|-------|-------|-----------|
| Long call/put | + | − | Time decay (must be right on direction AND timing) |
| Short call/put | − | + | Large moves (stock moves sharply against you) |
| Long straddle | ++ | −− | Needs big moves to profit |
| Short straddle | −− | ++ | Catastrophic on big moves |
| Iron condor | − | + | Range breakout |
| Calendar spread | small− | + | Large moves destroy the tent shape |

---

## The Quantitative Relationship

Gamma and theta are quantitatively linked through the Black-Scholes equation. For an ATM option:

> **Higher IV = higher both gamma AND theta**

When the market prices in higher future volatility:
- Options are worth more (higher price)
- They decay faster in dollar terms (higher theta)
- Their delta changes faster with moves (higher gamma)

This is why you cannot escape the tradeoff by choosing a high-vol environment — both sides amplify simultaneously.

---

## Near Expiration: The Tightening Vice

As expiration approaches for an ATM option:
- Theta increases (decay accelerates)
- Gamma increases (delta becomes more sensitive)

The short-vol trader near expiration is collecting the most theta per day — but is also most exposed to gamma risk. A small adverse move can quickly become a large loss. The "sweet spot" for short vol (maximum theta per unit of gamma risk) is often 3–6 weeks before expiration, not the final week.

---

## Common Misunderstandings

**Myth**: "I can collect theta without much gamma risk by going far OTM."
**Reality**: Far OTM options have low gamma AND low theta. The tradeoff doesn't disappear — you just scaled down both sides proportionally.

**Myth**: "Buying time spreads gives me positive theta without gamma risk."
**Reality**: Calendar spreads have a mild negative gamma. They are not "theta without gamma" — they are just a different balance point on the same spectrum.

**Myth**: "I should always sell options because theta always decays."
**Reality**: Theta decays but gamma can destroy the position faster than theta accumulates. Short vol without discipline on gamma management leads to catastrophic losses.

---

## Page References

- Gamma-theta relationship introduced: pp. 110–116 (Ch. 5)
- Quantitative relationship, ATM examples: pp. 50–57 (Ch. 2)
- Near-expiration acceleration: pp. 116–118 (Ch. 5)
- Gamma scalping as the active way to trade realized gamma: pp. 259–274 (Ch. 13)
