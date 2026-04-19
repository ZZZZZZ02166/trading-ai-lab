# Volatility Trading — Cheat Sheet
*Euan Sinclair — Quick Review*

---

## Core Formula Reference

| Formula | Description |
|---------|-------------|
| σ²_t = ω + αr²_{t-1} + βσ²_{t-1} | GARCH(1,1) |
| V_L = ω/(1−α−β) | GARCH long-run variance |
| E[σ²_{t+T}] = V_L + (σ²_t − V_L)(α+β)^T | GARCH term structure |
| σ²_YZ = σ²_overnight + k×σ²_RS | Yang-Zhang estimator |
| P/L ≈ Vega × (σ_implied − σ_realized) | Central vol trading result |
| σ_residual = σ × √(π/2N) | Discrete hedging dispersion |
| f* = p − q/b | Kelly criterion (binary) |
| S_max = 0.75σ | Optimal entry for mean-reverting asset |
| f(s) = k√s | Market impact (square root law) |
| dL/L = λdS/S − ½λ(λ−1)σ²dt | Leveraged ETF vol decay |

---

## Vol Estimator Comparison

| Estimator | Data | Efficiency |
|-----------|------|-----------|
| Close-to-Close | C only | 1× |
| Parkinson | H, L | 4.9× |
| Garman-Klass | O,H,L,C | 7.4× |
| Rogers-Satchell | O,H,L,C (drift-adj) | ~5× |
| Yang-Zhang | O,H,L,C+overnight | 14× |

---

## Six Stylized Facts About Volatility

1. Volatility clusters
2. Volatility mean-reverts (with shifting mean)
3. Fat tails — excess kurtosis > 0 universally
4. Leverage effect — vol rises as price falls
5. Volume and vol are highly correlated
6. Vol is approximately log-normally distributed

**Excess kurtosis by market**: Hang Seng 32.7, Nasdaq 9.9, FTSE 6.4, Nikkei 6.7, IBM 4.4, WTI 3.0

---

## Hedging Methods

| Method | Accuracy | Notes |
|--------|----------|-------|
| Hodges-Neuberger (HN) | Exact | Numerical PDE, full asymmetry |
| Whalley-Wilmott (WW) | Good approx | Analytic; loses L/S asymmetry |
| Zakamouline | Best analytic | Recommended; preserves asymmetry |

---

## Kelly Position Sizing

| Bet Size | Effect |
|----------|--------|
| < f* | Sub-optimal but safe |
| f* (full Kelly) | Maximum growth; brutal drawdowns |
| f*/2 (half Kelly) | 75% growth, 25% variance — recommended |
| > f* (over-Kelly) | Growth decreases; ruin above 2× Kelly |

---

## Variance Premium: QQQ Empirical Results

| Strategy | Sharpe | Avg Weekly Return | Max DD |
|----------|--------|------------------|--------|
| Short 50Δ straddle | 1.37 | 9.8% | 29.8% |
| Short 30Δ straddle | 1.13 | 9.7% | ~30% |
| Short ATM straddle | 1.14 | ~9% | ~30% |
| Short 30Δ risk reversal | 0.69 | 13.5% | 26.9% |

Premium is NOT reliably present for individual equities.

---

## Top Cognitive Biases for Vol Traders

| Bias | Danger | Counter |
|------|--------|---------|
| Self-attribution | Overconfidence after wins | Track all trades objectively |
| Availability | Overweight vivid events | Use base rates |
| Confirmation | Seek confirming evidence only | Actively look for contradicting views |
| Anchoring | Anchored to recent ATM IV | Quantify a range, not point estimate |
| Loss aversion | Hold losers too long | Pre-commit exit criteria |

---

## Key Warnings

⚠️ **P/L dispersion is enormous** even with positive edge. Evaluate over 100+ trades.

⚠️ **Path dependency is irreducible.** Same vol, different timing → different P/L.

⚠️ **Fat tails break Kelly.** Run fat-tailed simulations before sizing.

⚠️ **Variance premium varies.** High IV is necessary but NOT sufficient for profiting from selling.

⚠️ **VXX decays in contango.** Long VXX is structurally losing over time.

⚠️ **Leveraged ETF vol drag:** 2× on 20% vol underlying loses ~4% per year from compounding.

⚠️ **No single estimator is best.** Use all five — differences are diagnostic signals.
