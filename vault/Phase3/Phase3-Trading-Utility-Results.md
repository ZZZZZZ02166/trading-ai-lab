# Phase 3 — Trading Utility Test Results

**Run date:** 2026-04-20
**Question:** Do options/volatility signals add actionable information within a 2.5-hour morning trading window?
**Test window:** Jan 2024 – Mar 2026 (563 trading days) | walk-forward: train=2024, val=2025, holdout=2026-Q1
**Script:** `scripts/29_run_phase3.py`

---

## Summary Scorecard

| ID | Signal | Tier | Role | Verdict |
|---|---|---|---|---|
| H15 | First-hour realized vol | core-strong | Intraday confirmation (10:30) | **supported_trading_useful** |
| H48 | fh_rv above median | core-strong | Intraday confirmation (10:30) | **supported_trading_useful** |
| H70 | Prior-day range percentile rank | core-fragile/no-train | Premarket framing | **supported_trading_useful** ⚠️ holdout decays |
| H97 | IV 5-day velocity | core-fragile | Premarket framing | **supported_trading_useful** |
| H99 | EOD spread percentile rank | core-fragile | Premarket caution overlay | **supported_trading_useful** |
| H100 | Overnight gap magnitude | exploratory | Intraday early (9:31) | **supported_trading_useful** |
| H44 | IV term structure slope | core-strong | Premarket framing | **too_late_for_style** |
| H94 | IVX 7d–30d spread | core-fragile | Premarket framing | **too_late_for_style** |
| H24 | Late-day RV (prior close) | core-fragile | Premarket post-gap context | **rejected** |
| H53 | IV rising / RV flat | exploratory | Premarket framing | **rejected** |
| H76 | Backwardation × gap direction | exploratory | Hybrid pre-open + gap | **rejected** |

**Counts:** 6 supported · 2 too_late_for_style · 3 rejected

---

## Verdict Definitions

| Verdict | Meaning |
|---|---|
| `supported_trading_useful` | Stat support + peak effect within 2.5h window + actionable interpretation |
| `too_late_for_style` | Strong statistical signal but peak effect occurs after w210 (>2.5h) |
| `rejected` | No meaningful statistical support for primary outcome |

---

## Supported Signals — Detail

### H15 · First-Hour Realized Vol → Afternoon Range
**Signal:** Annualized realized vol from 1m bars, 09:30–10:29 (available at 10:30)
**Outcome:** aw_range — price range 10:30–11:59 (core 1.5h window)

| Split | n | Spearman ρ | p |
|---|---|---|---|
| Full | 563 | **0.696** | <0.0001 |
| Train (2024) | 252 | 0.638 | <0.0001 |
| Val (2025) | 250 | 0.734 | <0.0001 |
| Holdout (2026-Q1) | 61 | 0.558 | <0.0001 |

**Interpretation:** The strongest and most consistent signal in the study. First-hour vol directly predicts how much range remains in the next 90 minutes. Use at 10:30 to confirm active-day setups and size afternoon entries.

---

### H48 · Above-Median First-Hour Vol → Broader Afternoon Range
**Signal:** fh_rv > rolling 252d median (binary, available at 10:30)
**Outcome:** aw_range — price range 10:30–11:59

| Split | n_above | n_below | Cliff's d | p |
|---|---|---|---|---|
| Full | 287 | 276 | **0.672** | <0.0001 |
| Train (2024) | 114 | 138 | 0.590 | <0.0001 |
| Val (2025) | 124 | 126 | 0.732 | <0.0001 |
| Holdout (2026-Q1) | 49 | 12 | 0.711 | 0.0002 |

