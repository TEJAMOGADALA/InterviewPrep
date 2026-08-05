"""Curriculum Synchronization Phase 2 (metadata-only) tests.

Verifies the subject prerequisite DAG, unlock-chain, recommended-next-
subjects, curriculum-level, production-application, source-anchor and
language-support metadata added by
`scripts/generate_roadmap.py::_annotate_curriculum_sync_metadata`. None of
this metadata is enforced at runtime (roadmap.py's unlock/ranking/ROI
engines only ever read `prerequisites`/`learning_stage`), so these tests
only check the metadata graph itself: prerequisite/unlock integrity, no
broken references, metadata completeness and deterministic generation.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.generate_roadmap import build, TRACKS, _SUBJECT_PREREQUISITES, _ISOLATED_SUBJECTS

# The canonical multi-parent DAG (Curriculum Sync Phase 2 enrichment),
# mirroring the user-specified target graph literally so drift in the
# generator's own `_SUBJECT_PREREQUISITES` is also caught.
EXPECTED_SUBJECT_DAG = {
    "programming_fundamentals": [],
    "java": ["programming_fundamentals"],
    "dsa": ["java"],
    "dbms": ["java"],
    "operating_systems": ["java"],
    "computer_networks": ["java"],
    "lld": ["java", "dsa", "operating_systems"],
    "hld": ["java", "dbms", "operating_systems", "computer_networks", "lld"],
}

EXPECTED_SUBJECT_UNLOCKS = {
    "programming_fundamentals": ["java"],
    "java": ["dsa", "dbms", "operating_systems", "computer_networks", "lld", "hld"],
    "dsa": ["lld"],
    "dbms": ["hld"],
    "operating_systems": ["lld", "hld"],
    "computer_networks": ["hld"],
    "lld": ["hld"],
    "hld": [],
}


@pytest.fixture(scope="module")
def payload():
    return build()


def _by_id(tracks):
    return {t["id"]: t for t in tracks}


def test_programming_fundamentals_is_the_root_subject(payload):
    tracks = _by_id(payload["tracks"])
    pf = tracks["programming_fundamentals"]
    assert pf["subject_prerequisites"] == []


def test_generator_source_of_truth_matches_expected_dag():
    assert _SUBJECT_PREREQUISITES == EXPECTED_SUBJECT_DAG


def test_canonical_subject_dependency_dag(payload):
    tracks = _by_id(payload["tracks"])
    for subject, expected in EXPECTED_SUBJECT_DAG.items():
        assert sorted(tracks[subject]["subject_prerequisites"]) == sorted(expected), subject


def test_unlock_chain_is_exact_reverse_of_prerequisite_dag(payload):
    tracks = _by_id(payload["tracks"])
    for subject, expected in EXPECTED_SUBJECT_UNLOCKS.items():
        assert sorted(tracks[subject]["subject_unlocks"]) == sorted(expected), subject


def test_recommended_next_subjects_matches_unlocks(payload):
    """Advisory-only navigation metadata (item 2) — mirrors subject_unlocks
    today, matching the user's literal recommended_next_subjects example."""
    for t in payload["tracks"]:
        assert sorted(t["recommended_next_subjects"]) == sorted(t["subject_unlocks"])


def test_no_broken_subject_references(payload):
    track_ids = set(_by_id(payload["tracks"]).keys())
    for t in payload["tracks"]:
        for pid in t["subject_prerequisites"]:
            assert pid in track_ids
        for uid in t["subject_unlocks"]:
            assert uid in track_ids


def test_no_cycles_in_subject_prerequisite_graph(payload):
    tracks = _by_id(payload["tracks"])
    color = {tid: 0 for tid in tracks}

    def dfs(u):
        color[u] = 1
        for v in tracks[u]["subject_prerequisites"]:
            assert color[v] != 1, f"cycle at {u} -> {v}"
            if color[v] == 0:
                dfs(v)
        color[u] = 2

    for tid in tracks:
        if color[tid] == 0:
            dfs(tid)


def test_every_module_has_complete_curriculum_sync_metadata(payload):
    module_ids = {m["id"] for t in payload["tracks"] for m in (t.get("modules") or [])}
    for t in payload["tracks"]:
        for module in t.get("modules") or []:
            assert isinstance(module["module_prerequisites"], list)
            assert isinstance(module["curriculum_level"], str) and module["curriculum_level"]
            assert isinstance(module["production_application"], list)
            assert "source_anchor" in module
            for mid in module["module_prerequisites"]:
                assert mid in module_ids


