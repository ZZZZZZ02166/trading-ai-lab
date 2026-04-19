# Chapter 8 — Money Management
*Volatility Trading — Euan Sinclair, pp. 144–176*

---

## Summary
Kelly criterion for long-run growth, Browne for goal-reaching, optimal entry for mean-reverting assets. Fat tails break naive Kelly.

---

## Kelly Criterion
Maximize E[log(1 + f×G)].

For binary bet: **f* = p − q/b** (edge/odds)

Figure 8.4: expected bankroll bell-shaped vs bet size, peaks at f*. Betting > f* → bankroll depletes.

**Good**: maximizes long-run log wealth; zero ruin risk; asymptotically optimal.
**Bad**: requires knowing true p; brutal drawdowns; non-ergodic path; bet size changes constantly.

## Fractional Kelly
**Half-Kelly (f*/2)**: growth = 75% of Kelly, variance = 25% of Kelly.
Figures 8.6/8.7: half-Kelly PDF stays concentrated. **Practical recommendation for vol traders.**

## Browne Goal-Reaching
α* = μW / (σ²(G−W)) — aggressive when close to goal, conservative when far.
Table 8.1: beats Kelly by 10-40% in time to reach a specific target.
Use Browne when you have a specific return target; use Kelly to maximize long-term wealth.

## Optimal Entry for Mean-Reverting Assets
For Ornstein-Uhlenbeck process: **optimal entry = 0.75σ from mean** (Figure 8.18, P/L peaks here).

Applied to VIX: wait for VIX > mean + 0.75×std_dev before shorting vol.
Entering too close to mean: fewer opportunities. Too far: lower reversion probability.

## Fat Tails Warning (Figure 8.17)
Logistic distribution (kurtosis=9): Kelly-optimal size destroys bankroll. Normal distribution: works fine.
Always run fat-tailed simulations before deploying position sizing rules.

## Summary Rule
Trade size: big enough that profits mean something, small enough that losses are not catastrophic. If no such size exists, the strategy lacks sufficient edge.
