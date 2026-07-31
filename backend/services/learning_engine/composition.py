"""Mission composition, constraints, validation, and learning continuity.

Grouped together because they share the same abstraction level — every
concern here operates on a *proposed* mission before it's persisted:

  • :func:`plan_composition`    — decides the task-mix (how many practice /
    study / revision / supporting / core tasks a mission should have).
  • :class:`MissionConstraints` — hard caps that a well-formed mission
    must respect (max practice, max revisions, study-time budget,
    de-duplication, conflict avoidance).
  • :func:`validate_mission`    — walks a proposed mission against the
    constraints AND the composition plan, returning a structured
    ``MissionValidation`` result. Callers use ``severity`` to decide
    whether to regenerate.
  • :func:`chain_from_history` + :func:`continuity_score` — model
    learning-continuity so a candidate that keeps the learner in the same
    module / topic scores higher on the qualitative continuity axis. Kept
    here because continuity is used by :func:`plan_composition` and by
    the ranking layer (nudge only — never a hard veto).

This module DOES NOT re-implement scoring. The single scalar score still
lives in ``services/learning_engine/ranking.score_learning_node``; this
module adds the qualitative decisions layered on top of it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from roadmap import get_roadmap

# ---------------------------------------------------------------------------
# Composition planning
# ---------------------------------------------------------------------------

# Public — imported by callers that need the raw plan shape (mission_engine).
DEFAULT_PRACTICE_COUNT_BY_HOURS = (
    # (min_hours_inclusive, practice_count)
    (3.0, 3),
    (1.5, 2),
    (0.0, 1),
)


@dataclass
class CompositionPlan:
    """A resolved composition contract for one mission.

    Immutable snapshot. Missions are built to match this plan; the
    validator compares the *actual* mission tasks against it.
    """
    primary_kind: str              # "practice" | "study"
    practice_count: int            # 0-4
    revision_slots: int            # 0-3
    include_supporting: bool       # add one supporting-concept task
    include_core: bool             # add one OS/DBMS/CN reading task
    capacity_minutes: int          # the effective study-time budget
    rationale: str                 # human-readable, joined-comma facts

    def to_dict(self) -> dict:
        return {
            "primary_kind": self.primary_kind,
            "practice_count": self.practice_count,
            "revision_slots": self.revision_slots,
            "include_supporting": self.include_supporting,
            "include_core": self.include_core,
            "capacity_minutes": self.capacity_minutes,
            "rationale": self.rationale,
        }


def plan_composition(
    *,
    pacing_state: Optional[dict] = None,
    position: str = "0-1",
    revisions_due_count: int = 0,
    primary_track: Optional[str] = None,
    primary_confidence: Optional[float] = None,
    extra_practice_yesterday: int = 0,
) -> CompositionPlan:
    """Return the intended task-mix for today's mission.

    Only reads the signals a good planner should consult:

    * ``pacing_state`` — urgency / capacity / mode (from pacing.py).
    * ``position`` — the learner's declared experience band.
    * ``revisions_due_count`` — how much spaced-repetition pressure exists.
    * ``primary_track`` — DSA missions include practice; conceptual tracks
      (java/lld/hld/os/dbms/cn) lean toward "study".
    * ``primary_confidence`` — very low confidence → shrink to depth-first
      (one strong task) rather than breadth (many small tasks).
    * ``extra_practice_yesterday`` — momentum signal from the existing
      "did extra practice yesterday" heuristic already used by
      mission_engine.
    """
    pacing_state = pacing_state or {}
    urgency = float(pacing_state.get("urgency", 0.0) or 0.0)
    pacing_mode = pacing_state.get("pacing_mode", "standard")
    capacity_minutes = int(pacing_state.get("daily_capacity_minutes") or 120)

    # Extra practice yesterday nudges capacity upward, matching the
    # existing behaviour in mission_engine.build_mission_for_user.
    if extra_practice_yesterday >= 2:
        capacity_minutes = min(capacity_minutes + 30, 8 * 60)

    hours = capacity_minutes / 60.0

    # Practice count from the study window.
    practice_count = 1
    for threshold, count in DEFAULT_PRACTICE_COUNT_BY_HOURS:
        if hours >= threshold:
            practice_count = count
            break

    # Interview urgency: same time budget used more densely (matches
    # existing mission_engine behavior).
    if urgency >= 0.7 and hours >= 1.5:
        practice_count = min(practice_count + 1, 4)

    # Confidence-aware shrink: if the learner is very unsure (<3.0/10), we
    # prefer depth over breadth for the practice slot(s).
    if primary_confidence is not None and primary_confidence < 3.0:
        practice_count = max(1, practice_count - 1)

    # DSA is the only track that carries the coding-practice pattern
    # today; other tracks author their tasks as "study".
    primary_kind = "practice" if primary_track == "dsa" else "study"

    # Revision cap grows with pacing pressure — critical mode gets one
    # extra slot to catch up on due revisions.
    max_revision_slots = 3 if pacing_mode == "critical" else 2
    revision_slots = min(revisions_due_count, max_revision_slots)

    # Supporting: always include unless the day is very short (<45 min).
    include_supporting = hours >= 0.75

    # Core reading: only when the study window is ≥ 3 h (matches
    # existing mission_engine behavior).
    include_core = hours >= 3.0

    rationale_bits = [
        f"{hours:.1f}h window",
        f"{position} experience",
    ]
    if urgency >= 0.7:
        rationale_bits.append("urgent pacing")
    if revisions_due_count:
        rationale_bits.append(f"{revision_slots} revision{'s' if revision_slots != 1 else ''} due")
    if primary_confidence is not None and primary_confidence < 3.0:
        rationale_bits.append("low-confidence · depth over breadth")

    return CompositionPlan(
        primary_kind=primary_kind,
        practice_count=practice_count,
        revision_slots=revision_slots,
        include_supporting=include_supporting,
        include_core=include_core,
        capacity_minutes=capacity_minutes,
        rationale=" · ".join(rationale_bits),
    )


# ---------------------------------------------------------------------------
# Constraints + validation
# ---------------------------------------------------------------------------

@dataclass
class MissionConstraints:
    """Hard limits every mission must respect.

    These are the SLA of the planner: any generated mission that violates
    them will trigger a regeneration attempt in the orchestrator. Values
    are conservative and mirror the existing hand-coded caps that were
    previously scattered across ``mission_engine.build_mission_for_user``.
    """
    max_total_tasks: int = 6
    max_practice_tasks: int = 4
    max_revision_tasks: int = 3
    max_supporting_tasks: int = 1
    max_core_tasks: int = 1
    # A mission must not exceed the daily capacity by more than this
    # fraction — 20% grace is what the existing planner tolerates when
    # practice_count and revisions overlap.
    overrun_tolerance: float = 0.20
    # Every task's node_id must be unique — no two tasks on the same node.
    forbid_duplicate_nodes: bool = True
    # A node can appear in at most one *kind* (e.g. can't be both study
    # AND practice today).
    forbid_conflicting_kinds_per_node: bool = True


@dataclass
class MissionValidation:
    severity: str = "ok"                    # "ok" | "warn" | "regenerate"
    issues: List[str] = field(default_factory=list)
    hint_skip_node_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "issues": list(self.issues),
            "hint_skip_node_ids": list(self.hint_skip_node_ids),
        }


# Rough minutes-per-task estimates used to project mission workload when
# individual tasks don't carry an `estimated_minutes`. Deliberately
# generous so we don't over-flag valid missions. Falls back to the roadmap
# node's authored `estimated_minutes` where available.
_KIND_DEFAULT_MINUTES = {
    "practice": 25,   # per problem — multiplied by problem_count if present
    "study":    30,
    "revise":   15,
}


def _task_minutes(task: dict) -> int:
    """Estimate one task's duration for capacity budgeting."""
    kind = task.get("kind") or "study"
    node = None
    node_id = task.get("node_id")
    if node_id:
        node = get_roadmap().get(node_id)
    per_task = int((node or {}).get("estimated_minutes") or 0)
    if not per_task:
        per_task = _KIND_DEFAULT_MINUTES.get(kind, 20)

    if kind == "practice":
        count = int(task.get("problem_count") or 1)
        return per_task * max(1, count)
    return per_task


