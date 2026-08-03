"""Candidate Generation (RC1.3.6A · Phase 5).

Sits between the Eligibility Engine (Phase 4) and the Ranking Engine
(services/learning_engine/ranking.py, untouched — Phase 6 only changes what
it is called with) in the intended pipeline:

    ... -> Eligibility Engine -> Candidate Set -> Ranking Engine -> Planner

The eligibility-filtered pool is still too large to rank directly (order of
hundreds of nodes across every unlocked track). This narrows it to a compact
~15-30 node candidate set using ONLY cheap, already-available signals —
never a second scoring formula, since the real, precise scoring stays
entirely in `ranking.score_learning_node` (recency/skip/company/etc. are
already penalty/bonus terms there; duplicating them here would be exactly
the "duplicated logic" the task forbids). This module answers a coarser
question than ranking does: "which TRACKS deserve attention today, and how
many of their eligible nodes should even be considered" — not "which single
node is best".
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from services.learning_engine.stage_engine import SubjectLearningState

DEFAULT_MAX_CANDIDATES = 30
DEFAULT_PER_TRACK_CAP = 6


def _track_priority(
    track: str,
    subject_state: Optional[SubjectLearningState],
    *,
    roadmap,
    target_companies: Iterable[str],
    urgency: float,
    recent_track_ids: Iterable[str],
) -> float:
    """Coarse, explainable per-track priority — NOT a node-level score.

    Every term reuses an already-computed signal:
      - weakness / revision-due: Phase 3's SubjectLearningState.
      - company relevance: roadmap.company_importance (existing, unchanged).
      - continuity: whether the learner was recently active in this track.
      - urgency: generic pacing pressure (services/learning_engine/pacing.py).
    """
    priority = 0.0
    if subject_state is not None:
        priority += subject_state.current_weakness * 0.5  # 0-100 scale -> 0-50
        if subject_state.revision_state.get("has_due"):
            priority += 30.0

    company_scores = [roadmap.company_importance(track, c) for c in (target_companies or [])]
    if company_scores:
        priority += (max(company_scores) / 5.0) * 20.0  # company_importance is authored 0-5

    if track in set(recent_track_ids or ()):
        priority += 20.0  # continuity: finish what you started

    priority += urgency * 15.0  # generic pacing pressure nudges every track up a little

    return priority


def _node_sort_key(node: dict, progress_rows: Dict[str, dict]) -> tuple:
    """Deterministic within-track ordering: an already-started node (real
    continuity) before a cold one, then authored `order`, then id (stable)."""
    row = progress_rows.get(node.get("id")) or {}
    started = 0 if (row.get("status") or "not_started") != "not_started" else 1
    return (started, node.get("order", 0), node.get("id", ""))


def generate_candidate_nodes(
    eligible_nodes: List[dict],
    progress_rows: Dict[str, dict],
    subject_states: Dict[str, SubjectLearningState],
    *,
    roadmap,
    target_companies: Optional[Iterable[str]] = None,
    urgency: float = 0.0,
    recent_track_ids: Optional[Iterable[str]] = None,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
    per_track_cap: int = DEFAULT_PER_TRACK_CAP,
) -> List[dict]:
    """Narrow an eligible-node pool down to a compact ~15-30 node candidate set.

    Deterministic: same inputs always produce the same candidate set (ties
    broken by track priority, then the stable per-node sort key).
    """
    if len(eligible_nodes) <= max_candidates:
        # Already compact enough — nothing to trim, avoid discarding any
        # legitimately eligible node for no reason.
        return list(eligible_nodes)

    by_track: Dict[str, List[dict]] = {}
    for node in eligible_nodes:
        by_track.setdefault(node.get("track"), []).append(node)

    track_priorities = {
        track: _track_priority(
            track, subject_states.get(track),
            roadmap=roadmap, target_companies=target_companies or [],
            urgency=urgency, recent_track_ids=recent_track_ids or [],
        )
        for track in by_track
    }
    ordered_tracks = sorted(by_track.keys(), key=lambda t: track_priorities[t], reverse=True)

    candidates: List[dict] = []
    seen_ids = set()
    # Round-robin across tracks in priority order so the compact set stays
    # diversified instead of a single high-priority track eating the whole cap.
    track_cursors = {track: 0 for track in ordered_tracks}
    for track in ordered_tracks:
        by_track[track].sort(key=lambda n: _node_sort_key(n, progress_rows))

    while len(candidates) < max_candidates:
        added_this_round = False
        for track in ordered_tracks:
            if len(candidates) >= max_candidates:
                break
            cursor = track_cursors[track]
            nodes = by_track[track]
            taken_from_track = sum(1 for n in candidates if n.get("track") == track)
            if cursor >= len(nodes) or taken_from_track >= per_track_cap:
                continue
            node = nodes[cursor]
            track_cursors[track] += 1
            if node["id"] in seen_ids:
                continue
            seen_ids.add(node["id"])
            candidates.append(node)
            added_this_round = True
        if not added_this_round:
            break

    return candidates
