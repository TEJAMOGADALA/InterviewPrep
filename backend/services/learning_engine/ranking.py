"""Ranking model for additive learning recommendations."""
from __future__ import annotations

from typing import Iterable, List, Optional

from roadmap import get_roadmap
from services.learning_engine.roi import compute_learning_roi

_DIFFICULTY_PENALTY = {"easy": 0.0, "medium": 0.2, "hard": 0.4}

# Foundation RC1.2 item 1: a category can author several sibling learning
# nodes (e.g. dsa.foundations.arrays.traversal|prefix_sum|two_pointer) with
# an authored `order` but no explicit `prerequisites` edge between them yet.
# Rather than hand-authoring every such edge (or inventing a second graph),
# this gate reuses the roadmap's own existing `category`/`order` fields: a
# later-order sibling is heavily deprioritized in ranking while an earlier,
# unlocked, incomplete sibling in the same category still needs finishing.
# It never changes `roadmap.is_unlocked`/`get_unlocked_nodes` (no regression
# to Knowledge Base unlock state) — this is a ranking-time preference only.
_SEQUENCE_GATE_PENALTY = 1000.0

# Foundation RC1.2 item 6: a light nudge away from a node recommended in one
# of the learner's last few missions, so the planner doesn't repeat the same
# pick day after day. Small relative to knowledge_gap so it only breaks ties
# / near-ties — it never overrides a genuinely weak, unlocked, high-priority
# node, and it never violates prerequisites (candidates are already filtered
# to unlocked nodes before this runs).
_RECENCY_PENALTY = 12.0

# RC1.3.3 · Skipped-mission deferral penalty. Stronger than recency but
# weaker than the sequence gate. A node the learner actively skipped in
# a recent mission is deferred — never permanently blocked (so it will
# resurface once the pool rotates), but not immediately re-picked
# either. Kept intentionally decoupled from `_RECENCY_PENALTY` because
# "skipped" carries a different intent than "recently offered": the
# learner said no, so give them room to breathe.
_SKIP_DEFERRAL_PENALTY = 28.0

# RC1.3.3 · Same-track fatigue penalty. When the learner has already
# done 2+ consecutive missions on the same track AND their experience
# band is ≥ mid, a light penalty encourages variety. Never applied for
# students / juniors, where consecutive same-track sessions are
# pedagogically valuable (building foundations). Small enough to only
# break near-ties, never override strong-signal choices.
_TRACK_FATIGUE_PENALTY = 8.0

# RC1.3.3 · Foundation-first bonus. When the learner's onboarding self-
# assessment on a track is very low (< 3.5 / 10), boost candidates that
# have no prerequisites (roadmap-leaf entry points) so first missions
# genuinely start from the foundation. Same signal every existing
# consumer already reads (onboarding.self_assessment) — no new store.
# Additive so it can never OVERRIDE existing signals; it only breaks
# ties in favour of foundational nodes for beginners.
_FOUNDATION_BONUS = 22.0

# Experience bands that grant same-track fatigue penalty. Beginner bands
# ("student", "0-1") are excluded so they can safely stay in the same
# track for consecutive days while learning foundations.
_FATIGUE_ELIGIBLE_POSITIONS = {"1-3", "3-5", "5+"}

_COMPLETED_STATUSES = {"completed", "mastered", "revision_due"}


def _has_incomplete_earlier_sibling(node: dict, progress_map: dict) -> bool:
    """Return True if an earlier-`order` sibling in the same `category` is
    not yet completed — i.e. `node` is a later step in an authored sequence
    that hasn't been earned yet (see `_SEQUENCE_GATE_PENALTY`)."""
    category = node.get("category")
    order = node.get("order")
    if category is None or order is None:
        return False
    roadmap = get_roadmap()
    for sibling in roadmap.get_learning_nodes():
        if sibling.get("category") != category or sibling.get("id") == node.get("id"):
            continue
        sibling_order = sibling.get("order")
        if sibling_order is None or sibling_order >= order:
            continue
        row = progress_map.get(sibling.get("id")) or {}
        status = (row.get("status") or "").lower()
        if status not in _COMPLETED_STATUSES:
            return True
    return False


def _onboarding_score_for_track(onboarding_scores: Optional[dict], track: Optional[str]) -> Optional[float]:
    """Return the learner's self-assessment score (0-10) for a track, or
    None when we have no signal for it. Deliberately conservative —
    a missing entry is treated as "unknown", not as "very low", so we
    don't over-eagerly bias a random beginner toward foundations they
    haven't declared weakness on."""
    if not onboarding_scores or not track:
        return None
    val = onboarding_scores.get(track)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _is_foundation_node(node: dict) -> bool:
    """Return whether a node is a "foundational" entry point for its track.

    Heuristic uses only roadmap-authored fields — no new data. A node
    qualifies when it declares NO prerequisites (i.e. it can be
    entered directly), OR when its category order is 1 (first in
    an authored sequence).
    """
    prereqs = node.get("prerequisites") or []
    if not prereqs:
        return True
    if node.get("order") == 1:
        return True
    return False


