---
hypothesis_number: H40
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: proxy_tested
observations: 545
signals: 162
primary_metric: win_rate_calendar_signal_days
metric_value: 0.7284
---

# H40: QQQ Calendar Spread P&L Is Positive When Front-Month IV Exceeds GARCH-Implied Forward Vol by More Than 2 Vol Points

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _QQQ Calendar Spread P&L Is Positive When Front-Month IV Exceeds GARCH-Implied Forward Vol by More Than 2 Vol Points_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 564 |
| Rows after validation | 545 |
| Rows excluded | 19 |
| Exclusion reason | rows with missing iv_30d, garch_vol, or fwd_rv_20 excluded |
| Final observations tested | 545 |
| Signal days | 162 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 545 |
| Signals | 162 |
| Primary Metric | win_rate_calendar_signal_days |
| Metric Value | 0.7284 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.6 |
| Reject Threshold | 0.5 |

## Verdict

**✅ SUPPORTED**

Signal days win_rate=0.728 > 0.6 p=0.0000 n=162 mean_VP=2.22vpts.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_signal_days | 162 |
| n_nonsignal_days | 383 |
| n_wins_on_signal | 118 |
| win_rate_nonsignal | 0.624 |
| mean_vp_signal_vpts | 2.223 |
| p_binomial | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=162) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **71.5** | **100** | |

**Priority: 🟡 WATCHLIST**  Stat test: `binomial`
CI: [0.6599, 0.7969] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
