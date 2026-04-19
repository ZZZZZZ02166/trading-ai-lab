---
hypothesis_number: H84
verdict: inconclusive
ticker: QQQ
start_date: 2025-04-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 81
primary_metric: mean_next_return_diff_put_heavy_vs_call_heavy
metric_value: -0.0024
---

# H84: Delta-Band OI Asymmetry Predicts Next-Session Return Direction

**🟡 INCONCLUSIVE**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Delta-Band OI Asymmetry Predicts Next-Session Return Direction_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2026-04-05 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires C+P param files; next-session log_return from daily_series |
| Final observations tested | 190 |
| Signal days | 81 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2026-04-05 |
| Observations | 190 |
| Signals | 81 |
| Primary Metric | mean_next_return_diff_put_heavy_vs_call_heavy |
| Metric Value | -0.0024 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | -0.001 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

diff=-0.00237 (put_heavy=0.00146, call_heavy=0.00384), p_mannwhitney=0.1955, n_put=81, n_call=15, pct_middle_band=49.5%. Delta-band OI aggregates directional bets, portfolio hedges, covered writes, and dealer inventory indiscriminately. Cannot isolate institutional hedging demand. Exploratory association test — loose thresholds applied.

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_next_return_put_heavy | 0.001462 |
| mean_next_return_call_heavy | 0.003836 |
| n_put_heavy | 81 |
| n_call_heavy | 15 |
| p_mannwhitney | 0.195529 |
| median_oi_ratio | 1.3271 |
| pct_middle_band_excluded | 0.4947 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=81) | 14.6 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.3666 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **34.6** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
