"""Orchestrator for the additive learning engine."""
from __future__ import annotations

from typing import Iterable, Optional

from roadmap import get_roadmap
from services.learning_engine.builder import build_learning_recommendation
from services.learning_engine.ranking import rank_learning_nodes
from services.learning_engine.revision import get_highest_priority_revision
from services.learning_engine.unlock import get_unlocked_nodes, next_unlockable_nodes
from services.roadmap_progress.repository import RoadmapNodeProgressRepository

CORE_TRACKS = ["operating_systems", "dbms", "computer_networks"]
COMPLETED_STATUSES = {"completed", "mastered", "revision_due"}


def _completed_node_ids(progress_rows: Iterable[dict]) -> set[str]:
    completed = set()
    for row in progress_rows or []:
        if not isinstance(row, dict):
            continue
        status = (row.get("status") or "").lower()
        node_id = row.get("node_id")
        if node_id and status in COMPLETED_STATUSES:
            completed.add(node_id)
    return completed


def _choose_support_node(support_track: str, progress_rows: list) -> Optional[dict]:
    completed_ids = _completed_node_ids(progress_rows)
    unlocked = [
        node for node in get_unlocked_nodes(progress_rows)
        if node.get("track") == support_track and node.get("id") not in completed_ids
    ]
    if unlocked:
        return unlocked[0]

    for row in progress_rows:
        if row.get("track") == support_track and row.get("node_id") and row.get("node_id") not in completed_ids:
            roadmap_node = get_roadmap().get_learning_node(row["node_id"])
            if roadmap_node is not None:
                return roadmap_node

    for node in get_roadmap().get_learning_nodes():
        if node.get("track") == support_track and node.get("id") not in completed_ids:
            return node

    return None


def _build_support_recommendation(
    node: Optional[dict],
    progress_rows: list,
) -> Optional[dict]:
    """
    Build an adaptive secondary recommendation.

    The support recommendation should prioritize a roadmap node from the learner's
    weakest non-primary track, if one is available.
    """

    if not node:
        return None

    primary_track = node.get("track")
    candidates = {}

    for row in progress_rows:
        track = row.get("track")
        if not track or track == primary_track:
            continue

        status = row.get("status", "not_started")
        if status in COMPLETED_STATUSES:
            continue

        confidence = float(row.get("confidence", 0))
        weakness = float(row.get("weakness_score", 0))
        score = weakness - (confidence * 10)

        if (
            track not in candidates
            or score > candidates[track]["score"]
        ):
            candidates[track] = {"score": score}

    if not candidates:
        return None

    candidate_tracks = [track for track in candidates if _choose_support_node(track, progress_rows) is not None]
    if not candidate_tracks:
        return None

    support_track = max(
        ((track, candidates[track]) for track in candidate_tracks),
        key=lambda x: x[1]["score"],
    )[0]
    support_node = _choose_support_node(support_track, progress_rows)
    recommendation = {"support_track": support_track}
    if support_node is not None:
        recommendation["support_node"] = support_node.get("id")
    return recommendation


def _build_core_recommendation(progress_rows: list) -> Optional[dict]:
    """
    Build a roadmap-backed core reading recommendation from OS/DBMS/Networks.
    """
    completed_ids = _completed_node_ids(progress_rows)
    candidates = [
        node for node in next_unlockable_nodes(progress_rows)
        if node.get("track") in CORE_TRACKS
        and node.get("id") not in completed_ids
    ]
    if not candidates:
        candidates = [
            node for node in get_unlocked_nodes(progress_rows)
            if node.get("track") in CORE_TRACKS
            and node.get("id") not in completed_ids
        ]
    if not candidates:
        candidates = [
            node for node in get_roadmap().get_learning_nodes()
            if node.get("track") in CORE_TRACKS
            and node.get("id") not in completed_ids
        ]
    if not candidates:
        return None
    return {"core_node": candidates[0].get("id")}


async def _load_progress_rows(user_id: str, db=None) -> list:
    if db is None:
        return []
    repository = RoadmapNodeProgressRepository(db)
    return await repository.get_for_user(user_id)


async def get_today_learning_node(user_id: str, *, db=None) -> Optional[dict]:
    """Return the best learning recommendation for the user."""
    progress_rows = await _load_progress_rows(user_id, db)

    revision = get_highest_priority_revision(user_id, progress_rows=progress_rows)
    if revision is not None:
        roadmap = get_roadmap()
        node = roadmap.get(revision.get("node_id"))
        if node is not None:
            return build_learning_recommendation(
                node,
                progress=revision,
                support_recommendation=_build_support_recommendation(node, progress_rows),
                core_recommendation=_build_core_recommendation(progress_rows),
            )

    unlocked_nodes = get_unlocked_nodes(progress_rows)
    if not unlocked_nodes:
        return None

    progress_map = {row.get("node_id"): row for row in progress_rows if row.get("node_id")}
    ranked_nodes = rank_learning_nodes(unlocked_nodes, progress_map)
    if not ranked_nodes:
        return None

    top_node = ranked_nodes[0]
    return build_learning_recommendation(
        top_node,
        progress=progress_map.get(top_node.get("id"), {}),
        support_recommendation=_build_support_recommendation(top_node, progress_rows),
        core_recommendation=_build_core_recommendation(progress_rows),
    )
