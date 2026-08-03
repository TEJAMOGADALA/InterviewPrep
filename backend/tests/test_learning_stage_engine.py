"""Phase-3 adaptive mission engine: Learning Stage Engine
(services/learning_engine/stage_engine.py).

Verifies the canonical per-subject stage state is derived correctly from
roadmap `learning_stage` metadata + progress rows, without hardcoding any
specific node name.
"""
from roadmap import get_roadmap
from services.learning_engine.stage_engine import (
    compute_subject_learning_state, compute_all_subject_states, _STAGE_ORDER,
)


def test_beginner_with_no_progress_starts_at_foundation():
    roadmap = get_roadmap()
    state = compute_subject_learning_state("dsa", roadmap, {})

    assert state.track == "dsa"
    assert state.current_stage == "foundation"
    assert state.completed_stage is None
    assert state.next_stage == "foundation"
    assert state.learning_velocity is None
    assert state.revision_state == {"due_count": 0, "has_due": False, "due_node_ids": []}


def test_completing_all_foundation_nodes_advances_current_stage_to_core():
    roadmap = get_roadmap()
    foundation_nodes = [
        n for n in roadmap.get_track_learning_nodes("dsa") if n.get("learning_stage") == "foundation"
    ]
    assert foundation_nodes, "expected at least one dsa foundation-stage node"
    progress = {
        n["id"]: {"status": "completed", "confidence": 8.0, "mastery_percentage": 80.0, "weakness_score": 20.0}
        for n in foundation_nodes
    }

    state = compute_subject_learning_state("dsa", roadmap, progress)

    assert state.completed_stage == "foundation"
    assert state.current_stage == "core"
    # next_eligible_stage never skips more than one stage past current_stage.
    idx_current = _STAGE_ORDER.index(state.current_stage)
    idx_eligible = _STAGE_ORDER.index(state.next_eligible_stage)
    assert idx_eligible <= idx_current + 1


def test_revision_state_reflects_due_next_revision_field():
    roadmap = get_roadmap()
    a_node = roadmap.get_track_learning_nodes("dsa")[0]
    progress = {a_node["id"]: {"status": "in_progress", "next_revision": "2000-01-01T00:00:00+00:00"}}

    state = compute_subject_learning_state("dsa", roadmap, progress)

    assert state.revision_state["has_due"] is True
    assert a_node["id"] in state.revision_state["due_node_ids"]


def test_learning_velocity_requires_at_least_two_days_of_history():
    roadmap = get_roadmap()

    no_history = compute_subject_learning_state("dsa", roadmap, {}, completion_dates=None)
    assert no_history.learning_velocity is None

    single_day = compute_subject_learning_state(
        "dsa", roadmap, {}, completion_dates=["2025-01-01T00:00:00+00:00"],
    )
    assert single_day.learning_velocity is None

    multi_day = compute_subject_learning_state(
        "dsa", roadmap, {},
        completion_dates=["2025-01-01T00:00:00+00:00", "2025-01-03T00:00:00+00:00", "2025-01-05T00:00:00+00:00"],
    )
    assert multi_day.learning_velocity == 0.75  # 3 completions / 4-day span


def test_compute_all_subject_states_covers_every_track():
    roadmap = get_roadmap()
    states = compute_all_subject_states(roadmap, {})

    assert set(states.keys()) == set(roadmap.track_ids())
    for track, state in states.items():
        assert state.track == track
        assert state.current_stage in _STAGE_ORDER
