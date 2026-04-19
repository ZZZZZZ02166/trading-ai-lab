---
hypothesis_number: H77
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 536
signals: 179
primary_metric: mean_vp_stable_minus_volatile
metric_value: 0.0089
---

# H77: Low Vol-of-Vol Entry Filter: Stable IV Environments Deliver Larger Variance Premium

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Low Vol-of-Vol Entry Filter: Stable IV Environments Deliver Larger Variance Premium_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 536 |
| Rows excluded | 29 |
| Exclusion reason | 10-day vol-of-vol warmup; fwd_rv_20 NaN for last 20 rows |
| Final observations tested | 536 |
| Signal days | 179 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 536 |
| Signals | 179 |
| Primary Metric | mean_vp_stable_minus_volatile |
| Metric Value | 0.0089 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.005 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

diff=0.0089, p_mannwhitney=0.9961. Stable VP=-0.0009, Volatile VP=-0.0098. Low vol-of-vol does not predict larger variance premium.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_stable_vov | 179 |
| n_volatile_vov | 179 |
| mean_vp_stable | -0.00091 |
| mean_vp_volatile | -0.00976 |
| p_mannwhitney | 0.9961 |
| q33_vov | 0.009172 |
| q67_vov | 0.015978 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=179) | 22.4 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **42.4** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
