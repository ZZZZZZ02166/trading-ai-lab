---
hypothesis_number: H16
verdict: inconclusive
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 565
signals: 16
primary_metric: mean_iv_drop_post_fomc_vpts
metric_value: 0.2718
---

# H16: Intraday IV Crush After Economic Data Releases Decays Within 15 Minutes

**🟡 INCONCLUSIVE**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** [[Intraday IV Crush After Economic Data Releases Decays Within 15 Minutes]]

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 565 |
| Rows excluded | 0 |
| Exclusion reason | FOMC events outside window or insufficient pre/post trading days around announcement |
| Final observations tested | 565 |
| Signal days | 16 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 565 |
| Signals | 16 |
| Primary Metric | mean_iv_drop_post_fomc_vpts |
| Metric Value | 0.2718 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 1.0 |
| Reject Threshold | -0.5 |

## Verdict

**🟡 INCONCLUSIVE**

Drop present (0.27 vpts) but threshold not met (need pre_pct ≥ 0.40 AND drop ≥ 1.0 AND p < 0.05). pre_pct=0.48, p=0.3951

## Extra Metrics

| Metric | Value |
|--------|-------|
| n_fomc_events | 16 |
| mean_pre_iv_pct_rank | 0.4755 |
| mean_drop_vpts | 0.2718 |
| t_stat | 0.8756 |
| p_value | 0.3951 |
| fomc_dates_used | ['2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12', '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18', '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18', '2025-07-30', '2025-09-17', '2025-10-29', '2025-12-10'] |

## Event Records (up to 20)

| Date | Signal | Outcome | Notes |
|------|--------|---------|-------|
| 2024-01-31 | 0.1591 | 0.0334 | pre_pct=0.17, pre_iv=0.1591, drop=0.0334 |
| 2024-03-20 | 0.1731 | 0.0031 | pre_pct=0.37, pre_iv=0.1731, drop=0.0031 |
| 2024-05-01 | 0.1911 | 0.0072 | pre_pct=0.59, pre_iv=0.1911, drop=0.0072 |
| 2024-06-12 | 0.1496 | 0.0000 | pre_pct=0.06, pre_iv=0.1496, drop=0.0000 |
| 2024-07-31 | 0.2254 | -0.0225 | pre_pct=0.82, pre_iv=0.2254, drop=-0.0225 |
| 2024-09-18 | 0.2017 | 0.0164 | pre_pct=0.68, pre_iv=0.2017, drop=0.0164 |
| 2024-11-07 | 0.2195 | 0.0066 | pre_pct=0.75, pre_iv=0.2195, drop=0.0066 |
| 2024-12-18 | 0.1496 | -0.0099 | pre_pct=0.08, pre_iv=0.1496, drop=-0.0099 |
| 2025-01-29 | 0.1761 | 0.0101 | pre_pct=0.40, pre_iv=0.1761, drop=0.0101 |
| 2025-03-19 | 0.2580 | -0.0001 | pre_pct=0.92, pre_iv=0.2580, drop=-0.0001 |
| 2025-05-07 | 0.2466 | 0.0056 | pre_pct=0.90, pre_iv=0.2466, drop=0.0056 |
| 2025-06-18 | 0.1867 | -0.0037 | pre_pct=0.53, pre_iv=0.1867, drop=-0.0037 |
| 2025-07-30 | 0.1574 | -0.0107 | pre_pct=0.15, pre_iv=0.1574, drop=-0.0107 |
| 2025-09-17 | 0.1602 | 0.0020 | pre_pct=0.19, pre_iv=0.1602, drop=0.0020 |
| 2025-10-29 | 0.1872 | -0.0020 | pre_pct=0.54, pre_iv=0.1872, drop=-0.0020 |
| 2025-12-10 | 0.1796 | 0.0079 | pre_pct=0.47, pre_iv=0.1796, drop=0.0079 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=16) | 16.8 | 25 | Independence-adjusted count |
| Effect Size | 5.4 | 20 | Family: `iv_level_change` (stored) |
| Statistical Reliability | 0.0 | 20 | FDR-within-family p: 0.5956 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **32.3** | **100** | |

**Priority: 🔴 DEPRIORITIZE**  Stat test: `value`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
