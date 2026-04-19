---
hypothesis_number: H29
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 187
signals: 187
primary_metric: pnl_pct_1400_minus_1200
metric_value: -0.0839
---

# H29: 0DTE Straddle P&L Percentage Is Higher When Sold at 14:00 vs. 12:00

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _0DTE Straddle P&L Percentage Is Higher When Sold at 14:00 vs. 12:00_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 187 |
| Rows excluded | 10 |
| Exclusion reason | days without 12:00 and 14:00 ATM snapshots excluded |
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
| Primary Metric | pnl_pct_1400_minus_1200 |
| Metric Value | -0.0839 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.0 |
| Reject Threshold | -0.05 |

## Verdict

**❌ REJECTED**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 187/197 days. mean_1400=0.3834 mean_1200=0.4673 diff=-0.0839 p=0.0399 n=187.

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
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -0.047, 'verdict': 'inconclusive'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -0.2554, 'verdict': 'rejected'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': 0.0647, 'verdict': 'inconclusive'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': -0.2444, 'verdict': 'rejected'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': 0.0376, 'verdict': 'inconclusive'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.0693, 'verdict': 'inconclusive'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': -0.1356, 'verdict': 'rejected'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 18, 'metric_value': -0.1312, 'verdict': 'rejected'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': -0.1081, 'verdict': 'rejected'}} |
| mean_pnl_pct_1200 | 0.4673 |
| mean_pnl_pct_1400 | 0.3834 |
| n_paired_days | 187 |
| p_value | 0.0399 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=187) | 24.2 | 25 | Independence-adjusted count |
| Effect Size | 3.4 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 5.0 | 20 | FDR-within-family p: 0.1795 · IQ: strong |
| Stability | 6.7 | 10 | Measured (consistency: 67%) |
| **Phase 1 Score** | **59.3** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `value`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
