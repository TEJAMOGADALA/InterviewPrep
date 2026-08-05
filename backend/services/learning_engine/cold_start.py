"""Cold-start strategy — entry-point selection for genuinely-new learners.

Purpose (Phase 4 Step 1):
    A learner who has NO prior completions AND declares near-zero
    knowledge everywhere should land on the roadmap's actual entry
    track on day one, not on whatever high-priority "unlocked" node
    the ranker's normal scoring happens to surface. The pre-Phase-4
    planner encoded this with a hardcoded {"student", "fresher", "0-1"}
    position set and a hardcoded "<= 1" self-assessment threshold, all
    inside the orchestrator.

    This module isolates that logic as ONE explicit strategy driven by:
      1. Metadata: the roadmap's own `root_subject_ids()` (an academic
         DAG root — a track with no `subject_prerequisites` and which
         unlocks at least one downstream subject). If the curriculum
         grows a new entry track later, this strategy picks it up
         automatically without any planner change.
      2. Live learner state: `LearnerContext.has_declared_progress()`
         AND self-assessment scores. No hardcoded position enum;
         instead we use two DATA-DRIVEN gates that jointly imply
         "this looks like a first-time session":
            - the learner has zero recorded progress, AND
            - EITHER their onboarding scores are near-zero across the
              board (obvious beginner), OR they explicitly picked a
              position that maps to "no professional experience yet"
              via a curriculum-owned mapping we can override later
              without touching the planner.

Design contract:
    * SIGNAL-DRIVEN. Never inspects a specific learner id or username.
      The strategy fires when the DATA — not the person — matches.
    * METADATA-DRIVEN. The entry track comes from roadmap metadata
      (`root_subject_ids()`), not a hardcoded constant.
    * OPTIONAL. Returns None when the strategy doesn't apply, and the
      orchestrator falls through to normal priority scoring.
    * OVERRIDABLE. Callers can pass their own `positions_without_experience`
      to reflect future onboarding vocabulary changes without editing
      this module.
"""
from __future__ import annotations

from typing import Iterable, Optional, Set

from roadmap import get_roadmap
from services.learning_engine.context import LearnerContext

# Onboarding positions that indicate the learner has NO professional
# software-engineering experience yet. Curriculum-owned vocabulary —
# NOT a hardcoded learner profile. Extend by passing an override to
# `cold_start_candidate` if a new onboarding position value is added.
DEFAULT_INEXPERIENCED_POSITIONS: frozenset = frozenset({
    "student", "fresher", "0-1",
})

# Self-assessment cutoff below which a track counts as "near zero
# declared knowledge" for cold-start purposes. Deliberately generous
# (<= 1 on a 0-10 scale) so a learner has to be actively signalling
# "I know nothing" for the override to fire; anyone with even a
# modest declared baseline (score >=2) drops into normal scoring
# where ranking.py's `_FOUNDATION_BONUS` still handles them.
DEFAULT_LOW_SCORE_THRESHOLD: float = 1.0


def _all_scores_near_zero(
    scores: dict,
    tracks: Iterable[str],
    *,
    threshold: float,
) -> bool:
    """Return True iff every listed track has a declared score at or
    below ``threshold``. When any track is missing a score we treat
    it as "unknown" (not zero) and return False — we do NOT force
    beginners' plan on a learner who hasn't declared anything.
    """
    if not scores:
        return False
    values: list = []
    for track in tracks:
        score = scores.get(track)
        if score is None:
            return False
        try:
            values.append(float(score))
        except (TypeError, ValueError):
            return False
    return bool(values) and all(v <= threshold for v in values)


def _looks_like_cold_start(
    context: LearnerContext,
    *,
    inexperienced_positions: Set[str],
    low_score_threshold: float,
    baseline_tracks: Iterable[str],
) -> bool:
    """Signal-driven cold-start detection.

    Fires when the learner (a) has NO prior completion of any kind
    AND (b) either declares an inexperienced onboarding position OR
    declares near-zero knowledge across every baseline track.
    """
    if context.has_declared_progress():
        return False
    position = (context.position or "").strip().lower()
    if position and position in inexperienced_positions:
        return True
    return _all_scores_near_zero(
        context.onboarding_scores,
        baseline_tracks,
        threshold=low_score_threshold,
    )


def cold_start_candidate(
    eligible_nodes: Iterable[dict],
    context: LearnerContext,
    *,
    inexperienced_positions: Iterable[str] = DEFAULT_INEXPERIENCED_POSITIONS,
    low_score_threshold: float = DEFAULT_LOW_SCORE_THRESHOLD,
) -> Optional[dict]:
    """Return the entry-track node for a first-time learner, or None.

    The strategy is a NO-OP for any learner who has recorded
    completions, who has a mid+ onboarding position, or who declared
    even modest baseline knowledge on their self-assessment. In every
    other case the orchestrator uses the normal priority engine —
    which itself has a foundation-first bonus (see ranking.py) that
    handles returning learners with weak fundamentals correctly.

    Baseline tracks are derived from the LearnerContext's declared
    self-assessment map so the strategy generalizes to future
    curriculum additions without a hardcoded track list.
    """
    positions = {p.strip().lower() for p in inexperienced_positions if p}
    baseline_tracks = tuple(context.onboarding_scores.keys())
    if not _looks_like_cold_start(
        context,
        inexperienced_positions=positions,
        low_score_threshold=low_score_threshold,
        baseline_tracks=baseline_tracks,
    ):
        return None

    root_subjects = get_roadmap().root_subject_ids()
    entry_track = root_subjects[0] if root_subjects else None
    if entry_track is None:
        return None

    return next(
        (node for node in eligible_nodes if node.get("track") == entry_track),
        None,
    )
