---
hypothesis_number: H66
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 61
primary_metric: median_upper_shadow_ratio_diff_near_vs_far_wall
metric_value: -0.1143
---

# H66: Call Wall Intraday Resistance: Upper Shadow Ratio Test

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Call Wall Intraday Resistance: Upper Shadow Ratio Test_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires valid call_wall and put_wall; OHLC from daily_series; range >= 0.3% of close |
| Final observations tested | 190 |
| Signal days | 61 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 61 |
| Primary Metric | median_upper_shadow_ratio_diff_near_vs_far_wall |
| Metric Value | -0.1143 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.05 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No resistance ceiling: upper shadow ratio near-wall=0.306 vs far-wall=0.420 (diff=-0.114, p_mw=0.9357 one-sided). n_near=61, n_far=56.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_near_call_wall | 61 |
| n_far_call_wall | 56 |
| pct_near_wall_days | 0.321 |
| median_shadow_ratio_near | 0.3061 |
| median_shadow_ratio_far | 0.4204 |
| p_mannwhitney_one_sided | 0.9357 |
| cliffs_delta | -0.1628 |
| median_abs_giveback_near | 0.0022 |
| median_abs_giveback_far | 0.0044 |
| mirror_put_shadow_near | 0.419 |
| mirror_put_shadow_far | 0.6214 |
| n_near_put_wall | 23 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=61) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 4.6 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **49.6** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
