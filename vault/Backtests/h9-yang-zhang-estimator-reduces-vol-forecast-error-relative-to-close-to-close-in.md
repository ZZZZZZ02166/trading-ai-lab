---
hypothesis_number: H9
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 507
signals: 507
primary_metric: rmse_ratio_yz_vs_cc
metric_value: 0.9663
---

# H9: Yang-Zhang Estimator Reduces Vol Forecast Error Relative to Close-to-Close in Trending Markets

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** [[Yang-Zhang Estimator Reduces Vol Forecast Error Relative to Close-to-Close in Trending Markets]]

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 507 |
| Rows excluded | 58 |
| Exclusion reason | 20-day lookback warmup (hv_20_cc/hv_20_yz); 20-day forward window (fwd_rv_20) |
| Final observations tested | 507 |
| Signal days | 507 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 507 |
| Signals | 507 |
| Primary Metric | rmse_ratio_yz_vs_cc |
| Metric Value | 0.9663 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.99 |
| Reject Threshold | 1.01 |

## Verdict

**🟡 INCONCLUSIVE**

RMSE ratio=0.9663 (p=0.1192) — direction present but not significant or near 1.0

## Extra Metrics

| Metric | Value |
|--------|-------|
| rmse_cc | 0.105865 |
| rmse_yz | 0.102302 |
| improvement_pct | 3.37 |
| t_stat | -1.5609 |
| p_value | 0.1192 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=25) | 23.5 | 25 | Independence-adjusted count |
| Effect Size | 3.4 | 20 | Family: `estimator_accuracy` (stored) |
| Statistical Reliability | 3.0 | 20 | FDR-within-family p: 0.1551 · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **49.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `value`
CI: Not available (dm_se_not_stored)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
