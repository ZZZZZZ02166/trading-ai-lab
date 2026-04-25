# Phase 4 — Intraday Factor Research: Options/Vol Signals for Discretionary Model

**Run date:** 2026-04-20
**Scripts:** `scripts/31_run_phase4a.py` (EOD + 1m), `scripts/32_run_phase4b.py` (intraday chains)
**Data:** daily_series.parquet + Databento 1m bars (563 days, Jan 2024–Apr 2026) + 5-min option chains (317 days, Jan 2024–Dec 2025)
**Confirmed baseline from Phases 1–3B:** fh_rv (H15/H48), Gap magnitude (H100), Premarket composite (EqualWeight-4), Spread caution (H99)

> **Critical constraint:** These signals augment a discretionary model built on chart structure — liquidity sweeps, BOS, order blocks, FVGs, breaker blocks, equilibrium, HTF key levels. None of those concepts are quantified here. The signals provide probability context (day type, regime) and confirmation/caution filters. Chart reading remains the entry mechanism.

---

## Section 1 — Full Factor Table

### Category A: Already Confirmed — Integration Guidance

| Factor | Role | Timing | Key Stat | Integration |
|---|---|---|---|---|
| fh_rv (H15/H48) | CONFIRMATION + partial EARLY WARNING | 10:30 full; 9:45 partial | ρ=0.696 (vs aw_range) | High fh_rv → size up; low fh_rv → skip/reduce. At 9:45, w15_range already warns of explosive open |
| Gap magnitude (H100) | EARLY WARNING | 9:31 | Large gap: 4% fill rate; small gap: 28% fill rate | Large gap → expect continuation, don't fade; small gap → fade viable |
| Premarket composite EW-4 (H44+H97+H70+H99) | EARLY WARNING | Pre-open | ρ=0.511, Cliff's d=0.737, peak=w60 | Q4–Q5 → active day, more setups; Q1–Q2 → compression, fewer setups |
| Spread percentile H99 | CAUTION ONLY | Pre-open | ρ=0.300 (range only); zero direction | spread_pct_rank > 0.75 → add 20-30% friction to sizing; no directional content |

### Category B: New Factors — EOD/1m Stack (Script 31 results)

| Factor | Hypothesis | Verdict | Key Stat | Role |
|---|---|---|---|---|
| Opening Range Efficiency (B1) | H-NEW-1 | **rejected** | ρ=+0.559 (wrong sign) | — |
| RV Surprise Ratio (B2) | H-NEW-2 | **supported_trading_useful** | ρ=0.376 vs aw, 0.587 vs w150 | BOTH |
| Term Structure Velocity (B3) | H-NEW-3 | **supported_trading_useful** (weak) | ρ=0.134, peak=w120 | EARLY WARNING (pre-open) |
| Prior-Close Vol → Opening Range (B4) | H-NEW-4 | **too_late_for_style** | ρ=0.500 (vs w30), 0.627 (vs fh_rv); peak=w210 | — |
| fh_rv × Gap Magnitude 4-cell (B5) | H-NEW-5 | **supported_trading_useful** | Cliff's d=0.712 max vs min cell | CONFIRMATION at 10:30 |
| High-Range Streak (B6) | H-NEW-6 | **supported_trading_useful** | ρ=0.788, partial ρ=0.782 vs H70 | EARLY WARNING (pre-open) |

### Category C: New Factors — Intraday Chains (Script 32 results)

| Factor | Hypothesis | Verdict | Key Stat | Note |
|---|---|---|---|---|
| Intraday IV Velocity 30-min (C1) | C1 | **inconclusive** | ρ=−0.045, p=0.35 | Signal construction flaw — see detail |
| Ultra-early IV Velocity 15-min (C1b) | C1b | **inconclusive** | ρ=−0.064, p=0.22 | Same flaw as C1 |
| Near-ATM Call Volume Accumulation (C3) | C3 | **inconclusive** (WF limited) | ρ=−0.396, inverse direction | WF train n=19; notable inverse result |

### Category D: Not Tested — Low Priority

