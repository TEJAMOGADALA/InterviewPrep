"""Orchestrator for the additive learning engine."""
from __future__ import annotations

from typing import Iterable, Optional

from roadmap import get_roadmap
from services.learning_engine.builder import build_learning_recommendation
from services.learning_engine.insight import build_recommendation_insight
from services.learning_engine.pacing import forecast_completion
from services.learning_engine.ranking import rank_learning_nodes, score_learning_node
from services.learning_engine.revision import get_highest_priority_revision
from services.learning_engine.roi import direct_dependents
from services.learning_engine.unlock import get_unlocked_nodes, next_unlockable_nodes
from services.progress_engine import load_user_progress_rows

CORE_TRACKS = ["operating_systems", "dbms", "computer_networks"]
COMPLETED_STATUSES = {"completed", "mastered", "revision_due"}


def _completed_node_ids(progress_rows: Iterable[dict]) -> set[str]:
    completed = set()
    for row in progress_rows or []:
        if not isinstance(row, dict):
            continue
        status = (row.get("status") or "").lower()
        node_id = row.get("node_id")
        if node_id and status in COMPLETED_STATUSES:
            completed.add(node_id)
    return completed


def _choose_support_node(support_track: str, progress_rows: list) -> Optional[dict]:
    completed_ids = _completed_node_ids(progress_rows)
    unlocked = [
        node for node in get_unlocked_nodes(progress_rows)
        if node.get("track") == support_track and node.get("id") not in completed_ids
    ]
    if unlocked:
        return unlocked[0]

    for row in progress_rows:
        if row.get("track") == support_track and row.get("node_id") and row.get("node_id") not in completed_ids:
            roadmap_node = get_roadmap().get_learning_node(row["node_id"])
            if roadmap_node is not None:
                return roadmap_node

    for node in get_roadmap().get_learning_nodes():
        if node.get("track") == support_track and node.get("id") not in completed_ids:
            return node

    return None


def _qualifying_candidate(node_id: Optional[str], completed_ids: set) -> Optional[dict]:
    """Return the roadmap learning node for `node_id` if it's a real, unlocked,
    not-yet-completed candidate — the shared eligibility check every support
    tier below uses, so "reinforcement" never means a locked or finished node."""
    if not node_id or node_id in completed_ids:
        return None
    roadmap = get_roadmap()
    candidate = roadmap.get_learning_node(node_id)
    if candidate is None:
        return None
    if not roadmap.is_unlocked(node_id, completed_ids):
        return None
    return candidate


def _build_support_recommendation(
    node: Optional[dict],
    progress_rows: list,
) -> Optional[dict]:
    """
    Build an adaptive secondary recommendation.

    Priority (Foundation RC1.2 item 2), each tier only falling through to the
    next when it finds no qualifying (unlocked, incomplete) candidate:
      1. Same prerequisite chain — the immediate next step(s) that directly
         depend on today's primary node (reuses roi.py's existing
         reverse-prerequisite index; no second graph).
      2. Same concept family — another learning node authored under the same
         roadmap `category` (e.g. another binary-search variant).
      3. `roadmap.related()` — the explicit cross-reference graph.
      4. Cross-track — the learner's weakest non-primary track, only when
         nothing topically connected exists.
    """

    if not node:
        return None

    primary_id = node.get("id")
    primary_track = node.get("track")
    primary_category = node.get("category")
    roadmap = get_roadmap()
    completed_ids = _completed_node_ids(progress_rows)

    for dependent_id in direct_dependents(primary_id):
        candidate = _qualifying_candidate(dependent_id, completed_ids)
        if candidate:
            return {"support_track": candidate.get("track", primary_track), "support_node": candidate.get("id")}

    if primary_category:
        for sibling in roadmap.get_learning_nodes():
            if sibling.get("category") != primary_category or sibling.get("id") == primary_id:
                continue
            candidate = _qualifying_candidate(sibling.get("id"), completed_ids)
            if candidate:
                return {"support_track": candidate.get("track", primary_track), "support_node": candidate.get("id")}

    for related in roadmap.related(primary_id):
        candidate = _qualifying_candidate(related.get("id"), completed_ids)
        if candidate:
            return {"support_track": candidate.get("track", primary_track), "support_node": candidate.get("id")}

    candidates = {}

    for row in progress_rows:
        track = row.get("track")
        if not track or track == primary_track:
            continue

        status = row.get("status", "not_started")
        if status in COMPLETED_STATUSES:
            continue

        confidence = float(row.get("confidence", 0))
        weakness = float(row.get("weakness_score", 0))
        score = weakness - (confidence * 10)

        if (
            track not in candidates
            or score > candidates[track]["score"]
        ):
            candidates[track] = {"score": score}

    if not candidates:
        return None

    candidate_tracks = [track for track in candidates if _choose_support_node(track, progress_rows) is not None]
    if not candidate_tracks:
        return None

    support_track = max(
        ((track, candidates[track]) for track in candidate_tracks),
        key=lambda x: x[1]["score"],
    )[0]
    support_node = _choose_support_node(support_track, progress_rows)
    recommendation = {"support_track": support_track}
    if support_node is not None:
        recommendation["support_node"] = support_node.get("id")
    return recommendation


