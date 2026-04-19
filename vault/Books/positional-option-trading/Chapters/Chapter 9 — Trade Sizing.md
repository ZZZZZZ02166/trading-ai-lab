# Chapter 9: Trade Sizing
*Positional Option Trading, Euan Sinclair — pp. 186–215*

---

## Chapter Summary

Chapter 9 is the complete treatment of position sizing for options traders. The Kelly criterion maximizes long-term growth rate, but its standard form is dangerously wrong for options traders: it ignores negative skew, ignores tail events that are rare enough to miss in historical samples, and ignores parameter estimation uncertainty. Sinclair shows how to adjust Kelly for all three, and why fractional Kelly (25–50% of raw estimate) is almost always the right answer. He also debunks stops as a risk control tool, showing they fundamentally reshape (not improve) return distributions.

---

## The Kelly Criterion: Basics

The Kelly criterion selects the bet fraction f that maximizes the long-run growth rate of a bankroll.

**For continuous outcomes:**
> f* ≈ μ/σ² (when μ is small relative to σ)
> f* ≈ μ/(μ² + σ²) (more exact)

**Growth rate formula:**
> GR(f) ≈ (f − f²/2)·μ²/σ²

- Growth is maximized at f = 1 (full Kelly)
- Growth rate = 0 at f = 2 (half Kelly would have been optimal)
- f > 2 produces negative long-run growth

**Why Kelly is theoretically dominant:**
- Maximizes long-run growth rate
- Minimizes expected time to reach any goal
- Bankruptcy is impossible (mathematically)
- Unbeatable by any other sizing strategy in the long run

**Why Kelly is dangerous in practice:**
- Large, uncomfortable bet sizes
- High portfolio volatility and drawdowns
- Parameter estimation is uncertain — using the wrong f can destroy growth rate

---

## Extension 1: Rare Tail Events (Figs 9.1–9.2)

**Two-outcome model** (p1=0.55 win, p2=0.45 lose): f* = 10%

**Three-outcome model** adding a tail event (p3=0.02 chance of losing 3× stake):
- f* drops to 5% — **half** of the two-outcome estimate
- Growth rate becomes **negative for f > 10%**
- A 2% probability tail event is easily missed in historical data, yet it cuts optimal f in half

**Key insight**: Short-vol strategies have exactly this structure. The rare but large loss events are the ones most likely to be underestimated. The correct Kelly fraction is smaller than the naive estimate implies.

---

## Extension 2: Non-Normal Returns (Equations 9.11–9.22)

For continuous return distributions:

**With skewness correction:**
> f* = [μ² + σ² ± √((μ² + σ²)² − 4λ₃·μ)] / (2λ₃)

where λ₃ is the third raw moment of the return distribution (proxy for skewness).

**Practical rule:**
- **Negative skew** (typical for short options): reduce f below the normal-distribution estimate
- **Positive skew** (typical for long options): increase f above the normal-distribution estimate

**For options trading**: Short vol strategies have μ > 0, σ > 0, and **negative skew** — the standard Kelly formula overestimates the optimal bet size.

---

## Extension 3: Estimation Uncertainty (Tables 9.2–9.3)

Even with n=1000 trade samples:
- Kelly fraction estimate has a sampling distribution — it is only a point estimate
- The true Kelly fraction may be lower than our estimate
- If true f < 0, we should not trade (negative edge)

**For an option trade sample** (n=1000, mean=$0.059, sd=$1.137, skewness=−6.20):
- Estimated Kelly = 0.046
- SD of estimate = 0.031
- Probability true Kelly < 0: **7%**
- Probability we are over-betting enough to have negative growth rate: **25%**

**Table 9.2 — Fractional Kelly for target over-betting probabilities (normal distribution):**

| Max Over-Betting Probability | Kelly Scale Factor |
|------------------------------|-------------------|
| 10% | 0.048× Kelly |
| 15% | 0.230× Kelly |
| 20% | **0.375× Kelly** |

**Table 9.3 — With skewness correction:**

| Max Over-Betting Probability | Kelly Scale Factor |
|------------------------------|-------------------|
| 10% | 0.205× Kelly |
| 15% | 0.357× Kelly |
| 20% | **0.478× Kelly** |

