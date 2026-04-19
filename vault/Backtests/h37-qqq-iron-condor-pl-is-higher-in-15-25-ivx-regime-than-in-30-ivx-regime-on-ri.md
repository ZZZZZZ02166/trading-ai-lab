---
hypothesis_number: H37
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: proxy_tested
observations: 545
signals: 471
primary_metric: sharpe_ratio_mid_vs_fear_regime
metric_value: -0.0828
---

# H37: QQQ Iron Condor P&L Is Higher in 15-25% IVX Regime Than in >30% IVX Regime on Risk-Adjusted Basis

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _QQQ Iron Condor P&L Is Higher in 15-25% IVX Regime Than in >30% IVX Regime on Risk-Adjusted Basis_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 545 |
| Rows excluded | 19 |
| Exclusion reason | rows with missing iv_30d or fwd_rv_20 excluded |
| Final observations tested | 545 |
| Signal days | 471 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 545 |
| Signals | 471 |
| Primary Metric | sharpe_ratio_mid_vs_fear_regime |
| Metric Value | -0.0828 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.2 |
| Reject Threshold | -0.2 |

## Verdict

**🟡 INCONCLUSIVE**

diff=-0.083 not conclusive. sharpe_mid=0.075 sharpe_fear=0.158 p=0.4714.

## Extra Metrics

| Metric | Value |
|--------|-------|
| sharpe_mid_15_25 | 0.075 |
| sharpe_fear_30plus | 0.1578 |
| sharpe_low_sub15 | -0.2646 |
| n_mid | 471 |
| n_fear | 15 |
| n_low | 35 |
| p_ttest | 0.4714 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=471) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_sharpe` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.4714 · IQ: standard |
| Stability | 0.0 | 10 | Measured (consistency: 0%) |
| **Phase 1 Score** | **34.5** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `ttest`
CI: Not available (requires_raw_return_series)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