def score_learning_node(
    node: dict,
    progress: Optional[dict] = None,
    *,
    target_companies: Optional[Iterable[str]] = None,
    urgency: float = 0.0,
    progress_map: Optional[dict] = None,
    recent_node_ids: Optional[Iterable[str]] = None,
    skipped_node_ids: Optional[Iterable[str]] = None,
    recent_track_ids: Optional[Iterable[str]] = None,
    position: Optional[str] = None,
    onboarding_scores: Optional[dict] = None,
) -> dict:
    """Score one candidate node and return every factor that produced the score.

    This is the single scoring implementation `rank_learning_nodes` uses to sort
    candidates. `services/learning_engine/insight.py` calls it again for just the
    winning node so the "why was this picked" explanation can never drift from
    what actually ranked it — there is no second, duplicated scoring formula.

    `urgency` (0.0-1.0, default 0.0) is an optional interview-deadline pacing
    signal from services/learning_engine/pacing.py. At the default of 0.0 it
    contributes nothing, so callers that don't pass it get byte-identical
    scores to before. When >0, it rewards higher interview_importance /
    interview_frequency nodes and lightly penalizes long estimated_minutes,
    so accelerated/critical pacing naturally skips slow, low-yield detours.

    `target_companies` (Phase 4A) activates `company_score`, sourced via
    `roadmap.company_importance()` — the single source of truth for company
    weighting.

    `mastery_weight` (roadmap_v1.json, per node, default 1.0) scales the core
    knowledge-gap terms (confidence/weakness/mastery) so nodes the roadmap
    marks as counting more toward track mastery are prioritized higher.

    `roi` (Phase 4B, services/learning_engine/roi.py) is derived on demand
    from the roadmap's existing prerequisite graph — never stored, never
    duplicated — and contributes a light bonus for nodes that unlock more
    future curriculum, on the same weight scale as `company_score`.

    `progress_map` (Foundation RC1.2, optional) is the full user-progress map
    keyed by node_id — not just this node's own row — so `_SEQUENCE_GATE_PENALTY`
    can check sibling completion. Defaults to None (no-op: no penalty applied).

    `recent_node_ids` (Foundation RC1.2, optional) applies `_RECENCY_PENALTY`
    when this node was recommended in one of the learner's last few missions.

    RC1.3.3 additions (all optional; every existing caller keeps identical
    output when not passing them):

    * ``skipped_node_ids`` — nodes the learner recently skipped receive a
      moderate deferral penalty so we don't immediately re-offer them.
    * ``recent_track_ids`` — the tracks that appeared in the learner's
      last N missions (in order, newest last). When the learner's
      ``position`` indicates mid+ experience AND the same track appears
      2+ times consecutively at the end of that list, apply
      ``_TRACK_FATIGUE_PENALTY`` to candidates on that track. Beginner
      bands never receive this penalty (they benefit from continuity).
    * ``position`` — the learner's onboarding experience band, used by
      the fatigue rule above.
    * ``onboarding_scores`` — the learner's self-assessment dict
      (track_id → 0-10). Nodes on a track where the learner declared
      very low knowledge (<3.5) AND which are foundational entry points
      (no prerequisites, or order == 1) get ``_FOUNDATION_BONUS``. This
      is the mechanism that steers beginners to genuinely foundational
      concepts on day one instead of intermediate unlocks.
    """
    progress = progress or {}
    companies = [company.lower() for company in (target_companies or [])]

    confidence = float(progress.get("confidence", 0.0) or 0.0)
    weakness = float(progress.get("weakness_score", 100.0) or 100.0)
    mastery = float(
        progress.get("mastery_percentage", progress.get("mastery", 0.0)) or 0.0
    )
    difficulty = (node.get("difficulty") or "medium").lower()
    estimated_minutes = int(node.get("estimated_minutes") or 0)
    mastery_weight = float(node.get("mastery_weight") or 1.0)
    node_id = node.get("id")
    track = node.get("track")

    # roadmap_v1.json currently authors a uniform company_importance value on
    # every individual leaf node (no per-node variance), while its real,
    # differentiated company signal lives one level up on each track. Look up
    # by track so DSA-heavy companies (e.g. Google) and Java/DBMS-heavy
    # companies (e.g. Oracle) actually diverge across a multi-track candidate
    # pool. Falls back to the node id if it has no track.
    roadmap = get_roadmap()
    company_key = track or node_id
    company_score = sum(roadmap.company_importance(company_key, company) for company in companies)

    difficulty_penalty = _DIFFICULTY_PENALTY.get(difficulty, 0.2)
    interview_importance = float(node.get("interview_importance") or 0.0)
    interview_frequency = float(node.get("interview_frequency") or 0.0)
    urgency_bonus = urgency * (
        interview_importance * 3.0
        + interview_frequency * 3.0
        - min(estimated_minutes, 90) * 0.03
    )
    knowledge_gap = (
        (100.0 - confidence * 10.0) * 0.45
        + weakness * 0.35
        + (100.0 - mastery) * 0.15
    )

    roi = compute_learning_roi(node_id)
    roi_score = roi["roi_score"]

    sequence_penalty = (
        _SEQUENCE_GATE_PENALTY
        if progress_map is not None and _has_incomplete_earlier_sibling(node, progress_map)
        else 0.0
    )
    recency_penalty = (
        _RECENCY_PENALTY if node_id and node_id in (recent_node_ids or ()) else 0.0
    )

    # ---- RC1.3.3 · skipped-node deferral --------------------------------
    skip_penalty = (
        _SKIP_DEFERRAL_PENALTY
        if node_id and node_id in (skipped_node_ids or ())
        else 0.0
    )

    # ---- RC1.3.3 · same-track fatigue -----------------------------------
    # Applies only when the learner is mid+ experience AND the last two
    # missions were on this same track. Beginners are excluded.
    fatigue_penalty = 0.0
    recent_tracks_list = list(recent_track_ids or ())
    if (
        track
        and position in _FATIGUE_ELIGIBLE_POSITIONS
        and len(recent_tracks_list) >= 2
        and recent_tracks_list[-1] == track
        and recent_tracks_list[-2] == track
    ):
        fatigue_penalty = _TRACK_FATIGUE_PENALTY

    # ---- RC1.3.3 · foundation-first bias --------------------------------
    # Kick in only when the learner has a *declared* low self-assessment
    # on this track AND the candidate is a foundational entry point.
    onboarding_track_score = _onboarding_score_for_track(onboarding_scores, track)
    foundation_bonus = 0.0
    if onboarding_track_score is not None and onboarding_track_score < 3.5 and _is_foundation_node(node):
        foundation_bonus = _FOUNDATION_BONUS

    total_score = (
        knowledge_gap * mastery_weight
        + company_score * 3.0
        + roi_score * 0.05
        - difficulty_penalty * 10.0
        - min(estimated_minutes, 60) * 0.01
        + urgency_bonus
        - sequence_penalty
        - recency_penalty
        - skip_penalty
        - fatigue_penalty
        + foundation_bonus
    )

    return {
        "node_id": node_id,
        "total_score": total_score,
        "knowledge_gap": knowledge_gap,
        "confidence": confidence,
        "weakness": weakness,
        "mastery": mastery,
        "mastery_weight": mastery_weight,
        "company_score": company_score,
        "difficulty": difficulty,
        "difficulty_penalty": difficulty_penalty,
        "estimated_minutes": estimated_minutes,
        "interview_importance": interview_importance,
        "interview_frequency": interview_frequency,
        "urgency": urgency,
        "urgency_bonus": urgency_bonus,
        "roi": roi,
        "sequence_penalty": sequence_penalty,
        "recency_penalty": recency_penalty,
        # RC1.3.3 · additive audit fields — surfaced in the "why this?"
        # dialog through the same insight pipeline so learners can see
        # exactly which nudge fired.
        "skip_penalty": skip_penalty,
        "fatigue_penalty": fatigue_penalty,
        "foundation_bonus": foundation_bonus,
    }


