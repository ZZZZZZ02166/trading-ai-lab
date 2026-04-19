---
hypothesis_number: H20
verdict: supported
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 190
signals: 135
primary_metric: threshold_vs_fixed_hedge_cost_ratio
metric_value: 0.8878
---

# H20: Intraday Delta Hedging at Fixed 0.10-Delta Threshold Outperforms Fixed-Time Hedging for Short Straddles

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** [[Intraday Delta Hedging at Fixed 0.10-Delta Threshold Outperforms Fixed-Time Hedging for Short Straddles]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 190 |
| Rows excluded | 7 |
| Exclusion reason | days without delta time series excluded |
| Final observations tested | 190 |
| Signal days | 135 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 135 |
| Primary Metric | threshold_vs_fixed_hedge_cost_ratio |
| Metric Value | 0.8878 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.9 |
| Reject Threshold | 1.1 |

## Verdict

**✅ SUPPORTED**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 190/197 days. ratio=0.888 p=0.0000.

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
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.9387, 'verdict': 'inconclusive'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.8964, 'verdict': 'supported'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': 0.9142, 'verdict': 'inconclusive'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 0.8502, 'verdict': 'supported'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': 0.8685, 'verdict': 'supported'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.871, 'verdict': 'supported'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': 0.8867, 'verdict': 'supported'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 19, 'metric_value': 0.8747, 'verdict': 'supported'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 0.8914, 'verdict': 'supported'}} |
| mean_ratio | 0.8878 |
| pct_days_threshold_cheaper | 0.711 |
| p_value | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=135) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 11.2 | 20 | Family: `cost_ratio` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **72.7** | **100** | |

**Priority: 🟡 WATCHLIST**  Stat test: `value`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
