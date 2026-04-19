# Chapter 9: Vertical Spreads
*Trading Option Greeks 2e — pp. 173–193*

---

## Chapter Summary

Vertical spreads define maximum risk. By buying and selling options of the same type (both calls or both puts), same expiration, different strikes, you cap both maximum profit and maximum loss. The chapter walks through all four vertical spread types, compares them to outright options via greeks, and explains when each is appropriate.

---

## The Case for Spreads

Chapter 4 showed that long options have a directional thesis but also carry significant theta and vega risk. A trader can be right about direction and still lose to time decay. Vertical spreads solve this problem: by selling a further-strike option against the long option, you:
- Reduce the net premium paid (lower max loss)
- Dramatically reduce vega exposure (not as exposed to IV changes)
- Dramatically reduce theta drag (not paying as much daily time decay)
- Trade-off: cap the maximum profit

---

## Bull Call Spread

**Structure**: Buy lower-strike call + sell higher-strike call (same expiration).

**AAPL 395–405 example** (AAPL at $391, 40 DTE):
- Buy Feb 395 call @ $14.60
- Sell Feb 405 call @ $10.20
- Net debit: $4.40

| | Outright 395 Call | 395–405 Spread |
|--|---|---|
| Max loss | $14.60 | $4.40 |
| Max profit | Unlimited | $5.60 |
| Delta | 0.484 | 0.100 |
| Gamma | 0.0097 | 0.0001 |
| Theta | 0.208 | 0.014 |
| Vega | 0.513 | 0.020 |

The spread reduces vega by 96% and gamma by 99%. It is a fundamentally different position — not just a cheaper version of the same trade.

**Best for**: Traders who want directional exposure without paying for vega, or who expect a moderate bullish move (up to the short strike) rather than an explosive rally.

---

## Bear Call Spread

**Structure**: Sell lower-strike call + buy higher-strike call (same expiration). Net credit.

Maximum profit = credit received (if stock stays below the short strike at expiration).
Maximum loss = width of spread − credit.

**Best for**: Mildly bearish or neutral traders who want to sell premium with defined risk.

---

## Bear Put Spread

**Structure**: Buy higher-strike put + sell lower-strike put (same expiration). Net debit.

Maximum profit = width of spread − debit (if stock falls to or below the short strike).
Maximum loss = debit paid.

**Best for**: Traders expecting a moderate bearish move, not a large crash. The short put caps the profit at the lower strike.

---

## Bull Put Spread

**Structure**: Sell higher-strike put + buy lower-strike put. Net credit.

Economically equivalent to a bull call spread at the same strikes: same at-expiration payoff profile, just structured differently. Credit up front vs. debit. Choose based on bid-ask spreads and margin requirements.

---

## Credit vs. Debit: Not a Real Distinction

Serial credit spread traders often claim credit spreads are inherently better. Serial debit spread traders claim debit spreads are better. Passarelli demonstrates they are economically equivalent:

Sam sells a 62.5–65 credit put spread on JNJ for $1.22 credit.
Isabel buys a 62.5–65 debit call spread on JNJ for $1.28 debit.

These positions mirror each other exactly. Above $65: Sam wins $1.22, Isabel loses $1.22. Below $62.50: Isabel wins $1.22, Sam loses $1.22. Between strikes: mixed results that cancel out. The "credit vs. debit" preference is psychological, not economic.

---

## Managing Vertical Spreads

**When the long option wins early**: If AAPL rallies quickly and the 395 call goes deep ITM while the 405 call has minimal value (say, $0.05), consider closing only the 395 calls (the valuable leg) and leaving the 405 calls to expire. The cost of closing the 405 calls ($5 × lots) may not be worth it.

**Time decay advantages**: The lower theta of a spread means the passage of time hurts much less than an outright long option. When direction plays out slowly, spreads are more forgiving.

**Assignment risk at expiration**: If the stock is between the two strikes at expiration, the long (lower-strike) call may be ITM and get assigned, while the short call expires worthless, leaving an unexpected stock position. Be aware of this near expiration.

---

## Key Lessons

1. **Vertical spreads are defined-risk directional trades.** If you want to bet on direction without paying for vol or accepting unlimited loss, this is the vehicle.
2. **The greek reduction is dramatic.** A spread reduces vega by 95%+ compared to the outright option. This is not a small difference — it is a fundamentally different risk profile.
3. **Being right on direction but wrong on timing is more survivable with a spread.** Lower theta means you have more time to be right before the decay erodes your position.
4. **Credit and debit spreads are economically the same.** Choose based on liquidity and margin, not on a preference for receiving or paying premium.
5. **Strike selection determines the risk/reward.** Wider spreads = more premium captured, more risk. Tighter spreads = less exposure, less reward.

---

## Connection to the Rest of the Book

- Ch. 10 (wing spreads) combines two vertical spreads for a range trade
- Ch. 9 builds directly on Ch. 2 (greeks) and Ch. 3 (vol) to explain *why* spreads are appropriate
- Ch. 6 (put-call parity) explains why bull call and bull put spreads at the same strikes are equivalent (box spread = both combined)
