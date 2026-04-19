---
hypothesis_number: H19
verdict: insufficient_data
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: insufficient_data
observations: 0
signals: 0
primary_metric: mean_skew_change_after_pm_decline
metric_value: N/A
---

# H19: Intraday IV Skew Steepens After Afternoon Declines Larger Than 0.75%

**⬜ INSUFFICIENT DATA**

> ❓ **Insufficient data** — required data was unavailable (endpoint entitlement or coverage gap). No verdict can be drawn.

**Linked hypothesis:** [[Intraday IV Skew Steepens After Afternoon Declines Larger Than 0.75%]]

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 197 |
| Rows after validation | 0 |
| Rows excluded | 197 |
| Exclusion reason | Intraday price/options data unavailable — iVolatility subscription does not include intraday endpoints |
| Final observations tested | 0 |
| Signal days | 0 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 0 |
| Signals | 0 |
| Primary Metric | mean_skew_change_after_pm_decline |
| Metric Value | N/A |
| Data Source | ivolatility |
| Data Notes | insufficient_data |
| Support Threshold | 0.0 |
| Reject Threshold | -0.05 |

## Verdict

**⬜ INSUFFICIENT DATA**

Insufficient coverage across months: combined from M1+M2+M3+M4+M5+M6+M7+M8+M9: 5/197 days

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (D) | 0 | 25 | Data fidelity: `insufficient` (explicit) |
| Sample Adequacy (N_eff=0) | 0.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `iv_level_change` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **0.0** | **100** | |

**Priority: ⬜ BLOCKED**  Stat test: `—`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