| Factor | Why skipped |
|---|---|
| VIX/VIX3M ratio | High overlap with confirmed H44/H94; marginal addition unclear |
| OI pin risk by strike | Needs OI data by strike — not in current stack |
| Cross-asset gap alignment (NQ vs ES) | High complexity, uncertain marginal gain |
| Afternoon skew steepening (13:00+) | Outside 2.5h morning window scope |

---

## Section 2 — Priority Groups

### HIGHEST PRIORITY — Use Now

**Already confirmed (Category A):**
- fh_rv (H15/H48) — dominant signal at 10:30; also partial early warning at 9:45
- Gap magnitude (H100) — simplest, cleanest at 9:31
- Premarket composite EW-4 — pre-open regime dial
- Spread caution H99 — sizing filter only

**New, fully confirmed:**
- H-NEW-6 (High-Range Streak) — ρ=0.788, remarkable regime signal; operational immediately
- H-NEW-5 (fh_rv × Gap 4-cell) — adds conditional precision to H15/H100 combination at 10:30

### MEDIUM PRIORITY — Use with caveats

- H-NEW-2 (RV Surprise Ratio) — ρ=0.376 vs aw; strong confirmation at 9:31; MW test unreliable (9 low-surprise days)
- H-NEW-3 (Term Structure Velocity) — weak (ρ=0.134) but consistent across all splits including holdout; useful as a regime-flip flag

### NOT ACTIONABLE

- H-NEW-1 (Opening Range Efficiency) — rejected (sign reversal)
- H-NEW-4 (Prior-Close Vol → Opening) — effect is real (ρ=0.500) but peaks at w210; signal is available pre-open but its predictive edge accumulates all day — the morning piece is noise relative to the total effect
- C1/C1b (Intraday IV Velocity) — signal construction flaw; stale pre-open IV makes 98% of days look like "rising IV"
- C3 (Call Volume Accumulation) — inverse of hypothesis; walk-forward unverifiable (train n=19 after burn-in)

---

## Section 3 — High-Priority Factor Deep Dives

### 1. fh_rv (H15/H48) — Dual Role

**What it measures:** Annualized realized vol from 1-min bars over 09:30–10:29 (full), or 09:30–09:44 (partial early warning).

**Stats:** Full signal ρ=0.696 vs aw_range, Cliff's d=0.672. All splits consistent including holdout (ρ=0.558).

**Confirmation scenario:** HTF setup visible at 10:15 near a key level. Check fh_rv: if high (above 252d median), take full size — the vol is there to deliver range. If low (below median), reduce size or skip — the afternoon range is likely limited.

**Early warning (9:45):** At 9:45, `w15_range` (first 15 min) is already ~25-40% correlated with final fh_rv. If the opening 15 minutes are explosive (large w15_range), you can raise conviction for the 10:00–10:30 setup forming — vol is already proving itself. This is noisy but directionally correct.

**Chart integration:** High fh_rv + BOS at HTF key level → maximum aggression on the next pullback. Low fh_rv + BOS → wait for retest, reduce to half size, tighten targets.

---

### 2. Gap Magnitude (H100) — Cleanest Pre-Chart Signal

**What it measures:** |open_0930 – prev_close| / prev_close (available at 9:31).

**Stats:** Large gap (>0.55%) → 4% fill rate in 30 min. Small gap (<0.55%) → 28% fill rate. Fisher p<0.0001. Secondary: ρ=0.285 vs w30_range.

**Confirmation scenario:** Chart setup points long, gap opened up and is large → continuation is confirmed before price confirms. Don't look for short-side setups; gap is working in your direction.

**Early warning:** Large gap BEFORE any chart structure forms → bias established at 9:31. You know to only look for continuation setups that session, which saves time filtering out fade attempts in the wrong direction.

**Chart integration:** Large gap up + HTF bullish structure → first pullback to nearby OB/FVG is the entry. Large gap down + bearish structure → same logic inverted. Small gap → both fade and continuation are viable; wait for chart to decide.

---

### 3. Premarket Composite EW-4 (H44+H97+H70+H99) — Day Expansion Dial

