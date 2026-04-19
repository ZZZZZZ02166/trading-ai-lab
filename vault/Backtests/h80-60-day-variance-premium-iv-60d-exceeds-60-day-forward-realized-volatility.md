---
hypothesis_number: H80
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 505
signals: 505
primary_metric: mean_vp_60d
metric_value: 0.0044
---

# H80: 60-Day Variance Premium: iv_60d Exceeds 60-Day Forward Realized Volatility

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _60-Day Variance Premium: iv_60d Exceeds 60-Day Forward Realized Volatility_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 505 |
| Rows excluded | 60 |
| Exclusion reason | 60-day forward window: requires 60 future log returns (last 60 rows excluded) |
| Final observations tested | 505 |
| Signal days | 505 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 505 |
| Signals | 505 |
| Primary Metric | mean_vp_60d |
| Metric Value | 0.0044 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.01 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

mean_vp_60d=0.0044 positive but below 1 vol point threshold. Forward realized vol windows overlap by ~59/60 days. t-test p=0.1334 treats 505 obs as independent — effective N ≈ 8 non-overlapping blocks. Mean sign and magnitude are primary evidence.

## Extra Metrics

| Metric | Value |
|--------|-------|
| pct_days_positive_vp | 0.6515 |
| median_vp_60d | 0.015017 |
| p_ttest_vs_zero_approx | 0.133443 |
| t_stat_approx | 1.5031 |
| effective_n_approx | 8 |
| comparison_mean_vp_20d | 1.8417 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=505) | 23.4 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **33.4** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
