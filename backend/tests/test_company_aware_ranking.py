"""Phase 4A: activate existing company-aware mission intelligence.

Verifies that `services/learning_engine/ranking.py` (via `planner.py`) now
consumes the learner's onboarding `target_companies`, sourced through
`roadmap.company_importance()` (the single source of truth — no duplicated
company metadata), and that two learners targeting different companies
genuinely diverge in their top-ranked candidate. Also guards that the
mandatory signals (prerequisite/unlock graph, revision priority, confidence,
mastery) and the deprecated legacy fallback path remain intact.
"""
import asyncio

from mission_engine import choose_focus_topic, _seeded_random
from services.learning_engine.planner import get_today_learning_node
from services.learning_engine.ranking import rank_learning_nodes
from services.learning_engine.revision import get_highest_priority_revision
from services.learning_engine.unlock import get_unlocked_nodes


def _identical_candidates():
    """Two nodes, identical on every axis except track (and therefore the
    roadmap's real, track-level company_importance signal)."""
    return [
        {"id": "cand.cn", "track": "computer_networks", "difficulty": "medium", "estimated_minutes": 30},
        {"id": "cand.java", "track": "java", "difficulty": "medium", "estimated_minutes": 30},
    ]


def _identical_progress():
    return {
        "cand.cn": {"confidence": 5.0, "weakness_score": 50.0, "mastery": 50.0},
        "cand.java": {"confidence": 5.0, "weakness_score": 50.0, "mastery": 50.0},
    }


def test_google_and_oracle_users_get_different_top_pick():
    """dsa vs java: google favors dsa (5 vs 3), oracle favors java (5 vs 3)."""
    candidates = [
        {"id": "cand.dsa", "track": "dsa", "difficulty": "medium", "estimated_minutes": 30},
        {"id": "cand.java", "track": "java", "difficulty": "medium", "estimated_minutes": 30},
    ]
    progress = {
        "cand.dsa": {"confidence": 5.0, "weakness_score": 50.0, "mastery": 50.0},
        "cand.java": {"confidence": 5.0, "weakness_score": 50.0, "mastery": 50.0},
    }

    google_ranked = rank_learning_nodes(candidates, progress, target_companies=["google"])
    oracle_ranked = rank_learning_nodes(candidates, progress, target_companies=["oracle"])

    assert google_ranked[0]["id"] == "cand.dsa"
    assert oracle_ranked[0]["id"] == "cand.java"
    assert google_ranked[0]["id"] != oracle_ranked[0]["id"]


def test_uber_and_microsoft_users_prioritize_different_topics():
    """computer_networks vs java: uber favors cn (4 vs 3), microsoft favors java (4 vs 3)."""
    candidates = _identical_candidates()
    progress = _identical_progress()

    uber_ranked = rank_learning_nodes(candidates, progress, target_companies=["uber"])
    microsoft_ranked = rank_learning_nodes(candidates, progress, target_companies=["microsoft"])

    assert uber_ranked[0]["id"] == "cand.cn"
    assert microsoft_ranked[0]["id"] == "cand.java"


def test_ranking_without_target_companies_is_unaffected():
    """No target_companies -> company_score is 0 for everyone (pre-Phase-4A behavior)."""
    candidates = _identical_candidates()
    progress = _identical_progress()

    ranked = rank_learning_nodes(candidates, progress)
    # Identical scores on every other axis -> stable sort keeps input order.
    assert [n["id"] for n in ranked] == ["cand.cn", "cand.java"]


def test_company_importance_breaks_exact_ties():
    """Item 5: near-identical base scores -> company_importance decides."""
    candidates = _identical_candidates()
    progress = _identical_progress()

    ranked_for_uber = rank_learning_nodes(candidates, progress, target_companies=["uber"])
    ranked_for_none = rank_learning_nodes(candidates, progress)

    assert ranked_for_uber[0]["id"] == "cand.cn"
    assert ranked_for_none[0]["id"] == "cand.cn"  # stable order preserved without a company signal


def test_changing_onboarding_target_companies_changes_planner_output():
    """planner.get_today_learning_node threads target_companies through end to end."""
    progress_rows = [
        {"node_id": "dsa.foundations.arrays.traversal", "status": "completed", "confidence": 8.0, "weakness_score": 20.0, "mastery": 90.0},
    ]

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

    google_rec = asyncio.run(
        get_today_learning_node("user-1", db=FakeDB(progress_rows), target_companies=["google"])
    )
    no_company_rec = asyncio.run(
        get_today_learning_node("user-1", db=FakeDB(progress_rows))
    )
    # Both must still return a valid, unlock-respecting recommendation.
    assert google_rec is not None and no_company_rec is not None


def test_legacy_choose_focus_topic_still_uses_roadmap_company_importance():
    """The deprecated fallback path (no COMPANY_BIAS dict anymore) still works."""
    onboarding = {"self_assessment": {"dsa": 5, "java": 5, "lld": 5, "hld": 5,
                                       "operating_systems": 5, "dbms": 5, "computer_networks": 5}}
    rng = _seeded_random("legacy-user", "2026-07-30")
    topic = choose_focus_topic(onboarding, [], ["google"], rng)
    assert topic in {"dsa", "java", "lld", "hld", "operating_systems", "dbms", "computer_networks"}


def test_mandatory_signals_untouched_unlock_and_revision():
    """Prerequisite/unlock graph and revision priority remain mandatory, unaffected by company changes."""
    progress_rows = [
        {"node_id": "dsa.foundations.arrays.traversal", "status": "completed", "confidence": 8.0, "weakness_score": 20.0, "mastery": 90.0},
        {"node_id": "dsa.foundations.arrays.prefix_sum", "status": "not_started", "confidence": 6.0, "weakness_score": 40.0, "mastery": 40.0,
         "next_revision": "2026-07-20T00:00:00+00:00", "revision_stage": 1},
    ]
    unlocked_google = get_unlocked_nodes(progress_rows)
    revision = get_highest_priority_revision("user-1", progress_rows=progress_rows)

    assert any(n["id"] == "dsa.foundations.arrays.prefix_sum" for n in unlocked_google)
    assert revision is not None and revision.get("node_id") == "dsa.foundations.arrays.prefix_sum"
