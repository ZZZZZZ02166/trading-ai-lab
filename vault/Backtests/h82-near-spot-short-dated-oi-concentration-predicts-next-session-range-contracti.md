---
hypothesis_number: H82
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 38
primary_metric: median_range_diff_top_vs_bottom_quintile
metric_value: -0.0008
---

# H82: Near-Spot Short-Dated OI Concentration Predicts Next-Session Range Contraction

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Near-Spot Short-Dated OI Concentration Predicts Next-Session Range Contraction_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2026-04-05 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires C+P param files; next-day range from daily_series |
| Final observations tested | 190 |
| Signal days | 38 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2026-04-05 |
| Observations | 190 |
| Signals | 38 |
| Primary Metric | median_range_diff_top_vs_bottom_quintile |
| Metric Value | -0.0008 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | -0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

median_range_diff=-0.00081 (top_quintile=0.00961, bottom=0.01042), p_mannwhitney=0.6965, n_top=38, n_bottom=38. Adjusted HHI measures near-spot short-dated OI dispersion. Dealer gamma sign unknown — concentration may dampen (long gamma) or amplify (short gamma) depending on dealer position direction.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_top_quintile | 0.009612 |
| median_range_bottom_quintile | 0.010421 |
| p_mannwhitney | 0.696458 |
| n_top_quintile | 38 |
| n_bottom_quintile | 38 |
| mean_adj_hhi | 0.0253 |
| mean_qualifying_strikes | 55.1 |
| n_valid_dates | 190 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=38) | 10.8 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.9834 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **30.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
