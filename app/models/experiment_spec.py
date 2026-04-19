"""
experiment_spec.py — Machine-readable specification for a single backtest experiment.

Specs are stored as JSON in experiments/specs/.
Each spec fully defines the universe, data requirements, entry/exit rules,
metrics, verdict thresholds, and test type for one hypothesis.

test_type values:
  "direct_test"  — hypothesis is tested with the exact data it requires
  "proxy_tested" — hypothesis is approximated through available proxy data
  "provisional"  — endpoint or data availability is unconfirmed; result may be INSUFFICIENT_DATA
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class ExperimentSpec(BaseModel):
    hypothesis_number: str             # "H9", "H13", "H16"
    title: str

    universe: list[str]                # ["QQQ"]
    dte_buckets: Optional[list[int]]   # [0, 1, 2, 3, 4, 5] or None (n/a for non-options tests)
    contract_selection: Optional[str]  # "atm_call" | "atm_put" | "atm_straddle" | None
    call_put_filter: Optional[str]     # "C" | "P" | None

    data_requirements: list[str]       # e.g. ["eod_prices", "ivx", "intraday_chain"]
    entry_rule: str                    # human-readable entry condition
    exit_rule: str                     # human-readable exit condition

    metric_name: str                   # e.g. "rmse_ratio_yz_vs_cc"
    support_threshold: float           # metric value that triggers SUPPORTED verdict
    reject_threshold: float            # metric value that triggers REJECTED verdict

    test_type: Literal["direct_test", "proxy_tested", "provisional"]
    cost_model: Optional[str]          # "optimistic" | "realistic" | "conservative" | None

    notes: str                         # any important caveats, proxy explanations, etc.
