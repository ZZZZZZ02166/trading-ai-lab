---
title: How Market Makers Think & What Forces Them to Move
type: synthesis
created: 2026-06-13
sources: 6 books (517 cards) + 83 backtested hypotheses (QQQ, 2024-01 → 2026-04)
status: research deliverable
---

# How Market Makers Think & What Forces Them to Move

> A cross-book synthesis grounded in two evidence layers:
> **(1) Book theory** — 517 knowledge cards from 6 options texts.
> **(2) Empirical verdicts** — this repo's own backtests of 83 hypotheses on QQQ (Jan 2024–Apr 2026), with Phase 3/4 trading-utility tests.
>
> Confidence is graded the way Sinclair grades edges:
> **L3** = multi-book consensus *and* empirical support · **L2** = solid theory or one evidence layer · **L1** = suggestive / flagged caveats.

---

## PART 1 — How a Market Maker Actually Thinks (L3, 4 books agree)

The single most important, repeatedly-stated finding across the library:

> **Market makers do not predict price direction. They are structurally direction-indifferent.**
> - *"Market makers are not predicting direction — they are capturing edge in a vol view vs. market IV."* — OVP pp. 3014–3022
> - *"The goal is risk-neutral profit from providing liquidity, not from predicting price movement."* — Option Market Making pp. 10–13
> - *"Make a profit regardless of whether the market goes up or down."* — OMM pp. 18–19

### The mental model: the Three-Question Framework (OVP 3014–3022)
1. **What does the market think it's worth?** → mid-price → market IV
2. **What do I think it's worth?** → my theoretical value from my *vol* forecast (never a price forecast)
3. **What inventory am I carrying?** → shade quotes to shed risk, not to bet

Everything orbits **fair value** (OMM 23–24, "equal economic advantage"), and income is the **bid-offer edge** captured thousands of times (OMM 10–16), *not* a directional call. Iron rule: **hedge delta immediately; manage the net-greek book; survive the tails** (OVP 3022–3031 — "a market maker who fails to hedge promptly becomes an unintentional speculator").

**Implication for us:** "Thinking like an MM" is not about copying their opinion (they have none). It is about (a) judging whether vol is cheap/rich vs. what's coming, and (b) predicting the hedging they will be *forced* to execute. Those are the two channels below.

---

## PART 2 — What Actually FORCES a Market Maker to Move

These are the factors that compel dealer trading (and therefore move the tape). Each is rated and, where this repo tested it, tagged with the empirical verdict.

| # | Forcing factor | Mechanism | Book source | Empirical check (this repo) | Conf. |
|---|---|---|---|---|---|
| 1 | **Sign of dealer gamma** | Long γ → buy dips / sell rallies (**dampens**, pins). Short γ → buy highs / sell lows (**amplifies**, trends) | TOG 261–263, 267–268 | Vol persistence consistent with γ-hedging (see Part 3) | **L3** (theory) |
| 2 | **Volatility clustering / persistence** | Forced rehedging + autocorrelated vol → today's range predicts tomorrow's | Vol Trading 53; TOG 260–261 | **H15** ρ=0.696, **H39** Hurst=0.83, **H70** 80.5% win — all supported, holdout-robust | **L3** |
| 3 | **Variance premium (IV>RV)** | Crash-hedge demand inflates IV → short-γ dealers collect theta as the premium | Sinclair 183–185; OVP 710–720 | **H1** +1.84 vpts p≈0; **H28** largest in 15–20% IV; **H49** regime-conditional | **L3** |
| 4 | **Expiry / pin risk** | ATM γ explodes near expiry → violent hedging pulls price toward high-OI strikes | TOG 143–144; TOAP 210–213 | **H68** Fridays settle closer to wall (weak, p=0.039) | **L2** |
| 5 | **Rehedge intensity ∝ γ × move × (1/T)** | More gamma / bigger move / less time = more forced trading | OMM 51–52; TOAP 279–281 | implied by H15/H27 U-shape | **L2** |
| 6 | **Leverage effect** | Vol rises *more* on down moves → asymmetric hedging, steep put skew | Vol Trading 53; OVP 3754–3756 | **H22** down-move IV response 0.032 vs up 0.017, p=0.002 | **L3** |
| 7 | **Term-structure stress** | Backwardation = near-term fear → larger next-session range | Sinclair 65–66 | **H44** d=0.55; **H94** p≈0; **H59** Thu→Mon 65.5% | **L2/L3** |
| 8 | **Inventory limits** | Skew quotes to offload risk rather than add | OVP 3014–3022; TOG 322–325 | not directly tested (no quote data) | **L2** |
| 9 | **Information asymmetry / adverse selection** | High IV may mean *the market knows something* — not free premium | OVP 710–720 | **not indexed** — *Trading & Exchanges* has no cards yet | **L1 (gap)** |
| 10 | **Crowding + leverage feedback** | Convergence trades destabilize when leveraged (XIV blow-up) | Sinclair 88–96 | — | **L2** |

> ⚠️ **Honest limit on "dealer gamma moves the stock":** this repo *tried* to test it (**H83**, gamma-weighted OI proximity → next-day range contraction, p=0.0013) but the result explicitly states: *"Gross gamma-weighted OI only — dealer position sign unknown. Do NOT interpret as net dealer gamma or GEX."* So the directional GEX narrative remains **mechanistically sound but empirically unconfirmed here** (we lack signed dealer positioning). Treat it as a model, not a proven fact.

---

## PART 3 — THE BEST HYPOTHESIS (highest combined evidence)

Of 83 tested, the strongest, most coherent, MM-grounded thesis is a **regime-conditional short-variance-premium play, timed by the dealer-hedging tell.** It fuses the four highest-scoring supported hypotheses into one mechanism.

