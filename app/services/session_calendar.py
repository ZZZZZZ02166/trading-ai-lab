"""
session_calendar.py — Market session definitions, timezone handling, and trading calendar.

All times are America/New_York (Eastern Time). All dates use NYSE equity market calendar.

Exports:
  MARKET_TIMEZONE, MARKET_OPEN, MARKET_CLOSE, SESSION_WINDOWS
  is_trading_day(dt)              → bool
  get_trading_days(start, end)    → list[date]
  localize_et(ts)                 → datetime (timezone-aware, ET)
  assign_session_bucket(ts)       → str key from SESSION_WINDOWS
  is_market_open(ts)              → bool
  get_fomc_event_window(fomc_date, pre_days, post_days) → dict
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Union
from zoneinfo import ZoneInfo

MARKET_TIMEZONE = "America/New_York"
_ET = ZoneInfo(MARKET_TIMEZONE)

MARKET_OPEN  = time(9, 30)
MARKET_CLOSE = time(16, 0)

# ── Session windows ───────────────────────────────────────────────────────────────
# Each window: (start_time_inclusive, end_time_exclusive) in ET
SESSION_WINDOWS: dict[str, tuple[time, time]] = {
    "open":         (time(9, 30),  time(10, 0)),    # first 30 min
    "early":        (time(10, 0),  time(11, 30)),
    "mid":          (time(11, 30), time(14, 0)),
    "late":         (time(14, 0),  time(15, 30)),
    "close":        (time(15, 30), time(16, 0)),    # last 30 min
    "macro_window": (time(14, 0),  time(15, 0)),    # FOMC announcement window (overlaps late)
}

# ── NYSE equity market holidays 2024–2025 ────────────────────────────────────────
# Source: NYSE holiday schedule. Half-days are NOT included (treated as full trading days
# for the purpose of DTE and event window calculations).

_NYSE_HOLIDAYS: frozenset[date] = frozenset([
    # 2024
    date(2024, 1, 1),    # New Year's Day
    date(2024, 1, 15),   # Martin Luther King Jr. Day
    date(2024, 2, 19),   # Presidents' Day
    date(2024, 3, 29),   # Good Friday
    date(2024, 5, 27),   # Memorial Day
    date(2024, 6, 19),   # Juneteenth
    date(2024, 7, 4),    # Independence Day
    date(2024, 9, 2),    # Labor Day
    date(2024, 11, 28),  # Thanksgiving
    date(2024, 12, 25),  # Christmas

    # 2025
    date(2025, 1, 1),    # New Year's Day
    date(2025, 1, 20),   # Martin Luther King Jr. Day
    date(2025, 2, 17),   # Presidents' Day
    date(2025, 4, 18),   # Good Friday
    date(2025, 5, 26),   # Memorial Day
    date(2025, 6, 19),   # Juneteenth
    date(2025, 7, 4),    # Independence Day
    date(2025, 9, 1),    # Labor Day
    date(2025, 11, 27),  # Thanksgiving
    date(2025, 12, 25),  # Christmas
])


def is_trading_day(dt: Union[date, datetime]) -> bool:
    """Return True if dt is an NYSE equity trading day (not weekend or holiday)."""
    d = dt.date() if isinstance(dt, datetime) else dt
    return d.weekday() < 5 and d not in _NYSE_HOLIDAYS


def get_trading_days(start: Union[date, str], end: Union[date, str]) -> list[date]:
    """Return all NYSE trading days in [start, end] inclusive."""
    if isinstance(start, str):
        start = date.fromisoformat(start)
    if isinstance(end, str):
        end = date.fromisoformat(end)

    days = []
    current = start
    while current <= end:
        if is_trading_day(current):
            days.append(current)
        current += timedelta(days=1)
    return days


def localize_et(ts: Union[str, datetime]) -> datetime:
    """
    Parse a timestamp string or datetime and return it as a timezone-aware ET datetime.

    Handles:
      - ISO 8601 with timezone info (converted to ET)
      - ISO 8601 without timezone (assumed ET)
      - datetime objects (naive assumed ET; aware converted to ET)
    """
    if isinstance(ts, str):
        ts = ts.strip()
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(ts, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Cannot parse timestamp: {ts!r}")
    else:
        dt = ts

    if dt.tzinfo is None:
        return dt.replace(tzinfo=_ET)
    return dt.astimezone(_ET)


def assign_session_bucket(ts: Union[str, datetime]) -> str:
    """
    Return the SESSION_WINDOWS key for the given timestamp.

    If the timestamp falls outside all defined windows (e.g. pre-market),
    returns "pre_market" or "post_market" as appropriate.
    Returns "outside_session" if it cannot be placed.
    """
    try:
        dt_et = localize_et(ts)
    except (ValueError, TypeError):
        return "outside_session"

    t = dt_et.time()

    for bucket, (start, end) in SESSION_WINDOWS.items():
        if bucket == "macro_window":
            continue  # macro_window overlaps late; handle separately if needed
        if start <= t < end:
            return bucket

    if t < MARKET_OPEN:
        return "pre_market"
    if t >= MARKET_CLOSE:
        return "post_market"
    return "outside_session"


def is_market_open(ts: Union[str, datetime]) -> bool:
    """Return True if the timestamp falls within the regular NYSE session (9:30–16:00 ET)."""
    try:
        dt_et = localize_et(ts)
    except (ValueError, TypeError):
        return False
    t = dt_et.time()
    return MARKET_OPEN <= t < MARKET_CLOSE and is_trading_day(dt_et)


def get_fomc_event_window(
    fomc_date: date,
    pre_days: int = 5,
    post_days: int = 1,
) -> dict:
    """
    Return a dict describing the trading-day window around one FOMC event date.

    Args:
        fomc_date: The FOMC announcement date.
        pre_days:  Number of trading days BEFORE the event date to include.
        post_days: Number of trading days AFTER the event date to include.

    Returns dict with:
      event_date:   the FOMC date
      pre_window:   list[date] of pre_days trading days ending the day before
      post_window:  list[date] of post_days trading days starting the day after
    """
    # Walk backwards to find pre-window
    pre_window: list[date] = []
    current = fomc_date - timedelta(days=1)
    while len(pre_window) < pre_days:
        if is_trading_day(current):
            pre_window.insert(0, current)
        current -= timedelta(days=1)
        if current < date(2020, 1, 1):
            break

    # Walk forwards to find post-window
    post_window: list[date] = []
    current = fomc_date + timedelta(days=1)
    while len(post_window) < post_days:
        if is_trading_day(current):
            post_window.append(current)
        current += timedelta(days=1)
        if current > date(2030, 1, 1):
            break

    return {
        "event_date": fomc_date,
        "pre_window": pre_window,
        "post_window": post_window,
        "pre_days": pre_days,
        "post_days": post_days,
    }
