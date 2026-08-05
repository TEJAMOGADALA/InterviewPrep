"""LearnerContext — the single bundle of learner-scoped signals the
adaptive planning pipeline consumes.

Purpose (Phase 4 Step 1):
    The planner previously threaded ~10 individual keyword arguments
    through every scoring / candidate / insight call. Every time a new
    adaptive signal was introduced (skipped nodes, track fatigue,
    foundation bias, continuity …), every intermediate function had
    to grow another parameter. That coupling is what the Phase 4 brief
    explicitly asks us to remove: "New … learner attributes, and
    scoring signals should be introducible without requiring planner
    redesign or large conditional changes."

    Bundling them in ONE dataclass turns extension into an additive
    change: add a new field here, teach whichever engine layer cares
    about it to read it, and the planner code path stays untouched.

Design contract:
    * PURE data. Never touches Mongo, never fetches roadmap nodes
      directly, never mutates. The planner is responsible for
      populating it; every layer downstream is read-only.
    * OPTIONAL everywhere. Every field defaults to a safe empty value
      so a caller that only passes user_id + db still gets identical
      behaviour to the pre-refactor planner.
    * DETERMINISTIC. Derived properties (completed_node_ids,
      continuity_chain) are computed the same way as the pre-Phase-4
      code so the recommendation output is byte-identical for the same
      inputs.
    * METADATA-DRIVEN. No hardcoded position enums, no company-specific
      branching, no scenario-specific if/else lives here. Higher-level
      strategies (cold_start.py, companion.py, priority_engine.py) read
      these signals but never encode learner identities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set

from services.learning_engine.composition import (
    ContinuityChain, chain_from_history,
)

_COMPLETED_STATUSES = {"completed", "mastered", "revision_due"}


@dataclass
class LearnerContext:
    """Everything the adaptive planning pipeline needs to know about ONE learner.

    Populate ONCE at the top of the orchestrator; pass around by
    reference. No layer should ever hold a partial copy — that would
    reintroduce the "one signal missed one code path" bug the bundle
    was designed to eliminate.
    """

    # ---- Onboarding + curriculum baseline -----------------------------------
    onboarding: dict = field(default_factory=dict)

    # ---- Live progress ------------------------------------------------------
    # progress_rows: list ordering matches load_user_progress_rows(); the
    # planner uses this list for unlock/eligibility queries that iterate.
    progress_rows: List[dict] = field(default_factory=list)
    # progress_map: node_id -> row, used for O(1) lookups by ranking and
    # eligibility. Callers can populate either; the property below fills
    # the other on demand.
    progress_map: Dict[str, dict] = field(default_factory=dict)

    # ---- Pacing (interview deadline / capacity) -----------------------------
    pacing_state: dict = field(default_factory=dict)

    # ---- Recent mission history --------------------------------------------
    # All optional; every existing pre-Phase-4 caller path leaves these
    # empty and gets identical scoring to before.
    recent_completions: List[dict] = field(default_factory=list)
    recent_node_ids: List[str] = field(default_factory=list)
    recent_track_ids: List[str] = field(default_factory=list)
    skipped_node_ids: List[str] = field(default_factory=list)
    completed_dates: List[str] = field(default_factory=list)

    # ---- Company targeting --------------------------------------------------
    target_companies: List[str] = field(default_factory=list)

    # ---- Cross-cut helpers --------------------------------------------------
    # knowledge_rows is a separate view over knowledge (topic-level scores
    # for company-readiness estimation). Kept distinct from progress_rows
    # (node-level) because they serve different math.
    knowledge_rows: List[dict] = field(default_factory=list)
    # skip_node_ids is the RETRY hint from validate_mission — the planner
    # is instructed to avoid re-picking these on a regeneration attempt.
    skip_node_ids: Set[str] = field(default_factory=set)

    # -----------------------------------------------------------------
    # Derived, cached-on-first-access properties
    # -----------------------------------------------------------------

    @property
    def urgency(self) -> float:
        """Interview-deadline pacing pressure (0.0 - 1.0). 0.0 = no pressure."""
        try:
            return float(self.pacing_state.get("urgency", 0.0) or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @property
    def position(self) -> Optional[str]:
        """Learner's declared experience band (student / 0-1 / 1-3 / 3-5 / 5+).

        Consumers must treat this as an opaque tag — never hardcode a
        specific enum value here. ranking.py already does the right
        thing (its fatigue rule keys off a data-driven set), but if a
        new position label appears in onboarding we do not want to
        break scoring: unknown positions receive the default policy.
        """
        return (self.onboarding or {}).get("current_position")

    @property
    def onboarding_scores(self) -> dict:
        """Self-assessment map: track_id -> 0-10. Empty when not declared."""
        return (self.onboarding or {}).get("self_assessment") or {}

    def completed_node_ids(self) -> Set[str]:
        """Node ids that are done for planning purposes.

        A row counts as done when its `status` is one of `completed`,
        `mastered`, or `revision_due` (matches unlock.py + planner.py
        pre-refactor). Cached implicitly since progress_rows is
        immutable once the context is built.
        """
        completed: Set[str] = set()
        for row in self.progress_rows or []:
            if not isinstance(row, dict):
                continue
            status = (row.get("status") or "").lower()
            node_id = row.get("node_id")
            if node_id and status in _COMPLETED_STATUSES:
                completed.add(node_id)
        return completed

    def continuity_chain(self) -> ContinuityChain:
        """Return the learning-continuity breadcrumb built from the
        newest completed learning-node row. Same helper the pre-Phase-4
        planner called inline."""
        return chain_from_history(self.recent_completions or [])

    def has_declared_progress(self) -> bool:
        """Return whether the learner has ANY prior completion or activity.

        Used by cold-start detection to distinguish a genuine first
        session from a returning learner whose knowledge signals happen
        to be low. Recent completions is the strongest evidence of
        past activity; a populated progress_map is a weaker but valid
        signal too (they at least have knowledge_nodes rows).
        """
        if self.recent_completions:
            return True
        return bool(self.completed_node_ids())


def build_learner_context(
    *,
    onboarding: Optional[dict] = None,
    progress_rows: Optional[Iterable[dict]] = None,
    pacing_state: Optional[dict] = None,
    target_companies: Optional[Iterable[str]] = None,
    recent_completions: Optional[Iterable[dict]] = None,
    recent_node_ids: Optional[Iterable[str]] = None,
    recent_track_ids: Optional[Iterable[str]] = None,
    skipped_node_ids: Optional[Iterable[str]] = None,
    completed_dates: Optional[Iterable[str]] = None,
    knowledge_rows: Optional[Iterable[dict]] = None,
    skip_node_ids: Optional[Iterable[str]] = None,
) -> LearnerContext:
    """Assemble a LearnerContext from raw inputs.

    Every argument is optional — callers that pass nothing get a
    LearnerContext that behaves identically to the pre-Phase-4 planner
    when it was invoked with only `user_id + db`. The planner is the
    canonical caller; tests can also build contexts directly.
    """
    rows = list(progress_rows or [])
    progress_map = {row.get("node_id"): row for row in rows if row.get("node_id")}
    return LearnerContext(
        onboarding=dict(onboarding or {}),
        progress_rows=rows,
        progress_map=progress_map,
        pacing_state=dict(pacing_state or {}),
        target_companies=[str(c) for c in (target_companies or [])],
        recent_completions=list(recent_completions or []),
        recent_node_ids=list(recent_node_ids or []),
        recent_track_ids=list(recent_track_ids or []),
        skipped_node_ids=list(skipped_node_ids or []),
        completed_dates=list(completed_dates or []),
        knowledge_rows=list(knowledge_rows or []),
        skip_node_ids=set(skip_node_ids or []),
    )
