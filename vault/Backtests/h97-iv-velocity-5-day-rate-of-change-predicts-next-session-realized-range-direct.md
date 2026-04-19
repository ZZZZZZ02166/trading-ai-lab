---
hypothesis_number: H97
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 559
signals: 125
primary_metric: median_range_diff_rising_vs_falling_iv
metric_value: 0.0067
---

# H97: IV Velocity (5-Day Rate of Change) Predicts Next-Session Realized Range Direction

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _IV Velocity (5-Day Rate of Change) Predicts Next-Session Realized Range Direction_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 559 |
| Rows excluded | 6 |
| Exclusion reason | 5-day IV pct_change warmup + 1-day forward range |
| Final observations tested | 559 |
| Signal days | 125 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 559 |
| Signals | 125 |
| Primary Metric | median_range_diff_rising_vs_falling_iv |
| Metric Value | 0.0067 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_range=0.00674 (rising=0.01683, falling=0.01009), p_mannwhitney=0.0000, n_rising=125, n_falling=123, pct_rising=0.224, pct_falling=0.220.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_rising | 0.016833 |
| median_range_falling | 0.010094 |
| n_rising | 125 |
| n_falling | 123 |
| pct_days_rising | 0.2236 |
| pct_days_falling | 0.22 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=125) | 18.3 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.3** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
