from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BacktestVerdict(str, Enum):
    SUPPORTED = "supported"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"
    INSUFFICIENT_DATA = "insufficient_data"


class TradeRecord(BaseModel):
    date: str
    signal: float
    outcome: float
    notes: str = ""


class BacktestResult(BaseModel):
    backtest_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hypothesis_id: str
    hypothesis_title: str
    hypothesis_number: str  # e.g. "H9"
    ticker: str = "QQQ"
    period_start: str        # ISO date string "2024-01-01" — frozen test window start
    period_end: str          # ISO date string "2026-04-05" — frozen test window end

    # ── Data pipeline counts ──────────────────────────────────────────────────────
    raw_rows: int = 0              # rows in daily_series after window filter, before dropna
    rows_after_validation: int = 0 # rows with all required columns non-NaN
    rows_excluded: int = 0         # raw_rows - rows_after_validation
    exclusion_reason: str = ""     # why rows were excluded (warmup, forward window, etc.)
    n_observations: int = 0        # rows_after_validation (same as above; kept for API compat)
    n_signals: int = 0             # rows matching the entry signal condition

    metric_name: str         # e.g. "rmse_ratio", "mean_iv_drop_vpts"
    metric_value: float
    support_threshold: float  # metric value above which we call SUPPORTED
    reject_threshold: float   # metric value below which we call REJECTED
    verdict: BacktestVerdict
    verdict_reason: str
    # "directly_tested" | "proxy_tested" | "insufficient_data"
    data_notes: str
    trades: list[TradeRecord] = Field(default_factory=list)
    extra_metrics: dict = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    data_source: str = "ivolatility"

    # Optional fields set by runners to improve Phase 1 scoring accuracy.
    # When not set, 19b_score_phase1.py derives conservative defaults.
    data_fidelity: Optional[str] = None
    # "exact_contract"       — actual option contract data (strikes, greeks, exact prices)
    # "exact_underlying"     — real OHLCV price bars, no option approximation needed
    # "constant_maturity_iv" — iVol IV30d/IV60d/IVX surface (interpolated, not exact contract)
    # "index_proxy"          — IVX index as IV proxy for a strategy needing specific IV
    # "insufficient"         — data unavailable
    metric_family: Optional[str] = None
    # "estimator_accuracy" | "persistence" | "correlation" | "strategy_sharpe" |
    # "strategy_win_rate" | "premium_mean" | "iv_level_change" | "regime_comparison" |
    # "distribution" | "risk_sizing" | "mean_difference" | "intraday_pattern" |
    # "spread_comparison" | "cost_ratio" | "other"
