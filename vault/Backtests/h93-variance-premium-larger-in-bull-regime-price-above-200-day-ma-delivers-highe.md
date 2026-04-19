---
hypothesis_number: H93
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 347
signals: 301
primary_metric: mean_vp_diff_bull_vs_bear
metric_value: 0.1240
---

# H93: Variance Premium Larger in Bull Regime: Price Above 200-Day MA Delivers Higher iv_30d - fwd_rv_20

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Variance Premium Larger in Bull Regime: Price Above 200-Day MA Delivers Higher iv_30d - fwd_rv_20_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 347 |
| Rows excluded | 218 |
| Exclusion reason | 200-day MA warmup + 20-day forward window for fwd_rv_20 |
| Final observations tested | 347 |
| Signal days | 301 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 347 |
| Signals | 301 |
| Primary Metric | mean_vp_diff_bull_vs_bear |
| Metric Value | 0.1240 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.003 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff=0.12398 (mean_vp_bull=0.02197, mean_vp_bear=-0.10200), p_mannwhitney=0.0072, n_bull=301, n_bear=46.

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_vp_bull | 0.021972 |
| mean_vp_bear | -0.102003 |
| n_bull_days | 301 |
| n_bear_days | 46 |
| p_mannwhitney | 0.007237 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=301) | 19.2 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 12.8 | 20 | FDR-within-family p: 0.0155 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **42.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
