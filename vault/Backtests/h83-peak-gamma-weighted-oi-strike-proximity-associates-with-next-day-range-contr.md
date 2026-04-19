---
hypothesis_number: H83
verdict: supported
ticker: QQQ
start_date: 2025-04-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 107
primary_metric: median_next_range_near_vs_far
metric_value: -0.0065
---

# H83: Peak Gamma-Weighted OI Strike: Proximity Associates with Next-Day Range Contraction

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Peak Gamma-Weighted OI Strike: Proximity Associates with Next-Day Range Contraction_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2026-04-05 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires C+P param files; EOD close + next-day range from daily_series |
| Final observations tested | 190 |
| Signal days | 107 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2026-04-05 |
| Observations | 190 |
| Signals | 107 |
| Primary Metric | median_next_range_near_vs_far |
| Metric Value | -0.0065 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | -0.001 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

median_range_diff=-0.00654 (near=0.00981, far=0.01634), p_mannwhitney=0.0013, n_near=107, n_far=16. Gross gamma-weighted OI only — dealer position sign unknown. Do not interpret as net dealer gamma or GEX. This is an empirical proximity test; high gamma-OI at a strike means concentrated option sensitivity, not a known directional hedge.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_near | 0.009806 |
| median_range_far | 0.016342 |
| n_near_lt3 | 107 |
| n_far_gt8 | 16 |
| p_mannwhitney | 0.001269 |
| median_dist_to_peak | 2.31 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=107) | 16.9 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0032 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **56.9** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
