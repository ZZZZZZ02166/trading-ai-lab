---
hypothesis_number: H31
verdict: inconclusive
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 1120
signals: 88
primary_metric: spread_after_spike_vs_normal_slot
metric_value: 0.0014
---

# H31: ATM Bid-Ask Spread Widens in the 30-Minute Slot Following a Realized Vol Spike

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _ATM Bid-Ask Spread Widens in the 30-Minute Slot Following a Realized Vol Spike_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 1,120 |
| Rows excluded | -923 |
| Exclusion reason | slot pairs without both RV and bid-ask data excluded |
| Final observations tested | 1,120 |
| Signal days | 88 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 1,120 |
| Signals | 88 |
| Primary Metric | spread_after_spike_vs_normal_slot |
| Metric Value | 0.0014 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.0 |
| Reject Threshold | -0.01 |

## Verdict

**🟡 INCONCLUSIVE**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 187/197 days. spike=0.0266 normal=0.0251 diff=0.0014 p=0.8013 n_spike=88 n_normal=1032.

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
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 18, 'metric_value': None, 'verdict': 'insufficient_data'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 21, 'metric_value': None, 'verdict': 'insufficient_data'}} |
| mean_spread_after_spike | 0.0266 |
| mean_spread_after_normal | 0.0251 |
| n_spike_slots | 88 |
| n_normal_slots | 1032 |
| p_value | 0.8013 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=88) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `spread_comparison` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.8013 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `value`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
