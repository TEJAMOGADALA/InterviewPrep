"""Companion Recommendations — support and core reading tasks.

Purpose (Phase 4 Step 1):
    A mission is not one task. Yesterday's `planner.py` embedded two
    additional recommendation flows directly inside the orchestrator:

      * A four-tier support-node fallback (prerequisite chain -> same
        concept family -> roadmap.related() -> weakest cross-track).
      * A three-tier core-reading fallback (next-unlockable core track
        node -> any unlocked core node -> any core node).

    Both are legitimate metadata-driven strategies but they made the
    planner hard to extend: adding a new companion category (e.g. a
    "portfolio piece" task) meant editing planner.py.

    This module extracts each fallback tier as an EXPLICIT strategy
    function and iterates them in priority order. Adding a new tier
    (or a new companion category) is now an additive change — the
    orchestrator itself never needs to grow another conditional.

Design contract:
    * METADATA-DRIVEN. Every strategy reads roadmap graph fields
      (prerequisites, category, related edges, track ids) or the
      LearnerContext's live progress signals. No strategy hardcodes a
      learner profile.
    * DETERMINISTIC. The strategy list is ordered and each strategy
      returns the first qualifying candidate. No RNG, no wall-clock.
    * COMPATIBLE. The output shape (`support_track`, `support_node`,
      `core_node` keys on the recommendation dict) is byte-identical
      to the pre-refactor planner so builder.py and mission_engine.py
      keep working unchanged.
"""
from __future__ import annotations

from typing import Callable, List, Optional

from roadmap import get_roadmap
from services.learning_engine.context import LearnerContext
from services.learning_engine.roi import direct_dependents
from services.learning_engine.unlock import (
    get_unlocked_nodes, next_unlockable_nodes,
)

# ---------------------------------------------------------------------------
# Core-reading tracks
# ---------------------------------------------------------------------------
# Configured here rather than derived from the roadmap because the
# roadmap JSON does not currently declare a "reading category" attribute
# per track (and the Phase 4 brief forbids editing curriculum
# markdown). Kept as a module-level constant so adding a new core-
# reading track is a one-line change — not a planner-wide refactor.
#
# NOTE: this is NOT a learner-specific rule. It's a curriculum-scoped
# configuration that answers "which tracks provide daily systems
# reading?" — the same for every learner.
CORE_READING_TRACKS: List[str] = ["operating_systems", "dbms", "computer_networks"]


# ---------------------------------------------------------------------------
# Support recommendation strategies
# ---------------------------------------------------------------------------

# Strategy signature: (primary_node, context) -> Optional[node_dict]
# Each strategy returns the first qualifying support candidate or None.
SupportStrategy = Callable[[dict, LearnerContext], Optional[dict]]


def _qualifies(node_id: Optional[str], context: LearnerContext) -> Optional[dict]:
    """Shared eligibility check: the candidate is a real, unlocked,
    not-yet-completed roadmap learning node."""
    if not node_id:
        return None
    completed = context.completed_node_ids()
    if node_id in completed:
        return None
    roadmap = get_roadmap()
    candidate = roadmap.get_learning_node(node_id)
    if candidate is None:
        return None
    if not roadmap.is_unlocked(node_id, completed):
        return None
    return candidate


def _strategy_prerequisite_chain(primary: dict, context: LearnerContext) -> Optional[dict]:
    """Tier 1: the immediate next step(s) that directly depend on today's
    primary node (reuses roi.direct_dependents — the existing reverse-
    prerequisite index — so no second graph is maintained)."""
    for dependent_id in direct_dependents(primary.get("id") or ""):
        candidate = _qualifies(dependent_id, context)
        if candidate:
            return candidate
    return None


def _strategy_same_concept_family(primary: dict, context: LearnerContext) -> Optional[dict]:
    """Tier 2: another learning node authored under the same roadmap
    `category` (e.g. another binary-search variant). Category is a
    roadmap-authored field — no external taxonomy."""
    category = primary.get("category")
    if not category:
        return None
    roadmap = get_roadmap()
    primary_id = primary.get("id")
    for sibling in roadmap.get_learning_nodes():
        if sibling.get("category") != category or sibling.get("id") == primary_id:
            continue
        candidate = _qualifies(sibling.get("id"), context)
        if candidate:
            return candidate
    return None


def _strategy_related_edge(primary: dict, context: LearnerContext) -> Optional[dict]:
    """Tier 3: the roadmap's explicit `related` cross-reference graph.
    Roadmap authors curate this list; it is our final "topically
    connected" fallback before we jump tracks."""
    roadmap = get_roadmap()
    for related in roadmap.related(primary.get("id") or ""):
        candidate = _qualifies(related.get("id"), context)
        if candidate:
            return candidate
    return None