def _build_core_recommendation(progress_rows: list) -> Optional[dict]:
    """
    Build a roadmap-backed core reading recommendation from OS/DBMS/Networks.
    """
    completed_ids = _completed_node_ids(progress_rows)
    candidates = [
        node for node in next_unlockable_nodes(progress_rows)
        if node.get("track") in CORE_TRACKS
        and node.get("id") not in completed_ids
    ]
    if not candidates:
        candidates = [
            node for node in get_unlocked_nodes(progress_rows)
            if node.get("track") in CORE_TRACKS
            and node.get("id") not in completed_ids
        ]
    if not candidates:
        candidates = [
            node for node in get_roadmap().get_learning_nodes()
            if node.get("track") in CORE_TRACKS
            and node.get("id") not in completed_ids
        ]
    if not candidates:
        return None
    return {"core_node": candidates[0].get("id")}


async def _load_progress_rows(user_id: str, db=None) -> list:
    """Load the canonical roadmap progress rows used across PrepOS.

    ``roadmap_node_progress`` remains available for historical compatibility,
    but it is not written by the mission, KB, or feedback workflows. Reading
    it here made the planner observe a different learner state from every
    other consumer. The planner now reads ``knowledge_nodes`` directly.
    """
    if db is None:
        return []
    rows = await load_user_progress_rows(db, user_id)
    return list(rows.values())


async def get_today_learning_node(
    user_id: str, *, db=None, pacing_state: Optional[dict] = None,
    target_companies: Optional[Iterable[str]] = None,
    completed_dates: Optional[Iterable[str]] = None,
    recent_node_ids: Optional[Iterable[str]] = None,
) -> Optional[dict]:
    """Return the best learning recommendation for the user.

    `pacing_state` (services/learning_engine/pacing.py) is optional and
    defaults to None, which yields urgency=0.0 — identical ranking to before
    this parameter existed. When provided, it only nudges ranking toward
    higher interview-importance/frequency nodes; it never changes unlock or
    revision-priority logic.

    `target_companies` (Phase 4A) is the learner's onboarding company list.
    Defaults to None (no companies), which yields company_score=0.0 for every
    candidate — identical ranking to before this parameter existed. When
    provided, it activates `ranking.py`'s existing (previously unused)
    company-aware scoring and tie-breaking.

    `completed_dates` (Phase 4B) is the learner's `knowledge_nodes.completion_date`
    history. It never affects which node is picked — it is only forwarded to
    `pacing.forecast_completion()` to attach a completion forecast onto the
    returned recommendation's `insight`. Defaults to None (no history yet),
    which yields a zero-pace forecast.

    `recent_node_ids` (Foundation RC1.2 item 6) is the set of node ids the
    learner was recommended in their last few missions. Defaults to None (no
    history / no-op), which applies zero recency penalty in `ranking.py` —
    identical ranking to before this parameter existed.
    """
    progress_rows = await _load_progress_rows(user_id, db)
    pacing_state = pacing_state or {}
    urgency = float(pacing_state.get("urgency", 0.0))
    progress_map = {row.get("node_id"): row for row in progress_rows if row.get("node_id")}

    def _attach_insight(node: dict, progress: dict) -> dict:
        breakdown = score_learning_node(
            node, progress, target_companies=target_companies, urgency=urgency,
            progress_map=progress_map, recent_node_ids=recent_node_ids,
        )
        forecast = forecast_completion(pacing_state, completed_dates=completed_dates)
        return build_recommendation_insight(
            node, score_breakdown=breakdown, target_companies=target_companies,
            pacing_state=pacing_state, forecast=forecast,
        )

    revision = get_highest_priority_revision(user_id, progress_rows=progress_rows)
    if revision is not None:
        roadmap = get_roadmap()
        node = roadmap.get(revision.get("node_id"))
        if node is not None:
            return build_learning_recommendation(
                node,
                progress=revision,
                support_recommendation=_build_support_recommendation(node, progress_rows),
                core_recommendation=_build_core_recommendation(progress_rows),
                insight=_attach_insight(node, revision),
            )

    unlocked_nodes = get_unlocked_nodes(progress_rows)
    if not unlocked_nodes:
        return None

    ranked_nodes = rank_learning_nodes(
        unlocked_nodes, progress_map, target_companies=target_companies, urgency=urgency,
        recent_node_ids=recent_node_ids,
    )
    if not ranked_nodes:
        return None

    top_node = ranked_nodes[0]
    top_progress = progress_map.get(top_node.get("id"), {})
    return build_learning_recommendation(
        top_node,
        progress=top_progress,
        support_recommendation=_build_support_recommendation(top_node, progress_rows),
        core_recommendation=_build_core_recommendation(progress_rows),
        insight=_attach_insight(top_node, top_progress),
    )

