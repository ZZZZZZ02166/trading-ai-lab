---
hypothesis_number: H65
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 188
signals: 20
primary_metric: mean_return_diff_both_walls_up_vs_down
metric_value: -0.0005
---

# H65: Overnight Wall Shifts in the Same Direction Predict Next-Session Return Direction

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Overnight Wall Shifts in the Same Direction Predict Next-Session Return Direction_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 188 |
| Rows excluded | 2 |
| Exclusion reason | Requires consecutive-date wall calculations; 1-day forward shift for next return |
| Final observations tested | 188 |
| Signal days | 20 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 188 |
| Signals | 20 |
| Primary Metric | mean_return_diff_both_walls_up_vs_down |
| Metric Value | -0.0005 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

Rejected: no directional signal in claimed direction. mean_return_both_up=-0.00105 vs mean_down=-0.00053 (diff=-0.00052, Cliff's d=-0.030). Mann-Whitney p=0.5612 (one-sided, alternative: both_up > both_down). Two-sided p ≈ 0.88. N is critically small: n_both_up=20, n_both_down=10. Counter-intuitive pattern: win_rate_both_down=70% (7/10) vs win_rate_both_up=45% (9/20) — walls shifting down may weakly predict positive next-session return, opposite to hypothesis. N=10 is insufficient to conclude anything about the reverse direction.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_both_walls_up | 20 |
| n_both_walls_down | 10 |
| pct_both_up | 0.106 |
| pct_both_down | 0.053 |
| mean_return_both_up | -0.00105 |
| mean_return_both_down | -0.000532 |
| win_rate_both_up | 0.45 |
| win_rate_both_down | 0.7 |
| cliffs_delta | -0.03 |
| p_mannwhitney | 0.5612 |
| u_stat | 97.0 |
| p_mannwhitney_note | one-sided (alternative: both_up > both_down) |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=20) | 19.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.8502 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **39.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
