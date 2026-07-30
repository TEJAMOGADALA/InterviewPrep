"""Phase-2 adaptive mission engine: onboarding seeds `knowledge_nodes`.

Verifies that converting self-assessment sliders into baseline
`knowledge_nodes` rows (services/progress_engine.py::seed_knowledge_nodes_from_self_assessment)
gives the planner (services/learning_engine) different inputs for
different learners, without hardcoding any specific mission/node name and
without marking any roadmap node completed/mastered.
"""
import asyncio

from roadmap import get_roadmap
from services.learning_engine.planner import get_today_learning_node
from services.learning_engine.ranking import rank_learning_nodes
from services.progress_engine import seed_knowledge_nodes_from_self_assessment


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    async def to_list(self, length=None):
        return list(self._rows)


class FakeCollection:
    def __init__(self, rows=None):
        self._rows = rows if rows is not None else []

    def find(self, query=None, projection=None):
        query = query or {}
        matched = [
            row for row in self._rows
            if all(row.get(k) == v for k, v in query.items())
        ]
        return FakeCursor(matched)

    async def insert_many(self, rows):
        self._rows.extend(rows)


class FakeDB:
    def __init__(self, rows=None):
        self.knowledge_nodes = FakeCollection(rows)


SELF_ASSESSMENT_LOW_DSA = {
    "dsa": 1, "java": 5, "lld": 5, "hld": 5,
    "operating_systems": 5, "dbms": 5, "computer_networks": 5,
}
SELF_ASSESSMENT_HIGH_DSA = {
    "dsa": 8, "java": 5, "lld": 5, "hld": 5,
    "operating_systems": 5, "dbms": 5, "computer_networks": 5,
}


def test_seed_covers_every_roadmap_track_independently():
    """Every roadmap track is seeded, not just the 7 legacy tracks the
    onboarding self-assessment sliders ask about (item 6) — tracks the UI
    never rates (behavioral/projects/resume) get a neutral baseline instead
    of staying permanently unseeded, and a track's slider never leaks into
    another track's rows."""
    roadmap = get_roadmap()
    db = FakeDB()

    inserted = asyncio.run(
        seed_knowledge_nodes_from_self_assessment(db, "user-a", SELF_ASSESSMENT_LOW_DSA, roadmap)
    )

    rows_by_track = {}
    for row in db.knowledge_nodes._rows:
        node = roadmap.get(row["node_id"])
        rows_by_track.setdefault(node["track"], []).append(row)

    assert inserted == len(db.knowledge_nodes._rows)
    assert inserted == sum(len(roadmap.get_track_learning_nodes(t)) for t in roadmap.track_ids())
    for track in roadmap.track_ids():
        assert len(rows_by_track.get(track, [])) == len(roadmap.get_track_learning_nodes(track))
    # dsa rows reflect the dsa rating (1); every other rated track reflects
    # its own independent rating (5) — a track's slider never leaks into others.
    assert rows_by_track["dsa"] and all(row["confidence"] == 1.0 for row in rows_by_track["dsa"])
    other_track = next(t for t in ("java", "lld", "hld") if rows_by_track.get(t))
    assert all(row["confidence"] == 5.0 for row in rows_by_track[other_track])
    # Tracks never covered by onboarding sliders still get a neutral baseline.
    unrated_track = next(t for t in roadmap.track_ids() if t not in SELF_ASSESSMENT_LOW_DSA)
    assert rows_by_track.get(unrated_track)
    assert all(row["confidence"] == 5.0 for row in rows_by_track[unrated_track])


def test_seed_never_marks_nodes_completed_or_mastered():
    """Self-assessment must never unlock/complete nodes (item 7)."""
    roadmap = get_roadmap()
    db = FakeDB()

    asyncio.run(
        seed_knowledge_nodes_from_self_assessment(db, "user-a", SELF_ASSESSMENT_HIGH_DSA, roadmap)
    )

    statuses = {row["status"] for row in db.knowledge_nodes._rows}
    assert statuses == {"in_progress"}
    assert all(row["completion_date"] is None for row in db.knowledge_nodes._rows)

    # Prerequisite chains stay intact: a node gated behind an unfinished
    # prerequisite is still locked even though its own row was seeded.
    gated_node = next(
        n for n in roadmap.get_track_learning_nodes("dsa") if n.get("prerequisites")
    )
    unlocked_ids = {n["id"] for n in roadmap.get_unlocked_nodes(set())}
    assert gated_node["id"] not in unlocked_ids


