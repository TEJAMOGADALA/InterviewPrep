"""Phase 4C — Universal Learning Node Integration regression tests.

Root cause found: mission_engine.build_mission_for_user() validated the
Learning Engine's support-track recommendation against TOPIC_KEYS — a
legacy 7-track allowlist (dsa/java/lld/hld/operating_systems/dbms/
computer_networks) originally introduced only for onboarding self-assessment
sliders. The real roadmap has 10 tracks (it also includes behavioral,
projects, resume). Any support recommendation for a track outside TOPIC_KEYS
was silently discarded, so the fully track-agnostic
`_select_unlocked_roadmap_node()` fallback never ran for those tracks and no
`node_id` was attached to the resulting MissionTask — which is what actually
gates the "Open KB" / "AI Mentor" buttons in Mission Control
(`{t.node_id && (...)}`). The Knowledge Base routes, AI Mentor routing and
Mission Control button gate itself were already fully track-agnostic; only
this one hardcoded allowlist check needed to be generalized to the roadmap's
own track catalog (TOPIC_META, derived from roadmap.topic_meta()).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mission_engine import build_mission_for_user, TOPIC_META  # noqa: E402
from roadmap import get_roadmap  # noqa: E402


def _onboarding():
    return {"target_companies": [], "daily_study_hours": 2, "current_position": "0-1"}


def test_topic_meta_covers_every_real_roadmap_track():
    # TOPIC_META is derived straight from the roadmap (roadmap.topic_meta()),
    # so it is the correct single source of truth for "which tracks exist" —
    # unlike the legacy TOPIC_KEYS allowlist.
    for track in ("dsa", "java", "lld", "hld", "operating_systems", "dbms",
                  "computer_networks", "behavioral", "projects", "resume"):
        assert track in TOPIC_META
        assert TOPIC_META[track]["subtopics"], f"{track} must expose at least one subtopic"


def test_support_task_for_behavioral_track_gets_a_node_id_via_fallback_selection():
    # No explicit "support_node" key -> forces the _select_unlocked_roadmap_node
    # fallback path, which must not be skipped just because the support track
    # is outside the legacy TOPIC_KEYS allowlist.
    learning_recommendation = {
        "track": "dsa",
        "node_id": "dsa.foundations.arrays.traversal",
        "label": "Array Traversal",
        "difficulty": "easy",
        "support_track": "behavioral",
    }
    mission, _ = build_mission_for_user(
        user_id="u1",
        onboarding=_onboarding(),
        knowledge=[],
        revisions_due=[],
        knowledge_nodes={},
        learning_recommendation=learning_recommendation,
        ds="2026-01-01",
    )
    support_tasks = [t for t in mission.tasks if t.topic == "behavioral"]
    assert support_tasks, "expected a behavioral support task to be generated"
    assert support_tasks[0].node_id, (
        "behavioral support task must carry a node_id so Open KB / AI Mentor "
        "buttons in Mission Control can target it, same as any other track"
    )


def test_support_task_for_dsa_track_still_works_unchanged():
    # Non-regression: an existing TOPIC_KEYS track must behave exactly as before.
    learning_recommendation = {
        "track": "behavioral",
        "node_id": "behavioral.framework.star",
        "label": "STAR Method",
        "difficulty": "easy",
        "support_track": "dsa",
    }
    mission, _ = build_mission_for_user(
        user_id="u1",
        onboarding=_onboarding(),
        knowledge=[],
        revisions_due=[],
        knowledge_nodes={},
        learning_recommendation=learning_recommendation,
        ds="2026-01-01",
    )
    support_tasks = [t for t in mission.tasks if t.topic == "dsa"]
    assert support_tasks
    assert support_tasks[0].node_id


def test_every_track_produces_atomic_learning_nodes_not_just_dsa_and_lld():
    # Deeper root cause: RoadmapEngine.get_learning_nodes() used to filter on
    # type == "node" only. DSA/LLD nest an explicit "learning_nodes" container
    # under some topics (type "node"), but every other track's atomic study
    # unit IS the "topics" entry itself (a leaf, with its own prerequisites /
    # mastery_weight / estimated_minutes already on it). Before the fix, only
    # dsa/lld ever appeared here, so the planner, mission engine and any KB /
    # AI Mentor / Progress / Revision action driven by "learning nodes" simply
    # never saw java/hld/operating_systems/dbms/computer_networks/behavioral/
    # projects/resume content as first-class learning nodes.
    roadmap = get_roadmap()
    nodes_by_track = {}
    for node in roadmap.get_learning_nodes():
        nodes_by_track.setdefault(node.get("track"), 0)
        nodes_by_track[node.get("track")] += 1

    for track in ("dsa", "java", "lld", "hld", "operating_systems", "dbms",
                  "computer_networks", "behavioral"):
        assert nodes_by_track.get(track, 0) > 0, (
            f"{track} produced zero learning nodes — Open KB / AI Mentor / "
            f"Progress / Revision would have nothing to attach to"
        )


def test_leaf_topic_nodes_are_unlockable_and_lookup_by_id_works():
    # A representative leaf-topic-as-node from a non-dsa/lld track must behave
    # identically to a dsa "learning_nodes" entry: individually addressable,
    # carries prerequisites, and participates in unlock logic.
    roadmap = get_roadmap()
    for node_id, track in (
        # hld.foundations.cap is HLD's designated entry leaf and (as of the 2026
        # curriculum sync) now carries subject-level prerequisites on the other
        # 6 subjects, so hld.foundations.scalability is used here instead as the
        # representative "no prerequisites" HLD leaf. Likewise os.processes.basics
        # itself requires os.foundations.intro (OS's entry leaf, now gated behind
        # the same subject-level chain), so os.memory.paging is used instead.
        ("hld.foundations.scalability", "hld"),
        ("os.memory.paging", "operating_systems"),
        ("behavioral.framework.star", "behavioral"),
    ):
        node = roadmap.get_learning_node(node_id)
        assert node is not None, f"{node_id} should resolve as a learning node"
        assert node.get("track") == track
        assert roadmap.is_unlocked(node_id, completed_nodes=())  # no prerequisites -> unlocked
