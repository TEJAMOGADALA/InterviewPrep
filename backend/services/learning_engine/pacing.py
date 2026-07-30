"""Interview-deadline pacing engine — single source of truth for adaptive urgency.

The onboarding `interview_target_date` was previously only used to render a
UI countdown. This module converts it (plus daily study hours and remaining
curriculum size) into one canonical planning state, consumed identically by
mission generation (mission_engine.py, learning_engine/planner.py+ranking.py)
and the Mission Control dashboard response (routes_missions.py) — so neither
computes "days remaining" or urgency on its own.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from math import ceil
from typing import Iterable, Optional

STANDARD = "standard"
ON_TRACK = "on_track"
FOCUSED = "focused"
ACCELERATED = "accelerated"
CRITICAL = "critical"

# Ordered highest-threshold-first: first tier whose threshold `remaining_days`
# meets/exceeds wins. The last tier's threshold of 0 always matches.
_TIERS = (
    (120, ON_TRACK, "On Track", "\u2705", 0.15),
    (60, FOCUSED, "Focused", "\U0001F3AF", 0.4),
    (21, ACCELERATED, "Accelerated Plan", "\u26A1", 0.7),
    (0, CRITICAL, "High Priority", "\U0001F525", 1.0),
)


def _parse_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        return None


def compute_pacing_state(
    interview_target_date: Optional[str],
    daily_study_hours: Optional[float],
    remaining_curriculum_nodes: Optional[int] = None,
    *,
    today: Optional[date] = None,
) -> dict:
    """Return the canonical adaptive-pacing state for one user.

    Falls back to `pacing_mode="standard"` / `urgency=0.0` — a strict no-op
    for every consumer — when no interview date is set, so users without a
    target date keep exactly today's planner/mission behavior.
    """
    hours = float(daily_study_hours) if daily_study_hours else 2.0
    daily_capacity_minutes = hours * 60.0

    target = _parse_date(interview_target_date)
    if target is None:
        return {
            "has_target_date": False,
            "remaining_days": None,
            "daily_capacity_minutes": daily_capacity_minutes,
            "remaining_curriculum_nodes": remaining_curriculum_nodes,
            "required_daily_nodes": None,
            "pacing_mode": STANDARD,
            "label": None,
            "emoji": None,
            "urgency": 0.0,
        }

    today = today or datetime.now(timezone.utc).date()
    remaining_days = max(0, (target - today).days)

    for threshold, mode, label, emoji, urgency in _TIERS:
        if remaining_days >= threshold:
            break

    required_daily_nodes = None
    if remaining_curriculum_nodes is not None and remaining_days > 0:
        required_daily_nodes = round(remaining_curriculum_nodes / remaining_days, 3)

    return {
        "has_target_date": True,
        "remaining_days": remaining_days,
        "daily_capacity_minutes": daily_capacity_minutes,
        "remaining_curriculum_nodes": remaining_curriculum_nodes,
        "required_daily_nodes": required_daily_nodes,
        "pacing_mode": mode,
        "label": label,
        "emoji": emoji,
        "urgency": urgency,
    }


def forecast_completion(
    pacing_state: dict,
    *,
    completed_dates: Iterable[Optional[str]] = (),
    remaining_nodes: Optional[int] = None,
    window_days: int = 7,
    avg_minutes_per_node: float = 30.0,
    today: Optional[date] = None,
) -> dict:
    """Forecast whether the learner is on track to finish before their interview.

    Reuses `compute_pacing_state`'s own output (`required_daily_nodes`,
    `remaining_days`, `has_target_date`, `daily_capacity_minutes`) instead of
    re-deriving pacing math — this only adds the "how are we actually
    trending" half: a pace estimate projected forward.

    Pace prefers real history (`completed_dates`, recent `completion_date`
    values) when it exists. With no history yet (new user / first day) it
    falls back to a capacity-based estimate — `daily_capacity_minutes`
    (itself driven by `daily_study_hours`) divided by `avg_minutes_per_node`
    — so the forecast still reacts to today's declared study-hours budget
    from day one instead of reporting zero pace forever.
    """
    today = today or datetime.now(timezone.utc).date()
    if remaining_nodes is None:
        remaining_nodes = pacing_state.get("remaining_curriculum_nodes")

    window_start = today - timedelta(days=window_days)
    recent_completions = 0
    for raw in completed_dates or ():
        completed_on = _parse_date(raw) if isinstance(raw, str) else raw
        if completed_on and window_start <= completed_on <= today:
            recent_completions += 1
    historical_pace = round(recent_completions / window_days, 3)

    daily_capacity_minutes = pacing_state.get("daily_capacity_minutes")
    capacity_pace = round(daily_capacity_minutes / avg_minutes_per_node, 3) if daily_capacity_minutes else 0.0
    current_pace = historical_pace if recent_completions > 0 else capacity_pace

    estimated_completion_date = None
    if current_pace > 0 and remaining_nodes is not None:
        days_needed = ceil(remaining_nodes / current_pace)
        estimated_completion_date = (today + timedelta(days=days_needed)).isoformat()

    required_pace = pacing_state.get("required_daily_nodes")
    finish_confidence = None
    if pacing_state.get("has_target_date") and required_pace is not None:
        finish_confidence = 1.0 if required_pace <= 0 else round(max(0.0, min(1.0, current_pace / required_pace)), 3)

    return {
        "current_pace_nodes_per_day": current_pace,
        "historical_pace_nodes_per_day": historical_pace,
        "capacity_pace_nodes_per_day": capacity_pace,
        "required_pace_nodes_per_day": required_pace,
        "remaining_nodes": remaining_nodes,
        "remaining_days": pacing_state.get("remaining_days"),
        "estimated_completion_date": estimated_completion_date,
        "finish_confidence": finish_confidence,
        "on_track": finish_confidence is not None and finish_confidence >= 1.0,
    }
