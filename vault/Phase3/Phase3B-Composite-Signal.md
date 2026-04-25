# Phase 3B — Composite Premarket Signal

**Run date:** 2026-04-20
**Script:** `scripts/30_run_phase3b.py`
**Inputs:** 5 non-redundant premarket survivors from Phase 3 redundancy audit
**Outcome tested:** `w150_range` (09:30–11:59 session range, max 2.5h horizon)
**Walk-forward:** train=2024, val=2025, holdout=2026-Q1

---

## Signals Included

All 5 signals are pre-open (prior-day EOD) and point the same direction — higher = wider day expected.

| Signal | Hypothesis | Partial ρ (from audit) | Phase 3 verdict |
|---|---|---|---|
| `iv_spread_30_60` | H44 | 0.433 | too_late_for_style (individually) |
| `range_pct_rank` | H70 | 0.131 | supported_trading_useful |
| `iv_velocity_5d` | H97 | 0.168 | supported_trading_useful |
| `spread_pct_rank` | H99 | 0.144 | supported_trading_useful |
| `ivx_spread_7_30` | H94 | 0.138 | too_late_for_style (individually) |

> H44 and H94 were individually `too_late_for_style` — their peak effect occurs after w210. In the composite, they contribute marginal information but the composite timing gate is tested independently.

---

## Composite Variants

Three composites built, all from rank-normalized [0,1] signals:

| Composite | Signals | Weighting |
|---|---|---|
| EqualWeight-5 | All 5 | Equal (0.20 each) |
| PartialRho-Weighted-5 | All 5 | Weighted by partial ρ from audit |
| EqualWeight-4 | Excl H94 | Equal (0.25 each) — H94 most correlated with H44 |

---

## Results

### EqualWeight-5 (H44 + H94 + H97 + H70 + H99)

**Primary Spearman vs w150_range:** ρ=0.536, p=0.0000, n=562
**Verdict:** `too_late_for_style` | Peak window: `w210` | Early enough: False
**MW top-vs-bottom quartile:** Cliff's d=0.778, p=0.0000, n_high=141, n_low=141

| Split | n | ρ | p |
|---|---|---|---|
| Train | 251 | 0.377 | 0.0003 |
| Val | 250 | 0.661 | 0.0000 |
| Holdout | 61 | 0.287 | 0.0563 |

Window ρ by horizon:
| Window | ρ | p |
|---|---|---|
| w30 | 0.519 | 0.0000 |
| w60 | 0.535 | 0.0000 |
| w120 | 0.537 | 0.0000 |
| w150 | 0.536 | 0.0000 |
| w210 ← peak | 0.541 | 0.0000 |

---

### PartialRho-Weighted-5

**Primary Spearman vs w150_range:** ρ=0.647, p=0.0000, n=311
**Verdict:** `too_late_for_style` | Peak window: `w210` | Early enough: False
**MW top-vs-bottom quartile:** Cliff's d=0.857, p=0.0000, n_high=78, n_low=78

| Split | n | ρ | p |
|---|---|---|---|
| Train | 0 | n/a (burn-in) | — |
| Val | 250 | 0.664 | 0.0000 |
| Holdout | 61 | 0.328 | 0.0364 |

Window ρ by horizon:
| Window | ρ | p |
|---|---|---|
| w30 | 0.645 | 0.0000 |
| w60 | 0.646 | 0.0000 |
| w120 | 0.643 | 0.0000 |
| w150 | 0.647 | 0.0000 |
| w210 ← peak | 0.656 | 0.0000 |

---

### EqualWeight-4 (excl H94)

**Primary Spearman vs w150_range:** ρ=0.511, p=0.0000, n=562
**Verdict:** `supported_trading_useful` | Peak window: `w60` | Early enough: True
**MW top-vs-bottom quartile:** Cliff's d=0.737, p=0.0000, n_high=141, n_low=141

| Split | n | ρ | p |
|---|---|---|---|
| Train | 251 | 0.338 | 0.0007 |
| Val | 250 | 0.642 | 0.0000 |
| Holdout | 61 | 0.284 | 0.0611 |

Window ρ by horizon:
| Window | ρ | p |
|---|---|---|
| w30 | 0.507 | 0.0000 |
| w60 ← peak | 0.516 | 0.0000 |
| w120 | 0.513 | 0.0000 |
| w150 | 0.511 | 0.0000 |
| w210 | 0.509 | 0.0000 |

---

## Quintile Breakdown — PartialRho-Weighted-5

Range of the 2.5h session by composite score quintile (Q1=lowest signal, Q5=highest):

| Quintile | n | Median w150_range | Mean w150_range |
|---|---|---|---|
| Q1 | 63 | 0.00624 | 0.00731 |
| Q2 | 62 | 0.00752 | 0.00774 |
| Q3 | 62 | 0.00952 | 0.01072 |
| Q4 | 62 | 0.01122 | 0.01202 |
| Q5 | 62 | 0.01527 | 0.01756 |

---

## Key Takeaways

### Recommended Composite: EqualWeight-4 (H44 + H97 + H70 + H99)

**`supported_trading_useful`** — the only composite whose peak effect (w60) falls within the 2.5h morning window.

The PartialRho-Weighted-5 and EqualWeight-5 both have peak at w210 — the effect keeps growing past the morning horizon — because H94's weight pushes the combined score toward the later-peaking IVX signal. Removing H94 shifts the peak to w60 while retaining ρ=0.511 and Cliff's d=0.737.

**Counterintuitive detail:** H44 (iv_spread_30_60) is individually `too_late_for_style` — but in EqualWeight-4, combined with H70, H97, and H99 (all of which peak at or before w150), it contributes marginal signal without dragging the composite peak past w150.

### Quintile Gradient (PartialRho-Weighted-5 — highest ρ, shown for reference)

The weighted-5 composite produces a clean monotonic gradient even though it's formally `too_late_for_style`:
- **Q1 vs Q5 median range:** 0.00624 vs 0.01527 — a **2.4× difference** in morning range
- Gradient is monotonic Q1→Q5 with no inversions

This confirms the signals genuinely stratify the day's activity level. The `too_late_for_style` verdict means the *additional* effect past 12:59 is marginal — not that the within-window effect is meaningless.

### Practical Use (EqualWeight-4)

Compute each morning before open:
1. Rank-normalize `iv_spread_30_60`, `range_pct_rank`, `iv_velocity_5d`, `spread_pct_rank` each to [0,1]
2. Average the four — this is the pre-open vol regime score
3. **High score (Q4–Q5):** expect an active, wide-range morning — size up, widen targets, don't fade early
4. **Low score (Q1–Q2):** expect compression — reduce size, tighten targets, gap-fill setups more viable
5. Cross-reference with H99 caution flag: `spread_pct_rank > 0.75` → add friction to any entry regardless of composite level

---

## Phase 4 Continuation

Phase 4 intraday factor research (scripts 31 and 32) continues from this composite baseline.
See: `vault/Phase4/Phase4-Intraday-Factor-Research.md`

Key additions in Phase 4:
- **High-Range Streak (H-NEW-6):** ρ=0.788, Cliff's d=0.948 — pair with this composite for pre-open regime assessment (streak=duration, composite=level)
- **RV Surprise Ratio (H-NEW-2):** intraday confirmation at 10:00
- **fh_rv × Gap 4-cell (H-NEW-5):** conditional precision at 10:30
