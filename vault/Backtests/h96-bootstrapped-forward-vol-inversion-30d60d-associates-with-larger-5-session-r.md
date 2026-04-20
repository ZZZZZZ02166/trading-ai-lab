---
hypothesis_number: H96
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 560
signals: 186
primary_metric: median_range_5d_diff_inverted_vs_normal
metric_value: 0.0043
---

# H96: Bootstrapped Forward Vol Inversion (30d→60d) Associates with Larger 5-Session Realized Range

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Bootstrapped Forward Vol Inversion (30d→60d) Associates with Larger 5-Session Realized Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 560 |
| Rows excluded | 5 |
| Exclusion reason | iv_30d/iv_60d required + 5-day forward range window |
| Final observations tested | 560 |
| Signal days | 186 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 560 |
| Signals | 186 |
| Primary Metric | median_range_5d_diff_inverted_vs_normal |
| Metric Value | 0.0043 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_range_5d=0.00427 (inverted=0.01571, normal=0.01144), p_mannwhitney=0.0000, n_inverted=186, n_normal=374, pct_inverted=0.332.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_5d_inverted | 0.015714 |
| median_range_5d_normal | 0.011441 |
| pct_inverted | 0.3321 |
| n_inverted | 186 |
| n_normal | 374 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=186) | 23.6 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **60.6** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.


## Phase 2 — Intraday Robustness (Batch 2)

**Verdict: INCONCLUSIVE**
Redundancy gate failed: H96 REDUNDANT with H44: agreement_rate=100.0% — signals nearly identical in practice

**H44 Redundancy Gate: FAILED — H44 agreement rate = 100.0%**
The fwd_vol_30_60 / iv_30d signal is algebraically nearly equivalent to the iv_30d > iv_60d (H44) signal. On 100% of days, H96 (fwd_inverted) and H44 (backwardation) agree. This is because fwd_vol_30_60 = sqrt((iv_60d²×60 − iv_30d²×30)/30) < iv_30d iff iv_60d > iv_30d in almost all practical parameterizations. H96 adds no distinct information beyond H44.

### Underlying Effect (pre-gate; strong but not H96-specific)

n_inverted=191 (33.8% of days), n_normal=374

### Walk-Forward Spearman (fwd_ratio → 5d range)

| Split | rho | p_nw | n |
|---|---|---|---|
| full | -0.539 | 0.0000 | 560 |
| train | -0.274 | 0.0205 | 252 |
| val | -0.715 | 0.0000 | 250 |
| holdout | -0.343 | 0.0318 | 58 |

**Note:** rho is negative (−0.539) because lower fwd_ratio = more inverted = higher next range. Effect is real and consistent, but is entirely attributable to H44.

### Binary MW: Inverted vs Normal (5d range)

| Split | diff | p | Cliff's d | n_inv | n_norm |
|---|---|---|---|---|---|
| full | 0.0043 | 0.0000 | 0.556 | 186 | 374 |
| train | 0.0019 | 0.0000 | 0.323 | 71 | 181 |
| val | 0.0070 | 0.0000 | 0.742 | 84 | 166 |
| holdout | 0.0018 | 0.0391 | 0.271 | 31 | 27 |

### Quintile Gradient (fwd_ratio quintiles)

| Quintile | n | Median 5d Range |
|---|---|---|
| Q1 | 112 | 0.017109 |
| Q2 | 112 | 0.014601 |
| Q3 | 112 | 0.012146 |
| Q4 | 112 | 0.011417 |
| Q5 | 112 | 0.010193 |

**Conclusion:** H96 is RETIRED as a distinct signal. The underlying range-prediction effect is real and consistent across all splits, but belongs to H44 (iv_30d > iv_60d backwardation). H44's coverage should be extended to use the continuous fwd_ratio as an input, rather than maintaining H96 as a separate hypothesis. Do not promote H96 to Phase 3.
