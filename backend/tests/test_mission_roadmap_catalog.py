"""Regression tests for roadmap-backed mission content selection."""

from mission_engine import (
    TOPIC_META,
    _seeded_random,
    get_candidate_topics,
    rank_candidate_topics,
)
from models import TOPIC_KEYS
from roadmap import topic_meta


def test_mission_catalog_is_the_roadmap_catalog_for_supported_tracks():
    """Mission generation must not drift from the versioned roadmap."""
    roadmap_catalog = topic_meta()

    for track in TOPIC_KEYS:
        assert TOPIC_META[track] == roadmap_catalog[track]
        assert TOPIC_META[track]["subtopics"]


def test_mission_catalog_exposes_roadmap_content_outside_the_legacy_mvp_list():
    labels = {candidate["label"] for candidate in get_candidate_topics("hld")}

    # This roadmap topic was absent from the old five-item HLD mission catalog.
    assert "Design Amazon S3" in labels


def test_candidate_ranking_prefers_unlocked_topics_before_progress_signals():
    candidates = [
        {"id": "locked", "label": "Locked", "difficulty": "easy", "status": "locked"},
        {"id": "available", "label": "Available", "difficulty": "hard", "status": "available"},
    ]

    selected = rank_candidate_topics(
        candidates,
        knowledge_nodes={
            "locked": {"confidence": 0, "weakness_score": 100, "status": "not_started", "mastery_percentage": 0},
            "available": {"confidence": 10, "weakness_score": 0, "status": "mastered", "mastery_percentage": 100},
        },
        target_companies=[],
        rng=_seeded_random("ranking-user", "2026-07-23"),
    )

    assert selected["id"] == "available"


def test_candidate_ranking_uses_seeded_rng_for_exact_ties():
    candidates = [
        {"id": "first", "label": "First", "difficulty": "easy", "status": "available"},
        {"id": "second", "label": "Second", "difficulty": "easy", "status": "available"},
    ]
    user_id = "selection-regression-user"
    date = "2026-07-23"

    expected_rng = _seeded_random(user_id, date)
    expected = expected_rng.choice(candidates)
    actual = rank_candidate_topics(
        candidates,
        knowledge_nodes={},
        target_companies=[],
        rng=_seeded_random(user_id, date),
    )

    assert actual == expected
