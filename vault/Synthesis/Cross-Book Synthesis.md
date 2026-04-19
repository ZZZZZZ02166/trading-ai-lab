# Cross-Book Synthesis — Options Trading Library
*Updated: April 2026 — 4 books with study notes*

---

## Books Included

| Book | Author | Focus |
|------|--------|-------|
| Trading Option Greeks 2e | Dan Passarelli | Practitioner Greeks, delta-neutral, vol trading |
| Trading Options as a Professional | James B. Bittman | Market maker mechanics, synthetics, arbitrage, position Greeks |
| Option Market Making | Allen Jan Baird | Market maker operations, risk management, position archetypes |
| Positional Option Trading | Euan Sinclair | Quantitative edge, variance premium, Kelly sizing |

---

## Where All Four Books Agree

### 1. The Greeks Are Non-Negotiable

Every book dedicates substantial space to delta, gamma, theta, vega, and rho. All four authors agree: you cannot trade options professionally without understanding each Greek and how it changes dynamically. Static Greek snapshots are insufficient — every author emphasizes that Greeks evolve as market conditions change.

**Best explanation**: Bittman (*Trading Options as a Professional*, Ch. 4) provides the most systematic visual treatment — graphs of each Greek vs. stock price, time, and volatility for all three moneyness states. Use this as the reference for understanding Greek shapes.

### 2. Implied Volatility Is the Central Variable

All four books recognize IV as the primary unknown in options pricing. Selling options is selling IV; buying options is buying IV. Direction matters less than most retail traders believe — the IV bet dominates most option P/L outcomes.

**Best explanation**: Passarelli (*Trading Option Greeks 2e*, Ch. 14) provides the most practical vol chart pattern framework. Sinclair (*Positional Option Trading*) provides the most rigorous empirical basis — the variance premium.

### 3. The Gamma-Theta Tradeoff Is Inescapable

Every book states this explicitly. Long options = pay theta, collect gamma. Short options = collect theta, pay gamma. No strategy escapes this tradeoff — it is the structural tension of every option position.

**Best explanation**: Passarelli's formulation is the most memorable: "You cannot have positive theta without accepting negative gamma." Bittman's position Greek tables make it quantitative. Both are worth reading together.

### 4. Delta-Neutral Trading Isolates Volatility

Bittman, Passarelli, and Baird all describe delta-neutral trading as the mechanism for separating the vol bet from the directional bet. The mechanics are identical across books: hedge option delta with stock, rebalance as gamma drifts delta, profit from gamma scalps vs. theta paid.

**Best explanation**: Bittman (*Trading Options as a Professional*, Ch. 8) distinguishes most clearly between speculators (hold for days/weeks) and market makers (hold for minutes/hours). Passarelli (*Trading Option Greeks 2e*, Ch. 13) covers gamma scalping mechanics in most detail.

### 5. Put-Call Parity Constrains All Prices

Passarelli's "A put is a call; a call is a put" and Bittman's Chapter 5 on synthetics both derive all six synthetic positions from put-call parity. Baird's market-making risk profiles rely on the same foundation. All books agree: covered call = synthetic short put. Same risk. No additional protection.

---

## Where Books Differ or Offer Complementary Views

### On the Purpose of Options Trading

| Book | Primary Audience | Goal |
|------|-----------------|------|
| Bittman | Market makers, institutional traders | Provide liquidity; capture bid-ask spread |
| Baird | Floor market makers | Risk-neutral spread income; hedge immediately |
| Passarelli | Retail/semi-professional traders | Express vol views; manage directional exposure |
| Sinclair | Quantitative speculators | Systematically harvest variance premium; size with Kelly |

**Key divergence**: Baird and Bittman emphasize immediate delta hedging as non-negotiable discipline. Sinclair argues that disciplined speculative positions (with a quantified edge) are valid. These perspectives are not contradictory — they apply to different trader types.

### On Volatility Forecasting

| Book | Approach |
|------|---------|
| Bittman | Use IV vs. HV comparison; three-part forecast |
| Passarelli | Vol chart pattern analysis (9 patterns) |
| Baird | HV vs. IV comparison; fat-tail awareness |
| Sinclair | Econometric models; variance premium is primary edge |

Sinclair is the most rigorous here — he provides formal statistical tests for whether a vol edge exists. Passarelli is the most actionable — his 9-pattern chart framework is directly usable in trading decisions.

### On Position Sizing

Only Sinclair addresses position sizing rigorously. His fractional Kelly framework (25–50% of raw Kelly estimate) is the most principled sizing approach in the vault. Bittman and Passarelli both advocate dollar-denominated risk limits (max loss per Greek unit) but don't formalize a sizing framework.

**Recommendation**: Use Sinclair's Kelly framework for sizing; use Bittman/Passarelli's Greek-based limits for intra-trade risk management.

### On Skew

All four books mention volatility skew (OTM puts > OTM calls in IV). Differences in emphasis:
- Bittman: describes skew descriptively; notes OTM puts are structurally expensive
- Passarelli: mentions skew in context of volatility charts
- Baird: covers skew as a sixth Greek ("skew risk") that must be managed independently
- Sinclair: treats skew as a source of exploitable premium; provides empirical evidence that OTM puts are overpriced

**Best explanation of trading skew**: Sinclair. **Best explanation of hedging skew**: Baird.

---

## Which Book to Read First

| Reader Profile | Start With |
|---------------|-----------|
| Learning Greeks from scratch | Bittman or Passarelli |
| Understanding market maker mechanics | Bittman (more structured) or Baird (more operational) |
| Trading Greek-based strategies | Passarelli (most example-driven) |
| Quantitative/systematic vol trading | Sinclair |
| Deep mathematical theory | Option Volatility and Pricing (Natenberg) — not yet in vault |

---

## Most Important Topics Across All Books

| Topic | Best Book(s) |
|-------|-------------|
| Greeks reference (all five) | Bittman Ch. 4 |
| Gamma-theta tradeoff | Passarelli Ch. 5 |
| Put-call parity and synthetics | Bittman Ch. 5 / Passarelli Ch. 2,6 |
| Arbitrage mechanics | Bittman Ch. 6 / Baird |
| Vol chart patterns | Passarelli Ch. 14 |
| Delta-neutral gamma scalping | Bittman Ch. 8 / Passarelli Ch. 13 |
| Variance premium empirics | Sinclair |
| Position sizing | Sinclair |
| Position risk management | Bittman Ch. 10 |
| Market maker operations | Baird / Bittman Ch. 9 |

---

## Key Themes by Topic

### Implied vs. Realized Volatility

All four books agree: IV tends to overstate realized vol (variance premium). Sinclair quantifies this most rigorously — it is the most consistent edge in options. Passarelli's chart patterns describe the observable patterns of this divergence. Bittman provides the mechanics for expressing this view via delta-neutral positions.

### Risk Management

All four books advocate for:
- Pre-defined maximum acceptable loss before entry
- Dollar-denominated risk limits (not just percentage)
- Dynamic re-evaluation of Greeks as conditions change
- Discipline in hedging (Baird and Bittman most emphatic)

Sinclair adds: stops change the return distribution shape in ways traders rarely anticipate — they are not simply "insurance."

### The Professional Edge

Bittman and Baird define edge as bid-ask spread capture (market maker view). Passarelli defines edge as IV mispricing vs. realized vol (speculative view). Sinclair provides the most rigorous empirical basis: variance premium, skew premium, and earnings-event IV behavior.

All four agree: without an identifiable edge, risk management is just managing toward a slower loss.
