"""Persistence boundary for the roadmap_node_progress collection."""
from __future__ import annotations

from typing import Iterable, List, Optional

from pymongo import UpdateOne

from models import RoadmapNodeProgress


class RoadmapNodeProgressRepository:
    """Store and retrieve per-user progress for explicit roadmap learning nodes."""

    def __init__(self, db):
        self._collection = db.roadmap_node_progress

    async def ensure_indexes(self) -> None:
        """Ensure one progress row exists at most once per user and learning node."""
        await self._collection.create_index([("user_id", 1), ("node_id", 1)], unique=True)
        await self._collection.create_index([("user_id", 1), ("track", 1)])

    async def initialize_nodes(self, progress_rows: Iterable[RoadmapNodeProgress]) -> int:
        """Insert missing rows only; existing learner progress is never overwritten."""
        operations = [
            UpdateOne(
                {"user_id": row.user_id, "node_id": row.node_id},
                {"$setOnInsert": row.model_dump()},
                upsert=True,
            )
            for row in progress_rows
        ]
        if not operations:
            return 0
        result = await self._collection.bulk_write(operations, ordered=False)
        return int(result.upserted_count)

    async def get_for_user(self, user_id: str) -> List[dict]:
        """Return all roadmap-node progress rows belonging to a user."""
        cursor = self._collection.find({"user_id": user_id}, {"_id": 0})
        return await cursor.to_list(length=None)

    async def get_for_user_node(self, user_id: str, node_id: str) -> Optional[dict]:
        """Return progress for one user/node pair, if it has been initialized."""
        return await self._collection.find_one(
            {"user_id": user_id, "node_id": node_id}, {"_id": 0}
        )
