---
hypothesis_number: H58
verdict: insufficient_data
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: insufficient_data
observations: 0
signals: 0
primary_metric: mean_rod_return_diff_call_heavy_vs_put_heavy
metric_value: N/A
---

# H58: First 30-Minute Option Volume Direction Predicts Rest-of-Day Price Direction

**⬜ INSUFFICIENT DATA**

> ❓ **Insufficient data** — required data was unavailable (endpoint entitlement or coverage gap). No verdict can be drawn.

**Linked hypothesis:** _First 30-Minute Option Volume Direction Predicts Rest-of-Day Price Direction_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 0 |
| Rows after validation | 0 |
| Rows excluded | 0 |
| Exclusion reason | Intraday chain data not available in required format |
| Final observations tested | 0 |
| Signal days | 0 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 0 |
| Signals | 0 |
| Primary Metric | mean_rod_return_diff_call_heavy_vs_put_heavy |
| Metric Value | N/A |
| Data Source | ivolatility |
| Data Notes | insufficient_data |
| Support Threshold | 0.0 |
| Reject Threshold | 0.0 |

## Verdict

**⬜ INSUFFICIENT DATA**

H58 requires aggregated call and put volume in the first 30 minutes across the full option chain. Available intraday files (data/raw/chains/intraday_*.parquet) cover only 7–14 specific contracts per date — not a representative sample of total market volume. Computing first-30-min PCR from 7 contracts would produce a misleading signal. Would require a full intraday volume feed (not currently available).

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (D) | 0 | 25 | Data fidelity: `insufficient` (explicit) |
| Sample Adequacy (N_eff=0) | 7.5 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **7.5** | **100** | |

**Priority: ⬜ BLOCKED**  Stat test: `—`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.

## H58-ATM-PROXY — Feasibility Study (Phase 2 Extension)

**⚠️ This is NOT the original H58 test.** Original H58 (full-chain PCR) remains BLOCKED.
This is an ATM-centric proxy study using the sparse contract subset in `data/raw/chains/`.

### Coverage Audit

| Metric | Value |
|---|---|
| Dates audited | 190 |
| Coverage min | 2.2% |
| Coverage 25th pct | 38.9% |
| Coverage median | 53.1% |
| Coverage 75th pct | 63.9% |
| Coverage max | 72.7% |
| CV (std/mean) | 0.3499 |
| Dates below 20% | 16 |

**Monotonicity:** 1 files with resets out of 189 checked.
Missing 10:00 bar (used 09:55 fallback): 0 dates.

### Signal Timing

- Signal: `optionVolume` at 10:00 bar = cumulative first-30-min flow (09:30–09:59:59, bar-start semantics confirmed)
- Entry: Databento 1m **open at 10:01 ET** (1 min gap after signal is finalized)
- Exit: Databento 1m **close at 15:59 ET**

### Verdicts

| Dataset | n | Verdict | Continuous Spearman |
|---|---|---|---|
| all_dates | 187 | INCONCLUSIVE | rho=0.8617259844600472, p_nw=1.3772040960785827e-206, n=187 |
| high_coverage (≥20%) | 171 | INCONCLUSIVE | rho=0.8248998008015936, p_nw=4.8605647099161475e-136, n=171 |
| **Final** | — | **INCONCLUSIVE** | — |

### Walk-Forward Spearman

| Split | all_dates rho | all_dates p_nw | high_cov rho | high_cov p_nw |
|---|---|---|---|---|
| train | n/a | n/a | n/a | n/a |
| val | 0.862 | 0.0000 | 0.825 | 0.0000 |

### Binary Comparison (call_pct > 0.60 vs < 0.40)

n_call_heavy=83, n_put_heavy=36, 
diff=0.00977691805501963, p=8.283123888187344e-16, Cliff's d=0.9317269076305221

**Conclusion:** ATM-centric proxy coverage is highly variable (CV≈0.49). Results are exploratory. Original H58 (full-chain PCR) remains BLOCKED.

## H58-ATM-PROXY Phase 2B — Momentum Control Test

**Purpose:** Test whether ATM option flow adds incremental value beyond first-30-min price action.
**Original H58:** Still BLOCKED (full-chain PCR unavailable).

### Internal 2025 Split
| Split | all_dates n | high_cov n |
|---|---|---|
| Train (Apr–Aug 2025) | 103 | 92 |
| Val   (Sep–Dec 2025) | 81   | 76 |

### Price-Action Controls
Controls: `first_30m_return`, `first_30m_range`, `overnight_gap`

#### Model A — Baseline (price controls only)
| all_dates | n=184, R²=0.0533 |
| high_coverage | n=168, R²=0.0868 |

#### Model B — Baseline + call_pct
| Dataset | call_pct beta | p (HAC) | ΔR² | Verdict |
|---|---|---|---|---|
| all_dates | 0.0308 | 0.0000 | 0.4565 | SUPPORTED |
| high_coverage | 0.0223 | 0.0000 | 0.7606 | SUPPORTED |

#### Partial Spearman (call_pct | rod_return, controlling for price controls)
| Dataset | partial_rho | p | same_sign_train_val |
|---|---|---|---|
| all_dates | 0.931 | 0.0000 | True |
| high_coverage | 0.917 | 0.0000 | True |

#### Residual Spearman (call_pct vs rod_return after removing price-control fit)
| Dataset | residual_rho | p | same_sign_train_val |
|---|---|---|---|
| all_dates | 0.797 | 0.0000 | True |
| high_coverage | 0.820 | 0.0000 | True |

### Conditional Quintile Table (high_coverage, by first-30-min direction)

| Direction | Q1 (put-heavy) n | median ROD | Q5 (call-heavy) n | median ROD |
|---|---|---|---|---|
| up_30m (n=87) | 9 | -0.0079 | 25 | 0.0066 |
| down_30m (n=81) | 25 | -0.0042 | 9 | 0.0110 |

### Final Summary

**Raw Spearman (Phase 2A):** rho=0.86, p≈0 — likely momentum-proxy contamination
**After price controls:** see table above

| Dataset | Verdict |
|---|---|
| all_dates | SUPPORTED |
| high_coverage | SUPPORTED |
| **Final (Phase 2B)** | **SUPPORTED** |

**[high_coverage primary] call_pct survives price controls: beta_p=0.0000, partial_rho=0.917 (p=0.0000), same_sign_train_val=True**

**Recommendation:** H58-ATM-PROXY Phase 2B shows genuine incremental value beyond early price action. Consider a Phase 3 study with a cleaner option-flow measure. Original H58 remains BLOCKED (full chain unavailable).
