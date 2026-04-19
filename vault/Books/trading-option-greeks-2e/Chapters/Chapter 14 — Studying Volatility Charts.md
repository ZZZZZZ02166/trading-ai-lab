# Chapter 14: Studying Volatility Charts
*Trading Option Greeks 2e — pp. 276–289*

---

## Chapter Summary

Volatility charts plot IV and realized volatility (30-day HV) on the same graph over time. They are the primary tool for identifying vol-selling and vol-buying opportunities. Passarelli presents nine patterns covering all combinations of IV and realized vol rising, staying constant, or falling. Each pattern implies a specific type of trade.

---

## Why Volatility Charts Matter

You cannot make a good vol trade decision from option prices alone. You need to know:
1. Is IV above or below its historical range?
2. Is IV above or below current realized vol?
3. Are IV and realized vol converging or diverging?

Vol charts answer all three questions at a glance. They show the full context of where IV is in its own history and how it relates to what the stock has actually been doing.

---

## The Nine Patterns

### Pattern 1: Both IV and Realized Vol Rise
**What it looks like**: Both lines trending upward together.

Possible implications:
- If IV rises faster than realized: options are overpriced — sell vol (but with caution, as realized may catch up)
- If realized rises faster than IV: options are underpriced — buy vol
- If they rise together: fair pricing but elevated absolute vol environment

Context matters: a post-shock environment where the stock is becoming genuinely more volatile AND options are repricing appropriately.

---

### Pattern 2: Realized Rises, IV Stays Constant
**What it looks like**: Realized vol trends up while IV line stays flat.

Stock is moving more than expected. Options haven't repriced. This is a vol-buying signal: realized vol is outpacing what the market is pricing in. Long straddle or long gamma.

---

### Pattern 3: Realized Rises, IV Falls
**What it looks like**: Realized vol trending up while IV is declining.

Classic post-earnings setup: the event caused a large realized move but the option-implied uncertainty resolved. Long gamma position entered before the event would profit. Short vol here would be painful.

---

### Pattern 4: Realized Stays Constant, IV Rises
**What it looks like**: IV line climbs while realized vol stays flat.

This is the pre-earnings classic setup: the stock is quiet but options are becoming increasingly expensive. The market anticipates a volatility event. Passarelli: "the classic IV rush." Buy straddles early in this pattern before IV gets too expensive.

---

### Pattern 5: Both Constant
**What it looks like**: Both lines flat.

Nothing happening — quiet period. No structural vol edge available. Income strategies like iron condors and calendars work well here. No news = no catalyst for either IV rush or vol crush.

---

### Pattern 6: Realized Constant, IV Falls
**What it looks like**: IV declining toward realized vol while realized stays flat.

Vol premium compressing. IV has been elevated and is reverting to match realized. Classic short-vol opportunity: sell options while the premium is still elevated, profit from IV falling to realized. Two convergences on the same chart (mid-Sep to Nov in the book's example) signal multiple entry windows.

---

### Pattern 7: Realized Falls, IV Rises
**What it looks like**: IV climbing while realized vol is declining.

The clearest pre-event setup: stock is calm but options are getting expensive. Passarelli: "etched into the souls of anyone who has been reading up to this point." Buy straddles or buy delta-neutral options to participate in the IV rush and subsequent post-event move.

---

### Pattern 8: Realized Falls, IV Stays Constant
**What it looks like**: Realized vol declining while IV stays elevated.

A crossover is occurring or about to occur. The realized vol is falling toward or below IV. Convergence setup: options remain priced for more volatility than has been occurring. Short-vol opportunity — but be alert, because it's occurring in a stock that has been active and could reverse.

---

### Pattern 9: Both IV and Realized Fall
**What it looks like**: Both lines declining together.

Post-crisis normalization. The scary event has passed, uncertainty resolves, the stock settles down. Vol-selling strategies become attractive again after a period of elevated vol. Often coincides with stock stabilization at or near important price levels.

---

## How to Use These Patterns in Practice

1. Pull up a vol chart for any stock before deciding on a strategy.
2. Identify which of the nine patterns best describes the current state.
3. Determine whether the trade should be: buy vol, sell vol, or range/neutral.
4. Check IV against its own historical range to confirm the pattern isn't misleading.
5. Match the strategy (straddle, condor, calendar, etc.) to the diagnosed pattern.

---

## Key Lessons

1. **The chart, not the option price, tells the story.** A 35% IV on one stock may be cheap; on another, expensive. Context is everything.
2. **Pre-earnings IV rush (Pattern 7) is the most exploitable pattern.** It is predictable, recurring, and well-documented. The key is timing entry — not too early (theta cost), not too late (IV already elevated).
3. **Post-event vol crush (Pattern 3) rewards the gamma buyer, punishes the vol seller.** Short vol positions that survive into an earnings announcement take on enormous realized vol risk.
4. **Pattern 6 (IV falls, realized constant) is the textbook short-vol environment.** The Vol premium is unambiguously above fair value and compressing back toward realized.
5. **Never trade vol without a vol chart.** If you can't see where IV is relative to its history and relative to realized vol, you don't know if you're getting a good price.

---

## Connection to the Rest of the Book

- Ch. 15 (straddles) is the primary vehicle for Pattern 4/7 (IV rush trades)
- Ch. 12 (delta-neutral vol selling) is the primary vehicle for Pattern 6/8 (vol premium selling)
- Ch. 11 (calendar spreads) is the primary vehicle for Pattern 5 (quiet, term structure plays)
- Ch. 10 (iron condors) is the primary vehicle for quiet markets (Pattern 5)
