# Chapter 1: Options — A Summary
*Positional Option Trading, Euan Sinclair — pp. 25–37*

---

## Chapter Summary

Chapter 1 establishes the theoretical foundation for the entire book. Sinclair argues that BSM should not be treated as a predictive pricing model — it is a **parameterization tool** that converts the market's option prices into a single slowly-changing parameter: implied volatility. The real work of option trading is about that parameter, not about the model itself.

The chapter derives the core equation of delta-hedged option trading, shows the effect of hedging frequency on P/L distribution, and warns that transaction costs are a persistent, underappreciated drain.

---

## Key Concepts

### BSM as Parameterization, Not Prediction
- BSM was originally intended as a predictive valuation model (like quantum mechanics)
- In practice, traders use it **backwards**: they input the market price and solve for implied volatility
- The result is a slowly-varying parameter that makes analysis tractable
- The model is useful precisely because it's used this way — not because it's "correct"

### Why Drift Is Irrelevant for Hedgers
- Put-call parity alone is sufficient to show that drift cannot affect option value
- Dynamic replication enforces this: a market maker who continuously hedges is guaranteed a replication profit regardless of drift
- **Exception**: speculators who don't hedge (covered in Ch. 7 with Boness model)

### The Delta-Hedged P/L Equation (Core of Vol Trading)
The fundamental equation of option trading:

> **Profit/Hedge = ½Γ·S²·(σ_realized² − σ_implied²)·dt**

Derivation:
1. dC ≈ Δ·dS + ½Γ·(dS)² (second-order Taylor expansion)
2. After delta-hedging, directional term cancels: P/L = ½Γ·(dS)²
3. By Itô's lemma: (dS)² ≈ S²·σ_realized²·dt
4. BSM PDE says ½ΓS²σ² = -θ (gamma gain exactly offsets theta decay at fair pricing)
5. **Mismatch** between realized vol and implied vol is where profits come from

This is the single most important equation in the book. All talk of "theta decay" and "gamma scalping" reduces to this relationship.

### IV Surface
- If BSM were correct, all options on an underlying would have one IV
- In reality: a 3D **IV surface** — different IVs across strikes (smile/skew) and maturities (term structure)
- **Fig 1.1 (SPY, Sep 2019)**: Surface slopes upward for lower strikes (put skew) and slightly higher for shorter-dated near-the-money options
- The surface exists for two reasons: (1) BSM is misspecified (fat tails, skew, vol clustering), and (2) supply/demand for individual options creates additional distortions
- The distortions in the surface create edge opportunities (especially selling overpriced OTM puts — covered in Ch. 4)

### Hedging Frequency and P/L Distribution
- **Fig 1.2**: Unhedged short straddle P/L is strongly right-skewed — large losses in the tail, most outcomes small profits
- **Fig 1.3**: Daily delta-hedged short straddle has near-normal P/L distribution — much tighter and symmetric
- **Fig 1.4**: SD of P/L falls from ~$650 (0 hedges) to ~$300 (250 hedges) — **diminishing returns**: first 20–30 hedges eliminate most variance, beyond 50 adds little reduction

### Transaction Cost Warning
- Hedging costs (brokerage, exchange fees, infrastructure) accumulate
- **Table 1.1**: $0.10/share hedging cost reduces average P/L by ~$115 and drops profitable trade % from 44% to 30%
- This is equivalent to misestimating volatility by 2 points — a significant edge erosion
- **Implication**: Aggressive continuous hedging is for market makers. Most positional traders hedge infrequently or not at all.

---

## Key Lessons

1. **Use BSM as a tool, not a truth.** Think in IV terms — compare forecast vol to implied vol, not in raw option price terms.
2. **All option P/L reduces to one equation.** If implied vol ≠ realized vol, you make or lose money proportional to that mismatch × gamma × S².
3. **Structure matters for distribution shape, not for the mean P/L.** Straddle, strangle, condor — all have the same *average* P/L if IV mismatch is identical. Structure changes *how* you get there.
4. **Transaction costs are not trivial.** A 2-point IV edge can be entirely consumed by hedging friction. Size hedging frequency carefully.

---

## Connection to Rest of Book

- The P/L equation (Eq 1.7) is the mathematical foundation for everything in Ch. 4–9
- The IV surface (Fig 1.1) motivates the skew premium discussion in Ch. 4
- Hedging frequency tradeoff leads to the chapter's practical conclusion: positional traders should hedge infrequently, which shifts the emphasis toward structure and vol forecasting rather than continuous delta management
- Ch. 7 revisits when drift *does* matter (speculative/directional traders using Boness model)

---

## Source Pages

- BSM as parameterization: pp. 25–30
- Delta-hedged P/L derivation (Eqs 1.1–1.7): pp. 27–29
- IV surface and Fig 1.1: pp. 31–33
- Hedging frequency Figs 1.2–1.4, Table 1.1: pp. 33–37
