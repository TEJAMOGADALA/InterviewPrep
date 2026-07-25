"""Canonical Revision Engine — single source of truth for spaced repetition.

This service owns spaced-repetition scheduling math and "what's due" queries
so Mission Engine, the Knowledge Base, and AI Mentor all consume the same
logic (mirrors the `services/streak_engine.py` pattern already used in this
codebase).

Revision state is stored directly on the canonical `knowledge_nodes` rows
(the same collection `services/progress_engine.py` owns) via the
`next_revision` / `revision_stage` fields — there is no parallel revision
store. The legacy `revisions` collection (`RevisionItem`) is no longer
written to by production code; it is kept, unmodified, purely so historical
data remains queryable.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

REVISION_STAGES_DAYS = [1, 3, 7, 14, 30, 60]


def confidence_modifier_days(confidence: int) -> float:
    """Adjust default interval based on confidence 1-10."""
    if confidence <= 3:
        return 0.4  # revise much sooner
    if confidence <= 5:
        return 0.7
    if confidence >= 9:
        return 1.5  # can wait longer
    if confidence >= 7:
        return 1.2
    return 1.0


def schedule_next_revision(current_stage: int, confidence: int = 6) -> tuple[int, str]:
    """Return (next_stage, next_date_str)."""
    next_stage = min(current_stage + 1, len(REVISION_STAGES_DAYS) - 1)
    days = REVISION_STAGES_DAYS[next_stage] * confidence_modifier_days(confidence)
    days = max(1, round(days))
    d = (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()
    return next_stage, d


def first_revision_date(confidence: int = 6) -> str:
    days = REVISION_STAGES_DAYS[0] * confidence_modifier_days(confidence)
    days = max(1, round(days))
    return (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()


async def mark_node_for_revision(
    db, user_id: str, roadmap_version: str, node_id: str, confidence: int = 6,
) -> None:
    """Advance (or start) the spaced-repetition schedule for one canonical node.

    This is the only place that writes revision-scheduling state. It stamps
    `next_revision` / `revision_stage` directly onto the node's `knowledge_nodes`
    row (creating it if needed) instead of a separate revisions collection.
    """
    existing = await db.knowledge_nodes.find_one(
        {"user_id": user_id, "roadmap_version": roadmap_version, "node_id": node_id}, {"_id": 0},
    )
    if existing and existing.get("next_revision"):
        current_stage = int(existing.get("revision_stage") or 0)
        next_stage, next_date = schedule_next_revision(current_stage, confidence)
    else:
        next_stage, next_date = 0, first_revision_date(confidence)

    await db.knowledge_nodes.update_one(
        {"user_id": user_id, "roadmap_version": roadmap_version, "node_id": node_id},
        {"$set": {
            "user_id": user_id, "roadmap_version": roadmap_version, "node_id": node_id,
            "next_revision": next_date, "revision_stage": next_stage,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )


async def get_revisions_for_user(
    db, user_id: str, roadmap_version: str, *,
    roadmap=None, limit: int = 20, due_only: bool = True,
) -> List[dict]:
    """Canonical "what's due for revision" query — single source across the app.

    Reads from `knowledge_nodes` (the Progress Engine's own collection) keyed
    by `next_revision`. Returns items shaped to match the legacy `revisions`
    collection's public fields (`task_title`, `topic`, `next_review_date`,
    `stage`, `is_due`) so existing consumers (mission generation, the
    `/api/revisions/queue` response, the dashboard revisions widget) need no
    further shape changes.
    """
    if roadmap is None:
        from roadmap import get_roadmap as _get_roadmap, CURRENT_VERSION as _CURRENT_VERSION
        roadmap = _get_roadmap(roadmap_version or _CURRENT_VERSION)

    today = datetime.now(timezone.utc).date().isoformat()
    query: dict = {
        "user_id": user_id, "roadmap_version": roadmap_version,
        "next_revision": {"$ne": None},
    }
    if due_only:
        query["next_revision"]["$lte"] = today

    cur = db.knowledge_nodes.find(query, {"_id": 0}).sort("next_revision", 1).limit(limit)
    rows = await cur.to_list(length=limit)

    out: List[dict] = []
    for row in rows:
        node = roadmap.get(row["node_id"])
        label = node["label"] if node else row["node_id"]
        track = roadmap.find_track(row["node_id"]) if hasattr(roadmap, "find_track") else None
        topic = track["id"] if track else row["node_id"]
        next_review_date: Optional[str] = row.get("next_revision")
        out.append({
            "node_id": row["node_id"],
            "task_title": label,
            "topic": topic,
            "next_review_date": next_review_date,
            "stage": row.get("revision_stage", 0),
            "is_due": bool(next_review_date) and next_review_date <= today,
            "confidence": row.get("confidence"),
        })
    return out
