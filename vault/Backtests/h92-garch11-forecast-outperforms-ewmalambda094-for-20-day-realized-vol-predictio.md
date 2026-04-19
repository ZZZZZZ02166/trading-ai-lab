---
hypothesis_number: H92
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 544
signals: 544
primary_metric: rmse_ratio_garch_vs_ewma
metric_value: 0.8972
---

# H92: GARCH(1,1) Forecast Outperforms EWMA(lambda=0.94) for 20-Day Realized Vol Prediction

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _GARCH(1,1) Forecast Outperforms EWMA(lambda=0.94) for 20-Day Realized Vol Prediction_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 544 |
| Rows excluded | 21 |
| Exclusion reason | EWMA warmup (first ~20 rows) + 20-day forward window for fwd_rv_20 |
| Final observations tested | 544 |
| Signal days | 544 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 544 |
| Signals | 544 |
| Primary Metric | rmse_ratio_garch_vs_ewma |
| Metric Value | 0.8972 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.95 |
| Reject Threshold | 1.0 |

## Verdict

**✅ SUPPORTED**

rmse_ratio=0.8973 (GARCH=0.09131, EWMA=0.10176), p_paired_ttest=0.0000, n=544.

## Extra Metrics

| Metric | Value |
|--------|-------|
| rmse_garch | 0.091307 |
| rmse_ewma | 0.101763 |
| t_stat_paired | -4.3135 |
| p_paired_ttest | 1.9e-05 |
| n_valid | 544 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=27) | 24.4 | 25 | Independence-adjusted count |
| Effect Size | 10.3 | 20 | Family: `estimator_accuracy` (pattern_match) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **54.7** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (dm_se_not_stored)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
