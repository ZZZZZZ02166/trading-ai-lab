---
hypothesis_number: H13
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 187
signals: 187
primary_metric: u_shape_open_minus_mid
metric_value: -0.0884
---

# H13: SPX Intraday IV Follows a U-Shape: Higher at Open and Close, Lower at Midday

**❌ REJECTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

> ⚠️ **Instrument note**: Original hypothesis references SPX. This test was run on **QQQ** as an adaptation. QQQ tracks Nasdaq-100; SPX-specific microstructure effects may differ.

**Linked hypothesis:** [[SPX Intraday IV Follows a U-Shape: Higher at Open and Close, Lower at Midday]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 187 |
| Rows excluded | 10 |
| Exclusion reason | days without full open/mid/close IV buckets excluded |
| Final observations tested | 187 |
| Signal days | 187 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 187 |
| Signals | 187 |
| Primary Metric | u_shape_open_minus_mid |
| Metric Value | -0.0884 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.0 |
| Reject Threshold | -0.5 |

## Verdict

**❌ REJECTED**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 187/197 days. open=0.211 mid=0.299 close=0.357. open-mid=-0.0884 p=0.0000; close-mid=0.0583 p=0.0000.

## Extra Metrics

| Metric | Value |
|--------|-------|
| contract_selection_method | intraday_atm_approx_small_strike_ladder |
| strike_ladder_width | 3 |
| exact_chain_intraday | False |
| minute_type | MINUTE_5 |
| n_days_attempted | 197 |
| n_days_with_ladder_data | 187 |
| pct_days_with_data | 0.949 |
| intraday_endpoint_used | single-equity-optionsymbol-rawiv |
| is_combined | True |
| monthly_batch_mode | True |
| full_window_combined_from_month_batches | True |
| months_combined | ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9'] |
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -0.2546, 'verdict': 'rejected'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -0.0877, 'verdict': 'rejected'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': -0.0761, 'verdict': 'rejected'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': -0.0549, 'verdict': 'rejected'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': -0.0415, 'verdict': 'rejected'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -0.058, 'verdict': 'rejected'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': -0.0815, 'verdict': 'rejected'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 18, 'metric_value': -0.0876, 'verdict': 'rejected'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': -0.0537, 'verdict': 'rejected'}} |
| mean_iv_open | 0.2107 |
| mean_iv_mid | 0.2991 |
| mean_iv_close | 0.3574 |
| open_minus_mid | -0.0884 |
| close_minus_mid | 0.0583 |
| p_open_vs_mid | 0.0 |
| p_close_vs_mid | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=187) | 23.1 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `intraday_pattern` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **60.1** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `open_vs_mid`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
