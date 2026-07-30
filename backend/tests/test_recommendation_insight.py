"""Phase 4B: Intelligent Recommendation Engine (explainability + ROI + forecast).

Verifies that the Recommendation Insight object (services/learning_engine/insight.py)
is derived entirely from the same signals `ranking.score_learning_node()` used to
pick a node — never a hardcoded explanation — that ROI is computed live from the
roadmap's existing prerequisite graph, and that the completion forecast
(services/learning_engine/pacing.forecast_completion) reacts to both study hours
and interview date while reusing compute_pacing_state's own math.
"""
import asyncio
from datetime import date

from services.learning_engine.insight import build_recommendation_insight
from services.learning_engine.pacing import compute_pacing_state, forecast_completion
from services.learning_engine.planner import get_today_learning_node
from services.learning_engine.ranking import score_learning_node
from services.learning_engine.roi import compute_learning_roi


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
        self.knowledge_nodes = FakeCollection(rows)


def test_roi_is_derived_from_the_real_prerequisite_graph():
    # dsa.foundations.arrays.traversal is a direct prerequisite of several
    # real roadmap nodes (prefix_sum, diff_array, ...).
    roi = compute_learning_roi("dsa.foundations.arrays.traversal")
    assert roi["direct_unlocks"] > 0
    assert roi["total_downstream_unlocks"] >= roi["direct_unlocks"]
    assert roi["roi_score"] > 0

    # Unknown / not-yet-roadmap node -> safe zero, never a crash.
    assert compute_learning_roi("not.a.real.node") == {
        "direct_unlocks": 0, "total_downstream_unlocks": 0, "dependency_count": 0, "roi_score": 0.0,
    }


def test_insight_explanation_matches_the_ranking_breakdown_exactly():
    node = {"id": "dsa.foundations.arrays.traversal", "track": "dsa", "label": "Array Traversal",
            "difficulty": "medium", "estimated_minutes": 25}
    progress = {"confidence": 3.0, "weakness_score": 70.0, "mastery": 25.0}

    breakdown = score_learning_node(node, progress, target_companies=["google"])
    insight = build_recommendation_insight(node, score_breakdown=breakdown, target_companies=["google"])

    # No re-derivation: insight's numbers must equal the breakdown's numbers.
    assert insight["confidence"] == breakdown["confidence"]
    assert insight["weakness"] == breakdown["weakness"]
    assert insight["mastery"] == breakdown["mastery"]
    assert insight["overall_score"] == round(breakdown["total_score"], 2)
    assert insight["roi"] == breakdown["roi"]
    # Explanation text must actually contain the real signal values, not a template.
    assert "3.0/10" in insight["explanation"]
    assert "weakness 70" in insight["explanation"]
    assert "Weak topic" in insight["highlights"]


def test_highlights_are_generated_dynamically_not_hardcoded():
    strong_node = {"id": "cand.strong", "track": "dsa", "label": "Strong Node",
                   "difficulty": "medium", "estimated_minutes": 20}
    strong_progress = {"confidence": 9.0, "weakness_score": 5.0, "mastery": 95.0}
    breakdown = score_learning_node(strong_node, strong_progress)
    insight = build_recommendation_insight(strong_node, score_breakdown=breakdown)
    assert "Weak topic" not in insight["highlights"]

    weak_node = {"id": "cand.weak", "track": "dsa", "label": "Weak Node",
                 "difficulty": "medium", "estimated_minutes": 20}
    weak_progress = {"confidence": 1.0, "weakness_score": 90.0, "mastery": 5.0}
    breakdown2 = score_learning_node(weak_node, weak_progress)
    insight2 = build_recommendation_insight(weak_node, score_breakdown=breakdown2)
    assert "Weak topic" in insight2["highlights"]


