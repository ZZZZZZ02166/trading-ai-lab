---
hypothesis_number: H69
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 189
signals: 6
primary_metric: mean_next_return_diff_call_heavy_vs_put_heavy
metric_value: -0.0043
---

# H69: Prior-Day Call/Put Volume Imbalance Predicts Next-Session Return Direction (Exploratory)

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Prior-Day Call/Put Volume Imbalance Predicts Next-Session Return Direction (Exploratory)_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 189 |
| Rows excluded | 1 |
| Exclusion reason | Requires daily call_vol and put_vol from param files; log_return from daily_series |
| Final observations tested | 189 |
| Signal days | 6 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 189 |
| Signals | 6 |
| Primary Metric | mean_next_return_diff_call_heavy_vs_put_heavy |
| Metric Value | -0.0043 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No directional signal from call/put volume balance: mean_call=-0.00217 vs mean_put=0.00212 (diff=-0.00429, p_mw=0.8596 one-sided). EXPLORATORY: total EOD volume is not buyer-initiated imbalance. 0DTE put spikes on volatile sessions may make put-heavy = prior-day-volatile. Same-day return diff reported to check contemporaneous vs predictive signal.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_call_heavy | 6 |
| n_put_heavy | 36 |
| mean_call_frac_overall | 0.481 |
| pct_call_heavy | 0.032 |
| pct_put_heavy | 0.19 |
| mean_next_return_call | -0.002172 |
| mean_next_return_put | 0.002121 |
| p_mannwhitney_one_sided | 0.8596 |
| cliffs_delta | -0.2778 |
| same_day_return_diff | -0.012932 |
| exploratory | True |
| threshold_note | Support at p<0.15 (exploratory); total EOD vol ≠ buyer-initiated imbalance |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=6) | 10.9 | 25 | Independence-adjusted count |
| Effect Size | 0.2 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **31.1** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
