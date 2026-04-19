---
hypothesis_number: H42
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 551
signals: 229
primary_metric: median_amplitude_diff_mid_vs_outer
metric_value: 0.0059
---

# H42: IVX Percentile Regime Predicts Intraday Amplitude

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _IVX Percentile Regime Predicts Intraday Amplitude_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 551 |
| Rows excluded | 14 |
| Exclusion reason | 30-day rolling percentile warmup; missing OHLC or iv_30d |
| Final observations tested | 551 |
| Signal days | 229 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 551 |
| Signals | 229 |
| Primary Metric | median_amplitude_diff_mid_vs_outer |
| Metric Value | 0.0059 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.05 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No amplitude advantage in mid-regime: median_mid=1.021 vs median_outer=1.015 (diff=0.006, p=0.7663)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_mid | 229 |
| n_outer | 322 |
| median_mid | 1.0206 |
| median_outer | 1.0146 |
| cliffs_delta | -0.0363 |
| p_mannwhitney | 0.7663 |
| u_stat | 35531.0 |
| sensitivity_20_70 | -0.0363 |
| sensitivity_25_75 | -0.0113 |
| sensitivity_30_70 | 0.025 |
| sensitivity_20_80 | -0.0649 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=229) | 24.6 | 25 | Independence-adjusted count |
| Effect Size | 0.1 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: strong |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **54.7** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
