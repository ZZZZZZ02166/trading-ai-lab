---
hypothesis_number: H61
verdict: rejected
ticker: QQQ
start_date: 2025-04-01
end_date: 2025-12-31
data_source: ivolatility
data_notes: directly_tested
observations: 190
signals: 175
primary_metric: containment_rate_diff_inside_vs_outside_open
metric_value: 0.0000
---

# H61: Opening Inside Put/Call Wall Range Predicts Session Containment

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Opening Inside Put/Call Wall Range Predicts Session Containment_

## Data Coverage

| | |
|---|---|
| Tested window | 2025-04-01 → 2025-12-31 |
| Raw rows loaded | 190 |
| Rows after validation | 190 |
| Rows excluded | 0 |
| Exclusion reason | Requires valid put_wall and call_wall; OHLC from daily_series |
| Final observations tested | 190 |
| Signal days | 175 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2025-04-01 |
| End Date | 2025-12-31 |
| Observations | 190 |
| Signals | 175 |
| Primary Metric | containment_rate_diff_inside_vs_outside_open |
| Metric Value | 0.0000 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.1 |
| Reject Threshold | 0.0 |

## Verdict

**❌ REJECTED**

UNTESTABLE AS DEFINED: Wall width averages $35.93 (~7.3% of underlying), while the typical QQQ daily range is 1.5% and only 7 sessions in the test window had a range exceeding 3.7%. Close-based containment is structurally guaranteed (100% for both inside-open and outside-open groups) because a session would need to move ~$18 ($35.93/2) to breach one wall, which almost never occurs. The diff=0 does not mean walls have no effect — it means this metric cannot measure containment when walls are 5x the typical daily range. Lookahead note: walls use same-day EOD OI; the open is observed before that OI is final.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_inside_open | 175 |
| n_outside_open | 15 |
| pct_inside_open | 0.921 |
| containment_rate_inside | 1.0 |
| containment_rate_outside | 1.0 |
| p_fisher_exact | 1.0 |
| p_binomial | 1.0 |
| mean_wall_width | 35.93 |
| review_note | Metric trivially satisfied: wall width ~5x typical daily range. Test cannot distinguish wall-containment from no-wall baseline. |
| mean_wall_width_pct_of_underlying | 7.33 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=175) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `strategy_win_rate` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `binomial`
CI: [0.0000, 0.0016] (wilson_interval)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2025-04-01 → 2025-12-31. Results may not generalise to other tickers, regimes, or time periods without further testing.