### 🎯 Primary Hypothesis — "Regime-Gated Variance Premium Harvest"

> **Claim:** The variance premium (selling IV, delta-hedged) is *not* uniformly available — it is **largest in the 15–20% IV mid-regime and when IV>HV, collapses (turns negative) in high-IV regimes, and is larger in bull regimes.** First-hour realized vol is the real-time tell for whether dealer gamma-hedging is about to make the day expand.

**Why it's the best — every leg is independently supported in this repo:**

| Leg | Evidence (this repo) | Book mechanism |
|---|---|---|
| Premium is real | **H1**: IV>HV+2pt days → +1.84 vpts vs −0.61, p≈0 | Short γ collects theta (TOG 267–268) |
| Premium is regime-conditional | **H49** (top score **93.8**): high-IV median realized/implied **1.15** (short vol *loses*) vs low-IV **0.88** (short vol *wins*), r=0.289 p≈0 | Don't sell vol when the market knows something (OVP 710–720) |
| Sweet spot is mid-IV | **H28**: VP=+1.06 vpts in 15–20% regime vs −0.39 elsewhere, diff=1.45 | — |
| Bull-regime tilt | **H93**: VP bull +0.022 vs bear −0.102, p=0.007 | Crash demand vs realized calm |
| Real-time hedging tell | **H15** ρ=0.696 / **H48** Cliff's d=0.672 — *holdout-robust* (Phase 3: `supported_trading_useful`) | Rehedge intensity ∝ γ×move (OMM 51–52) |

**The MM logic in one line:** when you sell the regime-gated variance premium you are taking the other side of crash-hedgers as a *short-gamma dealer* — you survive because the premium pays you, and you only do it when realized vol is statistically likely to stay *below* implied (mid-IV, bull, IV>HV), stepping aside in high-IV where **H49 proves realized blows through implied**.

### Operating rules (derived from the verdicts)
- **Enter** delta-hedged short premium (straddle/strangle/condor) when: 15% ≤ IV ≤ 20%, IV > 30-day HV, price > 200-DMA.
- **Stand aside / go long vol** when IV regime is high (H49: realized/implied >1) — this is where naked short vol blows up.
- **Size by the morning tell:** at 10:30, if first-hour RV is *above* its 252-day median (H48), the day will likely expand → reduce short-gamma size or widen strikes. Low first-hour RV → full size.
- **Avoid the tails:** transaction-cost drag (OVP 3292–3301) and the XIV lesson (Sinclair 88–96 — never wrap this in leverage).

---

## PART 4 — Ranked Shortlist of Proven Edges (supported + trading-useful)

Beyond the headline, these survived backtest *and* (where tested) the Phase 3 utility gate:

1. **Volatility persistence** — H15 (ρ=0.696), H39 (Hurst 0.83), H70 (80.5% win), **H-NEW-6 high-range streak (ρ=0.788)**. *Today's vol predicts tomorrow's.* Phase 3: trading-useful.
2. **Intraday vol is U-shaped** — H27 (open+close 1.57× midday, p≈0). Trade range at the edges, mean-reversion at midday.
3. **0DTE straddle: sell at open > sell at noon** — H14 (open P&L 4.83 vs 1.73, p≈0). But H100: large overnight gap → expect expansion → *don't* sell the open straddle that day.
4. **Term-structure signals** — H44 / H94 (backwardation → wider next session), H59 (Thu slope predicts Mon IV, 65.5%), H57 (slope → calendar efficiency).
5. **GARCH beats EWMA** for 20-day RV forecasting — H92 (RMSE ratio 0.90, p≈0). Use GARCH for the vol estimate in the framework above.
6. **Delta-band hedging > fixed-time** — H20 (0.10-delta threshold, ratio 0.888, p≈0). Confirms TOAP 279–281's "rehedge on ~1σ drift."
7. **Calendar spread when front IV > GARCH forward** — H40 (72.8% win, p≈0).
8. **Buy-the-dip 3-session swing** — H74 (64.4% win after −1% days, p=0.005).

### Book-claimed but NOT yet empirically confirmed here (test next)
- **Skew/risk-reversal trade** (TOG 328–329; OVP 3754) — sell rich puts / buy cheap calls, delta-hedged. Maps to H52 (skew→direction), untested in backtest set.
- **Ratio put spread as crash hedge** — Sinclair 183–185 (collects skew premium). No backtest yet.
- **Short put ≡ covered call** (Sinclair 168–170) — execution choice, not an edge per se.

---

## PART 5 — What's Missing (to make this airtight)
1. **Signed dealer positioning** — without it, the GEX/"gamma-flip moves price" story stays a model (H83 caveat).
2. ***Trading & Exchanges* cards** — the order-flow / adverse-selection / manipulation layer is extracted+chunked but **uncarded**; generating its cards would unlock factor #9.
3. **Phase 5 full-chain EOD** — would let us test true net-OI walls (H61/H62 pinning) directly.

---

### Source key
OVP = *Option Volatility & Pricing* (Natenberg) · TOG = *Trading Option Greeks* · OMM = *Option Market Making* · TOAP = *Trading Options as a Professional* · Vol Trading = *Volatility Trading* (Sinclair) · Sinclair = *Positional Option Trading* (Sinclair).
Hypothesis IDs reference `experiments/backtest_summary.json` and `vault/Phase3/`, `vault/Phase4/`.

Related: [[Cross-Book Synthesis]] · [[gamma-theta-delta-neutral-the-complete-volatility-trading-engine]] · [[market-maker-edge-and-theoretical-value]] · [[expiration-risk-pin-risk-assignment-and-automatic-exercise]]
