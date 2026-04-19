# Chapter 7: Directional Option Trading
*Positional Option Trading, Euan Sinclair — pp. 149–163*

---

## Chapter Summary

Most retail traders use options directionally. This chapter gives the theoretical toolkit for doing it correctly. The core tool is the **Boness model** — a pre-BSM option pricing formula that explicitly incorporates the trader's actual drift forecast. The chapter also covers strike selection (which strike to buy given a directional view), expiration selection, and how different evaluation criteria (average return, median return, probability of profit) lead to different "optimal" choices.

---

## Why BSM Misleads Directional Traders

BSM removes drift because a *market maker who delta-hedges* is indifferent to it — they replicate the option regardless of where the underlying goes. But a **directional speculator who does not hedge** is doing the opposite: they *want* the underlying to move in the forecasted direction.

For a speculator, drift matters enormously. BSM gives the wrong value for a position held for directional exposure. Using N(d₂) = 32% and asking "is this call worth buying?" gives the wrong answer if you have a 10% drift forecast that implies N(d₄) = 45%.

---

## The Boness Model (1962)

The Boness model prices options using the trader's **actual drift forecast μ** instead of the risk-free rate r. It is not arbitrage-free (and doesn't need to be — we're speculating, not replicating), but it answers the right question: "Given my drift forecast, what is this option worth to me?"

**Call price:**
> C = S·exp(μT)·N(d₃) − X·N(d₄)

Where:
- d₃ = [ln(S/X) + (μ + σ²/2)·T] / (σ√T)
- d₄ = [ln(S/X) + (μ − σ²/2)·T] / (σ√T)
- μ = trader's actual forecast of stock drift (annualized)

**Generalized form** (with risk-free discounting of the strike):
> C = S·exp(μT)·N(d₃) − exp(−rT)·X·N(d₄)

**Drift Greek** (sensitivity of call price to drift estimate):
> ∂C/∂μ = T·S·exp(μT)·N(d₃)

For long-dated options (T large) or large positions (S large), small errors in μ produce large valuation errors.

---

## True ITM Probability vs Risk-Neutral Probability

| Measure | Formula | Used for |
|---------|---------|---------|
| Risk-neutral (BSM) | N(d₂) | Hedging, replication |
| Physical (Boness) | N(d₄) | True ITM probability under your drift forecast |

**Example**: 1-year 110 call, S=$100, σ=30%, r=0%, μ=10%
- Risk-neutral N(d₂) = 32% (what the market implies)
- Physical N(d₄) = 45% (what your 10% drift forecast implies)
- **Difference**: 13 percentage points — a 40% relative increase in ITM probability
- If you're paying for a call on this basis and using N(d₂) = 32% to evaluate it, you're significantly undervaluing your position

---

## Strike Selection

No single right answer — depends on what you're optimizing for.

**Setup**: $100 stock, σ=30%, μ=5%, 1-year options

**When stock rises to $120** (correct direction, large move):
- OTM options (110+) offer highest dollar profit per $100 invested
- But require the most precise forecast

**When stock only rises to $106** (correct direction, small move):
- 95-strike: $26 profit
- 100-strike: $7 profit
- 105-strike: −$68 **loss** (paid too much for a strike that wasn't reached)
- 110-strike: −$100 loss

**Critical insight**: Being right about direction but wrong about strike or magnitude is a common way to lose money on options. The precision of your forecast determines which strike is optimal.

**Different optimization criteria give different answers**:
- **Maximize average return**: choose low-delta OTM options
- **Maximize median return**: choose closer-to-ATM options
- **Maximize probability of profit**: choose deep ITM options

There is no universally correct answer. Match the criterion to your utility function and portfolio context.

---

## Key Lessons

1. **BSM gives the wrong price for directional speculators.** Use the Boness model — it's the right tool for the right question.
2. **True ITM probability (N(d₄)) can be far higher than risk-neutral probability (N(d₂)).** A 10% drift forecast can shift ITM probability from 32% to 45%.
3. **The harder part is being right about direction. The second-harder part is choosing the right strike.** Many traders are right about direction and still lose money by buying the wrong strike.
4. **Strike choice depends on what you're optimizing.** Average return, median return, and win rate all point to different strikes.
5. **Even directional traders must account for the variance premium.** If IV is 10 points above your forecast RV, your options have an embedded drag. You need to be extra right on direction to overcome it.

---

## Connection to Other Chapters

- **Ch. 1**: BSM drift irrelevance was established — Ch. 7 shows when it's irrelevant (market makers) vs when it matters (speculators)
- **Ch. 8**: Strike selection from Ch. 7 feeds directly into strategy selection (long call vs spread vs covered call)
- **Concept note**: See `Concepts/subjective-option-pricing.md` for detailed derivation and worked examples

---

## Source Pages

- Subjective option pricing theory, Boness formulas (Eqs 7.1–7.8): pp. 150–158
- True vs risk-neutral ITM probability: pp. 154–155
- Strike selection examples (Table 7.1): pp. 149–152
- Optimization criteria for strike choice: pp. 158–163
