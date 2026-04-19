---
hypothesis_number: H98
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 545
signals: 410
primary_metric: mean_vp_diff_contango_vs_inverted
metric_value: 0.0207
---

# H98: Variance Premium Conditional on Term Structure Contango: VP Is Larger When Curve Is Normal

**❌ REJECTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Variance Premium Conditional on Term Structure Contango: VP Is Larger When Curve Is Normal_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 545 |
| Rows excluded | 20 |
| Exclusion reason | 20-day forward window for fwd_rv_20 + iv_30d / iv_90d |
| Final observations tested | 545 |
| Signal days | 410 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 545 |
| Signals | 410 |
| Primary Metric | mean_vp_diff_contango_vs_inverted |
| Metric Value | 0.0207 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.005 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

diff_mean_vp=0.02069 (contango=0.01031, inverted=-0.01037), p_mannwhitney=0.7556, pct_positive_contango=0.649, pct_positive_inverted=0.674, n_contango=410, n_inverted=135.

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_vp_contango | 0.010313 |
| mean_vp_inverted | -0.010373 |
| pct_positive_contango | 0.6488 |
| pct_positive_inverted | 0.6741 |
| n_contango | 410 |
| n_inverted | 135 |
| p_mannwhitney | 0.755596 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=410) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.9834 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **34.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