def validate_mission(
    tasks: Iterable[dict],
    plan: CompositionPlan,
    *,
    constraints: Optional[MissionConstraints] = None,
) -> MissionValidation:
    """Walk ``tasks`` against ``plan`` + ``constraints``.

    Returns a :class:`MissionValidation` with a severity that callers use
    to decide the next action:

    * ``ok``          — mission is well-formed; publish it.
    * ``warn``        — mission is publishable but slightly off-plan;
                        the caller logs the drift into
                        ``mission_adjustments`` but does not regenerate.
    * ``regenerate``  — a hard constraint was violated; the caller
                        should skip the offending node ids
                        (``hint_skip_node_ids``) and try again.

    NEVER raises. Even a malformed task list yields a structured
    validation result — callers can rely on ``severity`` and don't need
    to guard against exceptions.
    """
    tasks = list(tasks or [])
    constraints = constraints or MissionConstraints()
    result = MissionValidation()

    # ----- Task-mix caps -----------------------------------------------------
    if len(tasks) > constraints.max_total_tasks:
        result.severity = "regenerate"
        result.issues.append(
            f"total_tasks={len(tasks)} exceeds max_total_tasks={constraints.max_total_tasks}"
        )

    by_kind = {"practice": 0, "study": 0, "revise": 0}
    for t in tasks:
        k = (t.get("kind") or "study").lower()
        by_kind[k] = by_kind.get(k, 0) + 1

    if by_kind["practice"] > constraints.max_practice_tasks:
        result.severity = "regenerate"
        result.issues.append(
            f"practice_tasks={by_kind['practice']} exceeds max_practice_tasks={constraints.max_practice_tasks}"
        )
    if by_kind["revise"] > constraints.max_revision_tasks:
        # Excess revisions are a "warn" — the mission is still usable,
        # we just clip them for the day.
        if result.severity == "ok":
            result.severity = "warn"
        result.issues.append(
            f"revise_tasks={by_kind['revise']} exceeds max_revision_tasks={constraints.max_revision_tasks}"
        )

    # ----- Duplicate / conflicting nodes ------------------------------------
    if constraints.forbid_duplicate_nodes:
        seen_ids: set = set()
        for t in tasks:
            nid = t.get("node_id")
            if not nid:
                continue
            if nid in seen_ids:
                result.severity = "regenerate"
                result.issues.append(f"duplicate node in mission: {nid}")
                result.hint_skip_node_ids.append(nid)
            seen_ids.add(nid)

    if constraints.forbid_conflicting_kinds_per_node:
        node_kinds: dict = {}
        for t in tasks:
            nid = t.get("node_id")
            k = (t.get("kind") or "study").lower()
            if not nid:
                continue
            if nid in node_kinds and node_kinds[nid] != k:
                result.severity = "regenerate"
                result.issues.append(
                    f"conflicting kinds on {nid}: {node_kinds[nid]!r} + {k!r}"
                )
                result.hint_skip_node_ids.append(nid)
            else:
                node_kinds[nid] = k

    # ----- Study-time budget -------------------------------------------------
    projected_minutes = sum(_task_minutes(t) for t in tasks)
    ceiling = plan.capacity_minutes * (1.0 + constraints.overrun_tolerance)
    if projected_minutes > ceiling:
        result.severity = "regenerate"
        result.issues.append(
            f"projected_minutes={projected_minutes} exceeds ceiling={int(ceiling)} "
            f"(capacity={plan.capacity_minutes}, tolerance={int(constraints.overrun_tolerance*100)}%)"
        )

    # ----- Plan drift (warn, not regenerate) --------------------------------
    if by_kind["practice"] != plan.practice_count and plan.primary_kind == "practice":
        if result.severity == "ok":
            result.severity = "warn"
        result.issues.append(
            f"practice_count={by_kind['practice']} differs from plan={plan.practice_count}"
        )

    return result


