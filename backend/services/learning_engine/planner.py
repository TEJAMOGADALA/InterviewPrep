"""Orchestrator for the additive learning engine."""
from __future__ import annotations

from typing import Optional

from roadmap import get_roadmap
from services.learning_engine.builder import build_learning_recommendation
from services.learning_engine.ranking import rank_learning_nodes
from services.learning_engine.revision import get_highest_priority_revision
from services.learning_engine.unlock import get_unlocked_nodes
from services.roadmap_progress.repository import RoadmapNodeProgressRepository


def _build_support_recommendation(
    node: Optional[dict],
    progress_rows: list,
) -> Optional[dict]:
    """
    Build an adaptive secondary recommendation.

    The support topic should reinforce the learner's weakest
    non-primary track.

    This is intentionally lightweight and does NOT influence
    today's primary recommendation.
    """

    if not node:
        return None

    primary_track = node.get("track")

    candidates = {}

    for row in progress_rows:

        track = row.get("track")

        if not track:
            continue

        if track == primary_track:
            continue

        status = row.get("status", "not_started")

        if status in ("completed", "mastered"):
            continue

        confidence = float(row.get("confidence", 0))
        weakness = float(row.get("weakness_score", 0))

        score = weakness - (confidence * 10)

        if (
            track not in candidates
            or score > candidates[track]["score"]
        ):
            candidates[track] = {
                "score": score
            }

    if not candidates:
        return None

    support_track = max(
        candidates.items(),
        key=lambda x: x[1]["score"]
    )[0]

    return {
        "support_track": support_track
    }



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
                support_recommendation=_build_support_recommendation(
                node,
                progress_rows,
                )
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
        support_recommendation=_build_support_recommendation(
        top_node,
        progress_rows,
        )   
    )
