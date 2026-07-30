"""Phase-3A: interview-deadline-driven adaptive pacing.

Verifies the pacing engine (services/learning_engine/pacing.py) computes the
correct urgency tier for a given interview date, that it plugs into ranking
and mission generation as an additive, backward-compatible signal (study
hours still cap workload; urgency only changes how densely that budget is
used), and that a missing interview date falls back to the exact
pre-Phase-3A behavior.
"""
from datetime import date

from mission_engine import build_mission_for_user
from services.learning_engine.pacing import compute_pacing_state
from services.learning_engine.ranking import rank_learning_nodes

TODAY = date(2026, 7, 30)

DSA_RECOMMENDATION = {
    "track": "dsa",
    "label": "Two Pointers",
    "difficulty": "medium",
    "subtopic": "Two Pointers",
    "node_id": "dsa.foundations.two_pointers.basics",
}


def _mission_shape(mission):
    """Comparable mission shape ignoring random ids/timestamps."""
    return {
        "title": mission.title,
        "focus_area": mission.focus_area,
        "focus_topic": mission.focus_topic,
        "difficulty": mission.difficulty,
        "estimated_duration_minutes": mission.estimated_duration_minutes,
        "learning_objective": mission.learning_objective,
        "tasks": [
            (t.kind, t.topic, t.pattern, t.problem_count, t.node_id, t.title)
            for t in mission.tasks
        ],
    }


# --------------------- Scenario 1-3: pacing tiers ---------------------

def test_pacing_state_180_days_is_on_track():
    state = compute_pacing_state("2027-01-26", daily_study_hours=2, today=TODAY)
    assert state["remaining_days"] == 180
    assert state["pacing_mode"] == "on_track"
    assert state["urgency"] < 0.3


def test_pacing_state_45_days_is_accelerated():
    state = compute_pacing_state("2026-09-13", daily_study_hours=2, today=TODAY)
    assert state["remaining_days"] == 45
    assert state["pacing_mode"] == "accelerated"


def test_pacing_state_15_days_is_critical():
    state = compute_pacing_state("2026-08-14", daily_study_hours=2, today=TODAY)
    assert state["remaining_days"] == 15
    assert state["pacing_mode"] == "critical"
    assert state["urgency"] == 1.0


# --------------------- Scenario 4: study hours vs urgency -------------

def test_mission_practice_count_still_driven_by_study_hours_at_same_urgency():
    pacing_state = compute_pacing_state("2026-09-13", daily_study_hours=2, today=TODAY)  # accelerated

    onboarding_low_hours = {"target_companies": ["google"], "self_assessment": {"dsa": 6}, "daily_study_hours": 1}
    onboarding_high_hours = {"target_companies": ["google"], "self_assessment": {"dsa": 6}, "daily_study_hours": 6}

    mission_low, _ = build_mission_for_user(
        "user-1", onboarding_low_hours, [], [], ds="2026-07-30",
        knowledge_nodes={}, learning_recommendation=DSA_RECOMMENDATION, pacing_state=pacing_state,
    )
    mission_high, _ = build_mission_for_user(
        "user-1", onboarding_high_hours, [], [], ds="2026-07-30",
        knowledge_nodes={}, learning_recommendation=DSA_RECOMMENDATION, pacing_state=pacing_state,
    )

    low_practice = next(t for t in mission_low.tasks if t.kind == "practice")
    high_practice = next(t for t in mission_high.tasks if t.kind == "practice")
    assert low_practice.problem_count < high_practice.problem_count
    # Duration is capped by each user's own declared hours, not by urgency.
    assert mission_low.estimated_duration_minutes == 60
    assert mission_high.estimated_duration_minutes == 360


def test_high_urgency_uses_same_daily_capacity_more_aggressively():
    onboarding = {"target_companies": ["google"], "self_assessment": {"dsa": 6}, "daily_study_hours": 2}

    normal_state = compute_pacing_state("2027-01-26", daily_study_hours=2, today=TODAY)  # on_track
    critical_state = compute_pacing_state("2026-08-14", daily_study_hours=2, today=TODAY)  # critical

    mission_normal, adj_normal = build_mission_for_user(
        "user-1", onboarding, [], [], ds="2026-07-30",
        knowledge_nodes={}, learning_recommendation=DSA_RECOMMENDATION, pacing_state=normal_state,
    )
    mission_critical, adj_critical = build_mission_for_user(
        "user-1", onboarding, [], [], ds="2026-07-30",
        knowledge_nodes={}, learning_recommendation=DSA_RECOMMENDATION, pacing_state=critical_state,
    )

    normal_practice = next(t for t in mission_normal.tasks if t.kind == "practice")
    critical_practice = next(t for t in mission_critical.tasks if t.kind == "practice")
    assert critical_practice.problem_count > normal_practice.problem_count
    # Never an impossible workload: same declared 2h capacity either way.
    assert mission_normal.estimated_duration_minutes == mission_critical.estimated_duration_minutes == 120
    assert adj_normal["pacing_mode"] == "on_track"
    assert adj_critical["pacing_mode"] == "critical"


def test_ranking_urgency_prioritizes_interview_value_and_shorter_nodes():
    nodes = [
        {"id": "low-value", "difficulty": "medium", "estimated_minutes": 20, "interview_importance": 1, "interview_frequency": 1},
        {"id": "high-value", "difficulty": "medium", "estimated_minutes": 20, "interview_importance": 5, "interview_frequency": 5},
    ]
    progress = {
        "low-value": {"confidence": 5.0, "weakness_score": 50.0, "mastery": 50.0},
        "high-value": {"confidence": 5.0, "weakness_score": 50.0, "mastery": 50.0},
    }

    baseline = rank_learning_nodes(nodes, progress, urgency=0.0)
    assert baseline[0]["id"] == "low-value"  # identical scores, urgency=0 does not distinguish them

    urgent = rank_learning_nodes(nodes, progress, urgency=1.0)
    assert urgent[0]["id"] == "high-value"


# --------------------- Scenario 5: no interview date -> fallback -------

def test_missing_interview_date_pacing_state_is_a_noop():
    state = compute_pacing_state(None, daily_study_hours=2, today=TODAY)
    assert state["has_target_date"] is False
    assert state["remaining_days"] is None
    assert state["pacing_mode"] == "standard"
    assert state["urgency"] == 0.0


def test_missing_interview_date_falls_back_to_current_mission_behavior():
    onboarding = {"target_companies": ["google"], "self_assessment": {"dsa": 6}, "daily_study_hours": 2}
    pacing_state = compute_pacing_state(None, daily_study_hours=2, today=TODAY)

    mission_with_state, adj_with_state = build_mission_for_user(
        "user-1", onboarding, [], [], ds="2026-07-30",
        knowledge_nodes={}, learning_recommendation=DSA_RECOMMENDATION, pacing_state=pacing_state,
    )
    mission_baseline, adj_baseline = build_mission_for_user(
        "user-1", onboarding, [], [], ds="2026-07-30",
        knowledge_nodes={}, learning_recommendation=DSA_RECOMMENDATION,
    )

    assert _mission_shape(mission_with_state) == _mission_shape(mission_baseline)
    assert adj_with_state["pacing_mode"] == adj_baseline["pacing_mode"] == "standard"
    assert adj_with_state["urgency"] == adj_baseline["urgency"] == 0.0
