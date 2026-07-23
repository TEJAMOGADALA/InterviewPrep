"""Idempotent initialization of per-learning-node roadmap progress."""
from __future__ import annotations

from typing import Optional

from models import RoadmapNodeProgress
from roadmap import CURRENT_VERSION, RoadmapEngine, get_roadmap
from services.roadmap_progress.repository import RoadmapNodeProgressRepository


def _last_segment(value: Optional[str], fallback: str) -> str:
    """Convert a dot-qualified roadmap field into its local identifier."""
    return (value or fallback).rsplit(".", 1)[-1]


def build_initial_progress(user_id: str, node: dict) -> RoadmapNodeProgress:
    """Create the default progress row for one explicit roadmap learning node."""
    return RoadmapNodeProgress(
        user_id=user_id,
        node_id=node["id"],
        track=node.get("track", ""),
        module=_last_segment(node.get("module"), node.get("track", "")),
        topic=_last_segment(node.get("category"), node.get("module", "")),
        subtopic=_last_segment(node.get("id"), ""),
    )


class RoadmapProgressInitializer:
    """Initialize the complete roadmap-node progress set for one learner."""

    def __init__(self, repository: RoadmapNodeProgressRepository, roadmap: RoadmapEngine):
        self._repository = repository
        self._roadmap = roadmap

    async def initialize_for_user(self, user_id: str) -> int:
        """Create missing rows for every explicit learning node and return insert count."""
        rows = [
            build_initial_progress(user_id, node)
            for node in self._roadmap.get_learning_nodes()
        ]
        return await self._repository.initialize_nodes(rows)


async def initialize_roadmap_progress_for_user(
    db, user_id: str, roadmap: Optional[RoadmapEngine] = None,
) -> int:
    """Convenience entry point used by application lifecycle hooks."""
    initializer = RoadmapProgressInitializer(
        RoadmapNodeProgressRepository(db),
        roadmap or get_roadmap(CURRENT_VERSION),
    )
    return await initializer.initialize_for_user(user_id)
