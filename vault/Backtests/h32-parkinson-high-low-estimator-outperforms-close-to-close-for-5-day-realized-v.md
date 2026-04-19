---
hypothesis_number: H32
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 539
signals: 174
primary_metric: rmse_ratio_parkinson_vs_cc
metric_value: 0.9540
---

# H32: Parkinson High-Low Estimator Outperforms Close-to-Close for 5-Day Realized Vol Forecasting

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Parkinson High-Low Estimator Outperforms Close-to-Close for 5-Day Realized Vol Forecasting_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 539 |
| Rows excluded | 25 |
| Exclusion reason | rows with missing OHLC or insufficient forward window excluded |
| Final observations tested | 539 |
| Signal days | 174 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 539 |
| Signals | 174 |
| Primary Metric | rmse_ratio_parkinson_vs_cc |
| Metric Value | 0.9540 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.95 |
| Reject Threshold | 1.0 |

## Verdict

**🟡 INCONCLUSIVE**

Direction correct (ratio=0.9540 < 1.0) but not significant (p=0.1551, need p<0.05 AND ratio<0.95).

## Extra Metrics

| Metric | Value |
|--------|-------|
| rmse_parkinson | 0.117564 |
| rmse_cc | 0.123233 |
| p_dm_test | 0.1551 |
| n_wide_range | 174 |
| rmse_ratio_wide_range | 0.9833 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=26) | 24.3 | 25 | Independence-adjusted count |
| Effect Size | 4.6 | 20 | Family: `estimator_accuracy` (stored) |
| Statistical Reliability | 4.2 | 20 | FDR-within-family p: 0.1551 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **53.2** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `dm_test`
CI: Not available (dm_se_not_stored)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
