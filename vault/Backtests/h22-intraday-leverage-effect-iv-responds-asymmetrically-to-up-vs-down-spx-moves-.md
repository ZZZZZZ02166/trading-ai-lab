---
hypothesis_number: H22
verdict: supported
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 190
signals: 515
primary_metric: mean_iv_change_down_minus_up
metric_value: 0.0144
---

# H22: Intraday Leverage Effect: IV Responds Asymmetrically to Up vs. Down SPX Moves Within 5 Minutes

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

> ⚠️ **Instrument note**: Original hypothesis references SPX. This test was run on **QQQ** as an adaptation. QQQ tracks Nasdaq-100; SPX-specific microstructure effects may differ.

**Linked hypothesis:** [[Intraday Leverage Effect: IV Responds Asymmetrically to Up vs. Down SPX Moves Within 5 Minutes]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 1,122 |
| Rows excluded | 7 |
| Exclusion reason | days without IV/return pairs excluded |
| Final observations tested | 190 |
| Signal days | 515 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 515 |
| Primary Metric | mean_iv_change_down_minus_up |
| Metric Value | 0.0144 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.001 |
| Reject Threshold | -0.001 |

## Verdict

**✅ SUPPORTED**

Combined combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 190/197 days. down=0.0319 up=0.0174 diff=0.0144 p=0.0021 (515 down, 607 up bars).

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
| month_summary | {'M1': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -0.0247, 'verdict': 'rejected'}, 'M2': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': 0.0246, 'verdict': 'supported'}, 'M3': {'n_days_attempted': 21, 'n_days_with_data': 20, 'metric_value': 0.0139, 'verdict': 'inconclusive'}, 'M4': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 0.0173, 'verdict': 'supported'}, 'M5': {'n_days_attempted': 21, 'n_days_with_data': 21, 'metric_value': 0.0026, 'verdict': 'inconclusive'}, 'M6': {'n_days_attempted': 22, 'n_days_with_data': 21, 'metric_value': -0.0, 'verdict': 'rejected'}, 'M7': {'n_days_attempted': 23, 'n_days_with_data': 23, 'metric_value': 0.0268, 'verdict': 'supported'}, 'M8': {'n_days_attempted': 20, 'n_days_with_data': 19, 'metric_value': 0.0458, 'verdict': 'supported'}, 'M9': {'n_days_attempted': 23, 'n_days_with_data': 22, 'metric_value': 0.0297, 'verdict': 'supported'}} |
| mean_iv_chg_down | 0.0319 |
| mean_iv_chg_up | 0.0174 |
| diff | 0.0144 |
| n_down_bars | 515 |
| n_up_bars | 607 |
| p_value | 0.0021 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=515) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 0.3 | 20 | Family: `iv_level_change` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0084 · IQ: standard |
| Stability | 7.8 | 10 | Measured (consistency: 78%) |
| **Phase 1 Score** | **59.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `value`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
