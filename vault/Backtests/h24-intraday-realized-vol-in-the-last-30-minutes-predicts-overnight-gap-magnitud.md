---
hypothesis_number: H24
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 564
signals: 564
primary_metric: daily_range_vs_overnight_gap_spearman_r
metric_value: 0.2407
---

# H24: Intraday Realized Vol in the Last 30 Minutes Predicts Overnight Gap Magnitude

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** [[Intraday Realized Vol in the Last 30 Minutes Predicts Overnight Gap Magnitude]]

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 564 |
| Rows excluded | 1 |
| Exclusion reason | 1 row lost to forward shift for overnight gap; OHLC NaN rows excluded |
| Final observations tested | 564 |
| Signal days | 564 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 564 |
| Signals | 564 |
| Primary Metric | daily_range_vs_overnight_gap_spearman_r |
| Metric Value | 0.2407 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 0.15 |
| Reject Threshold | -0.1 |

## Verdict

**✅ SUPPORTED**

Positive correlation between daily range and overnight gap: r=0.241, p=0.0000 (564 obs). Higher within-day vol precedes larger overnight gaps.

## Extra Metrics

| Metric | Value |
|--------|-------|
| spearman_r | 0.2407 |
| p_value | 0.0 |
| n_observations | 564 |
| mean_daily_range | 0.0141 |
| mean_overnight_gap_abs | 0.0057 |

## Event Records (up to 20)

| Date | Signal | Outcome | Notes |
|------|--------|---------|-------|
| 2024-08-02 | 0.0202 | 0.0551 | range=0.0202, gap=0.0551 |
| 2025-04-02 | 0.0294 | 0.0423 | range=0.0294, gap=0.0423 |
| 2025-05-09 | 0.0109 | 0.0382 | range=0.0109, gap=0.0382 |
| 2025-01-24 | 0.0106 | 0.0358 | range=0.0106, gap=0.0358 |
| 2025-04-04 | 0.0404 | 0.0337 | range=0.0404, gap=0.0337 |
| 2025-04-07 | 0.0997 | 0.0336 | range=0.0997, gap=0.0336 |
| 2025-04-22 | 0.0227 | 0.0303 | range=0.0227, gap=0.0303 |
| 2025-04-03 | 0.0218 | 0.0282 | range=0.0218, gap=0.0282 |
| 2025-04-09 | 0.1261 | 0.0271 | range=0.1261, gap=0.0271 |
| 2024-09-18 | 0.0169 | 0.0234 | range=0.0169, gap=0.0234 |
| 2024-07-30 | 0.0266 | 0.0223 | range=0.0266, gap=0.0223 |
| 2025-04-11 | 0.0325 | 0.0219 | range=0.0325, gap=0.0219 |
| 2024-02-21 | 0.0096 | 0.0206 | range=0.0096, gap=0.0206 |
| 2025-04-15 | 0.0136 | 0.0198 | range=0.0136, gap=0.0198 |
| 2026-03-02 | 0.0199 | 0.0195 | range=0.0199, gap=0.0195 |
| 2025-11-19 | 0.0194 | 0.0194 | range=0.0194, gap=0.0194 |
| 2024-08-01 | 0.0415 | 0.0193 | range=0.0415, gap=0.0193 |
| 2025-01-16 | 0.0118 | 0.0189 | range=0.0118, gap=0.0189 |
| 2024-02-12 | 0.0103 | 0.0187 | range=0.0103, gap=0.0187 |
| 2026-04-01 | 0.0126 | 0.0179 | range=0.0126, gap=0.0179 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=564) | 25.0 | 25 | Independence-adjusted count |
| Effect Size | 16.0 | 20 | Family: `correlation` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **68.0** | **100** | |

**Priority: 🟡 WATCHLIST**  Stat test: `value`
CI: [0.1613, 0.3170] (fisher_z_transform)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