def _strategy_cross_track_weakness(primary: dict, context: LearnerContext) -> Optional[dict]:
    """Tier 4: the learner's weakest non-primary track (only when
    nothing topically connected exists — variety, not compensation)."""
    primary_track = primary.get("track")
    completed = context.completed_node_ids()

    # Rank OTHER tracks by (weakness - confidence*10) so the one where
    # the learner is genuinely lagging surfaces first. Metadata-driven:
    # the signal comes from `knowledge_nodes` progress rows, never a
    # hardcoded track priority list.
    track_scores: dict = {}
    for row in context.progress_rows:
        track = row.get("track")
        if not track or track == primary_track:
            continue
        status = (row.get("status") or "not_started").lower()
        if status in {"completed", "mastered", "revision_due"}:
            continue
        try:
            weakness = float(row.get("weakness_score", 0) or 0)
            confidence = float(row.get("confidence", 0) or 0)
        except (TypeError, ValueError):
            continue
        score = weakness - confidence * 10.0
        if track not in track_scores or score > track_scores[track]:
            track_scores[track] = score

    # Try tracks in descending weakness order.
    for track, _score in sorted(track_scores.items(), key=lambda kv: -kv[1]):
        candidate = _pick_from_track(track, context)
        if candidate:
            return candidate
    return None


def _pick_from_track(track: str, context: LearnerContext) -> Optional[dict]:
    """Return the best unlocked, incomplete learning node in `track`.

    Preference order (metadata-driven):
      1. Unlocked, incomplete node the graph considers ready today.
      2. Any node the learner already has a knowledge_nodes row for
         that isn't finished (they at least started it).
      3. Any node on the track (last-resort catalog scan).
    """
    completed = context.completed_node_ids()
    for node in get_unlocked_nodes(context.progress_rows):
        if node.get("track") == track and node.get("id") not in completed:
            return node
    for row in context.progress_rows:
        if (
            row.get("track") == track
            and row.get("node_id")
            and row.get("node_id") not in completed
        ):
            roadmap_node = get_roadmap().get_learning_node(row["node_id"])
            if roadmap_node is not None:
                return roadmap_node
    for node in get_roadmap().get_learning_nodes():
        if node.get("track") == track and node.get("id") not in completed:
            return node
    return None


# Priority-ordered strategy list. Add new tiers by appending to this
# list — no other file needs to change.
_SUPPORT_STRATEGIES: List[SupportStrategy] = [
    _strategy_prerequisite_chain,
    _strategy_same_concept_family,
    _strategy_related_edge,
    _strategy_cross_track_weakness,
]


def support_recommendation(
    primary: Optional[dict],
    context: LearnerContext,
) -> Optional[dict]:
    """Return the support recommendation for today's primary node.

    Iterates ``_SUPPORT_STRATEGIES`` in order; the first tier that
    yields a qualifying candidate wins. Returns a dict in the same
    shape the pre-refactor planner emitted so ``builder.py`` and
    ``mission_engine.py`` need no changes:

        {"support_track": <track_id>, "support_node": <node_id>}
    """
    if not primary:
        return None

    primary_track = primary.get("track")
    for strategy in _SUPPORT_STRATEGIES:
        candidate = strategy(primary, context)
        if candidate:
            return {
                "support_track": candidate.get("track", primary_track),
                "support_node": candidate.get("id"),
            }
    return None


# ---------------------------------------------------------------------------
# Core-reading recommendation
# ---------------------------------------------------------------------------

def _core_reading_candidates(context: LearnerContext) -> List[dict]:
    """Fallback ladder for a core-reading node.

    Same three-tier order the pre-refactor planner used, but expressed
    declaratively so a new tier is a one-line append.
    """
    completed = context.completed_node_ids()
    ladders: List[List[dict]] = [
        # Tier 1: the roadmap says these are the next unlockable steps.
        [
            node for node in next_unlockable_nodes(context.progress_rows)
            if node.get("track") in CORE_READING_TRACKS
            and node.get("id") not in completed
        ],
        # Tier 2: any core-track node that is currently unlocked.
        [
            node for node in get_unlocked_nodes(context.progress_rows)
            if node.get("track") in CORE_READING_TRACKS
            and node.get("id") not in completed
        ],
        # Tier 3: any core-track node in the catalog (last-resort).
        [
            node for node in get_roadmap().get_learning_nodes()
            if node.get("track") in CORE_READING_TRACKS
            and node.get("id") not in completed
        ],
    ]
    for ladder in ladders:
        if ladder:
            return ladder
    return []


def core_recommendation(context: LearnerContext) -> Optional[dict]:
    """Return the core-reading recommendation, or None if no core node
    is currently available for this learner."""
    candidates = _core_reading_candidates(context)
    if not candidates:
        return None
    return {"core_node": candidates[0].get("id")}
