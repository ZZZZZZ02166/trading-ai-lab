# Chapter 10 — Managing Position Risk
*Source: Trading Options as a Professional — Ch. 10*

---

## Summary

Chapter 10 brings together everything in the book into a framework for managing a multi-option portfolio. It shows how position Greeks change dynamically as the stock moves, why static Greek snapshots are insufficient, and how to set risk limits that prevent catastrophic losses. The chapter uses a 20-contract bull call spread as the primary example, showing all five position Greeks across the full stock price range.

---

## Key Concepts

### Position Greeks: Additive Across All Legs

For any multi-leg position, each position Greek = sum of all component Greeks × their multipliers.

**Example: 20 long 70–75 call spreads** (from Chapter 10 tables):

| Greek | 70 Call | 75 Call (short) | Net per spread | × 100 × 20 |
|-------|---------|-----------------|----------------|------------|
| Delta | 0.535 | −0.262 | +0.273 | +546 |
| Gamma | 0.059 | −0.049 | +0.010 | +20 |
| Vega | 0.087 | −0.066 | +0.021 | +42 |
| Theta | −0.310 | +0.225 | +0.085 | +170/day |

Position interpretations:
- Delta +546: behaves like being long 546 shares
- Gamma +20: for each $1 stock rise, position delta increases by 20
- Vega +42: for each 1% IV rise, position gains $42
- Theta +170: position gains $170/day from time decay

### How Position Greeks Change With Stock Price

Greeks are not constant — they change as the stock moves. For the 20-contract bull call spread:

- **Below $70** (stock below lower strike): positive gamma, moderate delta, positive vega
- **Between $70 and $75** (stock between strikes): peak delta, positive gamma, positive vega — all Greeks are largest in magnitude here ("hot zone")
- **Above $75** (stock above upper strike): gamma becomes negative (short call dominates), delta falls, vega falls

**Critical insight — gamma sign flip**: below the lower strike, the position benefits from moves (positive gamma). Above the upper strike, the position is hurt by moves (negative gamma). The crossing happens between the strikes.

### Dynamic Risk Management

Three time horizons are relevant for the 20-contract spread (Figures 10-1 through 10-5):
- **Expiration**: position value is the straight-line bull spread shape
- **35 days to expiry**: curved lines showing time value; Greeks are at moderate levels
- **17 days to expiry**: Greeks have shifted further; crossing is more abrupt

A trader who evaluates Greeks only at entry will be surprised when the stock moves into or out of the spread's "hot zone."

### Setting Risk Limits

Risk limits should be set in dollar terms:
- **Delta limit**: max acceptable P/L from a $1 adverse move (position delta × $1)
- **Gamma limit**: max acceptable delta drift from a $5 adverse move (γ × $5 per dollar, compounded)
- **Vega limit**: max acceptable loss from a 5-vol-point IV rise
- **Theta benefit**: daily income to monitor against weekly gamma losses

**Example**: Position delta = +546. Acceptable daily loss = $10,000. → Stop-loss at approximately $18 adverse stock move ($10,000 / 546 ≈ $18). More precisely, gamma compresses this: with positive gamma below $70, large adverse moves (stock falling) generate compounding delta changes that make the real loss < the linear estimate.

### Identifying the Key Risk Greek

Different strategies have different primary risk Greeks:
- Bull call spread: primary risk is vega (IV change between strikes changes spread value most)
- Short straddle: primary risk is gamma (large moves) compounded by vega (IV spike)
- Long call: primary risks are theta (daily cost) and timing (direction + expiry)
- Covered call: primary risk is delta (stock decline below break-even)

Bittman advises identifying the single Greek that most threatens the position under adverse scenarios, then setting a dollar-denominated limit for that Greek.

### Neutralizing Greeks

Any Greek can be neutralized by adding positions:
- To reduce delta: trade the underlying stock
- To reduce gamma/vega: add offsetting option positions
- To reduce theta: it follows from gamma/vega adjustments (not independently adjustable)

Selective neutralization lets traders keep their desired exposure (e.g., long vega) while eliminating unintended risks (e.g., excessive delta).

---

## Key Lessons

1. **Position Greeks change dynamically**. A snapshot at entry is not sufficient. Monitor all five Greeks continuously as the stock moves.
2. **Gamma sign flips** at the short-call strike of a bull call spread. Below the lower strike: positive gamma. Above the upper: negative gamma. Don't be surprised by this.
3. **Dollar-denominated limits** translate Greek exposures into actionable stop-losses. "My position delta is 546" is less useful than "I lose $546 per $1 adverse stock move, and my max loss is $5,000, so my stop is ~$9 below current price."
4. **The gamma-theta linkage** means the "hot zone" (between strikes for a spread) is simultaneously where you collect the most theta AND where you have the most gamma exposure. There's no free lunch.

---

## Warnings

⚠️ **Greeks are snapshots, not constants.** A position with delta = +546 today may have delta = +800 if the stock rises $5. Always re-evaluate Greeks after significant stock moves.

⚠️ **Position Greeks can change sign.** A bull call spread's gamma is positive below the lower strike and negative above the upper strike. Traders who don't recognize this flip will misclassify their risk.

⚠️ **When interest rates are non-zero, neutralizing gamma doesn't fully neutralize theta** — the carry cost component of theta remains. This matters for large positions held over weeks or months.

---

## Connections to Rest of Book

- Chapters 3–4 provided the individual option Greeks that are aggregated in this chapter
- Chapter 8's delta-neutral framework is extended here to multi-position portfolios
- Chapter 9's bid-ask pricing shows what happens when market makers accumulate many unhedged positions
- All ten chapters of the book build toward this final chapter's portfolio risk framework

---

## Page References
- Position Greeks for 70–75 spread: pp. 322–332 (Ch. 10)
- Greek graphs (delta, gamma, vega, theta) vs. stock price: pp. 323–330 (Ch. 10)
- Risk limits and stop-loss: pp. 332–342 (Ch. 10)
- Greek neutralization: pp. 338–345 (Ch. 10)
