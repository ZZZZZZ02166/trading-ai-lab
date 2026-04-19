# Implied Volatility (IV)
*Source: Trading Option Greeks 2e — Ch. 3, 5, 11, 12, 14, 15*

---

## Definition

Implied volatility is the volatility value that, when plugged into an option pricing model with all other inputs known (stock price, strike price, time to expiration, interest rate, dividends), makes the model output match the observed market option price.

It is the market's forward-looking consensus estimate of how volatile the underlying will be over the life of the option. It is **not** the same as historical volatility (which is backward-looking).

---

## How to Interpret IV

- A $100 stock with 32% IV: the market implies ~68% probability the stock stays within $68–$132 over one year (±1 standard deviation)
- The **1-day expected σ** = IV / √256. At 32%: 32/16 = 2%. ~68% chance of <$2 move per day.
- IV is a per-year figure, but can be scaled to any time horizon

---

## What Drives IV

| Direction | Driver |
|-----------|--------|
| IV rises | Fear, uncertainty, anticipated events, demand for protection, earnings anticipation |
| IV falls | Complacency, post-event resolution ("vol crush"), market-maker arb normalizing extremes |

"Buy the rumor, sell the news" is literally an IV pattern: IV rises into events, collapses after — regardless of the size of the stock move.

---

## IV Mean Reversion

IV for most stocks and indices mean-reverts. It oscillates around a characteristic historical range. This is the foundation of all vol-selling strategies:
- IV elevated above historical range → sell vol
- IV depressed below historical range → buy vol

VIX demonstrates this at the index level. The same principle applies at the individual stock level.

---

## IV Term Structure

IV varies across expiration dates:
- **Contango (normal)**: longer-dated > shorter-dated (IV increases with time)
- **Backwardation (inverted)**: front-month > back-months (typically before known events)

The term structure is the analytical input for calendar spread decisions: buy the spread when front-month is elevated; sell the spread when back-month is unusually rich.

---

## Volatility Skew

Equity options show a persistent pattern: OTM puts > ATM > OTM calls in IV terms. This "smirk" shape reflects:
- Persistent demand for downside protection
- Market's asymmetric fear of crashes vs. rips

OTM puts can trade 10+ vol points above equidistant OTM calls. This creates exploitable patterns in risk reversals and put spread strategies.

---

## IV vs. Realized Vol: The Core Decision

Every vol trade is a bet on the relationship between IV (the market's forecast) and realized vol (what actually happens):

| IV vs. Realized | Bet | Trade |
|-----------------|-----|-------|
| IV > expected realized | Vol too expensive | Sell vol (straddle, iron condor, short puts) |
| IV < expected realized | Vol too cheap | Buy vol (straddle, long gamma, long options) |

The vol chart (Ch. 14) is the primary tool for making this assessment.

---

## Common Misunderstandings

- **IV is not a forecast of direction.** A 40% IV means the market expects large moves — not specifically up or down.
- **High IV does not automatically mean sell.** IV can remain elevated or rise further if realized vol keeps surprising.
- **IV can stay "wrong" for a long time.** Just because IV appears too high doesn't mean it will normalize before your position expires.

---

## Page References

- IV definition and BSM context: pp. 59–65 (Ch. 2), pp. 74–82 (Ch. 3)
- Mean reversion and VIX: pp. 80–82 (Ch. 3)
- Term structure: pp. 84–86 (Ch. 3), pp. 228–235 (Ch. 11)
- Skew: pp. 86–87 (Ch. 3)
- IV chart patterns: pp. 276–289 (Ch. 14)
- Straddle vega as pure IV play: pp. 294–296 (Ch. 15)
