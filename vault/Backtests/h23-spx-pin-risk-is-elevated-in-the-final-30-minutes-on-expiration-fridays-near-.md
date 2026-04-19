---
hypothesis_number: H23
verdict: insufficient_data
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: insufficient_data
observations: 0
signals: 0
primary_metric: final30_range_vs_nearby_oi_strike
metric_value: N/A
---

# H23: SPX Pin Risk Is Elevated in the Final 30 Minutes on Expiration Fridays Near Large Open-Interest Strikes

**⬜ INSUFFICIENT DATA**

> ❓ **Insufficient data** — required data was unavailable (endpoint entitlement or coverage gap). No verdict can be drawn.

> ⚠️ **Instrument note**: Original hypothesis references SPX. This test was run on **QQQ** as an adaptation. QQQ tracks Nasdaq-100; SPX-specific microstructure effects may differ.

**Linked hypothesis:** [[SPX Pin Risk Is Elevated in the Final 30 Minutes on Expiration Fridays Near Large Open-Interest Strikes]]

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 0 |
| Rows excluded | 565 |
| Exclusion reason | Intraday price/options data unavailable — iVolatility subscription does not include intraday endpoints |
| Final observations tested | 0 |
| Signal days | 0 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 0 |
| Signals | 0 |
| Primary Metric | final30_range_vs_nearby_oi_strike |
| Metric Value | N/A |
| Data Source | ivolatility |
| Data Notes | insufficient_data |
| Support Threshold | 0.0 |
| Reject Threshold | -0.5 |

## Verdict

**⬜ INSUFFICIENT DATA**

Requires intraday price bars (last 30 minutes) and strike-level open interest data to identify pinning. Intraday data unavailable.

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

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
