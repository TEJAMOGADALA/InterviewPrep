"""Phase-5 adaptive mission engine: Candidate Generation
(services/learning_engine/candidates.py).

Verifies the eligible-node pool is narrowed to a compact ~15-30 node
candidate set before ranking, without hardcoding any specific node name.
"""
from roadmap import get_roadmap
from services.learning_engine.stage_engine import compute_all_subject_states
from services.learning_engine.eligibility import eligible_learning_nodes
from services.learning_engine.candidates import generate_candidate_nodes, DEFAULT_MAX_CANDIDATES


def test_candidate_pool_is_compact_and_within_expected_range():
    roadmap = get_roadmap()
    # RC1.3.7 stage_engine fix: a fully blank-progress user now correctly sees
    # only foundation-stage, zero-prereq nodes (one small slice per track),
    # so completing a few foundation nodes is needed to unlock enough
    # downstream content for the pool to genuinely exceed DEFAULT_MAX_CANDIDATES
    # and exercise real trimming (rather than the previous, looser gating that
    # inflated the blank-progress pool to 189 nodes across every stage).
    progress = {
        n["id"]: {"status": "completed"}
        for n in roadmap.get_learning_nodes()
        if n.get("learning_stage") == "foundation"
    }
    states = compute_all_subject_states(roadmap, progress)
    eligible = eligible_learning_nodes(progress, states)
    assert len(eligible) > DEFAULT_MAX_CANDIDATES  # sanity: trimming is actually needed

    candidates = generate_candidate_nodes(
        eligible, progress, states, roadmap=roadmap, target_companies=["google"], urgency=0.0,
    )

    assert 1 <= len(candidates) <= DEFAULT_MAX_CANDIDATES
    assert len({n["id"] for n in candidates}) == len(candidates)  # no duplicates


def test_candidate_generation_is_a_noop_when_pool_already_compact():
    roadmap = get_roadmap()
    small_pool = roadmap.get_track_learning_nodes("dsa")[:5]
    progress = {}
    states = compute_all_subject_states(roadmap, progress)

    candidates = generate_candidate_nodes(small_pool, progress, states, roadmap=roadmap)

    assert candidates == small_pool


def test_candidate_generation_is_deterministic():
    roadmap = get_roadmap()
    progress = {}
    states = compute_all_subject_states(roadmap, progress)
    eligible = eligible_learning_nodes(progress, states)

    run1 = generate_candidate_nodes(eligible, progress, states, roadmap=roadmap, target_companies=["uber"], urgency=0.3)
    run2 = generate_candidate_nodes(eligible, progress, states, roadmap=roadmap, target_companies=["uber"], urgency=0.3)

    assert [n["id"] for n in run1] == [n["id"] for n in run2]


def test_weakest_or_revision_due_track_is_prioritized():
    """A track with a due revision must be represented in the candidate set
    even when its raw eligible-node count is small relative to other tracks."""
    roadmap = get_roadmap()
    dsa_node = roadmap.get_track_learning_nodes("dsa")[0]
    progress = {dsa_node["id"]: {"status": "in_progress", "next_revision": "2000-01-01T00:00:00+00:00"}}
    states = compute_all_subject_states(roadmap, progress)
    assert states["dsa"].revision_state["has_due"] is True

    eligible = eligible_learning_nodes(progress, states)
    candidates = generate_candidate_nodes(eligible, progress, states, roadmap=roadmap, urgency=0.0)

    assert any(n.get("track") == "dsa" for n in candidates)
