---
hypothesis_number: H95
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 535
signals: 284
primary_metric: mean_return_diff_high_vs_low_spread
metric_value: 0.0012
---

# H95: ATM Put-Call IV Spread (IVX 30d) Elevated Above Rolling Median Associates with Lower Next-Session Returns

**❌ REJECTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _ATM Put-Call IV Spread (IVX 30d) Elevated Above Rolling Median Associates with Lower Next-Session Returns_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 535 |
| Rows excluded | 30 |
| Exclusion reason | ivx join + 90-day rolling median warmup + 1-day forward return |
| Final observations tested | 535 |
| Signal days | 284 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 535 |
| Signals | 284 |
| Primary Metric | mean_return_diff_high_vs_low_spread |
| Metric Value | 0.0012 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | -0.001 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

diff_mean_return=0.00124 (high_spread=0.00116, low_spread=-0.00008), p_mannwhitney=0.8117, n_high=284, n_low=251, median_pc_iv_spread=-0.00276. Note: IVX ATM composite IV — not chain-derived skew. Associative finding only.

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_return_high_spread | 0.001164 |
| mean_return_low_spread | -7.7e-05 |
| median_pc_iv_spread | -0.002765 |
| n_high_spread | 284 |
| n_low_spread | 251 |
| p_mannwhitney | 0.811668 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (derived) |
| Sample Adequacy (N_eff=284) | 24.2 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.9834 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **34.2** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `mannwhitney`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
