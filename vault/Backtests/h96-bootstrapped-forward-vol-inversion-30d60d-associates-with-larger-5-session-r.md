---
hypothesis_number: H96
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 560
signals: 186
primary_metric: median_range_5d_diff_inverted_vs_normal
metric_value: 0.0043
---

# H96: Bootstrapped Forward Vol Inversion (30d→60d) Associates with Larger 5-Session Realized Range

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Bootstrapped Forward Vol Inversion (30d→60d) Associates with Larger 5-Session Realized Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 560 |
| Rows excluded | 5 |
| Exclusion reason | iv_30d/iv_60d required + 5-day forward range window |
| Final observations tested | 560 |
| Signal days | 186 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 560 |
| Signals | 186 |
| Primary Metric | median_range_5d_diff_inverted_vs_normal |
| Metric Value | 0.0043 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_range_5d=0.00427 (inverted=0.01571, normal=0.01144), p_mannwhitney=0.0000, n_inverted=186, n_normal=374, pct_inverted=0.332.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_5d_inverted | 0.015714 |
| median_range_5d_normal | 0.011441 |
| pct_inverted | 0.3321 |
| n_inverted | 186 |
| n_normal | 374 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=186) | 23.6 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **60.6** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
