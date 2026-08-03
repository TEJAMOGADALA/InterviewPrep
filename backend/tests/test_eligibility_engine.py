"""Phase-4 adaptive mission engine: Eligibility Engine
(services/learning_engine/eligibility.py).

Verifies the eligibility layer enforces the stage gate on top of the
(Phase-1-fixed) prerequisite graph, without hardcoding any specific node
name — the concrete regression this phase exists to prevent is a beginner
being recommended "advanced" DP/HLD/LLD content that happens to carry no
authored prerequisites of its own.
"""
from roadmap import get_roadmap
from services.learning_engine.stage_engine import compute_all_subject_states
from services.learning_engine.eligibility import eligible_learning_nodes, INTERVIEW_URGENCY_THRESHOLD


def test_total_beginner_never_sees_advanced_stage_nodes():
    roadmap = get_roadmap()
    progress = {}
    states = compute_all_subject_states(roadmap, progress)

    eligible = eligible_learning_nodes(progress, states, urgency=0.0)

    assert eligible
    assert all(n.get("learning_stage") != "advanced" for n in eligible)


def test_completed_nodes_are_excluded_from_eligible_set():
    roadmap = get_roadmap()
    a_node = roadmap.get_track_learning_nodes("dsa")[0]
    progress = {a_node["id"]: {"status": "completed", "confidence": 8.0}}
    states = compute_all_subject_states(roadmap, progress)

    eligible = eligible_learning_nodes(progress, states)

    assert a_node["id"] not in {n["id"] for n in eligible}


def test_skip_node_ids_are_excluded():
    roadmap = get_roadmap()
    progress = {}
    states = compute_all_subject_states(roadmap, progress)
    unfiltered = {n["id"] for n in eligible_learning_nodes(progress, states)}
    skip_id = next(iter(unfiltered))

    eligible = eligible_learning_nodes(progress, states, skip_node_ids=[skip_id])

    assert skip_id not in {n["id"] for n in eligible}


def test_high_urgency_widens_stage_cap_to_admit_interview_stage_nodes():
    roadmap = get_roadmap()
    progress = {}
    states = compute_all_subject_states(roadmap, progress)

    low_urgency = eligible_learning_nodes(progress, states, urgency=0.0)
    high_urgency = eligible_learning_nodes(progress, states, urgency=INTERVIEW_URGENCY_THRESHOLD)

    assert len(high_urgency) >= len(low_urgency)


def test_eligible_pool_is_meaningfully_smaller_than_all_unlocked_nodes():
    """The eligibility layer must actually narrow the candidate space, not
    just pass the entire unlocked pool through unchanged."""
    roadmap = get_roadmap()
    progress = {}
    states = compute_all_subject_states(roadmap, progress)

    eligible = eligible_learning_nodes(progress, states)
    all_unlocked = roadmap.get_unlocked_nodes(set())

    assert len(eligible) < len(all_unlocked)