**What it measures:** Equal-weighted rank-average of 4 pre-open signals: IV term structure slope, IV 5-day velocity, prior-day range rank, EOD spread rank.

**Stats:** ρ=0.511 vs w150_range, peak=w60, Cliff's d=0.737 (Q4+Q5 vs Q1+Q2). Full quintile gradient: Q1 median=0.00624, Q5 median=0.01527 (2.4× ratio).

**Confirmation:** Q4–Q5 composite + chart setup → trade full size with maximum targets. The market is in expansion mode — your targets should reflect it.

**Early warning (pre-open):** Q1–Q2 composite → compression likely → skip marginal setups entirely that session. Only take the sharpest, cleanest liquidity sweeps or BOS at the highest timeframe levels. Reduce number of trades.

**Chart integration:** Changes the NUMBER of setups you take, not which setups you take. On Q5 days, a mediocre-quality BOS at an HTF OB is still worth taking. On Q1 days, even a high-quality setup may not deliver enough range — wait for only the cleanest.

---

### 4. Spread Caution (H99) — Sizing Filter

**What it measures:** Rolling 60d rank of (ask–bid)/close, prior-day EOD.

**Stats:** ρ=0.300 vs range (caution confirmed). Direction: ρ=−0.014 (nil). Caution days (>p75): 25% of sample.

**Role:** Purely a sizing/premium filter. No directional content. On spread_pct_rank > 0.75 days, options premium is elevated and fills will be wider. Reduce size 20–30% regardless of composite level.

---

### 5. High-Range Streak (H-NEW-6) — Regime Membership Signal

**What it measures:** Number of consecutive days where w150_range > 252d rolling median. Resets to 0 when streak breaks.

**Stats:** ρ=0.788 vs w150_range, n=563. Walk-forward: train=0.713, val=0.848, holdout=0.658 — all excellent. Partial ρ=0.782 controlling for H70 (not redundant). MW streak≥3 vs streak=0: Cliff's d=0.948 — near-perfect separation. Median range on streak≥3 days: 0.01390 vs streak=0 days: 0.00671 (2.1× difference).

**How to use:** Compute every morning before open.
- streak ≥ 5: you are deep in a high-vol regime. Expect a wide day. Trade aggressively, use max targets.
- streak ≥ 1: still in regime. Hold your targets, don't over-tighten.
- streak = 0 (just broke): regime reset. Today could be quiet or could be the first day of a new regime. Default to conservative sizing until confirmed by fh_rv at 10:30.
- streak = 0 for 5+ days: persistently quiet regime. Compression likely. Only take the highest-quality setups.

**Critical distinction from H70 (range_pct_rank):** H70 measures where TODAY's prior-day range sits in the 252-day distribution (level). H-NEW-6 measures HOW LONG you've been above median (duration). Both contribute independently (partial ρ=0.782) — streak duration captures regime persistence that a single-day percentile cannot. They should both be used.

---

### 6. RV Surprise Ratio (H-NEW-2) — Vol Pricing Error Signal

**What it measures:** w30_range / (iv_30d_prior / √(252×13)) — did the opening 30 minutes deliver more or less range than what IV implied?

**Stats:** ρ=0.376 vs aw_range (10:30–11:59), ρ=0.587 vs w150_range (full morning). Walk-forward vs aw: train=0.261, val=0.481, holdout=0.243. Consistent positive direction.

**Caveat:** Signal median=1.60, p25=1.23 — meaning the median day delivers 60% MORE range than IV implies. Nearly all days have surprise>1, so the MW (high vs low) comparison has only 9 low-surprise days. The binary MW is unreliable. Use the continuous Spearman interpretation only.

**Confirmation scenario:** At 10:00, compute surprise_ratio from the past 30 min. If surprise_ratio > 2.0 (realized vol strongly exceeded implied), the options market was underpriced — expect continued range expansion. Setups that form at 10:00–10:15 near HTF structure have higher conviction. If surprise_ratio < 1.0 (rare), vol is compressing intraday — reduce conviction.

