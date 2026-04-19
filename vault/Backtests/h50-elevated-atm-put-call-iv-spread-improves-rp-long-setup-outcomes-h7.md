---
hypothesis_number: H50
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: proxy_tested
observations: 546
signals: 195
primary_metric: median_next_return_diff_elevated_vs_normal_skew
metric_value: 0.0007
---

# H50: Elevated ATM Put-Call IV Spread Improves RP-Long Setup Outcomes (H7)

**❌ REJECTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _Elevated ATM Put-Call IV Spread Improves RP-Long Setup Outcomes (H7)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 546 |
| Rows after validation | 546 |
| Rows excluded | 0 |
| Exclusion reason | — |
| Final observations tested | 546 |
| Signal days | 195 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 546 |
| Signals | 195 |
| Primary Metric | median_next_return_diff_elevated_vs_normal_skew |
| Metric Value | 0.0007 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

No predictive edge from put-call spread: elev=0.00198 vs normal=0.00131 (diff=0.00067, p=0.8924). Caveat: ATM spread is imprecise skew proxy.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_elevated | 195 |
| n_normal | 351 |
| median_return_elevated | 0.00198 |
| median_return_normal | 0.00131 |
| spearman_r | 0.0355 |
| p_spearman | 0.4077 |
| cliffs_delta | 0.007 |
| p_mannwhitney | 0.8924 |
| pct_elevated_days | 0.357 |
| skew_proxy_caveat | ATM 30d put-call spread, not true 25-delta skew |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=195) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.8502 · IQ: strong |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **55.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `spearman`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
