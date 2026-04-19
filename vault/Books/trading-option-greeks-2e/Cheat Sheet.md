# Trading Option Greeks 2e — Cheat Sheet
*Dan Passarelli — Quick Review*

---

## The Five Greeks at a Glance

| Greek | Measures | Long Option | Short Option | Highest For |
|-------|---------|-------------|--------------|-------------|
| Delta | Price sensitivity | + (call) / − (put) | opposite | Deep ITM options |
| Gamma | Delta sensitivity | + (convexity helps) | − (concavity hurts) | ATM near expiration |
| Theta | Time decay | − (daily cost) | + (daily income) | ATM options |
| Vega | IV sensitivity | + (benefits from rising IV) | − (hurt by rising IV) | ATM / LEAPS |
| Rho | Rate sensitivity | + (calls) | varies | LEAPS |

---

## Delta Rules of Thumb

- ATM call delta ≈ 0.50; ATM put delta ≈ −0.50
- Call delta + |put delta| ≈ 1.00 (for same strike)
- Delta ≈ probability of expiring ITM (rough heuristic only)
- Higher vol → OTM deltas increase, ITM deltas decrease

---

## Formulas

| Formula | What It Gives |
|---------|---------------|
| IV / √256 | 1-day expected σ |
| Strike × interest rate × (days / 365) | Dollar interest component of carry |
| Put-call parity: call = put + stock − strike + interest − dividends | All synthetic positions |

---

## Gamma-Theta Tradeoff

**The fundamental rule**: You cannot have positive theta without accepting negative gamma. They are two sides of the same coin.

- Long option = pay theta daily, benefit from gamma
- Short option = collect theta daily, suffer from gamma
- Near expiration, ATM: both theta AND gamma increase simultaneously

---

## Strategy Selection Quick Reference

| Market View | IV Level | Preferred Strategy |
|------------|---------|-------------------|
| Bullish, strong conviction | High | Covered call or short put |
| Bullish, strong conviction | Low | Long call or bull call spread |
| Neutral (range-bound) | High | Iron condor, short strangle |
| Neutral (range-bound) | Low | Calendar spread, long straddle |
| Bullish, want defined risk | Any | Bull call spread |
| Vol is expensive vs. realized | High | Short delta-neutral (sell straddle, sell options) |
| Vol is cheap vs. realized | Low | Long delta-neutral (buy straddle, gamma scalp) |

---

## Volatility Chart Pattern → Trade

| IV | Realized | Trade |
|----|---------|-------|
| Rising fast | Constant/rising slow | Sell vol |
| Rising | Falling (pre-earnings) | Buy straddle early |
| Falling | Constant (convergence) | Sell vol |
| Falling | Rising (post-event) | Buy gamma |
| Both calm | Both calm | Iron condor, calendar |
| Both falling | Both falling | Return to short vol |

---

## Critical Rules and Principles

1. **A put is a call; a call is a put.** (Put-call parity enables all synthetic positions.)
2. **Gamma amplifies losses faster than delta predicts.** Always calculate stop-loss distances using gamma, not just delta.
3. **Theta and gamma rise together near expiration.** The best theta-collecting period is also the most gamma-dangerous.
4. **IV must be compared to its own historical range.** A 35% IV is cheap on a stock that normally trades at 50%; expensive on a stock that normally trades at 20%.
5. **Credit spreads and debit spreads at the same strikes are economically identical.** Choose based on liquidity, not preference for receiving vs. paying premium.
6. **Would I Do It Now? Rule**: at any point during a trade, ask "would I enter this position fresh at current prices?" If no, close it.
7. **Plan for the worst before entering.** Define max acceptable loss and exit triggers before putting on any trade.

---

## Key Warnings

⚠️ **Gamma acceleration**: A short call with delta=0.34 and gamma=0.15 hits a stop-loss at 1.10 after only a $1.01 adverse move — not $1.32 as delta alone implies.

⚠️ **OTM option buyers start in the hole**: Most OTM options expire worthless. Win rate < 25% is common. You need big wins to overcome frequent small losses.

⚠️ **Early exercise before ex-dates**: Deep ITM calls with time value < dividend may be exercised early. Monitor short deep-ITM calls heading into ex-dividend dates.

⚠️ **Backspread greek flip**: A call backspread that starts as "long vol" can become "short vol" if the stock falls far below the short strike. Understand the full risk profile across all price scenarios.

⚠️ **Short straddles are among the riskiest positions.** Unlimited losses in both directions. Define max loss threshold before entry. Never average into a losing short straddle.

⚠️ **Whipsaw risk increases with IV.** Higher-volatility environments make stop-loss prices reachable from random noise — you can be stopped out of a position that would have recovered.

---

## Quick Greek Formulas

- New delta after $1 move ≈ old delta + gamma
- New option price after $1 move ≈ old price + delta (first approximation)
- Time to recover theta from a move: (option price × Δstock) / theta_per_day
- 1-day σ from IV: IV / 16 (using 256-day convention)

---

## Synthetics Reference

| Want | Build With |
|------|-----------|
| Long call | Long put + long stock |
| Long put | Long call + short stock |
| Long stock | Long call + short put (same strike) |
| Conversion (riskless) | Long stock + long put + short call |
| Box (riskless interest) | Bull call spread + bear put spread |
