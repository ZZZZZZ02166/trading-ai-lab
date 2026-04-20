# Phase 2 Batch Summary — Intraday Robustness

**Run date:** 2026-04-19
**Batch:** H15, H24, H44, H48, H53, H73, H94, H97, H100

| H# | Title | Class | Verdict | Phase 1 Alignment |
|---|---|---|---|---|
| H15 | First-Hour Realised Vol Predicts Full-Day Realised Vol  | intraday_primary | ✅ SUPPORTED | extends |
| H24 | Late-Session (15:30-16:00) RV Predicts Next-Day Overnig | intraday_primary | ✅ SUPPORTED | extends |
| H44 | IV Term Structure Backwardation → Next-Session Intraday | hybrid | ✅ SUPPORTED | confirmed |
| H48 | High First-Hour RV Predicts Larger Afternoon Session Ra | intraday_primary | ✅ SUPPORTED | extends |
| H53 | Pattern 4 (IV Rising, RV Flat) → Next-Session Range Exp | hybrid | ⚠️ INCONCLUSIVE | partial |
| H73 | Compound Signal (Pattern 4 AND Backwardation) → Larger  | hybrid | ❌ REJECTED | extends |
| H94 | Front-End Term Structure (7d/30d) Backwardation → Next- | hybrid | ✅ SUPPORTED | confirmed |
| H97 | IV Velocity (5-Day Pct Change) → Next-Session Range | hybrid | ✅ SUPPORTED | confirmed |
| H100 | Overnight Gap (1m precision) → Same-Session Intraday Ra | intraday_primary | ⚠️ INCONCLUSIVE | extends |

## Verdicts by Category

- **INCONCLUSIVE:** H53, H100
- **REJECTED:** H73
- **SUPPORTED:** H15, H24, H44, H48, H94, H97