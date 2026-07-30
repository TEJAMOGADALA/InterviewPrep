"""Canonical progress engine for roadmap-based learning progress.

This service is the single backend source of truth for roadmap progress. It
derives parent rollups strictly from child progress so that topic, section,
track, and overall progress all remain consistent — and it owns the shared
read/write helpers (`load_user_progress_rows`, `score_to_node_fields`) so
every consumer (Mission Engine, Roadmap API, AI Mentor) reads and writes the
same `knowledge_nodes` collection the same way.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, Iterable, Optional


def _normalize_status(raw: Optional[str]) -> str:
    return raw or "not_started"


def build_canonical_progress(roadmap, progress_rows: Optional[Dict[str, dict]] = None) -> Dict[str, dict]:
    """Return canonical progress rollups keyed by roadmap node id."""
    progress_rows = progress_rows or {}
    cache: Dict[str, dict] = {}

    def _leaf_topic_count(node_id: str) -> int:
        node = roadmap.get(node_id)
        if not node:
            return 0
        children = roadmap.children(node_id)
        if not children:
            return 1
        return sum(_leaf_topic_count(child["id"]) for child in children)

    def _rollup(node_id: str) -> dict:
        if node_id in cache:
            return cache[node_id]

        node = roadmap.get(node_id)
        if not node:
            return {
                "status": "not_started",
                "confidence": 0.0,
                "weakness_score": 0.0,
                "mastery_percentage": 0.0,
                "total_topics": 0,
                "completed_topics": 0,
                "remaining_topics": 0,
                "completion_pct": 0.0,
                "estimated_hours_remaining": 0.0,
            }

        children = roadmap.children(node_id)
        direct = progress_rows.get(node_id)
        # A progress row keyed at this node id only represents true leaf-level
        # progress when the node has no children. Legacy per-track progress rows
        # (node_id == track id) must fall through to the structural rollup below
        # instead of collapsing a non-leaf node's total_topics to 1.
        if direct and not children:
            status = _normalize_status(direct.get("status"))
            confidence = float(direct.get("confidence", 0.0))
            weakness = float(direct.get("weakness_score", 0.0))
            mastery = float(direct.get("mastery_percentage", 0.0))
            total_topics = 1
            completed_topics = 1 if status in {"completed", "mastered"} else 0
            remaining_topics = total_topics - completed_topics
            completion_pct = 100.0 if completed_topics else 0.0
            result = {
                "status": status,
                "confidence": round(confidence, 2),
                "weakness_score": round(weakness, 2),
                "mastery_percentage": round(mastery, 2),
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "remaining_topics": remaining_topics,
                "completion_pct": completion_pct,
                "estimated_hours_remaining": 0.0,
            }
            cache[node_id] = result
            return result

        child_rollups = [_rollup(child["id"]) for child in children]
        total_topics = _leaf_topic_count(node_id)
        completed_topics = sum(r["completed_topics"] for r in child_rollups)
        remaining_topics = total_topics - completed_topics
        completion_pct = round((completed_topics / total_topics) * 100.0, 2) if total_topics else 0.0

        if not child_rollups:
            result = {
                "status": "not_started",
                "confidence": 0.0,
                "weakness_score": 0.0,
                "mastery_percentage": 0.0,
                "total_topics": 1,
                "completed_topics": 0,
                "remaining_topics": 1,
                "completion_pct": 0.0,
                "estimated_hours_remaining": 0.0,
            }
            cache[node_id] = result
            return result

        any_progress = any(r["status"] != "not_started" for r in child_rollups)
        # A parent is only "completed" when EVERY child is completed/mastered.
        # Do NOT filter out not_started children before this check — doing so
        # made a single completed child (out of many untouched siblings)
        # vacuously satisfy all(), misreporting the whole parent as "completed".
        all_completed = all(r["status"] in {"completed", "mastered"} for r in child_rollups)
        status = "completed" if all_completed else "in_progress" if any_progress else "not_started"
        avg_conf = sum(r["confidence"] for r in child_rollups) / len(child_rollups) if child_rollups else 0.0
        avg_mastery = sum(r["mastery_percentage"] for r in child_rollups) / len(child_rollups) if child_rollups else 0.0
        avg_weak = sum(r["weakness_score"] for r in child_rollups) / len(child_rollups) if child_rollups else 0.0
        result = {
            "status": status,
            "confidence": round(avg_conf, 2),
            "weakness_score": round(avg_weak, 2),
            "mastery_percentage": round(avg_mastery, 2),
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "remaining_topics": remaining_topics,
            "completion_pct": completion_pct,
            "estimated_hours_remaining": 0.0,
        }
        cache[node_id] = result
        return result

    def _initial_root_ids() -> list[str]:
        root = roadmap.get("root") if hasattr(roadmap, "get") else None
        if root:
            return [root["id"]]

        tracks = getattr(roadmap, "tracks", None)
        if callable(tracks):
            track_nodes = tracks()
            if track_nodes:
                return [track["id"] for track in track_nodes if track]

        return []

    for node_id in _initial_root_ids():
        _rollup(node_id)

    # Walk every reachable node so parent rollups exist for the whole tree.
    seen = set()
    stack = [roadmap.get(node_id) for node_id in _initial_root_ids() if roadmap.get(node_id)]
    while stack:
        node = stack.pop()
        node_id = node["id"]
        if node_id in seen:
            continue
        seen.add(node_id)
        _rollup(node_id)
        stack.extend(roadmap.children(node_id))

    return cache


def count_remaining_learning_nodes(roadmap, progress_rows: Dict[str, dict]) -> int:
    """Count roadmap learning nodes not yet completed/mastered.

    This is the "remaining_curriculum" input to the pacing engine
    (services/learning_engine/pacing.py) — kept here alongside the other
    canonical `knowledge_nodes` readers rather than duplicated per caller.
    """
    done_statuses = {"completed", "mastered"}
    remaining = 0
    for node in roadmap.get_learning_nodes():
        row = progress_rows.get(node["id"])
        if not row or row.get("status") not in done_statuses:
            remaining += 1
    return remaining


async def load_user_progress_rows(db, user_id: str) -> Dict[str, dict]:
    """Canonical loader for a user's `knowledge_nodes` rows, keyed by node_id.

    Single shared query used by every consumer (Roadmap API, Mission Engine,
    dashboard readiness) instead of each route module querying the collection
    independently.
    """
    cur = db.knowledge_nodes.find({"user_id": user_id}, {"_id": 0})
    docs = await cur.to_list(length=2000)
    return {d["node_id"]: d for d in docs}


def score_to_node_fields(score: float) -> dict:
    """Convert a 0-100 mastery-style score into derived KnowledgeNode fields.

    Single canonical mapping (confidence / weakness_score / revision_bucket /
    status) replacing the near-identical inline conversions that used to be
    duplicated across the migration in server.py and the feedback-sync path
    in routes_missions.py.
    """
    score = max(0.0, min(100.0, score))
    confidence = round(score / 10.0, 2)
    weakness = round(max(0.0, 100.0 - score), 2)
    bucket = "green" if confidence >= 7 else "yellow" if confidence >= 4 else "red"
    status = "mastered" if confidence >= 9 else "in_progress" if score > 0 else "not_started"
    return {
        "confidence": confidence,
        "mastery_percentage": round(score, 2),
        "weakness_score": weakness,
        "revision_bucket": bucket,
        "status": status,
    }


async def seed_knowledge_nodes_from_self_assessment(
    db, user_id: str, self_assessment: Dict[str, float], roadmap,
) -> int:
    """Onboarding-only baseline seed of `knowledge_nodes` from self-assessment.

    Converts each track's self-assessment slider (1-10) into a starting
    confidence/weakness/mastery baseline for every learning node in that
    track only, so the ranking model in services/learning_engine/ranking.py
    sees different learners differently from day one instead of the
    identical zeroed defaults every new user previously had.

    Self-assessment is a perceived-confidence signal, not proof of mastery:
    `status` is always forced to "in_progress" (never "completed"/
    "mastered") so seeding can never satisfy a prerequisite, unlock a
    downstream roadmap node, or bypass the prerequisite chain in
    services/learning_engine/unlock.py.

    Idempotent and non-destructive — a learning node that already has a
    `knowledge_nodes` row for this user + roadmap version is left untouched.
    """
    cur = db.knowledge_nodes.find(
        {"user_id": user_id, "roadmap_version": roadmap.version}, {"_id": 0, "node_id": 1},
    )
    existing_ids = {row["node_id"] for row in await cur.to_list(length=5000)}

    now = datetime.now(timezone.utc).isoformat()
    rows = []
    self_assessment = self_assessment or {}
    # Seed every roadmap track, not just the ones covered by the onboarding
    # self-assessment sliders (dsa/java/lld/hld/os/dbms/cn). Tracks the
    # onboarding UI never asks about (behavioral/projects/resume) used to be
    # left completely unseeded, which made every one of their nodes look
    # maximally weak (ranking.py's cold-start default) forever — causing them
    # to dominate the cross-track recommendation regardless of target
    # company. A neutral baseline (matching the "5" default used elsewhere
    # for unrated tracks, e.g. mission_engine.compute_readiness) keeps every
    # track on equal footing until the learner actually engages with it.
    for track in roadmap.track_ids():
        rating = self_assessment.get(track)
        if rating is None:
            rating = 5.0
        fields = score_to_node_fields(float(rating) * 10.0)
        fields["status"] = "in_progress"  # never "mastered" — must not unlock/complete nodes
        for node in roadmap.get_track_learning_nodes(track):
            node_id = node["id"]
            if node_id in existing_ids:
                continue
            existing_ids.add(node_id)
            rows.append({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "roadmap_version": roadmap.version,
                "node_id": node_id,
                **fields,
                "last_revision": None,
                "next_revision": None,
                "revision_stage": 0,
                "completion_date": None,
                "attempts": 0,
                "actual_solve_minutes": 0,
                "bookmarked": False,
                "favorite": False,
                "notes": None,
                "updated_at": now,
            })

    if rows:
        await db.knowledge_nodes.insert_many(rows)
    return len(rows)
