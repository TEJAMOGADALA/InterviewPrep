"""Unit tests for roadmap-node progress infrastructure."""
import asyncio

from roadmap import get_roadmap
from services.roadmap_progress.initializer import (
    RoadmapProgressInitializer,
    build_initial_progress,
)


class InMemoryProgressRepository:
    """Small repository fake that models the production uniqueness constraint."""

    def __init__(self):
        self.rows = {}

    async def initialize_nodes(self, progress_rows):
        inserted = 0
        for row in progress_rows:
            key = (row.user_id, row.node_id)
            if key not in self.rows:
                self.rows[key] = row
                inserted += 1
        return inserted


def test_learning_node_traversal_helpers_follow_roadmap_prerequisites():
    roadmap = get_roadmap()
    traversal = "dsa.foundations.arrays.traversal"
    prefix_sum = "dsa.foundations.arrays.prefix_sum"

    learning_nodes = roadmap.get_learning_nodes()
    assert learning_nodes
    assert roadmap.get_learning_node(traversal)["id"] == traversal
    assert roadmap.get_track_learning_nodes("dsa")
    assert not roadmap.is_unlocked(prefix_sum)
    assert roadmap.is_unlocked(prefix_sum, {traversal})
    assert prefix_sum in {
        node["id"] for node in roadmap.get_unlocked_nodes({traversal})
    }
    assert roadmap.get_next_learning_node(traversal)


def test_initializer_builds_one_idempotent_progress_row_per_learning_node():
    async def run():
        roadmap = get_roadmap()
        repository = InMemoryProgressRepository()
        initializer = RoadmapProgressInitializer(repository, roadmap)

        first_insert_count = await initializer.initialize_for_user("test-user")
        second_insert_count = await initializer.initialize_for_user("test-user")

        assert first_insert_count == len(roadmap.get_learning_nodes())
        assert second_insert_count == 0

        row = repository.rows[("test-user", "dsa.foundations.arrays.traversal")]
        assert row.track == "dsa"
        assert row.module == "foundations"
        assert row.topic == "arrays"
        assert row.subtopic == "traversal"
        assert row.status == "not_started"
        assert row.weakness_score == 100

    asyncio.run(run())


def test_initial_progress_defaults_do_not_depend_on_existing_progress_collections():
    node = get_roadmap().get_learning_node("dsa.foundations.arrays.traversal")
    progress = build_initial_progress("test-user", node)

    assert progress.times_practiced == 0
    assert progress.times_completed == 0
    assert progress.mastery == 0
    assert progress.confidence == 0
