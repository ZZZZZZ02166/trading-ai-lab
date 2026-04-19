---
hypothesis_number: H14
verdict: supported
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 190
signals: 190
primary_metric: open_vs_noon_pnl_diff
metric_value: 3.0974
---

# H14: 0DTE Straddle Sold at Market Open Has Higher Expected P&L Than One Sold at Noon

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** [[0DTE Straddle Sold at Market Open Has Higher Expected P&L Than One Sold at Noon]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 190 |
| Rows excluded | 7 |
| Exclusion reason | days without open+noon snapshots excluded |
| Final observations tested | 190 |
| Signal days | 190 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 190 |
| Primary Metric | open_vs_noon_pnl_diff |
| Metric Value | 3.0974 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.5 |
| Reject Threshold | -0.5 |

## Verdict

**✅ SUPPORTED**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 190/197 days. open=4.828 noon=1.731 diff=3.097 p=0.0000.

## Extra Metrics

| Metric | Value |
|--------|-------|
| contract_selection_method | intraday_atm_approx_small_strike_ladder |
| strike_ladder_width | 3 |
| exact_chain_intraday | False |
| minute_type | MINUTE_5 |
| n_days_attempted | 197 |
| n_days_with_ladder_data | 190 |
| pct_days_with_data | 0.964 |
| intraday_endpoint_used | single-equity-optionsymbol-rawiv |
| is_combined | True |
| monthly_batch_mode | True |
| full_window_combined_from_month_batches | True |
| months_combined | ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9'] |
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 6.0152, 'verdict': 'supported'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 3.7665, 'verdict': 'supported'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': 2.2315, 'verdict': 'supported'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 1.4509, 'verdict': 'supported'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': 2.7888, 'verdict': 'supported'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 1.8664, 'verdict': 'supported'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': 3.3674, 'verdict': 'supported'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 19, 'metric_value': 3.5722, 'verdict': 'supported'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 2.8843, 'verdict': 'supported'}} |
| mean_open_pnl | 4.8285 |
| mean_noon_pnl | 1.7311 |
| mean_diff | 3.0974 |
| p_value | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=190) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **81.5** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `value`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
