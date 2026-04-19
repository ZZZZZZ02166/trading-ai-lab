---
hypothesis_number: H70
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 564
signals: 113
primary_metric: win_rate_top_quintile
metric_value: 0.8053
---

# H70: Top-Quintile Daily Range Autocorrelation: High-RV Days Predict High-RV Next Session

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Top-Quintile Daily Range Autocorrelation: High-RV Days Predict High-RV Next Session_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 1-day forward shift; next_range NaN on last row |
| Final observations tested | 564 |
| Signal days | 113 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 113 |
| Primary Metric | win_rate_top_quintile |
| Metric Value | 0.8053 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.6 |
| Reject Threshold | 0.5 |

## Verdict

**✅ SUPPORTED**

win_rate=0.805 (91/113) > 0.60 threshold, p_binomial=0.0000 < 0.10. Top-quintile range threshold: 0.0184.

## Extra Metrics

| Metric | Value |
|--------|-------|
| q80_threshold | 0.01837 |
| median_range | 0.01192 |
| n_signal | 113 |
| n_wins | 91 |
| p_binomial | 0.0 |
| mean_next_range_signal | 0.02023 |
| mean_next_range_rest | 0.01256 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=113) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `strategy_win_rate` (pattern_match) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **85.0** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `binomial`
CI: [0.7323, 0.8783] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
