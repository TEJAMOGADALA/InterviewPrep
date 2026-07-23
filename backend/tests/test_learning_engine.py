import asyncio

import pytest

from services.learning_engine.builder import build_learning_recommendation
from services.learning_engine.planner import get_today_learning_node
from services.learning_engine.ranking import rank_learning_nodes
from services.learning_engine.revision import (
    get_due_revision_nodes,
    get_highest_priority_revision,
    has_due_revision,
)
from services.learning_engine.unlock import (
    first_unlockable_node,
    get_unlocked_nodes,
    is_node_unlocked,
    next_unlockable_nodes,
)


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    async def to_list(self, length=None):
        return list(self._rows)


class FakeCollection:
    def __init__(self, rows):
        self._rows = rows

    def find(self, query=None, projection=None):
        return FakeCursor(list(self._rows))


class FakeDB:
    def __init__(self, rows):
        self.roadmap_node_progress = FakeCollection(rows)


def test_unlock_logic_respects_prerequisites():
    progress_rows = [
        {"node_id": "dsa.foundations.arrays.traversal", "status": "completed", "confidence": 8.0, "weakness_score": 20.0, "mastery": 90.0},
    ]

    assert is_node_unlocked("dsa.foundations.arrays.prefix_sum", progress_rows)
    assert not is_node_unlocked("dsa.foundations.arrays.diff_array", progress_rows)


def test_get_unlocked_and_next_unlockable_nodes():
    progress_rows = [
        {"node_id": "dsa.foundations.arrays.traversal", "status": "completed", "confidence": 8.0, "weakness_score": 20.0, "mastery": 90.0},
        {"node_id": "dsa.foundations.arrays.prefix_sum", "status": "completed", "confidence": 7.0, "weakness_score": 30.0, "mastery": 80.0},
    ]

    unlocked = get_unlocked_nodes(progress_rows)
    next_nodes = next_unlockable_nodes(progress_rows)

    assert any(node["id"] == "dsa.foundations.arrays.prefix_sum" for node in unlocked)
    assert any(node["id"] == "dsa.foundations.arrays.diff_array" for node in next_nodes)
    assert first_unlockable_node(progress_rows)["id"] == "dsa.foundations.arrays.kadane"


def test_ranking_prefers_low_confidence_and_high_weakness():
    nodes = [
        {"id": "node-1", "difficulty": "easy", "estimated_minutes": 20, "company_importance": {"google": 2}},
        {"id": "node-2", "difficulty": "hard", "estimated_minutes": 60, "company_importance": {"google": 5}},
    ]
    progress = {
        "node-1": {"confidence": 8.0, "weakness_score": 20.0, "mastery": 80.0},
        "node-2": {"confidence": 2.0, "weakness_score": 80.0, "mastery": 20.0},
    }

    ranked = rank_learning_nodes(nodes, progress, target_companies=["google"])
    assert ranked[0]["id"] == "node-2"


def test_planner_returns_revision_before_other_candidates():
    rows = [
        {"node_id": "dsa.foundations.arrays.traversal", "status": "completed", "confidence": 8.0, "weakness_score": 20.0, "mastery": 90.0},
        {"node_id": "dsa.foundations.arrays.prefix_sum", "status": "not_started", "confidence": 3.0, "weakness_score": 70.0, "mastery": 20.0},
        {"node_id": "dsa.foundations.arrays.diff_array", "status": "not_started", "confidence": 6.0, "weakness_score": 50.0, "mastery": 40.0, "next_revision": "2026-07-20T00:00:00+00:00", "revision_stage": 1},
    ]

    recommendation = asyncio.run(get_today_learning_node("user-1", db=FakeDB(rows)))
    assert recommendation["node_id"] == "dsa.foundations.arrays.diff_array"


def test_builder_output_shape():
    node = {
        "id": "dsa.foundations.arrays.prefix_sum",
        "track": "dsa",
        "module": "dsa.foundations",
        "difficulty": "medium",
        "estimated_minutes": 25,
        "label": "Prefix Sum",
    }
    recommendation = build_learning_recommendation(node, progress={"confidence": 3.0, "weakness_score": 70.0, "mastery": 25.0})

    assert recommendation["node_id"] == "dsa.foundations.arrays.prefix_sum"
    assert recommendation["recommendation_type"] == "learning"
    assert recommendation["difficulty"] == "medium"
    assert recommendation["estimated_minutes"] == 25
    assert recommendation["reason"]


def test_revision_selection_uses_due_reviews():
    rows = [
        {"node_id": "dsa.foundations.arrays.traversal", "status": "completed", "confidence": 8.0, "weakness_score": 20.0, "mastery": 90.0},
        {"node_id": "dsa.foundations.arrays.prefix_sum", "status": "completed", "confidence": 6.0, "weakness_score": 50.0, "mastery": 70.0, "next_revision": "2026-07-20T00:00:00+00:00", "revision_stage": 2},
    ]

    due_nodes = get_due_revision_nodes("user-1", progress_rows=rows)
    assert len(due_nodes) == 1
    assert has_due_revision("user-1", progress_rows=rows)
    assert get_highest_priority_revision("user-1", progress_rows=rows)["node_id"] == "dsa.foundations.arrays.prefix_sum"
