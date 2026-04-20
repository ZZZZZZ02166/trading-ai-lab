---
hypothesis_number: H48
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: directly_tested
observations: 563
signals: 192
primary_metric: spearman_r_fh_rv_vs_session_range
metric_value: 0.6097
---

# H48: High First-Hour RV Justifies Holding RP-Long Past 60 Min (H4)

**✅ SUPPORTED**

> 🔬 **Directly tested** on live QQQ price/options data.

**Linked hypothesis:** _High First-Hour RV Justifies Holding RP-Long Past 60 Min (H4)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 563 |
| Rows after validation | 563 |
| Rows excluded | 0 |
| Exclusion reason | missing session_range or fh_rv |
| Final observations tested | 563 |
| Signal days | 192 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 563 |
| Signals | 192 |
| Primary Metric | spearman_r_fh_rv_vs_session_range |
| Metric Value | 0.6097 |
| Data Source | ivolatility |
| Data Notes | directly_tested |
| Support Threshold | 0.15 |
| Reject Threshold | 0.05 |

## Verdict

**✅ SUPPORTED**

First-hour RV predicts session range: r=0.610, p=0.0000, med_diff=0.0077, Cliff's d=0.739

## Extra Metrics

| Metric | Value |
|--------|-------|
| spearman_r | 0.6097 |
| p_spearman | 0.0 |
| n_low_rv | 186 |
| n_mid_rv | 185 |
| n_high_rv | 192 |
| median_range_low_rv | 0.00896 |
| median_range_mid_rv | 0.01132 |
| median_range_high_rv | 0.01663 |
| median_diff_high_vs_low | 0.00767 |
| cliffs_delta | 0.7392 |
| p_mannwhitney | 0.0 |
| is_monotonic | True |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `exact_underlying` (explicit) |
| Sample Adequacy (N_eff=563) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `correlation` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **85.0** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `spearman`
CI: [0.5550, 0.6591] (fisher_z_transform)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.

---

## Phase 2 — Intraday Robustness

**Classification:** intraday_primary  
**Phase 2 Verdict:** ✅ SUPPORTED  
**Reason:** diff=0.0035 > 0.003, p=0.0000 < 0.1, consistent  
**Phase 1 Alignment:** extends

> Phase 1 stripped RP-Long conditioning. Phase 2 tests unconditional: high fh_rv → larger afternoon range.

### Walk Forward Session

| Split | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| full | 0.0060 | 0.0000 | 0.676 | 281 | 282 |
| train | 0.0036 | 0.0000 | 0.496 | 101 | 151 |
| val | 0.0085 | 0.0000 | 0.815 | 130 | 120 |
| holdout | 0.0070 | 0.0000 | 0.869 | 50 | 11 |
**Consistency:** consistent (3/3 splits positive)

### Walk Forward Afternoon

| Split | diff | p | cliff_d | n_a | n_b |
|---|---|---|---|---|---|
| full | 0.0035 | 0.0000 | 0.536 | 281 | 282 |
| train | 0.0025 | 0.0000 | 0.403 | 101 | 151 |
| val | 0.0047 | 0.0000 | 0.630 | 130 | 120 |
| holdout | 0.0051 | 0.0000 | 0.924 | 50 | 11 |
**Consistency:** consistent (3/3 splits positive)

---

## Phase 3 — Trading Utility Test

**Verdict:** ✅ SUPPORTED — Trading Useful
**Signal Strength Tier:** core-strong
**Role:** intraday_confirmation
**Signal:** fh_rv > rolling 252d median of fh_rv (binary)
**Primary Outcome:** aw_range (10:30-11:59, core 1.5h)
**n:** 563
**Verdict Reason:** cliff_d_aw_core=0.672, p=0.0000, sign_ok=True

| Split | Cliff's d | p | n_a | n_b |
|---|---|---|---|---|
| full | 0.672 | 0.0000 | 287 | 276 |
| train | 0.590 | 0.0000 | 114 | 138 |
| val | 0.732 | 0.0000 | 124 | 126 |
| holdout | 0.711 | 0.0002 | 49 | 12 |
**Consistency:** consistent (3/3)
