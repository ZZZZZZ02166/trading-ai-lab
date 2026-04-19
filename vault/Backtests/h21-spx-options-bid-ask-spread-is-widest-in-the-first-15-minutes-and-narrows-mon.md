---
hypothesis_number: H21
verdict: inconclusive
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 189
signals: 144
primary_metric: spread_open_minus_midday_pct
metric_value: 0.0292
---

# H21: SPX Options Bid-Ask Spread Is Widest in the First 15 Minutes and Narrows Monotonically to Midday

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

> ⚠️ **Instrument note**: Original hypothesis references SPX. This test was run on **QQQ** as an adaptation. QQQ tracks Nasdaq-100; SPX-specific microstructure effects may differ.

**Linked hypothesis:** [[SPX Options Bid-Ask Spread Is Widest in the First 15 Minutes and Narrows Monotonically to Midday]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 189 |
| Rows excluded | 8 |
| Exclusion reason | days without bid/ask time series excluded |
| Final observations tested | 189 |
| Signal days | 144 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 189 |
| Signals | 144 |
| Primary Metric | spread_open_minus_midday_pct |
| Metric Value | 0.0292 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.05 |
| Reject Threshold | -0.05 |

## Verdict

**🟡 INCONCLUSIVE**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 189/197 days. open=0.0511 mid=0.0219 diff=0.0292 p=0.0000.

## Extra Metrics

| Metric | Value |
|--------|-------|
| contract_selection_method | intraday_atm_approx_small_strike_ladder |
| strike_ladder_width | 3 |
| exact_chain_intraday | False |
| minute_type | MINUTE_5 |
| n_days_attempted | 197 |
| n_days_with_ladder_data | 189 |
| pct_days_with_data | 0.959 |
| intraday_endpoint_used | single-equity-optionsymbol-rawiv |
| is_combined | True |
| monthly_batch_mode | True |
| full_window_combined_from_month_batches | True |
| months_combined | ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9'] |
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.0584, 'verdict': 'supported'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.0804, 'verdict': 'inconclusive'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': 0.0224, 'verdict': 'inconclusive'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 0.0184, 'verdict': 'inconclusive'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': 0.0197, 'verdict': 'inconclusive'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.0075, 'verdict': 'inconclusive'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': 0.0145, 'verdict': 'inconclusive'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 18, 'metric_value': 0.0228, 'verdict': 'inconclusive'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 0.0194, 'verdict': 'inconclusive'}} |
| mean_open_spread | 0.0511 |
| mean_midday_spread | 0.0219 |
| diff | 0.0292 |
| p_value | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=144) | 24.4 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `spread_comparison` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **61.4** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `value`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
