---
hypothesis_number: H49
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-01
data_source: ivolatility
data_notes: proxy_tested
observations: 546
signals: 238
primary_metric: spearman_r_iv_vs_rv_iv_ratio
metric_value: 0.2895
---

# H49: IV Regime Predicts Whether Setup Outcome Justifies Long vs Short Premium (H5)

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** _IV Regime Predicts Whether Setup Outcome Justifies Long vs Short Premium (H5)_

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-01 |
| Raw rows loaded | 565 |
| Rows after validation | 546 |
| Rows excluded | 19 |
| Exclusion reason | missing iv_30d, OHLC, or insufficient rolling history |
| Final observations tested | 546 |
| Signal days | 238 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-01 |
| Observations | 546 |
| Signals | 238 |
| Primary Metric | spearman_r_iv_vs_rv_iv_ratio |
| Metric Value | 0.2895 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.1 |
| Reject Threshold | 0.05 |

## Verdict

**✅ SUPPORTED**

IV level predicts realized/implied ratio: r=0.289, p=0.0000. High-IV median ratio=1.15 vs low-IV=0.88

## Extra Metrics

| Metric | Value |
|--------|-------|
| spearman_r | 0.2895 |
| p_spearman | 0.0 |
| n_low_iv | 180 |
| n_mid_iv | 128 |
| n_high_iv | 238 |
| median_ratio_low_iv | 0.8824 |
| median_ratio_mid_iv | 1.0079 |
| median_ratio_high_iv | 1.1522 |
| median_diff_high_vs_low | 0.2698 |
| cliffs_delta | 0.3683 |
| p_mannwhitney | 0.0 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (B) | 20 | 25 | Data fidelity: `constant_maturity_iv` (explicit) |
| Sample Adequacy (N_eff=546) | 24.5 | 25 | Independence-adjusted count |
| Effect Size | 19.3 | 20 | Family: `correlation` (stored) |
| Statistical Reliability | 20.0 | 20 | FDR-within-family p: 0.0000 · IQ: strong |
| Stability | 10.0 | 10 | Measured (consistency: 100%) |
| **Phase 1 Score** | **93.8** | **100** | |

**Priority: 🟢 PROMOTE**  Stat test: `spearman`
CI: [0.2107, 0.3646] (fisher_z_transform)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-01. Results may not generalise to other tickers, regimes, or time periods without further testing.
