---
hypothesis_number: H58
verdict: insufficient_data
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: insufficient_data
observations: 0
signals: 0
primary_metric: mean_rod_return_diff_call_heavy_vs_put_heavy
metric_value: N/A
---

# H58: First 30-Minute Option Volume Direction Predicts Rest-of-Day Price Direction

**⬜ INSUFFICIENT DATA**

> ❓ **Insufficient data** — required data was unavailable (endpoint entitlement or coverage gap). No verdict can be drawn.

**Linked hypothesis:** _First 30-Minute Option Volume Direction Predicts Rest-of-Day Price Direction_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 0 |
| Rows after validation | 0 |
| Rows excluded | 0 |
| Exclusion reason | Intraday chain data not available in required format |
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
| Primary Metric | mean_rod_return_diff_call_heavy_vs_put_heavy |
| Metric Value | N/A |
| Data Source | ivolatility |
| Data Notes | insufficient_data |
| Support Threshold | 0.0 |
| Reject Threshold | 0.0 |

## Verdict

**⬜ INSUFFICIENT DATA**

H58 requires aggregated call and put volume in the first 30 minutes across the full option chain. Available intraday files (data/raw/chains/intraday_*.parquet) cover only 7–14 specific contracts per date — not a representative sample of total market volume. Computing first-30-min PCR from 7 contracts would produce a misleading signal. Would require a full intraday volume feed (not currently available).

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (D) | 0 | 25 | Data fidelity: `insufficient` (explicit) |
| Sample Adequacy (N_eff=0) | 7.5 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `mean_difference` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: — · IQ: weak |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **7.5** | **100** | |

**Priority: ⬜ BLOCKED**  Stat test: `—`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