def test_every_topic_has_complete_curriculum_sync_metadata(payload):
    topic_ids = {
        top["id"] for t in payload["tracks"] for m in (t.get("modules") or [])
        for top in (m.get("topics") or [])
    }
    for t in payload["tracks"]:
        for module in t.get("modules") or []:
            for topic in module.get("topics") or []:
                assert isinstance(topic["topic_prerequisites"], list)
                assert isinstance(topic["curriculum_level"], str) and topic["curriculum_level"]
                assert "source_anchor" in topic
                for tid in topic["topic_prerequisites"]:
                    assert tid in topic_ids


def test_first_module_of_a_subject_links_to_every_prerequisite_subjects_last_module(payload):
    """A DAG node may have several parents (e.g. LLD/HLD) — the first
    module of a subject must link to the LAST module of EVERY prerequisite
    subject, not just a single predecessor."""
    tracks = _by_id(payload["tracks"])
    for subject, prereq_subjects in EXPECTED_SUBJECT_DAG.items():
        if not prereq_subjects:
            continue
        first_module = tracks[subject]["modules"][0]
        expected_prereqs = [tracks[p]["modules"][-1]["id"] for p in prereq_subjects]
        assert sorted(first_module["module_prerequisites"]) == sorted(expected_prereqs), subject


def test_isolated_subjects_have_no_academic_prerequisite_edges(payload):
    """Projects/Behavioral/Resume are independent career-readiness tracks
    (item 3) — no prerequisite relationships in or out of the academic
    curriculum graph."""
    tracks = _by_id(payload["tracks"])
    assert _ISOLATED_SUBJECTS == frozenset({"projects", "behavioral", "resume"})
    for tid in _ISOLATED_SUBJECTS:
        t = tracks[tid]
        assert t["subject_prerequisites"] == []
        assert t["subject_unlocks"] == []
        assert t["recommended_next_subjects"] == []


def test_academic_subjects_never_reference_isolated_subjects(payload):
    for t in payload["tracks"]:
        if t["id"] in _ISOLATED_SUBJECTS:
            continue
        for pid in t["subject_prerequisites"]:
            assert pid not in _ISOLATED_SUBJECTS
        for uid in t["subject_unlocks"]:
            assert uid not in _ISOLATED_SUBJECTS
        for rid in t["recommended_next_subjects"]:
            assert rid not in _ISOLATED_SUBJECTS


def test_language_support_metadata_is_future_ready(payload):
    """Item 4: only Java is supported today, but the shape (a list of
    supported languages + a family map) allows adding more later without
    changing the roadmap structure."""
    lang = payload["language_support"]
    assert lang["primary_language_supported"] == "java"
    assert lang["supported_languages"] == ["java"]
    assert lang["language_family"]["java"]
    assert lang["primary_language_supported"] in lang["supported_languages"]
    for supported_lang in lang["language_family"]:
        assert supported_lang in lang["supported_languages"]


def test_existing_prerequisites_field_is_untouched_by_phase2_metadata(payload):
    """Phase 2 is metadata-only \u2014 the pre-existing, runtime-enforced
    `prerequisites`/`learning_stage` fields must be unaffected."""
    all_nodes = []

    def visit(n):
        all_nodes.append(n)
        for key in ("modules", "topics", "subtopics", "learning_nodes"):
            for c in n.get(key) or []:
                visit(c)

    for t in payload["tracks"]:
        visit(t)

    for n in all_nodes:
        assert "prerequisites" in n
        assert isinstance(n["prerequisites"], list)


def test_roadmap_generation_is_deterministic_across_processes():
    """The real determinism contract: two independent, fresh subprocess
    runs of the generator produce byte-identical JSON output. Computes
    `build()` in-memory and prints it rather than calling `main()`, so this
    never writes to the shared `data/roadmap_v1.json` (tests run under
    pytest-xdist and must not race on that file)."""
    backend_dir = Path(__file__).resolve().parent.parent
    code = (
        "import sys, json; sys.path.insert(0, r'" + str(backend_dir) + "'); "
        "from scripts.generate_roadmap import build; "
        "print(json.dumps(build(), sort_keys=True))"
    )

    def run_and_read():
        result = subprocess.run(
            [sys.executable, "-c", code], check=True, capture_output=True, text=True,
        )
        return result.stdout

    first = run_and_read()
    second = run_and_read()
    assert first == second


def test_total_node_count_unchanged_by_regeneration(payload):
    """Preserve all existing roadmap IDs and learner compatibility: no
    nodes added or removed by the Phase 2 metadata annotation pass."""
    assert payload["stats"]["total_nodes"] == 1223
    assert payload["stats"]["tracks"] == 11