**Early warning:** At 9:31 (one bar), a large w1_range relative to IV gives a noisy early read. Not reliable enough on one bar alone — confirm at 9:45–10:00.

---

### 7. Term Structure Velocity (H-NEW-3) — Regime Flip Signal

**What it measures:** Day-over-day change in iv_30d – iv_60d (term structure slope). Positive = slope steepening (backwardation increasing); negative = slope flattening.

**Stats:** ρ=0.134 vs w150_range, p=0.0004. Peak at w120 (within window). Walk-forward: train=0.112 (p=0.037), val=0.118 (p=0.061), holdout=0.255 (p=0.006). Consistent direction across all splits.

**Important:** This is a WEAK signal on its own (ρ=0.134). Its value is as a regime-flip alert, not a standalone predictor.

**Confirmation scenario:** Overnight slope steepened into backwardation (positive ts_velocity) → options market is pricing increasing near-term risk → combine with composite score to raise regime confidence.

**Early warning:** A sudden flip to backwardation when the prior week was in contango signals a vol regime transition. On these days, raise attention for BOS/sweep setups in the first hour — the options market is sensing something before it appears in price structure.

---

### 8. fh_rv × Gap Magnitude 4-cell (H-NEW-5) — Conditional Precision

**What it measures:** 4 cells from {high/low fh_rv (>/<252d median)} × {large/small gap (>/<0.40% median)}.

| Cell | n | Median aw_range |
|---|---|---|
| High fh_rv + Large gap | 167 | 0.00721 |
| High fh_rv + Small gap | 114 | 0.00703 |
| Low fh_rv + Large gap | 114 | 0.00412 |
| Low fh_rv + Small gap | 167 | 0.00395 |

**MW max vs min cell:** Cliff's d=0.712, p<0.0001

**Key insight:** fh_rv is the dominant driver. When fh_rv is high, the afternoon range is roughly 0.00710 regardless of whether the gap was large or small. When fh_rv is low, afternoon range drops to ~0.00400 regardless of gap size. Gap magnitude adds marginal precision within the fh_rv split but doesn't rescue a low-fh_rv day.

**Practical use:** At 10:30, check fh_rv alone first. If high → trade actively. If low → skip or dramatically reduce. The gap check is useful as a secondary confirmation when fh_rv is borderline (near the median).

---

## Section 4 — Hypotheses with Results

