---
hypothesis_number: H34
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: proxy_tested
observations: 534
signals: 304
primary_metric: mean_implied_minus_realized_fwd_vol_vpts
metric_value: 0.7469
---

# H34: QQQ Forward Volatility Implied by Term Structure Exceeds Subsequently Realized Forward Vol (Forward Variance Premium)

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _QQQ Forward Volatility Implied by Term Structure Exceeds Subsequently Realized Forward Vol (Forward Variance Premium)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 534 |
| Rows excluded | 30 |
| Exclusion reason | rows without paired fwd window or missing iv_30d/iv_60d excluded |
| Final observations tested | 534 |
| Signal days | 304 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 534 |
| Signals | 304 |
| Primary Metric | mean_implied_minus_realized_fwd_vol_vpts |
| Metric Value | 0.7469 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 1.0 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

Direction present (diff=0.75 vpts) but threshold/significance not met (need >1.0 AND p<0.05). p=0.0725 n=534.

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_implied_fwd_vol | 19.673 |
| mean_realized_fwd_vol | 18.926 |
| p_ttest | 0.0725 |
| n_obs | 534 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=534) | 24.2 | 25 | Independence-adjusted count |
| Effect Size | 10.0 | 20 | Family: `premium_mean` (stored) |
| Statistical Reliability | 8.5 | 20 | FDR-within-family p: 0.0725 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **52.7** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `ttest`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
