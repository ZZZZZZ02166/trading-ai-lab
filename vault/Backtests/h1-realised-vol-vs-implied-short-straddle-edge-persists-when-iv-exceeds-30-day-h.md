---
hypothesis_number: H1
verdict: supported
ticker: QQQ
start_date: 2024-01-01
end_date: 2026-04-05
data_source: ivolatility
data_notes: proxy_tested
observations: 526
signals: 246
primary_metric: mean_variance_premium_signal_days_vpts
metric_value: 1.8417
---

# H1: Realised Vol vs. Implied: Short Straddle Edge Persists When IV Exceeds 30-Day HV

**✅ SUPPORTED**

> ⚠️ **Proxy tested** — result uses IVX constant-maturity index as IV proxy, not specific option contracts. Evidence strength is lower than a direct test.

**Linked hypothesis:** [[Realised Vol vs. Implied: Short Straddle Edge Persists When IV Exceeds 30-Day HV]]

## Data Coverage

| | |
|---|---|
| Tested window | 2024-01-01 → 2026-04-05 |
| Raw rows loaded | 565 |
| Rows after validation | 526 |
| Rows excluded | 39 |
| Exclusion reason | 20-day lookback warmup (hv_20_cc); 20-day forward window (fwd_rv_20) |
| Final observations tested | 526 |
| Signal days | 246 |

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Ticker | QQQ |
| Start Date | 2024-01-01 |
| End Date | 2026-04-05 |
| Observations | 526 |
| Signals | 246 |
| Primary Metric | mean_variance_premium_signal_days_vpts |
| Metric Value | 1.8417 |
| Data Source | ivolatility |
| Data Notes | proxy_tested |
| Support Threshold | 1.0 |
| Reject Threshold | 0.0 |

## Verdict

**✅ SUPPORTED**

Mean variance premium on IV>HV+2pt days: 1.84 vol pts (vs -0.61 on non-signal days), p=0.0000

## Extra Metrics

| Metric | Value |
|--------|-------|
| mean_vp_signal_days_vpts | 1.8417 |
| mean_vp_non_signal_days_vpts | -0.6098 |
| n_signal_days | 246 |
| n_non_signal_days | 280 |
| iv_hv_threshold_vpts | 2.0 |
| t_stat | 5.23 |
| p_value | 0.0 |

## Event Records (up to 20)

| Date | Signal | Outcome | Notes |
|------|--------|---------|-------|
| 2024-02-16 | 2.0300 | -1.4170 | iv=0.1705 hv=0.1502 fwd_rv=0.1847 |
| 2024-02-20 | 3.0510 | 0.0200 | iv=0.1839 hv=0.1533 fwd_rv=0.1837 |
| 2024-02-21 | 2.8870 | 0.1450 | iv=0.1825 hv=0.1536 fwd_rv=0.1810 |
| 2024-04-01 | 2.3540 | -1.6440 | iv=0.1656 hv=0.1421 fwd_rv=0.1821 |
| 2024-04-02 | 2.5660 | -1.2170 | iv=0.1705 hv=0.1449 fwd_rv=0.1827 |
| 2024-04-03 | 4.1870 | -2.0930 | iv=0.1707 hv=0.1289 fwd_rv=0.1917 |
| 2024-04-04 | 4.9490 | -0.3420 | iv=0.1885 hv=0.1390 fwd_rv=0.1919 |
| 2024-04-05 | 4.5820 | -1.2210 | iv=0.1803 hv=0.1345 fwd_rv=0.1925 |
| 2024-04-08 | 5.4200 | -2.3520 | iv=0.1781 hv=0.1239 fwd_rv=0.2017 |
| 2024-04-09 | 5.3610 | -2.8480 | iv=0.1772 hv=0.1236 fwd_rv=0.2057 |
| 2024-04-10 | 6.4300 | -2.4330 | iv=0.1809 hv=0.1166 fwd_rv=0.2053 |
| 2024-04-11 | 4.6030 | -2.9670 | iv=0.1731 hv=0.1271 fwd_rv=0.2028 |
| 2024-04-12 | 5.4370 | -0.0140 | iv=0.1943 hv=0.1399 fwd_rv=0.1944 |
| 2024-04-15 | 6.3490 | 2.3800 | iv=0.2094 hv=0.1460 fwd_rv=0.1856 |
| 2024-04-16 | 5.8890 | 2.6930 | iv=0.2014 hv=0.1425 fwd_rv=0.1745 |
| 2024-04-17 | 5.6970 | 2.9310 | iv=0.2046 hv=0.1476 fwd_rv=0.1753 |
| 2024-04-18 | 6.8060 | 3.4020 | iv=0.2077 hv=0.1396 fwd_rv=0.1737 |
| 2024-04-19 | 6.7530 | 4.7410 | iv=0.2191 hv=0.1515 fwd_rv=0.1717 |
| 2024-04-22 | 4.6650 | 5.7950 | iv=0.2050 hv=0.1584 fwd_rv=0.1471 |
| 2024-04-23 | 2.2640 | 4.7480 | iv=0.1934 hv=0.1707 fwd_rv=0.1459 |

## Phase 1 Screening

| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Evidence Tier (C) | 10 | 25 | Data fidelity: `index_proxy` (explicit) |
| Sample Adequacy (N_eff=526) | 24.0 | 25 | Independence-adjusted count |
| Effect Size | 20.0 | 20 | Family: `premium_mean` (stored) |
| Statistical Reliability | 17.0 | 20 | FDR-within-family p: 0.0000 · IQ: standard |
| Stability | 0.0 | 10 | Not measured (0 pts) |
| **Phase 1 Score** | **71.0** | **100** | |

**Priority: 🟡 WATCHLIST**  Stat test: `value`
CI: Not available (mean_std_not_in_extra_metrics)

## How to Interpret

- **Supported**: Evidence is consistent with the hypothesis in this test window. Not a proof — regime-specific.
- **Rejected**: Evidence contradicts the hypothesis claim in this test window.
- **Inconclusive**: Direction may be correct but statistical significance was not reached, or threshold not met.
- **Insufficient Data**: Required data was unavailable. No statistical verdict is possible.

**Scope**: QQQ only, 2024-01-01 → 2026-04-05. Results may not generalise to other tickers, regimes, or time periods without further testing.
