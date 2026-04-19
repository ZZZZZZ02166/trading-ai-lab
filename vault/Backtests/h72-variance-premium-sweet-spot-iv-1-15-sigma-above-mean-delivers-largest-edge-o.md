---
hypothesis_number: H72
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 456
signals: 38
primary_metric: mean_vp_sweetspot_minus_overextended
metric_value: -0.0325
---

# H72: Variance Premium Sweet Spot: IV 1-1.5 Sigma Above Mean Delivers Largest Edge Over Realized Vol

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Variance Premium Sweet Spot: IV 1-1.5 Sigma Above Mean Delivers Largest Edge Over Realized Vol_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 456 |
| Rows excluded | 109 |
| Exclusion reason | 90-day rolling warmup; fwd_rv_20 NaN for last 20 rows |
| Final observations tested | 456 |
| Signal days | 38 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 456 |
| Signals | 38 |
| Primary Metric | mean_vp_sweetspot_minus_overextended |
| Metric Value | -0.0325 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.005 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No sweet-spot advantage: diff=-0.0325, p_mannwhitney=0.7068. VP sweet=-0.0330, VP over=-0.0005.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_sweetspot | 38 |
| n_overextended | 44 |
| n_baseline | 315 |
| mean_vp_sweetspot | -0.03302 |
| mean_vp_overextended | -0.00053 |
| mean_vp_baseline | 0.01472 |
| p_mannwhitney | 0.7068 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=38) | 7.9 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.9834 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **27.9** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
