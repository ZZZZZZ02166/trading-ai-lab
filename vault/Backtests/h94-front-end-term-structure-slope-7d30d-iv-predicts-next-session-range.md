---
hypothesis_number: H94
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 564
signals: 217
primary_metric: median_range_diff_backwardation_vs_contango
metric_value: 0.0041
---

# H94: Front-End Term Structure Slope (7d/30d IV) Predicts Next-Session Range

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Front-End Term Structure Slope (7d/30d IV) Predicts Next-Session Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 7d IV join + 1-day forward range |
| Final observations tested | 564 |
| Signal days | 217 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 217 |
| Primary Metric | median_range_diff_backwardation_vs_contango |
| Metric Value | 0.0041 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_range=0.00409 (backwardation=0.01470, contango=0.01061), p_mannwhitney=0.0000, n_backwardation=217, n_contango=347, mean_slope_7_30=0.9649.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_backwardation | 0.014704 |
| median_range_contango | 0.010614 |
| n_backwardation | 217 |
| n_contango | 347 |
| mean_slope_7_30 | 0.9649 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=217) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **52.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
