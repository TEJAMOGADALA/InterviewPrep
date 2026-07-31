"""Ranking model for additive learning recommendations."""
from __future__ import annotations

from typing import Iterable, List, Optional

from roadmap import get_roadmap
from services.learning_engine.roi import compute_learning_roi

_DIFFICULTY_PENALTY = {"easy": 0.0, "medium": 0.2, "hard": 0.4}

# Foundation RC1.2 item 1: a category can author several sibling learning
# nodes (e.g. dsa.search.binary_search.basic/rotated/on_answer/matrix) with
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


def score_learning_node(
    node: dict,
    progress: Optional[dict] = None,
    *,
    target_companies: Optional[Iterable[str]] = None,
    urgency: float = 0.0,
    progress_map: Optional[dict] = None,
    recent_node_ids: Optional[Iterable[str]] = None,
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
    weighting. Looked up at track granularity (the level at which the
    roadmap actually authors differentiated company data today) rather than
    per-node, so a multi-track candidate pool genuinely diverges by target
    company.

    `mastery_weight` (roadmap_v1.json, per node, default 1.0) scales the core
    knowledge-gap terms (confidence/weakness/mastery) so nodes the roadmap
    marks as counting more toward track mastery are prioritized higher.

    `roi` (Phase 4B, services/learning_engine/roi.py) is derived on demand
    from the roadmap's existing prerequisite graph — never stored, never
    duplicated — and contributes a light bonus for nodes that unlock more
    future curriculum, on the same weight scale as `company_score`.

    `progress_map` (Foundation RC1.2, optional) is the full user-progress map
    keyed by node_id — not just this node's own row — so `_SEQUENCE_GATE_PENALTY`
    can check sibling completion. Defaults to None (no-op: no penalty applied),
    so any existing caller that only ever passed a single node's `progress`
    keeps identical scores.

    `recent_node_ids` (Foundation RC1.2, optional) applies `_RECENCY_PENALTY`
    when this node was recommended in one of the learner's last few missions.
    Defaults to None (no-op).
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

    # roadmap_v1.json currently authors a uniform company_importance value on
    # every individual leaf node (no per-node variance), while its real,
    # differentiated company signal lives one level up on each track. Look up
    # by track so DSA-heavy companies (e.g. Google) and Java/DBMS-heavy
    # companies (e.g. Oracle) actually diverge across a multi-track candidate
    # pool. Falls back to the node id if it has no track.
    roadmap = get_roadmap()
    company_key = node.get("track") or node_id
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

    total_score = (
        knowledge_gap * mastery_weight
        + company_score * 3.0
        + roi_score * 0.05
        - difficulty_penalty * 10.0
        - min(estimated_minutes, 60) * 0.01
        + urgency_bonus
        - sequence_penalty
        - recency_penalty
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
    }


def rank_learning_nodes(
    candidates: Iterable[dict],
    progress_map: Optional[dict] = None,
    *,
    target_companies: Optional[Iterable[str]] = None,
    urgency: float = 0.0,
    recent_node_ids: Optional[Iterable[str]] = None,
) -> List[dict]:
    """Rank nodes by a simple, isolated scoring model (see `score_learning_node`).

    When two candidates land on the same overall score, the one more relevant
    to the learner's target companies is preferred (`company_score` tie-break).

    `recent_node_ids` (Foundation RC1.2, optional) is forwarded to
    `score_learning_node`'s recency penalty (item 6). Defaults to None (no-op).
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
        )
        scored.append((breakdown["total_score"], breakdown["company_score"], node))

    return [
        node
        for _, _, node in sorted(scored, key=lambda item: (item[0], item[1]), reverse=True)
    ]
