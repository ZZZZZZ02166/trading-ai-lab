---
hypothesis_number: H57
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 560
signals: 112
primary_metric: median_slope_convergence_diff_top_vs_bottom_quintile
metric_value: 0.0097
---

# H57: Continuous IV Term Structure Slope Predicts Calendar Spread Efficiency

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Continuous IV Term Structure Slope Predicts Calendar Spread Efficiency_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 560 |
| Rows excluded | 5 |
| Exclusion reason | 5-day forward shift for slope convergence; requires both iv_30d and iv_60d |
| Final observations tested | 560 |
| Signal days | 112 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 560 |
| Signals | 112 |
| Primary Metric | median_slope_convergence_diff_top_vs_bottom_quintile |
| Metric Value | 0.0097 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Steep contango shows more slope convergence: median_top=0.0033 vs median_bottom=-0.0064 (diff=0.0097, p=0.0000, Cliff's d=0.539). Note: convergence is a proxy for calendar spread P&L; actual P&L requires options pricing.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_top_quintile | 112 |
| n_bottom_quintile | 112 |
| median_convergence_top | 0.0033 |
| median_convergence_bottom | -0.0064 |
| cliffs_delta | 0.5394 |
| p_mannwhitney | 0.0 |
| u_stat | 9655.0 |
| slope_q20 | -0.004 |
| slope_q80 | 0.0111 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=112) | 24.9 | 25 | Independence-adjusted count |
| Effect Size | 0.1 | 20 | Family: `regime_comparison` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **65.0** | **100** | |

**Priority: 🟡 WATCHLIST**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
