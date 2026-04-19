---
hypothesis_number: H25
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 190
signals: 10
primary_metric: 1_minus_var_ratio_reversal_vs_non
metric_value: -39.0351
---

# H25: 0DTE Straddle P&L Variance Is Lower When Sold After a Large Morning Move Has Partially Reverted

**❌ REJECTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** [[0DTE Straddle P&L Variance Is Lower When Sold After a Large Morning Move Has Partially Reverted]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 190 |
| Rows excluded | 7 |
| Exclusion reason | days without 11:30 straddle snapshot excluded |
| Final observations tested | 190 |
| Signal days | 10 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 10 |
| Primary Metric | 1_minus_var_ratio_reversal_vs_non |
| Metric Value | -39.0351 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.0 |
| Reject Threshold | -0.1 |

## Verdict

**❌ REJECTED**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 190/197 days. ratio=40.035 metric=-39.035 Levene p=0.0000 (10 reversal, 180 non).

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
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 19, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': None, 'verdict': 'insufficient_data'}} |
| n_reversal_days | 10 |
| n_non_reversal_days | 180 |
| var_reversal | 120.1979 |
| var_non_reversal | 3.0023 |
| var_ratio | 40.0351 |
| levene_p | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=10) | 12.8 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **22.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: [0.0000, 0.0063] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
