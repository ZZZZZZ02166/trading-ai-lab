---
hypothesis_number: H46
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 85
signals: 29
primary_metric: win_rate_diff_mid_vs_outer_regime
metric_value: 0.0326
---

# H46: IVX Percentile Regime Improves RP-Long Setup Win Rate (H1)

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _IVX Percentile Regime Improves RP-Long Setup Win Rate (H1)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 88 |
| Rows after validation | 85 |
| Rows excluded | 3 |
| Exclusion reason | missing iv_pct_prev or ret_60m |
| Final observations tested | 85 |
| Signal days | 29 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 85 |
| Signals | 29 |
| Primary Metric | win_rate_diff_mid_vs_outer_regime |
| Metric Value | 0.0326 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.05 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No IV regime edge: mid win_rate=58.6% vs outer=55.4% (diff=0.033, p=0.4649)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_mid | 29 |
| n_outer | 56 |
| win_rate_mid | 0.5862 |
| win_rate_outer | 0.5536 |
| cliffs_delta | 0.0123 |
| p_mannwhitney | 0.4649 |
| sens_wr_diff_25_75 | 0.0759 |
| sens_wr_diff_30_70 | 0.1795 |
| sens_wr_diff_20_80 | 0.1008 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=29) | 23.9 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.6881 · IQ: standard |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **53.9** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: [0.0000, 0.0972] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