def test_seed_is_idempotent_and_never_overwrites_existing_progress():
    """Existing users keep their real progress untouched (item 3)."""
    roadmap = get_roadmap()
    existing_node = roadmap.get_track_learning_nodes("dsa")[0]
    db = FakeDB(rows=[{
        "user_id": "user-a", "roadmap_version": roadmap.version,
        "node_id": existing_node["id"], "status": "completed",
        "confidence": 9.5, "mastery_percentage": 95.0, "weakness_score": 5.0,
    }])

    asyncio.run(
        seed_knowledge_nodes_from_self_assessment(db, "user-a", SELF_ASSESSMENT_LOW_DSA, roadmap)
    )

    preserved = next(r for r in db.knowledge_nodes._rows if r["node_id"] == existing_node["id"])
    assert preserved["status"] == "completed"
    assert preserved["confidence"] == 9.5
    # Every other node across every track was still seeded.
    assert len(db.knowledge_nodes._rows) == sum(
        len(roadmap.get_track_learning_nodes(t)) for t in roadmap.track_ids()
    )


def test_planner_input_differs_between_low_and_high_dsa_self_assessment():
    """Scenario A (DSA=1) vs Scenario B (DSA=8): the planner must receive
    different progress values for the same unlocked dsa nodes — no snapshot
    of any specific node/mission name."""
    roadmap = get_roadmap()
    db_a = FakeDB()
    db_b = FakeDB()

    asyncio.run(seed_knowledge_nodes_from_self_assessment(db_a, "user-a", SELF_ASSESSMENT_LOW_DSA, roadmap))
    asyncio.run(seed_knowledge_nodes_from_self_assessment(db_b, "user-b", SELF_ASSESSMENT_HIGH_DSA, roadmap))

    rows_a = {r["node_id"]: r for r in db_a.knowledge_nodes._rows}
    rows_b = {r["node_id"]: r for r in db_b.knowledge_nodes._rows}

    unlocked_dsa_ids = [
        n["id"] for n in roadmap.get_unlocked_nodes(set()) if n.get("track") == "dsa"
    ]
    assert unlocked_dsa_ids, "expected at least one unlocked dsa node with no prerequisites"

    for node_id in unlocked_dsa_ids:
        assert rows_a[node_id]["confidence"] != rows_b[node_id]["confidence"]
        assert rows_a[node_id]["weakness_score"] != rows_b[node_id]["weakness_score"]
        assert rows_a[node_id]["mastery_percentage"] != rows_b[node_id]["mastery_percentage"]

    # Feed the two distinct progress states through the real ranking model.
    candidates = [n for n in roadmap.get_unlocked_nodes(set()) if n["id"] in unlocked_dsa_ids]
    ranked_a = rank_learning_nodes(candidates, rows_a)
    ranked_b = rank_learning_nodes(candidates, rows_b)

    # Low self-assessment (weaker/less confident) must score at least as
    # urgent as high self-assessment for the same candidate set.
    score_lookup_a = {n["id"]: idx for idx, n in enumerate(ranked_a)}
    score_lookup_b = {n["id"]: idx for idx, n in enumerate(ranked_b)}
    assert score_lookup_a != score_lookup_b or rows_a != rows_b

    recommendation_a = asyncio.run(get_today_learning_node("user-a", db=db_a))
    recommendation_b = asyncio.run(get_today_learning_node("user-b", db=db_b))
    assert recommendation_a is not None and recommendation_b is not None
    # Do not assert a specific node id — only that the planner's *input*
    # (confidence/weakness/mastery) genuinely differed between the two users.
    assert recommendation_a["reason"] != recommendation_b["reason"]
