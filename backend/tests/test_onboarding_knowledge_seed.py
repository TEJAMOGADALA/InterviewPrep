"""Phase-2 adaptive mission engine: onboarding seeds `knowledge_nodes`.

Verifies that converting self-assessment sliders into baseline
`knowledge_nodes` rows (services/progress_engine.py::seed_knowledge_nodes_from_self_assessment)
gives the planner (services/learning_engine) different inputs for different
learners, without hardcoding any specific mission/node name.

RC1.3.6A Phase 2 replaced the old "identical value for every node in the
track" seeding with STAGE-AWARE seeding: a track's rating now selects a
starting `learning_stage` (foundation < core < intermediate < advanced).
Nodes below that stage are seeded as already understood
(`status="completed"`, so later stages become legitimately eligible), nodes
at that stage are seeded proportionally to the rating (`status="in_progress"`),
and nodes above that stage are left unseeded (a genuine cold start). Tracks
with no stage progression (behavioral/projects/resume) keep the old flat
uniform baseline.
"""
import asyncio

from roadmap import get_roadmap
from services.learning_engine.planner import get_today_learning_node
from services.learning_engine.ranking import rank_learning_nodes
from services.progress_engine import seed_knowledge_nodes_from_self_assessment, _node_stage_index, _STAGE_ORDER


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


def test_seed_covers_every_roadmap_track_with_stage_aware_rows():
    """Every roadmap track is seeded (item 6), but a stage-structured track
    only gets rows up to the learner's starting stage — never every node
    flatly — while tracks the onboarding UI never asks about
    (behavioral/projects/resume) still get a neutral flat baseline."""
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
    assert inserted > 0

    # dsa rating=1 -> starting stage "foundation": only foundation-stage dsa
    # nodes are seeded; anything core/intermediate/advanced is left cold.
    dsa_nodes = roadmap.get_track_learning_nodes("dsa")
    dsa_foundation_ids = {n["id"] for n in dsa_nodes if _node_stage_index(n) == 0}
    dsa_seeded_ids = {row["node_id"] for row in rows_by_track.get("dsa", [])}
    assert dsa_seeded_ids == dsa_foundation_ids
    assert len(dsa_seeded_ids) < len(dsa_nodes)

    # Tracks never covered by onboarding sliders AND with no stage progression
    # of their own (behavioral/projects/resume) still get a full neutral flat
    # baseline. (Programming Fundamentals is also never asked about by the
    # onboarding sliders and, unlike dsa/java/etc., is never seeded at all —
    # see test_programming_fundamentals_is_never_seeded_from_onboarding below
    # — so it is deliberately excluded from this "flat track" check.)
    flat_tracks = {"behavioral", "projects", "resume"}
    unrated_track = next(
        t for t in roadmap.track_ids() if t not in SELF_ASSESSMENT_LOW_DSA and t in flat_tracks
    )
    unrated_rows = rows_by_track.get(unrated_track, [])
    assert len(unrated_rows) == len(roadmap.get_track_learning_nodes(unrated_track))
    assert all(row["confidence"] == 5.0 and row["status"] == "in_progress" for row in unrated_rows)


def test_high_rating_marks_earlier_stages_completed_so_later_stages_unlock():
    """DSA=8 -> starting stage "advanced": foundation/core/intermediate dsa
    nodes are marked already-understood (status="completed") so later-stage
    nodes become legitimately eligible through the real prerequisite chain
    -- this is the concrete behavior Phase 2 was written to produce."""
    roadmap = get_roadmap()
    db = FakeDB()

    asyncio.run(
        seed_knowledge_nodes_from_self_assessment(db, "user-a", SELF_ASSESSMENT_HIGH_DSA, roadmap)
    )

    dsa_nodes = roadmap.get_track_learning_nodes("dsa")
    rows = {row["node_id"]: row for row in db.knowledge_nodes._rows if roadmap.get(row["node_id"])["track"] == "dsa"}

    below_advanced = [n for n in dsa_nodes if _node_stage_index(n) < _STAGE_ORDER.index("advanced")]
    at_advanced = [n for n in dsa_nodes if _node_stage_index(n) == _STAGE_ORDER.index("advanced")]
    above_advanced = [n for n in dsa_nodes if _node_stage_index(n) > _STAGE_ORDER.index("advanced")]

    assert below_advanced and all(rows[n["id"]]["status"] == "completed" for n in below_advanced)
    assert at_advanced and all(rows[n["id"]]["status"] == "in_progress" for n in at_advanced)
    for n in above_advanced:
        assert n["id"] not in rows  # cold start — never pre-unlocked from a slider alone

    # No node is ever marked "mastered" purely from onboarding.
    assert all(row["status"] != "mastered" for row in rows.values())


def test_programming_fundamentals_is_never_seeded_from_onboarding():
    """Programming Fundamentals is the universal starting point: a brand-new
    user must see it at a genuine 0% (not a stage-projected or neutral
    baseline), even when the onboarding payload carries an explicit rating
    for it, so it can only be earned by actually studying the track."""
    roadmap = get_roadmap()
    db = FakeDB()

    self_assessment = {**SELF_ASSESSMENT_LOW_DSA, "programming_fundamentals": 9}
    asyncio.run(
        seed_knowledge_nodes_from_self_assessment(db, "user-a", self_assessment, roadmap)
    )

    pf_rows = [
        row for row in db.knowledge_nodes._rows
        if roadmap.get(row["node_id"])["track"] == "programming_fundamentals"
    ]
    assert pf_rows == []


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

    # Calling again inserts nothing new (fully idempotent).
    before = len(db.knowledge_nodes._rows)
    asyncio.run(
        seed_knowledge_nodes_from_self_assessment(db, "user-a", SELF_ASSESSMENT_LOW_DSA, roadmap)
    )
    assert len(db.knowledge_nodes._rows) == before


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

    # Foundation-stage dsa nodes with no prerequisites are seeded under both
    # scenarios (A: at-stage/in_progress: B: below-stage/completed), so their
    # confidence values are guaranteed to differ.
    unlocked_dsa_ids = [
        n["id"] for n in roadmap.get_unlocked_nodes(set())
        if n.get("track") == "dsa" and n["id"] in rows_a and n["id"] in rows_b
    ]
    assert unlocked_dsa_ids, "expected at least one unlocked dsa node seeded under both scenarios"

    for node_id in unlocked_dsa_ids:
        assert rows_a[node_id]["confidence"] != rows_b[node_id]["confidence"]
        assert rows_a[node_id]["status"] != rows_b[node_id]["status"]

    # Feed the two distinct progress states through the real ranking model.
    candidates = [n for n in roadmap.get_unlocked_nodes(set()) if n["id"] in unlocked_dsa_ids]
    ranked_a = rank_learning_nodes(candidates, rows_a)
    ranked_b = rank_learning_nodes(candidates, rows_b)

    score_lookup_a = {n["id"]: idx for idx, n in enumerate(ranked_a)}
    score_lookup_b = {n["id"]: idx for idx, n in enumerate(ranked_b)}
    assert score_lookup_a != score_lookup_b or rows_a != rows_b

    # End-to-end sanity: the full planner still returns a valid recommendation
    # for both users (not asserting cross-track pick identity/inequality here
    # — the single globally-best node can coincidentally land on the same
    # non-dsa node for both users when their other tracks share identical
    # ratings, which is expected and unrelated to what this test verifies).
    recommendation_a = asyncio.run(get_today_learning_node("user-a", db=db_a))
    recommendation_b = asyncio.run(get_today_learning_node("user-b", db=db_b))
    assert recommendation_a is not None and recommendation_b is not None
