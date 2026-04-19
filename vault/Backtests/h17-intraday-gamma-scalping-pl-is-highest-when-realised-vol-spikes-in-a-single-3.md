---
hypothesis_number: H17
verdict: inconclusive
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 187
signals: 106
primary_metric: mean_gamma_pnl_spike_vs_flat
metric_value: 0.2827
---

# H17: Intraday Gamma Scalping P&L Is Highest When Realised Vol Spikes in a Single 30-Minute Window

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** [[Intraday Gamma Scalping P&L Is Highest When Realised Vol Spikes in a Single 30-Minute Window]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 187 |
| Rows excluded | 10 |
| Exclusion reason | days without full bar data or option ladder excluded |
| Final observations tested | 187 |
| Signal days | 106 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 187 |
| Signals | 106 |
| Primary Metric | mean_gamma_pnl_spike_vs_flat |
| Metric Value | 0.2827 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.0 |
| Reject Threshold | -0.5 |

## Verdict

**🟡 INCONCLUSIVE**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 187/197 days. spike=-4.0923 flat=-4.3750 p=0.5668 n_spike=106 n_flat=81.

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
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 1.8353, 'verdict': 'inconclusive'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -1.2037, 'verdict': 'rejected'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': -1.1564, 'verdict': 'rejected'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': 0.4424, 'verdict': 'inconclusive'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': -1.482, 'verdict': 'rejected'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -2.4198, 'verdict': 'rejected'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': -0.0691, 'verdict': 'rejected'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 18, 'metric_value': 2.1754, 'verdict': 'inconclusive'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': -1.0402, 'verdict': 'rejected'}} |
| mean_pnl_spike_days | -4.0923 |
| mean_pnl_flat_days | -4.375 |
| n_spike_days | 106 |
| n_flat_days | 81 |
| p_value | 0.5668 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=106) | 24.2 | 25 | Independence-adjusted count |
| Effect Size | 11.3 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.8502 · IQ: strong |
| Stability | 3.3 | 10 | Measured (consistency: 33%) |
| **Phase 1 Score** | **58.9** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `value`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
