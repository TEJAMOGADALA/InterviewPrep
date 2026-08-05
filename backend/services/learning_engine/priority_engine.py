"""Priority Engine — the single generalized scoring layer.

Purpose (Phase 4 Step 1):
    Score every eligible roadmap candidate using the existing
    curriculum metadata together with learner context, then pick the
    highest-priority candidate for today. Historically this decision
    was split between:
        - inline calls to ranking.score_learning_node inside planner.py
        - a manual continuity tie-break loop inside planner.py
        - insight builder recomputing the same breakdown
    …which made adding a new signal a three-file change. The Priority
    Engine collapses that into one API surface:

        top = top_candidate(candidates, context)
        top.node           # the winning roadmap node
        top.score          # scalar priority (for logs / audit)
        top.breakdown      # every signal that produced the score
        top.continuity     # continuity level vs recent history

    The underlying scoring model is unchanged (ranking.score_learning_node
    remains the canonical formula — new signals should be added as
    penalty/bonus terms there, not duplicated in this layer). This
    module simply exposes the model as a first-class engine that
    accepts a LearnerContext and returns structured PriorityScore rows.

Design contract:
    * Generalized. Consumes only what LearnerContext exposes; the
      formula never inspects a specific learner id, company id,
      programming language, or roadmap track by name.
    * Reusable. Companion recommendations (companion.py) re-run the
      same engine over their own candidate pool so support/core tasks
      are picked with the same yardstick as the primary task.
    * Deterministic. Same context + same candidate list => same
      output. Ties are broken by (company_score desc, node id asc) —
      no wall-clock, no random.
    * Extensible. New signals go into LearnerContext + ranking.py; no
      change needed here or in the planner.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from services.learning_engine.composition import (
    ContinuityChain, continuity_score,
)
from services.learning_engine.context import LearnerContext
from services.learning_engine.ranking import score_learning_node

# Tie-break threshold: when the top scalar score and a runner-up are
# within this fractional distance, we consult continuity as a tie-break.
# Matches the pre-Phase-4 planner behaviour ("within 5%").
CONTINUITY_TIE_BREAK_RATIO = 0.95

# Number of runners-up to consider for the continuity tie-break. Matches
# the pre-Phase-4 planner's `ranked_nodes[1:4]` slice.
CONTINUITY_TIE_BREAK_WINDOW = 3


@dataclass
class PriorityScore:
    """A structured priority-scoring result for one candidate.

    Immutable snapshot of every signal that produced the score. Kept
    together (rather than returning parallel lists) so downstream
    consumers (insight builder, audit logs, why-this? dialog) can
    reason about one row without holding multiple maps.
    """
    node: dict
    score: float
    breakdown: dict = field(default_factory=dict)
    continuity: dict = field(default_factory=dict)

    @property
    def node_id(self) -> Optional[str]:
        return self.node.get("id") if self.node else None

    @property
    def company_score(self) -> float:
        return float(self.breakdown.get("company_score", 0.0) or 0.0)


def _compute_breakdown(node: dict, context: LearnerContext) -> dict:
    """Run the canonical scoring model over one node + one context.

    All signals are read from the LearnerContext; new signals go into
    the context and then into `ranking.score_learning_node`. This
    wrapper intentionally has NO branching of its own — it's a thin
    adapter that hides the argument-drilling.
    """
    return score_learning_node(
        node,
        context.progress_map.get(node.get("id"), {}),
        target_companies=context.target_companies,
        urgency=context.urgency,
        progress_map=context.progress_map,
        recent_node_ids=context.recent_node_ids,
        skipped_node_ids=context.skipped_node_ids,
        recent_track_ids=context.recent_track_ids,
        position=context.position,
        onboarding_scores=context.onboarding_scores,
    )


def score_candidate(node: dict, context: LearnerContext) -> PriorityScore:
    """Score ONE candidate against the given learner context.

    Also attaches the continuity signal so downstream (insight,
    tie-break) never has to recompute it.
    """
    breakdown = _compute_breakdown(node, context)
    cont = continuity_score(node, context.continuity_chain())
    return PriorityScore(
        node=node,
        score=float(breakdown.get("total_score", 0.0) or 0.0),
        breakdown=breakdown,
        continuity=cont,
    )


def score_candidates(
    candidates: Iterable[dict],
    context: LearnerContext,
) -> List[PriorityScore]:
    """Score every candidate and return them highest-priority first.

    Tie-break order:
        1. total_score  (descending) — the canonical scalar.
        2. company_score (descending) — matches pre-Phase-4 ranking.
        3. node id (ascending)        — stable, deterministic tiebreaker
                                        so equal-score candidates never
                                        depend on iteration order.
    """
    scored = [score_candidate(node, context) for node in candidates]
    return sorted(
        scored,
        key=lambda s: (
            -s.score,
            -s.company_score,
            s.node_id or "",
        ),
    )


def top_candidate(
    candidates: Iterable[dict],
    context: LearnerContext,
    *,
    tie_break_ratio: float = CONTINUITY_TIE_BREAK_RATIO,
    tie_break_window: int = CONTINUITY_TIE_BREAK_WINDOW,
) -> Optional[PriorityScore]:
    """Return the winning PriorityScore, with a continuity tie-break.

    When the top two candidates land within `tie_break_ratio` of each
    other on scalar score, prefer the one that keeps the learner
    closer to yesterday's topic/module (smaller continuity distance).
    Never applied when the top is a strong winner (the ratio guards
    against that) and never applied for a first-session learner (their
    continuity chain is empty, so `distance` defaults to 3+ for
    everything and no tie-break flip is possible).

    Returns None only when `candidates` is empty. Callers must handle
    the empty-eligible-pool case themselves.
    """
    ranked = score_candidates(candidates, context)
    if not ranked:
        return None

    top = ranked[0]
    chain = context.continuity_chain()
    if not chain.last_track_id or top.score <= 0 or len(ranked) < 2:
        return top

    top_distance = top.continuity.get("distance", 4)
    for runner_up in ranked[1: 1 + tie_break_window]:
        ratio = runner_up.score / top.score if top.score > 0 else 0.0
        if ratio < tie_break_ratio:
            break
        if runner_up.continuity.get("distance", 4) < top_distance:
            return runner_up
    return top


# ---------------------------------------------------------------------------
# Backwards-compatible aliases for existing callers
# ---------------------------------------------------------------------------

def rank_by_priority(candidates: Iterable[dict], context: LearnerContext) -> List[dict]:
    """Return candidates sorted highest-priority first (nodes only, no
    breakdown). Convenience for callers that only need the ordering."""
    return [scored.node for scored in score_candidates(candidates, context)]
