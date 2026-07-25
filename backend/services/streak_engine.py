"""Canonical streak service for learning activity.

This service owns all streak updates so mission completion, dashboard, and any
future widgets consume the same logic.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional


def today_date_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def update_streak_on_completion(streak: Optional[dict]) -> dict:
    today = today_date_str()
    yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()

    if not streak:
        return {
            "current_streak": 1,
            "longest_streak": 1,
            "last_active_date": today,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    if streak.get("last_active_date") == today:
        return streak

    current = int(streak.get("current_streak", 0))
    if streak.get("last_active_date") == yesterday:
        current += 1
    else:
        current = 1

    longest = max(int(streak.get("longest_streak", 0)), current)
    return {
        "current_streak": current,
        "longest_streak": longest,
        "last_active_date": today,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def streak_days_grid(streak: Optional[dict]) -> List[bool]:
    if not streak or not streak.get("last_active_date"):
        return [False] * 7

    last_active = datetime.fromisoformat(streak["last_active_date"]).date()
    today = datetime.now(timezone.utc).date()
    result = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        start = last_active - timedelta(days=int(streak.get("current_streak", 0)) - 1)
        active = start <= d <= last_active
        result.append(active)
    return result
