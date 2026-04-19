---
hypothesis_number: H71
verdict: rejected
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: directly_tested
observations: 564
signals: 224
primary_metric: gap_fill_rate
metric_value: 0.3304
---

# H71: Opening Gap Fill: Gaps > 0.5% Close Nearer to Prior Close than to Open by End of Session

**❌ REJECTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _Opening Gap Fill: Gaps > 0.5% Close Nearer to Prior Close than to Open by End of Session_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | Rows with NaN in open/close/log_return dropped |
| Final observations tested | 564 |
| Signal days | 224 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 224 |
| Primary Metric | gap_fill_rate |
| Metric Value | 0.3304 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.55 |
| Reject Threshold | 0.5 |

## Verdict

**❌ REJECTED**

Gap fill rate=0.330 (74/224), p_binomial=1.0000. No reliable gap-fill bias for gaps > 0.5%.

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_gap_days | 224 |
| n_filled | 74 |
| p_binomial | 1.0 |
| fill_rate_up_gaps | 0.3233 |
| fill_rate_down_gaps | 0.3407 |
| n_up_gaps | 133 |
| n_down_gaps | 91 |
| pct_gap_days | 0.397 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (derived) |
| Sample Adequacy (N_eff=224) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 0.0 | 20 | Family: `other` (ai_assisted) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 1.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **45.0** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `binomial`
CI: Not available (insufficient_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
