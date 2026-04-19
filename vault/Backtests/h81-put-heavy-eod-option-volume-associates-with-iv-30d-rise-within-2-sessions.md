---
hypothesis_number: H81
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 188
signals: 47
primary_metric: mean_iv_change_diff_put_heavy_vs_control
metric_value: 0.0034
---

# H81: Put-Heavy EOD Option Volume Associates with iv_30d Rise Within 2 Sessions

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Put-Heavy EOD Option Volume Associates with iv_30d Rise Within 2 Sessions_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2026-04-05 |
| Raw rows loaded | 190 |
| Rows after validation | 188 |
| Rows excluded | 2 |
| Exclusion reason | Requires both C and P param files; iv_30d from daily_series |
| Final observations tested | 188 |
| Signal days | 47 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2026-04-05 |
| Observations | 188 |
| Signals | 47 |
| Primary Metric | mean_iv_change_diff_put_heavy_vs_control |
| Metric Value | 0.0034 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

diff=0.0034 (mean_put_heavy=0.0005, mean_control=-0.0029), p_mannwhitney=0.5956, n_signal=47, n_control=47. Thresholds data-driven: signal=PCR≥p75(0.5425), control=PCR≤p25(0.4950). QQQ aggregate PCR clusters in 0.43–0.61; fixed 0.58/0.42 thresholds produce empty groups. Same-day vol confound: 0DTE put volume spikes on large down days mechanically inflate PCR on days when IV tends to rise regardless. Association may reflect coincident conditions rather than PCR predicting IV. Treat as exploratory.

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_iv_change_put_heavy | 0.00049 |
| mean_iv_change_control | -0.002872 |
| n_signal | 47 |
| n_control | 47 |
| p_mannwhitney | 0.595602 |
| median_pcr_overall | 0.5187 |
| pcr_threshold_p75 | 0.5425 |
| pcr_threshold_p25 | 0.495 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=47) | 24.8 | 25 | Independence-adjusted count |
| Effect Size | 0.1 | 20 | Family: `iv_level_change` (pattern_match) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.5956 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **44.9** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