### H-NEW-1 (B1): Opening Range Efficiency → Afternoon Range
**Signal:** w30_range / rolling_252d_median(w30_range) — how much of the expected daily vol arrived in the first 30 min
**Outcome:** aw_range (10:30–11:59)
**Expected:** Negative ρ (low efficiency → vol hasn't come yet → more afternoon range)
**Result:** ρ=+0.559 (POSITIVE — OPPOSITE SIGN). Walk-forward consistent: train=0.428, val=0.650, holdout=0.409.
**Verdict: rejected**

**Interpretation:** The hypothesis assumed vol front-loading leaves less for the afternoon. The data shows the opposite: high early vol days remain active all morning. High efficiency = high-vol regime, and high-vol regimes persist. This is actually a confirmation that vol regimes are sticky — not a reason to fade early activity. The signal is not useful as an "afternoon range predictor" but confirms H-NEW-6's regime interpretation.

---

### H-NEW-2 (B2): RV Surprise Ratio → Range Persistence
**Signal:** w30_range / (iv_30d_prior / √(252×13))
**Outcome:** aw_range (primary), w150_range (secondary)
**Walk-forward (aw_range):** full=0.376, train=0.261, val=0.481, holdout=0.243
**Walk-forward (w150_range):** full=0.587 (stronger vs full morning)
**Verdict: supported_trading_useful**

---

### H-NEW-3 (B3): Term Structure Velocity → Range Expansion
**Signal:** Δ(iv_30d – iv_60d) day-over-day
**Outcome:** w150_range
**Walk-forward:** full=0.134, train=0.112, val=0.118, holdout=0.255
**Peak window:** w120 (within 2.5h horizon)
**Verdict: supported_trading_useful (weak)**

---

### H-NEW-4 (B4): Prior-Close Vol → Opening Range (NOT gap fill)
**Signal:** Realized vol from 15:30–15:59 prior day (available pre-open)
**Outcomes:** w30_range (ρ=0.500), fh_rv (ρ=0.627)
**Walk-forward vs w30_range:** train=0.428, val=0.604, holdout=0.402
**Walk-forward vs fh_rv:** train=0.613, val=0.688, holdout=0.370
**Peak window:** w210 — effect keeps growing all day
**Verdict: too_late_for_style**

**Note:** The signal itself is available pre-open (prior-day EOD) but predicts the LEVEL of activity, not just the morning piece. Because vol regimes persist for days, prior-close vol essentially predicts today's entire session — not specifically the morning. The opening range relationship (ρ=0.500) is real but the signal is already captured by the streak counter (H-NEW-6, partial ρ=0.782) and premarket composite. Not independently actionable.

**Distinction from H24 (rejected):** H24 tested `late_rv → gap_fill_30/60` (Fisher test, rejected, p=0.278/0.910). This tested `late_rv → w30_range + fh_rv` (opening range, different outcome). The opening range relationship is genuine; H24's gap-fill relationship was not.

---

### H-NEW-5 (B5): fh_rv × Gap Magnitude → Afternoon Range
**Signal:** 4-cell grid {high/low fh_rv} × {large/small gap}
**Outcome:** aw_range (10:30–11:59)
**Result:** Max cell (high×large) median=0.00721; min cell (low×small) median=0.00395; Cliff's d=0.712
**Verdict: supported_trading_useful**

---

### H-NEW-6 (B6): High-Range Streak → Next-Day Expansion
**Signal:** Consecutive days with w150_range > rolling_252d_median(w150_range)
**Outcome:** w150_range
**Walk-forward:** full=0.788, train=0.713, val=0.848, holdout=0.658
**Partial ρ controlling for H70:** 0.782 — not redundant
**MW streak≥3 vs streak=0:** Cliff's d=0.948 — median 0.01390 vs 0.00671 (2.1× range)
**Verdict: supported_trading_useful**

---

### C1: Intraday IV Velocity (9:30→10:00) → Afternoon Range
**Signal:** (IV_10:00 – IV_9:30) / IV_9:30 for near-ATM call
**Outcome:** aw_range
**Result:** ρ=−0.045, p=0.35 — not significant
**Verdict: inconclusive**

**Root cause of failure:** The 9:30 bar in the intraday chain data uses stale pre-open IV — the `calcTimestamp` for the 9:30 row shows the prior day's closing calculation time (e.g., "2024-01-10 16:02:01" for a 2024-01-11 trading day). This means `IV_9:30` is effectively prior-day EOD IV, not a live 9:30 market quote. The velocity from 9:30→10:00 overwhelmingly captures the jump from stale pre-open pricing to live market pricing, not genuine intraday IV movement. Result: 98.1% of days have "rising" IV with a median velocity of +52% — nearly zero variation in direction, making the signal useless for prediction.

**To fix this in future:** Use the 9:35 or 9:40 bar as the opening reference (after the market-open repricing settles). Measure velocity from 9:40→10:00 or 9:45→10:00 rather than from 9:30. The 5-minute data exists; re-running with a shifted reference is feasible.

---

### C1b: Ultra-early IV Velocity (9:30→9:45)
**Result:** ρ=−0.064, p=0.22 — same stale-IV flaw as C1
**Verdict: inconclusive**

---

### C3: Near-ATM Call Volume Accumulation → Range
**Signal:** Total call option volume by 10:00 minus volume at 9:30, rank-normalized rolling 252d
**Outcome:** aw_range
**Result:** ρ=−0.396 (INVERSE), p<0.0001. MW top Q vs bot Q: Cliff's d=−0.612. Top Q median=2.30, bot Q median=4.42.
**Walk-forward:** train n=19 (burn-in kills 2024), val ρ=−0.435
**Verdict: inconclusive (walk-forward insufficient)**

**Inverse signal finding:** High early call volume correlates with LESS afternoon range. The directional hypothesis (high volume → expansion) was wrong. The inverse makes sense: high early call volume reflects a lot of activity happening in the opening 30 min — if the market moved hard early (generating volume), the afternoon tends to quiet down. This could also reflect dealers gamma-hedging settling down after an active open.

The inverse finding is real (ρ=−0.396, confirmed in val=−0.435) but cannot be walk-forward validated because the 252-day normalization period consumes all 2024 data (train n=19). With more data or a shorter normalization window, this would be testable.

---

## Section 5 — Final Judgment

### Most likely to improve discretionary trading (rank order):

**1. High-Range Streak (H-NEW-6)** — the most powerful new finding. ρ=0.788, Cliff's d=0.948 for streak≥3 vs streak=0. Available pre-open. Captures regime membership better than any single-day signal. Compute streak count every morning; it directly calibrates your aggression level for the day.

**2. fh_rv (H15/H48)** — already confirmed; the dominant intraday signal. At 10:30, no other confirmed signal comes close in strength (ρ=0.696, consistent across all splits). Use the partial 9:45 version for early warning when aggressive.

**3. Premarket composite EW-4** — pre-open probability dial. Pair with H-NEW-6 streak for a dual pre-open regime read: streak captures duration, composite captures level via 4 independent signals.

**4. fh_rv × Gap 4-cell (H-NEW-5)** — adds conditional precision at 10:30. fh_rv is the dominant driver; gap adds marginal information when fh_rv is near the median. Most useful for borderline decisions about whether to take or skip a setup.

**5. RV Surprise Ratio (H-NEW-2)** — useful confirmation at 10:00. The continuous signal (not the MW) is the right interpretation: the higher the ratio, the more the morning has exceeded IV's implied range, and the more likely continued expansion. Most useful when ratio > 2.0.

**6. Term Structure Velocity (H-NEW-3)** — weak but consistent. Worth including in pre-open checklist as a regime-flip warning. If overnight term structure flipped to backwardation after a period of contango, attention up.

**7. Gap magnitude (H100)** — simplest and cleanest at 9:31. Large gap → don't fade. Operational immediately.

### What didn't work and why:

- **Opening Range Efficiency (H-NEW-1):** Hypothesis reversed. Vol front-loading does NOT predict quieter afternoons — high-vol regimes persist. Useful as a regime confirmation but not as a fade signal.
- **Prior-Close Vol (H-NEW-4):** Effect is real but accumulates all day (peak=w210). Not actionable as a morning-specific signal; already captured by streak and composite.
- **Intraday IV Velocity (C1/C1b):** Stale pre-open IV in the 9:30 bar kills the signal. Fixable with a 9:40 or 9:45 reference bar, but not tested.
- **Call Volume Accumulation (C3):** Inverse direction, walk-forward unverifiable. Worth revisiting with more data or a shorter normalization window.

### Recommended pre-open checklist (operational):

1. **Range streak:** How many consecutive above-median days? Set aggression level.
2. **Premarket composite EW-4:** High or low regime? Set number of setups you'll attempt.
3. **Term structure velocity:** Any overnight flip to backwardation? If yes, raise attention for first-hour moves.
4. **Spread percentile (H99):** > 0.75? If yes, reduce size 20-30% all day.
5. **Gap at open (H100):** Large or small? Sets fade-vs-continue bias from 9:31.

### Recommended intraday confirmation (10:00–10:30):

1. **RV Surprise Ratio:** At 10:00, is realized vol exceeding IV? Raises conviction.
2. **fh_rv (H15):** At 10:30, is first-hour vol above/below 252d median? Primary go/no-go for afternoon range plays.
3. **4-cell (H-NEW-5):** fh_rv + gap cell → refined estimate of afternoon range available.

---

## Data Coverage Notes

| Script | Data period | Holdout available? |
|---|---|---|
| 31_run_phase4a.py | Jan 2024 – Mar 2026 | Yes (2026-Q1) |
| 32_run_phase4b.py | Jan 2024 – Dec 2025 | No (chain data ends Dec 2025) |
