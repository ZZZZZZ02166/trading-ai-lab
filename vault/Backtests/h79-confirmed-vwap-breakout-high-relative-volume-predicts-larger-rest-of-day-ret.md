---
hypothesis_number: H79
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 563
signals: 400
primary_metric: mean_rod_return_high_minus_low_overall
metric_value: 0.0002
---

# H79: Confirmed VWAP Breakout — High Relative Volume Predicts Larger Rest-of-Day Return (Bucket-Stratified)

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Confirmed VWAP Breakout — High Relative Volume Predicts Larger Rest-of-Day Return (Bucket-Stratified)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 563 |
| Rows after validation | 563 |
| Rows excluded | 0 |
| Exclusion reason | 5-min bar sessions; rel-vol split (>=1.2 vs <=0.8) + bucket stratification |
| Final observations tested | 563 |
| Signal days | 400 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 563 |
| Signals | 400 |
| Primary Metric | mean_rod_return_high_minus_low_overall |
| Metric Value | 0.0002 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

diff_overall=0.00021, p_mw_overall=0.8405. High-vol breakouts do not outperform low-vol. n_high=62, n_low=183, median_rel_vol=0.831.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_high_vol_total | 62 |
| n_low_vol_total | 183 |
| n_breakout_signals_total | 400 |
| n_middle_band_excluded | 155 |
| pct_middle_band | 0.3875 |
| mean_rod_high_overall | 0.000184 |
| mean_rod_low_overall | -3.1e-05 |
| diff_overall | 0.000215 |
| p_mannwhitney_overall | 0.8405 |
| cliffs_delta_overall | -0.0846 |
| median_rel_vol_at_breakout | 0.8308 |
| n_high_vol_early | 37 |
| n_low_vol_early | 120 |
| mean_rod_high_early | -0.000522 |
| mean_rod_low_early | 0.000558 |
| p_mannwhitney_early | 0.9691 |
| n_high_vol_late | 25 |
| n_low_vol_late | 63 |
| mean_rod_high_late | 0.001229 |
| mean_rod_low_late | -0.001151 |
| p_mannwhitney_late | 0.2586 |
| vol_profile_version | rolling_expanding |
| n_fallback_sessions | 5 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=400) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
