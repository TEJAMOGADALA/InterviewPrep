"""Additive learning engine for recommending the next roadmap learning node.

This package is intentionally isolated and read-only. It reuses the existing
roadmap engine and roadmap_node_progress collection but never writes to Mongo or
modifies mission generation.
"""

from .builder import build_learning_recommendation
from .planner import get_today_learning_node
from .ranking import rank_learning_nodes
from .revision import (
    get_due_revision_nodes,
    get_highest_priority_revision,
    has_due_revision,
)
from .unlock import get_unlocked_nodes, is_node_unlocked, next_unlockable_nodes

__all__ = [
    "build_learning_recommendation",
    "get_today_learning_node",
    "rank_learning_nodes",
    "get_due_revision_nodes",
    "get_highest_priority_revision",
    "has_due_revision",
    "get_unlocked_nodes",
    "is_node_unlocked",
    "next_unlockable_nodes",
]
