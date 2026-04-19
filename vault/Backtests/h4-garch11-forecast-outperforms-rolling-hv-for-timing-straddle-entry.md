---
hypothesis_number: H4
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 526
signals: 284
primary_metric: garch_vp_minus_hv_vp_vpts
metric_value: 0.1128
---

# H4: GARCH(1,1) Forecast Outperforms Rolling HV for Timing Straddle Entry

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** [[GARCH(1,1) Forecast Outperforms Rolling HV for Timing Straddle Entry]]

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 526 |
| Rows excluded | 39 |
| Exclusion reason | 20-day lookback warmup (hv_20_cc); 20-day forward window (fwd_rv_20); GARCH burn-in (garch_vol) |
| Final observations tested | 526 |
| Signal days | 284 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 526 |
| Signals | 284 |
| Primary Metric | garch_vp_minus_hv_vp_vpts |
| Metric Value | 0.1128 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.5 |
| Reject Threshold | 0.0 |

## Verdict

**🟡 INCONCLUSIVE**

GARCH VP=1.59 vpts vs HV VP=1.48 vpts (edge=0.11 vpts) but threshold not met (need ≥ 0.5 AND p < 0.05). p_garch=0.0001

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_vp_garch_signal_vpts | 1.5917 |
| mean_vp_hv_signal_vpts | 1.4789 |
| garch_edge_vpts | 0.1128 |
| n_garch_signal_days | 284 |
| n_hv_signal_days | 327 |
| t_garch_vs_zero | 4.0088 |
| p_garch_vs_zero | 0.0001 |
| t_garch_vs_hv | 0.2251 |
| p_garch_vs_hv | 0.822 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=526) | 24.0 | 25 | Independence-adjusted count |
| Effect Size | 1.5 | 20 | Family: `premium_mean` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0002 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **52.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `garch_vs_zero`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
