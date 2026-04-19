---
hypothesis_number: H43
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 564
signals: 422
primary_metric: median_range_diff_small_vs_large_gap
metric_value: -0.0027
---

# H43: Overnight Gap Budget Consumption Reduces Remaining Intraday Range

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Overnight Gap Budget Consumption Reduces Remaining Intraday Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 1-day lag for prev_close; missing OHLC or iv_30d |
| Final observations tested | 564 |
| Signal days | 422 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 422 |
| Primary Metric | median_range_diff_small_vs_large_gap |
| Metric Value | -0.0027 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No gap-budget effect: small_gap range=0.0105 vs large_gap=0.0132 (diff=-0.0027, p=1.0000)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_small | 185 |
| n_mid | 142 |
| n_large | 237 |
| median_range_small | 0.0105 |
| median_range_mid | 0.0115 |
| median_range_large | 0.0132 |
| cliffs_delta_small_vs_large | -0.2234 |
| p_mannwhitney | 1.0 |
| is_monotonic | False |
| kruskal_stat | 17.1864 |
| kruskal_p | 0.0002 |
| pct_small_gap_days | 0.328 |
| pct_large_gap_days | 0.42 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=422) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: strong |
| Stability | 0.0 | 10 | Measured (consistency: 0%) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