**Practical result**: After accounting for estimation uncertainty and negative skew, the appropriate Kelly fraction is approximately **20–50% of the raw estimate**. This is the basis for the standard "quarter Kelly" to "half Kelly" heuristic.

---

## The Stops Myth: What Stops Actually Do (Figs 9.10–9.13)

Most traders believe stops "truncate" the left tail of the distribution. This is wrong.

**What traders imagine** (Fig 9.11): A normal distribution with the left tail cut off at −15%.

**What actually happens** (Fig 9.12 — Fixed Stop):
- Distribution becomes **bimodal**: a spike at exactly −15% (all stopped trades) plus a truncated bell for survivors
- Mean drops from 10% to **9.6%**, median from 10% to **8.6%**
- Many trades that would have recovered from −15% drawdowns are stopped out early and counted as losses
- The "cost" of stops: eliminating potential winning trades that temporarily dipped past the stop level

**Trailing Stop** (Fig 9.13):
- Even worse for the upper tail — cuts off the largest winners
- Mean drops to **9.4%**, median to **8.0%**
- The distribution is completely changed: the shape you were betting on no longer exists

**When stops actually help:**
- When the return distribution is negatively autocorrelated (momentum strategies — losses tend to keep losing)
- For trend-following strategies with strong autocorrelation in losses
- Stops have positive expected value **only if losing streaks imply more losses to come**

**For vol-selling** (mean-reverting, negatively autocorrelated outcomes):
- Losses often precede recoveries
- Stops eliminate the recovery trades → strictly negative expected value

---

## Subaccount Method (Practical Solution)

**Problem**: Kelly tells you how to size the risky portion of your portfolio, but doesn't tell you how to handle the psychological discomfort of large drawdowns.

**Solution**: Split the portfolio:
- **Untraded reserve** (e.g., 75% of account): sits in cash/T-bills
- **Trading account** (e.g., 25%): apply full Kelly to this portion

This produces the same growth rate as quarter-Kelly on the full account but with better psychological framing.

**Table comparing approaches** (1-year simulation, starting $100):

| Statistic | Quarter Kelly | Fixed Stop Subaccount | Trailing Stop Subaccount |
|-----------|--------------|----------------------|--------------------------|
| Average | $101.70 | $102.20 | $117.13 |
| Minimum | $78.30 | $68.75 | $69.36 |
| 10th pct | $91.70 | $86.30 | $89.30 |
| 90th pct | $111.10 | $120.90 | $153.40 |
| Avg Max DD | 9% | 12% | 12% |
| Max DD | 26% | 38% | 30% |

Quarter Kelly has the smallest maximum drawdown — consistent with the theory that fractional Kelly reduces variance significantly.

---

## Key Formulas

| Formula | Use |
|---------|-----|
| f* ≈ μ/σ² | Basic Kelly (normal distribution, μ << σ) |
| f* ≈ μ/(μ² + σ²) | More exact Kelly |
| GR(f) = (f − f²/2)·μ²/σ² | Growth rate as function of f |
| GR = 0 at f = 2 | Never bet more than 2× Kelly |
| Practical f = 0.25–0.50 × raw Kelly | After skew + uncertainty corrections |

---

## Key Lessons

1. **Kelly is theoretically optimal but practically dangerous without adjustments.** The three extensions (tail risk, skew, estimation uncertainty) all push toward smaller f.
2. **Fractional Kelly (25–50%) is almost always right for short-vol strategies.** Negative skew alone justifies betting well below the raw Kelly estimate.
3. **Stops change distribution shape — they do not improve it for mean-reverting strategies.** They eliminate trades that would recover, creating a bimodal distribution. For vol traders, stops hurt expected value.
4. **The subaccount method is the practical implementation** of fractional Kelly — easier psychologically and equivalent mathematically.
5. **Tail events cut optimal f in half.** A 2% chance of a 3× loss is enough to halve optimal position size. Short-vol strategies have exactly this structure.

---

## Source Pages

- Kelly basics, growth rate (Figs 9.1–9.2, Eqs 9.1–9.10): pp. 186–193
- Non-normal returns and skew adjustment (Eqs 9.11–9.22): pp. 193–201
- Estimation uncertainty / fractional Kelly (Tables 9.2–9.3, Eq 9.38): pp. 200–206
- Stops analysis (Figs 9.10–9.13): pp. 204–210
- Subaccount method (comparison table): pp. 211–215
