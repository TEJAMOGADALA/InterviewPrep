"""Revision selection for the additive learning engine."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List, Optional


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        # ISO string (supports both YYYY-MM-DD and full ISO timestamps)
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        # Normalize to UTC-aware datetime
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def get_due_revision_nodes(user_id: str, *, progress_rows: Optional[Iterable[dict]] = None) -> List[dict]:
    """Return revision candidates whose next_revision date is due."""
    rows = list(progress_rows or [])
    now = datetime.now(timezone.utc)
    due = []
    for row in rows:
        next_revision = _parse_datetime(row.get("next_revision"))
        if next_revision and next_revision <= now:
            due.append(row)
    return sorted(due, key=lambda row: (row.get("next_revision") or "", row.get("revision_stage") or 0))


def has_due_revision(user_id: str, *, progress_rows: Optional[Iterable[dict]] = None) -> bool:
    """Return whether any revision is due."""
    return bool(get_due_revision_nodes(user_id, progress_rows=progress_rows))


def get_highest_priority_revision(user_id: str, *, progress_rows: Optional[Iterable[dict]] = None) -> Optional[dict]:
    """Return the highest priority revision candidate."""
    due = get_due_revision_nodes(user_id, progress_rows=progress_rows)
    if not due:
        return None
    return min(due, key=lambda row: (row.get("next_revision") or "", row.get("revision_stage") or 0))