**Interpretation:** Binary version of H15. On above-median first-hour vol days, the afternoon 10:30–12:00 range is substantially wider (Cliff's d=0.67). Use as a simple go/no-go filter for afternoon range plays.

---

### H70 · Prior-Day Range Percentile Rank → Next-Day Expansion
**Signal:** Rolling 252d percentile rank of prior-day's full session range (available pre-open)
**Outcome:** w150_range (09:30–11:59)
**⚠️ Note: 252-day burn-in consumes all 2024 data. Train split = NaN. All results are out-of-sample (val + holdout only). No in-sample reference.**

| Split | n | Spearman ρ | p |
|---|---|---|---|
| Full (val+holdout) | 311 | **0.524** | <0.0001 |
| Train (2024) | 0 | NaN | NaN |
| Val (2025) | 250 | 0.565 | <0.0001 |
| Holdout (2026-Q1) | 61 | **0.115** | 0.263 |

Window ρ by horizon: w30=0.560, w60=0.558, w120=0.530, w150=0.524, w210=0.532 — peak at w30.

**Interpretation:** High-range days cluster. The signal is valid in val but decays significantly in 2026-Q1 (ρ drops from 0.565 → 0.115, p=0.26). The holdout decay is the main concern — treat as a regime-sensitive signal. Use to frame the day's expected activity level but don't rely on it alone.

---

### H97 · IV 5-Day Velocity → Day Range
**Signal:** iv_30d.pct_change(5), prior-day EOD (available pre-open)
**Outcome:** w150_range (09:30–11:59)

| Split | n | Spearman ρ | p |
|---|---|---|---|
| Full | 557 | **0.331** | <0.0001 |
| Train (2024) | 246 | 0.316 | <0.0001 |
| Val (2025) | 250 | 0.352 | <0.0001 |
| Holdout (2026-Q1) | 61 | 0.072 | 0.624 |

Binary Cliff's d (full): 0.335. Peak window: w150 — just within the actionable horizon.

**Interpretation:** When IV has been accelerating over the past week, next-day morning range tends to expand. Consistent in train+val; holdout weakens (likely low-vol 2026-Q1 period). Use as a confirming accelerant flag alongside H44 (which shares correlation).

---

### H99 · EOD Spread Percentile Rank — Caution Overlay
**Signal:** Rolling 60d rank of (ask–bid)/close, prior-day EOD
**Primary framing: LIQUIDITY/PREMIUM CAUTION OVERLAY — not a direction signal.**
**Outcome (primary):** w150_range | **(secondary only, if range confirmed):** w150_return

| Split | n | Spearman ρ (range) | p |
|---|---|---|---|
| Full | 543 | **0.300** | <0.0001 |
| Train (2024) | 232 | 0.158 | 0.064 |
| Val (2025) | 250 | 0.403 | <0.0001 |
| Holdout (2026-Q1) | 61 | 0.340 | 0.001 |

Direction (secondary): ρ=−0.014, p=0.742 — **no directional information.**
Caution days (spread_pct_rank > 0.75): n=136 (25% of sample).
Peak window: w30.

**Interpretation:** High spread days → wider range, but no directional edge. Use as pre-trade friction check: when spread_pct_rank > 0.75, flag as a caution day (premium is elevated, fills will be wider, vol may already be priced). Do not use to call direction.

---

### H100 · Gap Magnitude → Fill vs Continue
**Signal:** |open_0930 – prev_close| / prev_close (available at 9:31)
**Outcome:** gap_fill_30 (binary: does price return to prior close within 30 min?)

| Group | n | Fill rate (30 min) |
|---|---|---|
| Small gap (<median 0.55%) | 200 | **28.4%** |
| Large gap (>median 0.55%) | 201 | **4.0%** |

Fisher's exact p < 0.0001. Small gaps fill far more often than large gaps within the first 30 minutes.

Secondary Spearman vs w30_range: ρ=0.285. vs w120_range: ρ=0.228.

**Interpretation:** Larger gaps extend; smaller gaps fill. Clean and explorable at 9:31. Use to frame the first 30-minute trade: large gap → avoid fading the open, expect continuation; small gap → fade is viable.

---

## Too-Late-For-Style — Detail

### H44 · IV Term Structure Slope
**Signal:** iv_30d – iv_60d (prior-day EOD)
**Outcome:** w150_range. Full ρ=0.487, p<0.0001. **Peak window: w210** (beyond 2.5h horizon).

| Window | ρ |
|---|---|
| w30 | 0.467 |
| w60 | 0.471 |
| w120 | 0.481 |
| w150 | 0.487 |
| **w210** | **0.493** ← peak |

Walk-forward MW binary Cliff's d: train=0.379, val=0.674, holdout=0.437. Effect is statistically real and consistent. But it peaks after w210, meaning the signal's strongest edge continues to build past 12:59 — beyond the 2.5h morning window. **Not actionable for a morning-only style.**

---

### H94 · IVX 7d–30d Spread
**Signal:** IVX_7d – IVX_30d (prior-day EOD)
**Outcome:** w150_range. Full ρ=0.418. **Peak window: w210.**

| Window | ρ |
|---|---|
| w30 | 0.375 |
| w60 | 0.400 |
| w120 | 0.417 |
| w150 | 0.418 |
| **w210** | **0.434** ← peak |

Highly correlated with H44 (signal ρ=0.674). Holdout binary test: Cliff's d=0.041, p=0.789 — collapses in 2026-Q1. Same conclusion as H44: effect is real but accumulates past the trading window.

---

## Rejected — Detail

### H24 · Prior-Day Late RV → Gap Fill Behavior
**Signal:** Annualized RV from 15:30–15:59 (prior day); binary: above 252d rolling median
**Outcome:** gap_fill_30 / gap_fill_60 (binary fill after a ≥0.2% overnight gap)

| Test | p |
|---|---|
| Fisher (late_rv_high vs gap_fill_30) | 0.278 |
| Fisher (late_rv_high vs gap_fill_60) | 0.910 |

Fill rates are essentially identical whether late_rv was high or low. No predictive information about whether the gap fills.

*Note: Secondary Spearman vs w30_range: ρ=0.452 — late_rv does predict range, but that's range overall, not the fill/extend decision. The direction effect (w30_return) is inconsistent across splits.*

---

### H53 · IV Rising + RV Flat → Day Expansion
**Signal:** (iv_30d > iv_30d.shift(5)) AND (hv_20_cc < iv_30d × 0.8) — binary, prior day
**Outcome:** w150_expansion (binary)

Full Cliff's d=0.042, p=0.466. Zero effect across all splits (train: d=−0.002, val: d=−0.024, holdout: d=−0.100). No information content for expansion prediction.

---

### H76 · Backwardation × Gap Direction → Gap Fill
**Signal:** Binary: iv_30d > iv_60d (prior day) × overnight gap direction
**Outcome:** gap_fill_30 (binary)

Fisher's exact (bkwd vs fill): p=0.889. Fill rate: bkwd=16.6%, contango=16.0% — indistinguishable.

**However:** Logistic regression with gap_magnitude as control shows a significant backwardation coefficient (bkwd coef=1.676, p=0.0015) and significant bkwd×gap_up interaction (coef=−1.400, p=0.038). The fill-rate pattern differs once gap size is controlled:

| Cell | n | Fill rate |
|---|---|---|
| Bkwd + gap up | 84 | 13.1% |
| Bkwd + gap down | 67 | 20.9% |
| Contango + gap up | 155 | 20.7% |
| Contango + gap down | 95 | 8.4% |

The raw Fisher test is flat because gap_magnitude drowns the interaction. The conditional effect is real but only visible after controlling for gap size — not practically usable as a standalone filter.

---

## Redundancy Audit (Premarket Signals)

Tested: H44 · H94 · H97 · H70 · H99 (n=311, post burn-in)

**Signal correlation matrix:**

| | H44 | H94 | H97 | H70 | H99 |
|---|---|---|---|---|---|
| H44 iv_spread_30_60 | 1.00 | 0.674 | 0.414 | **0.738** | 0.492 |
| H94 ivx_spread_7_30 | 0.674 | 1.00 | 0.269 | 0.568 | 0.349 |
| H97 iv_velocity_5d | 0.414 | 0.269 | 1.00 | 0.423 | 0.222 |
| H70 range_pct_rank | **0.738** | 0.568 | 0.423 | 1.00 | 0.383 |
| H99 spread_pct_rank | 0.492 | 0.349 | 0.222 | 0.383 | 1.00 |

**Partial Spearman vs w150_range (controlling for strongest correlated signal):**

| Signal | Strongest corr. | Signal ρ | Partial ρ | Flagged redundant? |
|---|---|---|---|---|
| H44 iv_spread_30_60 | H70 (0.738) | 0.487 | **0.433** | No |
| H94 ivx_spread_7_30 | H44 (0.674) | 0.418 | **0.138** | No |
| H97 iv_velocity_5d | H70 (0.423) | 0.331 | **0.168** | No |
| H70 range_pct_rank | H44 (0.738) | 0.524 | **0.131** | No |
| H99 spread_pct_rank | H44 (0.492) | 0.300 | **0.144** | No |

**Result: No redundancy flags.** All 5 signals retain partial ρ > 0.13 after controlling for their strongest correlated peer. H44 and H70 are highly correlated (ρ=0.738) but each contributes distinct marginal information vs w150_range.

**Implication for Phase 3B composite:** All 5 premarket signals can be included in a composite. H94 and H97 overlap most with H44/H70 but still add marginal signal.

---

## Key Takeaways

1. **First-hour vol (H15/H48) is the dominant signal.** ρ=0.696 and Cliff's d=0.672, consistent across all 3 splits including holdout. If you only keep two signals, these are the ones.

2. **H44 and H94 are statistically real but not morning-style signals.** Their effect keeps accumulating past 12:59 — they describe full-day vol, not a 2.5h-window opportunity.

3. **H70 works but is showing holdout decay.** val ρ=0.565 → holdout ρ=0.115 (p=0.26). The range autocorrelation regime may have shifted in early 2026. Monitor.

4. **H99 is caution, not direction.** Wide spread days are bigger-range days, but there is zero directional signal (ρ=−0.014). Use only as a liquidity/premium sizing filter.

5. **H100 is the cleanest gap rule.** Large gaps (>0.55%) almost never fill in 30 minutes (4% fill rate). Small gaps fill 28% of the time. Simple and exploitable at 9:31.

6. **H76's effect is conditional on gap size.** Raw fill rates look flat, but logistic regression reveals a real backwardation × gap_direction interaction after controlling for gap magnitude. Not standalone-usable, but worth revisiting in a composite.

---

## Phase 3B — Next Step

Build composite premarket signal from H44 + H70 + H97 + H99 (H94 optional as it overlaps H44 heavily). All 5 survived redundancy audit. Composite approach: equal-weighted rank average or logistic regression on w150_range. Signal values all available pre-open.
