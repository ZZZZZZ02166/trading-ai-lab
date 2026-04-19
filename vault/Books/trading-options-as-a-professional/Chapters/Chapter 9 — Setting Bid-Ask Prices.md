# Chapter 9 — Setting Bid and Ask Prices
*Source: Trading Options as a Professional — Ch. 9*

---

## Summary

Chapter 9 explains the professional mechanics of option market making — how market makers set bids and asks, use theoretical value as an anchor, delta-hedge to manage risk, and execute arbitrage strategies at precise price levels. This chapter is the most operationally specific in the book and is primarily relevant for understanding what market makers do and why option prices behave as they do.

---

## Key Concepts

### Theory of the Bid-Ask Spread

Market makers earn profit by selling at the ask and buying at the bid. Their "edge" is half the bid-ask spread. They immediately delta-hedge each trade to neutralize directional risk, then attempt to close the hedge at a profit before conditions change.

**Trade 1 (Favorable scenario, Table 9-1)**:
- 10:00 am: sell 10 calls at bid 1.85, hedge with +460 shares at $54.03
- 11:00 am: stock at $55.00; buy back calls at ask 1.85, sell 460 shares at $55.00
- Stock gain from hedge: 460 × ($55 − $54.03) = $446
- Net P/L: positive (the stock rise is pure profit from the hedge)

**Trade 2 (Adverse scenario)**:
- Buy 10 calls at bid 1.85, hedge with −400 shares at $54.01
- Stock falls to $53.00; buy back stock at $53.01, sell calls at bid 1.46
- Call loss partially offset by stock gain
- Still profitable if the bid-ask edge exceeds the adverse move impact

### Theoretical Value as Pricing Anchor

Market makers set bids/asks around their theoretical value (TV). Quote = TV ± edge. A call with TV = 3.50 → quote 3.40–3.60. The edge per round-trip = 2 × (spread/2) = spread = $0.20 per share.

Profitability requires: bid-ask edge > average adverse move impact on the position before closing.

### NBBO and Customer Protection

The National Best Bid and Offer ensures public orders are filled at the best price across all exchanges. This forces market makers to compete aggressively — spreads narrow until the edge just covers hedging costs and risk.

### Pricing Formulas for Arbitrage Strategies

**Conversion target call price:**
> Call = Strike + (interest × days/365) + Put − Stock

If market call > this price → conversion is profitable.

**Reverse conversion target call price:**
> Call = Stock − Put + (interest × days/365)

If market call < this price → reverse conversion is profitable.

**Box spread fair value:**
> FV = (High strike − Low strike) × [1 − (interest × days/365)]

**Two-trade arbitrage**: execute each leg of a conversion/box at separate times, capturing bid-ask spread on each leg individually. Total profit = sum of edges minus transaction costs.

---

## Example: Creating a Conversion in Two Trades (Table 9-10C)

- Target: reverse conversion at 1% vol below theoretical
- Theoretical call: $79.51 (computed from formula)
- Actual execution: buy call at $79.61 (market price allows 10-cent edge)
- Net credit: $0.10 per share = $10 per contract

Table 9-11C (Long Box Spread): 
- +10 × 90 call spread + 10 × 95 put spread
- Box theoretical value: $9.93
- Box execution cost: $9.14 (favorable entry)
- Locked-in profit: $0.79 per share = $79 per box

---

## Key Lessons

1. Market makers are not predicting direction. They are pricing liquidity and hedging it away immediately. Their profit is the bid-ask spread captured, not directional gain.
2. The delta hedge doesn't eliminate risk — it converts directional risk into vol risk and execution risk (adverse moves before the hedge can be closed).
3. Arbitrage pricing formulas are exact. The formulas in Chapter 9 tell market makers precisely what price they need to lock in a target profit from conversions and box spreads.
4. Short stock rebate is critical for reverse conversion profitability. Without it, many reverse conversions are unprofitable for retail traders.

---

## Warnings

⚠️ Market makers who hold positions too long become speculators by accident. The goal is to close positions quickly at bid or ask — holding through adverse moves defeats the strategy.

⚠️ In fast markets, the delta hedge may not execute at the intended price. Slippage in the hedge can turn a profitable bid-ask capture into a loss.

---

## Connections to Rest of Book

- Chapter 5 and 6's synthetic relationships and parity formulas are applied in this chapter's pricing formulas
- Chapter 8's delta-neutral technique is the short-term version of the bid-ask hedging described here
- Chapter 10 shows what happens when market makers accumulate multiple unhedged positions (position risk)

---

## Page References
- Bid-ask theory: pp. 280–290 (Ch. 9)
- Theoretical value and pricing: pp. 290–300 (Ch. 9)
- Conversion/reversal formulas: pp. 304–315 (Ch. 9)
- Box spread execution: pp. 307–315 (Ch. 9)
- Two-trade arbitrage: pp. 315–325 (Ch. 9)
