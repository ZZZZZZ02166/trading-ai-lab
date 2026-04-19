---
hypothesis_number: H99
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 545
signals: 112
primary_metric: median_hv_diff_high_vs_low_spread
metric_value: 0.0390
---

# H99: EOD Bid-Ask Spread Percentile Predicts Next-Session Realized Volatility

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _EOD Bid-Ask Spread Percentile Predicts Next-Session Realized Volatility_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 545 |
| Rows excluded | 20 |
| Exclusion reason | bid/ask spread + 60-day rolling rank warmup + hv_20_cc next-day |
| Final observations tested | 545 |
| Signal days | 112 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 545 |
| Signals | 112 |
| Primary Metric | median_hv_diff_high_vs_low_spread |
| Metric Value | 0.0390 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.005 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

diff_median_hv=0.03898 (high_spread=0.18436, low_spread=0.14538), p_mannwhitney=0.0000, n_high=112, n_low=198, median_spread_pct=0.00002. Note: EOD bid/ask is regime proxy — not intraday fill estimate.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_hv_high_spread | 0.184356 |
| median_hv_low_spread | 0.145378 |
| median_spread_pct | 2.3e-05 |
| n_high_spread | 112 |
| n_low_spread | 198 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=112) | 16.8 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (other) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **43.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
