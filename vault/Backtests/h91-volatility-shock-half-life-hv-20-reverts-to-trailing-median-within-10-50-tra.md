---
hypothesis_number: H91
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 446
signals: 5
primary_metric: median_days_to_revert_after_spike
metric_value: 40.5000
---

# H91: Volatility Shock Half-Life: hv_20 Reverts to Trailing Median Within 10-50 Trading Days After Spike

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Volatility Shock Half-Life: hv_20 Reverts to Trailing Median Within 10-50 Trading Days After Spike_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 446 |
| Rows excluded | 119 |
| Exclusion reason | 252-day rolling quantile warmup for p80/p50 thresholds |
| Final observations tested | 446 |
| Signal days | 5 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 446 |
| Signals | 5 |
| Primary Metric | median_days_to_revert_after_spike |
| Metric Value | 40.5000 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 50.0 |
| Reject Threshold | 60.0 |

## Verdict

**✅ SUPPORTED**

n_spike_events=5, n_reverted_within_120d=4, median_days_to_revert=40.5, pct_within_30d=40.0%, pct_within_60d=80.0%.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_spike_events | 5 |
| n_reverted_within_120d | 4 |
| n_did_not_revert | 1 |
| pct_reverted_within_30d | 0.4 |
| pct_reverted_within_60d | 0.8 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=5) | 4.8 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **24.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
