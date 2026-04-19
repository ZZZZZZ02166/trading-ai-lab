# Concept: Delta Hedging
*From: Option Market Making, Allen Jan Baird*

---

## Definition

**Delta hedging** is the practice of taking an offsetting position in the underlying asset (futures or stock) to eliminate the directional price sensitivity of an options position. After hedging, a small move in the underlying causes neither gain nor loss — the position is *delta neutral*.

Delta = dollar change in option price per $1 change in underlying. A long 100 call with delta +0.50 requires selling 0.50 futures contracts to hedge (net delta = 0).

---

## Why It Matters

Delta hedging is the **foundation of pure market making.** A market maker who does not hedge delta is speculating — taking a directional position — not market making. The entire logic of earning the bid/offer spread without directional exposure depends on maintaining delta neutrality.

Delta hedging converts an option position into a pure volatility/time decay trade:
- Long option + delta hedge = long gamma, short theta (profits from large moves, costs daily decay)
- Short option + delta hedge = short gamma, long theta (profits from calm markets, at risk from large moves)

---

## How It Works in Practice

1. After completing an option trade, immediately calculate the net delta of the position
2. Buy or sell the required number of futures contracts to bring net delta to zero
3. As the underlying price moves, delta changes (gamma) — rehedge periodically
4. Near expiration, delta changes rapidly — hedge more frequently

---

## Common Mistakes (from Baird, Chapter 8)

**Mistake 1 — Delayed hedging:** Waiting to hedge at a "better" level. This is speculation. The cardinal rule: *hedge when you should, not when it's convenient.* Any delay is a directional bet.

**Mistake 2 — Incorrect hedge price:** Using stale board prices instead of actual traded futures prices. If options were priced off futures at 100 but actual futures are at 101, the delta calculation is wrong — the hedge is too small or too large.

---

## Key Relationships

- Delta neutral position → sensitive only to vol, time, IV (not price direction)
- Rehedging frequency → driven by gamma (high gamma positions need frequent rehedges)
- Rehedging cost → a cost that effectively reduces the gamma benefit; accounted for in the spread
- Delta vs probability → ATM delta ≈ 0.50 ≈ 50% probability of expiring ITM

---

## Source Page References

- Delta definition: pp. 38–40
- Delta neutral concept: p. 41
- Delta drift and gamma: pp. 40–42
- Failure to hedge (common mistake 1): pp. 181–182
- Incorrect delta hedging (mistake 2): pp. 182–183