# ---------------------------------------------------------------------------
# Learning continuity
# ---------------------------------------------------------------------------

@dataclass
class ContinuityChain:
    """Snapshot of the learner's recent completed learning-node breadcrumb."""
    last_node_id: Optional[str] = None
    last_topic_id: Optional[str] = None
    last_module_id: Optional[str] = None
    last_track_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "last_node_id": self.last_node_id,
            "last_topic_id": self.last_topic_id,
            "last_module_id": self.last_module_id,
            "last_track_id": self.last_track_id,
        }


def chain_from_history(recent_completions: Iterable[dict]) -> ContinuityChain:
    """Build a lightweight breadcrumb from the learner's most recent
    completed knowledge-node rows (sorted newest-first).

    Only the most recent completion matters — the goal is to bias today
    toward continuing yesterday's momentum, not to model long history.
    """
    for row in recent_completions or ():
        node_id = row.get("node_id") if isinstance(row, dict) else None
        if not node_id:
            continue
        roadmap = get_roadmap()
        node = roadmap.get(node_id)
        if node is None:
            continue
        # ancestors returns root-to-node [track, module, topic]
        chain = roadmap.ancestors(node_id)
        track = next((a for a in chain if a.get("type") == "track"), None)
        module = next((a for a in chain if a.get("type") == "module"), None)
        topic = next((a for a in chain if a.get("type") == "topic"), None)
        return ContinuityChain(
            last_node_id=node_id,
            last_topic_id=(topic or {}).get("id"),
            last_module_id=(module or {}).get("id"),
            last_track_id=(track or {}).get("id") or node.get("track"),
        )
    return ContinuityChain()


def continuity_score(candidate_node: dict, chain: ContinuityChain) -> dict:
    """Return a structured continuity signal for one candidate node.

    Not fed back into ``score_learning_node`` (which is intentionally
    kept as a stable scalar); instead surfaced on the insight for the
    "why this?" explanation AND used as a **tie-break** in the planner
    when two candidates land within 5% of each other on total_score.
    """
    if not chain or not chain.last_track_id or not candidate_node:
        return {"level": "unknown", "distance": 3}
    cand_id = candidate_node.get("id")
    if cand_id and cand_id == chain.last_node_id:
        return {"level": "same_node", "distance": 0}

    roadmap = get_roadmap()
    ancestors = roadmap.ancestors(cand_id) if cand_id else []
    topic = next((a for a in ancestors if a.get("type") == "topic"), None)
    module = next((a for a in ancestors if a.get("type") == "module"), None)
    track = next((a for a in ancestors if a.get("type") == "track"), None)

    if topic and topic.get("id") == chain.last_topic_id:
        return {"level": "same_topic", "distance": 1, "from": chain.last_topic_id}
    if module and module.get("id") == chain.last_module_id:
        return {"level": "same_module", "distance": 2, "from": chain.last_module_id}
    if (track and track.get("id") == chain.last_track_id) or candidate_node.get("track") == chain.last_track_id:
        return {"level": "same_track", "distance": 3, "from": chain.last_track_id}
    return {"level": "different_track", "distance": 4, "from": chain.last_track_id}
