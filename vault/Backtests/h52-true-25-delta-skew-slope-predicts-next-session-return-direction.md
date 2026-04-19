---
hypothesis_number: H52
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 190
signals: 38
primary_metric: mean_return_diff_high_skew_vs_low_skew
metric_value: 0.0038
---

# H52: True 25-Delta Skew Slope Predicts Next-Session Return Direction

**❌ REJECTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _True 25-Delta Skew Slope Predicts Next-Session Return Direction_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires both 25-delta call and put contracts with valid IV; 1-day forward shift for next return |
| Final observations tested | 190 |
| Signal days | 38 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 38 |
| Primary Metric | mean_return_diff_high_skew_vs_low_skew |
| Metric Value | 0.0038 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | -0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No directional bias from 25-delta skew: mean_high=0.00440 vs mean_low=0.00060 (diff=0.00380, p=0.9823)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_high_skew | 38 |
| n_low_skew | 38 |
| mean_return_high_skew | 0.004404 |
| mean_return_low_skew | 0.000601 |
| cliffs_delta | 0.2798 |
| p_mannwhitney | 0.9823 |
| u_stat | 924.0 |
| median_skew_all_dates | 0.0331 |
| mean_skew_all_dates | 0.0391 |
| skew_q20 | 0.0242 |
| skew_q80 | 0.046 |
| n_dates_with_25d_data | 190 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=38) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.2 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.9823 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.1** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
