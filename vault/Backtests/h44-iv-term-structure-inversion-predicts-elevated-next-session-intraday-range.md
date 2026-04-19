---
hypothesis_number: H44
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 564
signals: 190
primary_metric: median_next_range_diff_backwardation_vs_contango
metric_value: 0.0058
---

# H44: IV Term Structure Inversion Predicts Elevated Next-Session Intraday Range

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _IV Term Structure Inversion Predicts Elevated Next-Session Intraday Range_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 1-day forward shift for next-session range; missing iv_30d/iv_60d or OHLC |
| Final observations tested | 564 |
| Signal days | 190 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 190 |
| Primary Metric | median_next_range_diff_backwardation_vs_contango |
| Metric Value | 0.0058 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Backwardation days have higher next-session range: median_back=0.0163 vs median_cont=0.0106 (diff=0.0058, p=0.0000, Cliff's d=0.550)

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_backwardation | 190 |
| n_contango | 374 |
| median_range_backwardation | 0.0163 |
| median_range_contango | 0.0106 |
| cliffs_delta | 0.5498 |
| p_mannwhitney | 0.0 |
| u_stat | 55065.0 |
| pct_backwardation_days | 0.337 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=190) | 25.0 | 25 | Independence-adjusted count |
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
