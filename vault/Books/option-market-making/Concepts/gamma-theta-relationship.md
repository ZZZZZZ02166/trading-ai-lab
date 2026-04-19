# Concept: Gamma-Theta Relationship
*From: Option Market Making, Allen Jan Baird*

---

## Definition

For long options positions, **gamma and theta have opposite signs and approximately equal magnitudes**:
- **Long option:** Positive gamma (benefits from large moves) + Negative theta (loses value daily)
- **Short option:** Negative gamma (hurt by large moves) + Positive theta (gains value daily)

This is not a coincidence — it is a fundamental no-arbitrage constraint. If a position had positive gamma AND positive theta, it would be risk-free money.

---

## The Break-Even Move

For a long ATM option position, there is a daily break-even move in the underlying that exactly offsets the theta cost:

> **Break-even move ≈ √(2 × daily theta / gamma)**

If the underlying moves more than this each day, the long position profits. If it moves less, the position loses. This defines the profitability condition for long options:

> **Long options profit when: realized volatility > implied volatility**

Because theta is priced based on implied vol, and gamma benefit depends on realized vol.

---

## Why It Matters for Market Makers

This relationship is the core of **volatility trading:**

- **Long gamma / short theta** (long options, hedged): You are betting realized vol > implied vol. You want markets to move — large moves help you, calm markets hurt you.

- **Short gamma / long theta** (short options, hedged): You are betting realized vol < implied vol. You want markets to stay calm — calm markets earn you theta, large moves hurt you.

For a market maker, this means:
- If you believe actual market moves will be larger than IV implies → accumulate positive gamma
- If you believe markets will be calmer than IV implies → accumulate positive theta (short gamma)

---

## Gamma-Theta Across Position Types

| Position | Gamma Sign | Theta Sign | Interpretation |
|----------|-----------|-----------|----------------|
| Long call/put | + | − | Pays for the right to benefit from large moves |
| Short call/put | − | + | Earns decay, at risk of large moves |
| Long straddle | + | − | Pays decay; needs large moves to profit |
| Short straddle | − | + | Earns decay; needs calm to profit |
| Long butterfly | +/− (trimodal) | + near center | Earns theta near center, negative gamma in wings |
| Short butterfly | −/+ (trimodal) | − near center | Pays theta near center, positive gamma in wings |

---

## Source Page References

- Gamma definition and ATM spike: pp. 41–43
- Theta definition: pp. 43–44
- Theta-gamma relationship: pp. 43–44 (note: identical form, opposite sign)
- Break-even move concept: implied throughout Chapter 3
