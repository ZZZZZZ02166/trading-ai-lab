---
hypothesis_number: H51
verdict: inconclusive
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: proxy_tested
observations: 313
signals: 107
primary_metric: median_next_range_diff_high_vs_normal_pcr
metric_value: -0.0002
---

# H51: Prior-Day Put/Call Volume Ratio vs Baseline Predicts RP-Long Setup Quality (H9)

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Prior-Day Put/Call Volume Ratio vs Baseline Predicts RP-Long Setup Quality (H9)_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 317 |
| Rows after validation | 313 |
| Rows excluded | 4 |
| Exclusion reason | no matching next-session data or missing rolling PCR baseline |
| Final observations tested | 313 |
| Signal days | 107 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 313 |
| Signals | 107 |
| Primary Metric | median_next_range_diff_high_vs_normal_pcr |
| Metric Value | -0.0002 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.002 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

Weak relationship: r=-0.073, p=0.1991, diff=-0.0002. Put chain data covers 2025-04-01–2025-12-31 only (317 PCR dates).

## Extra Metrics

| Metric | Value |
|--------|-------|
| spearman_r_pcr_vs_next_range | -0.0728 |
| p_spearman | 0.1991 |
| n_elevated_pcr | 107 |
| n_normal_pcr | 206 |
| median_range_elevated | 0.01131 |
| median_range_normal | 0.01154 |
| median_diff | -0.00022 |
| cliffs_delta | -0.002 |
| p_mannwhitney | 0.9774 |
| n_pcr_dates | 317 |
| put_data_window | 2025-04-01 to 2025-12-31 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=107) | 24.8 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.5973 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **34.8** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `spearman`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
