# Delta-Neutral Trading
*Source: Trading Option Greeks 2e — Ch. 12, 13, 16*

---

## Definition

Delta-neutral trading means maintaining a net delta of approximately zero in a position by hedging the option's delta with an offsetting position in the underlying stock. This neutralises the directional exposure and leaves the position exposed primarily to volatility (IV and realized vol), time decay, and other greeks.

---

## How to Establish Delta Neutrality

1. Open an option position (long calls, long straddle, etc.) — this creates delta exposure.
2. Calculate the total position delta: delta per contract × 100 shares × number of contracts.
3. Offset with the underlying: if total delta is +1,000, short 1,000 shares.
4. The resulting position has delta ≈ 0.

**Example**: Long 20 calls at 50 delta each = 2,000 long deltas. Short 2,000 shares (= −2,000 deltas). Net delta ≈ 0. Remaining exposure: gamma, theta, vega.

---

## Why Go Delta-Neutral?

The goal is to **isolate the volatility bet**. Instead of betting on the stock going up or down (which is uncertain), you bet on whether:
1. IV will rise or fall (vega play, Ch. 12)
2. The stock will move more or less than IV implies (realized vol play, Ch. 13)

You strip out direction and trade pure volatility.

---

## Delta Drift and Continuous Rebalancing

Once established, delta neutrality doesn't last. As the underlying price moves, gamma causes the delta to drift. The position becomes directionally biased over time.

**Long gamma drift**: if stock rises, delta becomes positive (you're effectively long). Must sell stock to re-neutralize.

**Short gamma drift**: if stock rises, delta becomes negative (you're effectively short). Must buy stock to re-neutralize.

Rebalancing frequency is a judgment call — too frequent creates transaction costs; too infrequent leaves large directional exposure.

---

## Long Delta-Neutral (Volatility Buying)

- **Position**: long options + short underlying
- **View**: IV is too low OR realized vol will exceed IV
- **P/L driver**: gamma scalps (if the stock moves a lot) + vega gains (if IV rises)
- **Risk**: theta erosion if the stock doesn't move and IV stays flat

**Best setup**: IV is depressed below its historical range; an anticipated catalyst may cause realized vol to spike (or IV to rush before the event).

---

## Short Delta-Neutral (Volatility Selling)

- **Position**: short options + long underlying
- **View**: IV is too high OR realized vol will be less than IV implies
- **P/L driver**: theta income + vega gains (if IV falls)
- **Risk**: large realized moves generate gamma losses that exceed theta collected

**Best setup**: IV is elevated above its historical range; stock is in a calm, range-bound period; approaching a period where the market has overpriced future uncertainty.

---

## P/L Attribution

Always decompose P/L from a delta-neutral trade into components:
- **Vega P/L**: IV change × position vega
- **Gamma P/L**: sum of stock scalp profits (or losses from adverse drift)
- **Theta P/L**: daily decay credit or debit

Example: If vega P/L = +$3,000, gamma P/L = −$225, theta P/L = −$75: total = +$2,700. The vega component dominated. Without decomposition, you might think it was a gamma trade when it was actually an IV trade.

---

## Common Misunderstandings

- **"Delta-neutral means no risk."** False. Gamma and vega create substantial risk even when delta is zero.
- **"Delta-neutral trading is only for market makers."** False. It is the correct framework for anyone who wants to trade pure volatility rather than direction.
- **"You have to rebalance constantly."** False. Experienced traders rebalance based on market feel and 1σ price triggers, not at every tick.

---

## Page References

- Delta-neutral introduction: pp. 243–249 (Ch. 12)
- Establishing delta neutrality: pp. 250–254 (Ch. 12)
- P/L attribution examples: pp. 254–258 (Ch. 12)
- Gamma scalping (realized vol version): pp. 259–274 (Ch. 13)
- Market maker position management: pp. 316–321 (Ch. 16)
