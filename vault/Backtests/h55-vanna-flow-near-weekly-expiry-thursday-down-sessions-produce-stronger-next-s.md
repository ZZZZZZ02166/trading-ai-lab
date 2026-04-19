---
hypothesis_number: H55
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 563
signals: 32
primary_metric: mean_iv_rebound_diff_thursday_vs_other_down
metric_value: 0.0045
---

# H55: Vanna Flow Near Weekly Expiry: Thursday Down Sessions Produce Stronger Next-Session IV Rebounds

**❌ REJECTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Vanna Flow Near Weekly Expiry: Thursday Down Sessions Produce Stronger Next-Session IV Rebounds_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 563 |
| Rows excluded | 2 |
| Exclusion reason | 1-day forward shift for next-session IV; requires date column for day-of-week |
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
| Primary Metric | mean_iv_rebound_diff_thursday_vs_other_down |
| Metric Value | 0.0045 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No vanna-expiry IV rebound: mean_thu=-0.0009 vs mean_other=-0.0054 (diff=0.0045, p=0.5408)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_thursday_down | 32 |
| n_other_down | 107 |
| mean_iv_rebound_thursday | -0.0009 |
| mean_iv_rebound_other | -0.0054 |
| cliffs_delta | -0.0117 |
| p_mannwhitney | 0.5408 |
| u_stat | 1692.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=32) | 24.9 | 25 | Independence-adjusted count |
| Effect Size | 0.1 | 20 | Family: `iv_level_change` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.5956 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