def test_different_companies_produce_different_explanations():
    node = {"id": "cand.dsa", "track": "dsa", "label": "DSA Node", "difficulty": "medium", "estimated_minutes": 20}
    progress = {"confidence": 5.0, "weakness_score": 50.0, "mastery": 50.0}

    google_breakdown = score_learning_node(node, progress, target_companies=["google"])
    oracle_breakdown = score_learning_node(node, progress, target_companies=["oracle"])
    google_insight = build_recommendation_insight(node, score_breakdown=google_breakdown, target_companies=["google"])
    oracle_insight = build_recommendation_insight(node, score_breakdown=oracle_breakdown, target_companies=["oracle"])

    # dsa track: google company_importance=5, oracle=3 (roadmap_v1.json).
    assert google_insight["company_relevance"]["per_company"]["google"] > oracle_insight["company_relevance"]["per_company"]["oracle"]
    assert google_insight["explanation"] != oracle_insight["explanation"]
    assert "High relevance to google" in google_insight["highlights"]
    assert "High relevance to google" not in oracle_insight["highlights"]


def test_forecast_changes_when_study_hours_change():
    pacing_low = compute_pacing_state("2026-12-01", 1.0, 100, today=date(2026, 7, 30))
    pacing_high = compute_pacing_state("2026-12-01", 6.0, 100, today=date(2026, 7, 30))

    # No completion history yet -> forecast falls back to capacity-based pace,
    # which must scale with daily_study_hours.
    forecast_low = forecast_completion(pacing_low, remaining_nodes=100)
    forecast_high = forecast_completion(pacing_high, remaining_nodes=100)

    assert forecast_high["capacity_pace_nodes_per_day"] > forecast_low["capacity_pace_nodes_per_day"]
    assert forecast_high["current_pace_nodes_per_day"] > forecast_low["current_pace_nodes_per_day"]
    assert forecast_high["finish_confidence"] >= forecast_low["finish_confidence"]


def test_forecast_changes_when_interview_date_changes():
    pacing_soon = compute_pacing_state("2026-08-15", 3.0, 100, today=date(2026, 7, 30))
    pacing_later = compute_pacing_state("2027-06-01", 3.0, 100, today=date(2026, 7, 30))

    forecast_soon = forecast_completion(pacing_soon, remaining_nodes=100)
    forecast_later = forecast_completion(pacing_later, remaining_nodes=100)

    assert forecast_soon["required_pace_nodes_per_day"] > forecast_later["required_pace_nodes_per_day"]
    assert forecast_soon["remaining_days"] < forecast_later["remaining_days"]
    assert forecast_soon["finish_confidence"] < forecast_later["finish_confidence"]


def test_planner_recommendation_still_backward_compatible_and_now_carries_insight():
    rows = [
        {"node_id": "dsa.foundations.arrays.prefix_sum", "status": "completed", "confidence": 7.0, "weakness_score": 30.0, "mastery": 80.0},
    ]
    recommendation = asyncio.run(
        get_today_learning_node("user-1", db=FakeDB(rows), target_companies=["google"])
    )

    # Pre-existing keys (backward compatibility — no API contract broken).
    assert "node_id" in recommendation
    assert "track" in recommendation
    assert "reason" in recommendation
    assert recommendation["recommendation_type"] == "learning"

    # New Phase 4B key.
    insight = recommendation["insight"]
    assert insight["node_id"] == recommendation["node_id"]
    assert "explanation" in insight and insight["explanation"]
    assert "roi" in insight
    assert "forecast" in insight
    assert "highlights" in insight


def test_planner_without_new_params_is_still_a_no_op_default():
    rows = [
        {"node_id": "dsa.foundations.arrays.prefix_sum", "status": "completed", "confidence": 7.0, "weakness_score": 30.0, "mastery": 80.0},
    ]
    recommendation = asyncio.run(get_today_learning_node("user-1", db=FakeDB(rows)))
    assert recommendation is not None
    assert recommendation["insight"]["company_relevance"]["target_companies"] == []
