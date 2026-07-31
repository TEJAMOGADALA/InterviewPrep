"""Forward-looking planner helpers — Likely Next Topics and readiness estimate.

Both concerns model "what does completing today's mission move toward?"
and are grouped together for that reason. Neither promises a deterministic
outcome:

  • :func:`likely_next_topics` is deliberately named "likely" (not
    "future unlocks"). Future missions remain adaptive; unlocking a
    prerequisite is a *necessary condition* but not a sufficient one for
    a topic being picked next. This helper walks the reverse-prerequisite
    graph and returns the topics the planner would MOST LIKELY reach for
    next — a preview, not a guarantee.

  • :func:`estimate_company_readiness_gain` returns a planner ESTIMATE,
    not a prediction. Callers surface it in the UI clearly labelled as
    an estimate ("planner estimate · not a guarantee"). Derived from the
    canonical ``compute_company_readiness`` model in
    ``mission_engine.py`` so it can never contradict the readiness the
    dashboard shows.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from roadmap import get_roadmap
from services.learning_engine.roi import compute_learning_roi, direct_dependents


# ---------------------------------------------------------------------------
# Likely Next Topics
# ---------------------------------------------------------------------------

_MAX_LIKELY = 3


def likely_next_topics(
    node_id: Optional[str],
    completed_ids: Optional[Iterable[str]] = None,
    *,
    limit: int = _MAX_LIKELY,
) -> List[dict]:
    """Return up to ``limit`` topics the planner is most likely to reach
    next after ``node_id`` is completed.

    Ranking heuristic (deterministic, no user state read):

    1. Immediate reverse-prerequisites of ``node_id`` come first. These
       become "unlocked" the moment ``node_id`` is completed — the most
       tangible preview we can offer.
    2. Among those, the ones with the highest ROI (largest downstream
       reach) rank higher, because they're the ones the planner is most
       likely to prioritise next.
    3. Anything already in ``completed_ids`` is filtered out.

    Emits a lightly-shaped dict so the UI can render a strip without
    another network round-trip:

        { "node_id", "label", "track", "when", "why" }

    ``when`` is a qualitative bucket (``next`` | ``then`` | ``later``);
    the UI is free to render it exactly, or use it to time-order the
    preview strip. The choice of qualitative labels (rather than "day
    +N") is deliberate — again, no promise about specific future missions.
    """
    if not node_id:
        return []
    completed = set(completed_ids or ())
    roadmap = get_roadmap()

    dependents = direct_dependents(node_id)
    dependents = [d for d in dependents if d not in completed]

    scored: List[tuple] = []
    for dep_id in dependents:
        node = roadmap.get(dep_id)
        if not node:
            continue
        roi = compute_learning_roi(dep_id)
        scored.append((roi.get("roi_score", 0.0), roi.get("direct_unlocks", 0), node))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)

    when_buckets = ["next", "then", "later"]
    out: List[dict] = []
    for i, (_, direct_unlocks, node) in enumerate(scored[:limit]):
        when = when_buckets[min(i, len(when_buckets) - 1)]
        why_bits: List[str] = []
        if direct_unlocks:
            why_bits.append(f"unlocks {direct_unlocks} more topic{'s' if direct_unlocks != 1 else ''}")
        if node.get("interview_frequency"):
            why_bits.append(f"IF {node.get('interview_frequency')}/5")
        out.append({
            "node_id": node.get("id"),
            "label": node.get("label") or node.get("id"),
            "track": node.get("track"),
            "when": when,
            "why": ", ".join(why_bits) or "next in your dependency chain",
        })
    return out


# ---------------------------------------------------------------------------
# Company readiness estimate
# ---------------------------------------------------------------------------

def estimate_company_readiness_gain(
    node: dict,
    *,
    onboarding: dict,
    knowledge_rows: List[dict],
    target_companies: Iterable[str],
    difficulty: str = "medium",
    task_kinds: Iterable[str] = ("study",),
) -> dict:
    """Return an *estimate* of the readiness gain per target company from
    completing today's mission.

    The estimate is deliberately conservative and labelled as such:

    * Uses the same weight tables the dashboard uses
      (``COMPANY_READINESS_WEIGHTS`` in ``mission_engine.py``), so we
      never diverge from what the user already sees.
    * Applies the same knowledge-gain formula (``apply_knowledge_gain``)
      the toggle-task workflow uses — so the estimate matches the
      *actual* update the learner will observe when they complete the
      mission, not a fabricated number.
    * Clamps to two decimal places and returns both the projected
      before/after readiness values AND the delta, so consumers can
      render either without recomputing.
    * Always returns ``estimate: true`` and ``label`` so the UI can
      prominently display "planner estimate".

    Deliberately returns an empty ``per_company`` when ``target_companies``
    is empty rather than fabricating a global estimate.
    """
    # Local imports to avoid a circular dependency with mission_engine
    # (which itself imports from the learning_engine package).
    from mission_engine import (
        compute_company_readiness, apply_knowledge_gain,
        COMPANY_READINESS_WEIGHTS, DEFAULT_READINESS,
    )

    companies = [str(c).lower() for c in (target_companies or [])]
    empty = {
        "estimate": True,
        "label": "planner estimate",
        "before": {}, "after": {}, "delta": {},
        "note": None,
    }
    if not companies:
        empty["note"] = "No target companies selected."
        return empty

    # Current readiness (dashboard-consistent).
    before = {c: compute_company_readiness(c, knowledge_rows, onboarding) for c in companies}

    # Project the "after" state: apply one knowledge_gain to the primary
    # node's topic for each task-kind the mission will contain. This
    # mirrors the write path in `_record_completed_task_progress`.
    projected_by_topic: Dict[str, float] = {
        row.get("topic"): float(row.get("score", 0.0))
        for row in (knowledge_rows or [])
        if isinstance(row, dict) and row.get("topic")
    }
    topic = node.get("track") or node.get("topic") or (node.get("id") or "").split(".")[0]
    baseline = (onboarding or {}).get("self_assessment", {})
    current = projected_by_topic.get(topic)
    if current is None:
        current = float(baseline.get(topic, 5)) * 10

    for kind in task_kinds or ("study",):
        try:
            current = apply_knowledge_gain(current, difficulty, kind)
        except (KeyError, TypeError, ValueError):
            # If a task carries an unexpected kind/difficulty we skip it
            # rather than fabricating a number.
            continue

    projected_by_topic[topic] = current
    projected_rows = [
        {"topic": t, "score": s} for t, s in projected_by_topic.items()
    ]
    after = {c: compute_company_readiness(c, projected_rows, onboarding) for c in companies}

    delta = {c: round(after[c] - before[c], 2) for c in companies}

    max_gain = max(delta.values()) if delta else 0.0
    if max_gain <= 0.01:
        note = "Very small change — this session is mostly reinforcement."
    elif max_gain < 1.0:
        note = "Modest gain — one mission moves the needle by less than 1 pt."
    elif max_gain < 3.0:
        note = "Solid gain for a single session."
    else:
        note = "Large projected gain — verify by revisiting the topic in a few days."

    return {
        "estimate": True,
        "label": "planner estimate",
        "before": {c: round(v, 2) for c, v in before.items()},
        "after": {c: round(v, 2) for c, v in after.items()},
        "delta": delta,
        "note": note,
        # Unit is percentage points on the 0-100 readiness scale.
        "unit": "pp",
        # Used by callers that want to render only the top target(s).
        "top_company": max(delta, key=delta.get) if delta else None,
    }
