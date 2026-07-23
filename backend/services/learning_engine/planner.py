"""Orchestrator for the additive learning engine."""
from __future__ import annotations

from typing import Optional

from roadmap import get_roadmap
from services.learning_engine.builder import build_learning_recommendation
from services.learning_engine.ranking import rank_learning_nodes
from services.learning_engine.revision import get_highest_priority_revision
from services.learning_engine.unlock import get_unlocked_nodes
from services.roadmap_progress.repository import RoadmapNodeProgressRepository


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
            return build_learning_recommendation(node, progress=revision)

    unlocked_nodes = get_unlocked_nodes(progress_rows)
    if not unlocked_nodes:
        return None

    progress_map = {row.get("node_id"): row for row in progress_rows if row.get("node_id")}
    ranked_nodes = rank_learning_nodes(unlocked_nodes, progress_map)
    if not ranked_nodes:
        return None

    top_node = ranked_nodes[0]
    return build_learning_recommendation(top_node, progress=progress_map.get(top_node.get("id"), {}))
