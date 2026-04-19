"""
calendar.py — Scheduled macro / monetary policy event dates.

Hardcoded from public Federal Reserve release schedule.
These are the second-day (announcement) dates for each FOMC meeting.
All dates reflect the day the policy decision is announced (usually ~2 PM ET).

Update this file when new FOMC schedules are released.
Source: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
"""

from __future__ import annotations

from datetime import date


# ── FOMC announcement dates (decision day = last day of two-day meeting) ────────

FOMC_DATES_2024: list[date] = [
    date(2024, 1, 31),
    date(2024, 3, 20),
    date(2024, 5, 1),
    date(2024, 6, 12),
    date(2024, 7, 31),
    date(2024, 9, 18),
    date(2024, 11, 7),
    date(2024, 12, 18),
]

FOMC_DATES_2025: list[date] = [
    date(2025, 1, 29),
    date(2025, 3, 19),
    date(2025, 5, 7),
    date(2025, 6, 18),
    date(2025, 7, 30),
    date(2025, 9, 17),
    date(2025, 10, 29),
    date(2025, 12, 10),
]

ALL_FOMC_DATES: list[date] = sorted(FOMC_DATES_2024 + FOMC_DATES_2025)


def get_fomc_dates(start: date | str, end: date | str) -> list[date]:
    """
    Return FOMC announcement dates within [start, end] inclusive.

    Args:
        start: Start date (date or ISO string "YYYY-MM-DD").
        end:   End date (date or ISO string "YYYY-MM-DD").

    Returns:
        Sorted list of date objects.
    """
    if isinstance(start, str):
        start = date.fromisoformat(start)
    if isinstance(end, str):
        end = date.fromisoformat(end)
    return [d for d in ALL_FOMC_DATES if start <= d <= end]


def get_event_windows(
    event_dates: list[date],
    pre_days: int = 5,
    post_days: int = 1,
) -> list[dict]:
    """
    For each event date, return a dict with pre-window start, event date, post-window end.

    Args:
        event_dates: List of event announcement dates.
        pre_days:    Number of trading days before event to include in pre-window.
        post_days:   Number of trading days after event to include in post-window.

    Returns:
        List of dicts: {"event_date": date, "pre_days": int, "post_days": int}
    """
    return [
        {
            "event_date": d,
            "pre_days": pre_days,
            "post_days": post_days,
        }
        for d in event_dates
    ]
