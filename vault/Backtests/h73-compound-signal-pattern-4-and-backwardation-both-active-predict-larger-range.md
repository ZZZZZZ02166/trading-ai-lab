---
hypothesis_number: H73
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 563
signals: 32
primary_metric: median_range_both_minus_p4_only
metric_value: 0.0050
---

# H73: Compound Signal: Pattern 4 AND Backwardation Both Active Predict Larger Range Than Either Alone

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Compound Signal: Pattern 4 AND Backwardation Both Active Predict Larger Range Than Either Alone_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 563 |
| Rows excluded | 2 |
| Exclusion reason | 5-day rolling warmup; 1-day forward shift |
| Final observations tested | 563 |
| Signal days | 32 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 563 |
| Signals | 32 |
| Primary Metric | median_range_both_minus_p4_only |
| Metric Value | 0.0050 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Compound signal range=0.01727 > P4-only range=0.01229 (diff=0.00497), p_mannwhitney=0.0018. n_both=32, n_p4_only=41.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_both | 32 |
| n_p4_only | 41 |
| n_backwardation_only | 158 |
| n_neither | 332 |
| median_range_both | 0.017265 |
| median_range_p4_only | 0.012293 |
| median_range_backwardation_only | 0.016072 |
| median_range_neither | 0.010096 |
| p_mannwhitney_both_vs_p4 | 0.0018 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=32) | 10.2 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **30.2** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