def rank_learning_nodes(
    candidates: Iterable[dict],
    progress_map: Optional[dict] = None,
    *,
    target_companies: Optional[Iterable[str]] = None,
    urgency: float = 0.0,
    recent_node_ids: Optional[Iterable[str]] = None,
    skipped_node_ids: Optional[Iterable[str]] = None,
    recent_track_ids: Optional[Iterable[str]] = None,
    position: Optional[str] = None,
    onboarding_scores: Optional[dict] = None,
) -> List[dict]:
    """Rank nodes by a simple, isolated scoring model (see `score_learning_node`).

    When two candidates land on the same overall score, the one more relevant
    to the learner's target companies is preferred (`company_score` tie-break).

    All RC1.3.3 additions are forwarded to `score_learning_node`. Each is
    optional (default None) — callers that don't pass them get byte-
    identical ranking to before.
    """
    progress_map = progress_map or {}

    scored = []
    for node in candidates:
        breakdown = score_learning_node(
            node,
            progress_map.get(node.get("id"), {}),
            target_companies=target_companies,
            urgency=urgency,
            progress_map=progress_map,
            recent_node_ids=recent_node_ids,
            skipped_node_ids=skipped_node_ids,
            recent_track_ids=recent_track_ids,
            position=position,
            onboarding_scores=onboarding_scores,
        )
        scored.append((breakdown["total_score"], breakdown["company_score"], node))

    return [
        node
        for _, _, node in sorted(scored, key=lambda item: (item[0], item[1]), reverse=True)
    ]
