---
hypothesis_number: H26
verdict: insufficient_data
ticker: VX
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: insufficient_data
observations: 0
signals: 0
primary_metric: vix_roll_yield_first_last_hour_vs_mid
metric_value: N/A
---

# H26: Intraday VIX Futures Roll Yield Is Concentrated in the First and Last Hour

**⬜ INSUFFICIENT DATA**

> ❓ **Insufficient data** — required data was unavailable (endpoint entitlement or coverage gap). No verdict can be drawn.

**Linked hypothesis:** [[Intraday VIX Futures Roll Yield Is Concentrated in the First and Last Hour]]

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 0 |
| Rows excluded | 565 |
| Exclusion reason | VIX futures intraday data not present in current dataset |
| Final observations tested | 0 |
| Signal days | 0 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | VX |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 0 |
| Signals | 0 |
| Primary Metric | vix_roll_yield_first_last_hour_vs_mid |
| Metric Value | N/A |
| Data Source | ivolatility |
| Data Notes | insufficient_data |
| Support Threshold | 0.0 |
| Reject Threshold | -0.5 |

## Verdict

**⬜ INSUFFICIENT DATA**

Requires intraday VIX futures and VIX spot data by time of day. VIX futures data not present — this test requires a separate data source (e.g., CBOE futures settlement files or a futures data vendor).

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (D) | 0 | 25 | Data fidelity: `insufficient` (explicit) |
| Sample Adequacy (N_eff=0) | 0.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **0.0** | **100** | |

**Priority: ⬜ BLOCKED**  Stat test: `—`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: VX only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
