---
hypothesis_number: H41
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 563
signals: 47
primary_metric: excess_kurtosis_full
metric_value: 11.5101
---

# H41: QQQ Fat-Tail Realized Kurtosis Exceeds 3.0 and Is Higher in High-IV Regimes Than Low-IV Regimes

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _QQQ Fat-Tail Realized Kurtosis Exceeds 3.0 and Is Higher in High-IV Regimes Than Low-IV Regimes_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 563 |
| Rows excluded | 1 |
| Exclusion reason | rows with missing close or iv_30d excluded |
| Final observations tested | 563 |
| Signal days | 47 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 563 |
| Signals | 47 |
| Primary Metric | excess_kurtosis_full |
| Metric Value | 11.5101 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 1.0 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

Full-sample EK confirmed (11.510 > 1.0, p=0.0000) but regime ratio=nanx or p_regime=0.0000 not sufficient for full support.

## Extra Metrics

| Metric | Value |
|--------|-------|
| excess_kurtosis_full | 11.5101 |
| excess_kurtosis_low_iv | -0.7178 |
| excess_kurtosis_mid_iv | 1.0669 |
| excess_kurtosis_high_iv | 5.7725 |
| n_low | 35 |
| n_mid | 481 |
| n_high | 47 |
| p_kurtosis_bootstrap | 0.0 |
| p_regime_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=563) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `distribution` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 8.3 | 10 | Measured (consistency: 83%) |
| **Phase 1 Score** | **93.3** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `kurtosis_bootstrap`
CI: Not available (bootstrap_values_not_stored)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
