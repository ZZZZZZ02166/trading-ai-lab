---
hypothesis_number: H100
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 564
signals: 224
primary_metric: median_range_diff_large_vs_small_gap
metric_value: 0.0039
---

# H100: Overnight Gap Magnitude Predicts Same-Session Realized Range (0DTE Entry Confirmation)

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Overnight Gap Magnitude Predicts Same-Session Realized Range (0DTE Entry Confirmation)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 1-day gap requires prev close; same-session high/low/close |
| Final observations tested | 564 |
| Signal days | 224 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 224 |
| Primary Metric | median_range_diff_large_vs_small_gap |
| Metric Value | 0.0039 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.004 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

diff_median_range=0.00386 (large_gap=0.01368, small_gap=0.00982), p_mannwhitney=0.0000, n_large=224, n_small=77, pct_days_large_gap=0.397, median_gap_pct=0.00395. Practical use: large gap at open → expect expanded intraday range → avoid 0DTE short straddle entry at open.

## Extra Metrics

| Metric | Value |
|--------|-------|
| median_range_large_gap | 0.013682 |
| median_range_small_gap | 0.009819 |
| n_large_gap | 224 |
| n_small_gap | 77 |
| pct_days_large_gap | 0.3972 |
| median_gap_pct | 0.003946 |
| p_mannwhitney | 3e-06 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=224) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (other) |
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
