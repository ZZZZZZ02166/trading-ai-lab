---
hypothesis_number: H76
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 564
signals: 99
primary_metric: gap_fill_rate_backw_minus_contango
metric_value: 0.1320
---

# H76: Gap Days in Backwardation Fill More Frequently Than Gap Days in Contango

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Gap Days in Backwardation Fill More Frequently Than Gap Days in Contango_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | Gap > 0.5% filter + backwardation/contango split |
| Final observations tested | 564 |
| Signal days | 99 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 99 |
| Primary Metric | gap_fill_rate_backw_minus_contango |
| Metric Value | 0.1320 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.08 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Gap fill rate: backwardation=0.404 vs contango=0.272 (diff=0.132), p_fisher=0.0261. n_backw=99, n_contango=125.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_backwardation_gaps | 99 |
| n_contango_gaps | 125 |
| fill_rate_backwardation | 0.404 |
| fill_rate_contango | 0.272 |
| p_fisher_exact | 0.0261 |
| total_gap_days | 224 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=99) | 16.1 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **36.1** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
