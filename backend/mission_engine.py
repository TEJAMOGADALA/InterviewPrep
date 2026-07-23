"""Mission Engine V2 — adaptive.

Builds tomorrow's mission from yesterday's feedback (confidence, hints, time),
inserts prerequisite root-cause revisions, and honors company weighting +
target date. Task-level toggling is idempotent.
"""
import hashlib
import random
from datetime import datetime, timezone, timedelta, date as date_cls
from typing import Dict, List, Optional, Tuple

from models import (
    DailyMission, MissionTask, TOPIC_KEYS,
)
from problem_bank import (
    SUBTOPIC_TO_PATTERN, PATTERN_TO_DOMAIN, PATTERN_PREREQUISITES,
    problems_by_pattern,
)
from roadmap import get_roadmap, topic_meta


# --------------------- Content library ---------------------
# The roadmap owns the learning catalog.  Keep this legacy-shaped name because
# routes and the mission builder already consume it, but derive it once from
# the versioned graph rather than maintaining a second, incomplete catalog.
TOPIC_META = topic_meta()

# Company weighting bias for topic urgency.
COMPANY_BIAS = {
    "google":      {"dsa": 0.3, "hld": 0.2},
    "microsoft":   {"dsa": 0.25, "lld": 0.2},
    "uber":        {"hld": 0.3, "dsa": 0.15},
    "adobe":       {"lld": 0.25, "dsa": 0.2},
    "atlassian":   {"lld": 0.25, "hld": 0.15},
    "linkedin":    {"hld": 0.25, "dsa": 0.15},
    "stripe":      {"hld": 0.25, "dsa": 0.2, "java": 0.15},
    "salesforce":  {"java": 0.2, "lld": 0.2},
    "phonepe":     {"hld": 0.2, "dsa": 0.2},
    "flipkart":    {"dsa": 0.25, "lld": 0.2},
    "oracle":      {"dbms": 0.3, "java": 0.2},
    "amazon":      {"dsa": 0.3, "lld": 0.2},
    "others":      {},
}

# Weighted readiness formula per company.
# Missing companies default to READINESS_WEIGHTS.
COMPANY_READINESS_WEIGHTS = {
    "google":      {"dsa": 0.45, "hld": 0.20, "lld": 0.10, "java": 0.05, "operating_systems": 0.07, "dbms": 0.07, "computer_networks": 0.06},
    "microsoft":   {"dsa": 0.35, "lld": 0.20, "hld": 0.15, "java": 0.10, "operating_systems": 0.07, "dbms": 0.07, "computer_networks": 0.06},
    "amazon":      {"dsa": 0.40, "lld": 0.20, "hld": 0.15, "java": 0.05, "operating_systems": 0.07, "dbms": 0.07, "computer_networks": 0.06},
    "adobe":       {"dsa": 0.30, "lld": 0.25, "hld": 0.10, "java": 0.15, "operating_systems": 0.07, "dbms": 0.07, "computer_networks": 0.06},
    "atlassian":   {"dsa": 0.30, "lld": 0.25, "hld": 0.20, "java": 0.05, "operating_systems": 0.07, "dbms": 0.07, "computer_networks": 0.06},
    "stripe":      {"dsa": 0.30, "hld": 0.25, "java": 0.15, "lld": 0.10, "operating_systems": 0.07, "dbms": 0.07, "computer_networks": 0.06},
    "uber":        {"dsa": 0.30, "hld": 0.30, "lld": 0.10, "java": 0.05, "operating_systems": 0.07, "dbms": 0.10, "computer_networks": 0.08},
    "phonepe":     {"dsa": 0.30, "hld": 0.25, "lld": 0.15, "java": 0.05, "operating_systems": 0.07, "dbms": 0.10, "computer_networks": 0.08},
    "flipkart":    {"dsa": 0.35, "lld": 0.20, "hld": 0.15, "java": 0.05, "operating_systems": 0.08, "dbms": 0.10, "computer_networks": 0.07},
    "salesforce":  {"dsa": 0.20, "java": 0.25, "lld": 0.20, "hld": 0.10, "operating_systems": 0.08, "dbms": 0.10, "computer_networks": 0.07},
    "oracle":      {"dsa": 0.20, "java": 0.20, "dbms": 0.25, "lld": 0.10, "hld": 0.10, "operating_systems": 0.08, "computer_networks": 0.07},
    "linkedin":    {"dsa": 0.30, "hld": 0.25, "lld": 0.15, "java": 0.10, "operating_systems": 0.07, "dbms": 0.07, "computer_networks": 0.06},
}

DEFAULT_READINESS = {
    "dsa": 0.35, "java": 0.15, "lld": 0.15, "hld": 0.15,
    "operating_systems": 0.0667, "dbms": 0.0667, "computer_networks": 0.0666,
}


# --------------------- Helpers ---------------------

def today_date_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _seeded_random(user_id: str, ds: str) -> random.Random:
    h = hashlib.sha256(f"{user_id}:{ds}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def _pattern_from_subtopic(sub: str) -> Optional[str]:
    return SUBTOPIC_TO_PATTERN.get(sub)


def choose_focus_topic(
    onboarding: dict, knowledge: List[dict], target_companies: List[str], rng: random.Random,
) -> str:
    baseline = onboarding.get("self_assessment", {}) if onboarding else {}
    progress = {kp["topic"]: kp.get("score", 0.0) for kp in knowledge}
    weights = {}
    for t in TOPIC_KEYS:
        base = baseline.get(t, 5) * 10
        score = progress.get(t, base)
        weights[t] = max(0.0, 100.0 - score)
    for c in target_companies or []:
        for topic, bias in COMPANY_BIAS.get(c, {}).items():
            weights[topic] = weights.get(topic, 0) * (1 + bias)
    total = sum(weights.values()) or 1.0
    r = rng.random() * total
    acc = 0.0
    for t in TOPIC_KEYS:
        acc += weights[t]
        if r <= acc:
            return t
    return TOPIC_KEYS[0]


# --------------------- Adaptive analysis ---------------------

def analyze_recent_feedback(feedbacks: List[dict]) -> dict:
    """Summarize signals from recent feedback (last 24-48 hours worth).

    Returns:
      { avg_confidence, hint_ratio, timeout_ratio, weak_patterns [set], strong_patterns [set], failed_patterns [set] }
    """
    if not feedbacks:
        return {"avg_confidence": None, "hint_ratio": 0, "timeout_ratio": 0,
                "weak_patterns": set(), "strong_patterns": set(), "failed_patterns": set()}

    total = len(feedbacks)
    confs = [f["confidence"] for f in feedbacks]
    avg_conf = sum(confs) / total
    hints = sum(1 for f in feedbacks if f["solved_status"] in ("one_hint", "multi_hints"))
    fails = sum(1 for f in feedbacks if f["solved_status"] == "could_not_solve")

    weak, strong, failed = set(), set(), set()
    for f in feedbacks:
        low = f["confidence"] <= 4 or f["solved_status"] in ("multi_hints", "could_not_solve")
        high = f["confidence"] >= 8 and f["solved_status"] == "without_hints"
        if f["solved_status"] == "could_not_solve":
            failed.add(f["pattern"])
        if low:
            weak.add(f["pattern"])
        if high:
            strong.add(f["pattern"])

    return {
        "avg_confidence": avg_conf,
        "hint_ratio": hints / total,
        "timeout_ratio": fails / total,
        "weak_patterns": weak,
        "strong_patterns": strong,
        "failed_patterns": failed,
    }


def determine_mode(analysis: dict) -> str:
    """Return one of: 'revise', 'advance', 'continue'."""
    if not analysis["avg_confidence"]:
        return "continue"
    if analysis["failed_patterns"] or analysis["avg_confidence"] < 5 or analysis["hint_ratio"] > 0.5:
        return "revise"
    if analysis["avg_confidence"] >= 8 and analysis["hint_ratio"] < 0.2:
        return "advance"
    return "continue"


def prerequisite_revisions_for(pattern: str) -> List[Tuple[str, str]]:
    """Return list of (domain, subtopic) prerequisites for a pattern."""
    return PATTERN_PREREQUISITES.get(pattern, [])


def get_candidate_topics(topic: str) -> List[dict]:
    """Return roadmap-backed learning topics eligible within one track."""
    roadmap = get_roadmap()
    track = roadmap.get(topic)
    if not track:
        return []

    candidates = []
    for module in roadmap.children(track["id"]):
        candidates.extend(
            node for node in roadmap.children(module["id"])
            if node.get("type") == "topic"
        )
    return candidates


def rank_candidate_topics(
    candidates: List[dict],
    knowledge_nodes: Dict[str, dict],
    target_companies: List[str],
    rng: random.Random,
) -> dict:
    """Return the best learner-aware candidate, using RNG for exact ties."""
    roadmap = get_roadmap()

    def ranking_key(candidate: dict) -> tuple:
        progress = knowledge_nodes.get(candidate["id"], {})
        status = progress.get("status", "not_started")
        company_importance = sum(
            roadmap.company_importance(candidate["id"], str(company).lower())
            for company in target_companies
        )
        return (
            candidate.get("status") != "locked",
            -float(progress.get("confidence", 0.0)),
            float(progress.get("weakness_score", 0.0)),
            status not in ("completed", "mastered"),
            company_importance,
            -float(progress.get("mastery_percentage", 0.0)),
        )

    best_key = max(ranking_key(candidate) for candidate in candidates)
    tied_candidates = [
        candidate for candidate in candidates if ranking_key(candidate) == best_key
    ]
    return rng.choice(tied_candidates)


def select_primary_topic(
    onboarding: dict,
    knowledge: List[dict],
    target_companies: List[str],
    analysis: dict,
    mode: str,
    rng: random.Random,
    knowledge_nodes: Optional[Dict[str, dict]] = None,
) -> Tuple[str, str, str]:
    """Select the primary mission track, topic label, and base difficulty.

    The branch order and random draws intentionally match the original mission
    builder so this extraction is behavior-preserving.
    """
    if mode == "revise" and analysis["weak_patterns"]:
        weak_pattern = sorted(analysis["weak_patterns"])[0]
        domain, subtopic = PATTERN_TO_DOMAIN.get(weak_pattern, ("dsa", "Arrays"))
        return domain, subtopic, "easy"

    if mode == "advance" and analysis["strong_patterns"]:
        # Move to next challenging area of DSA (rotate through hard patterns)
        pattern_choice = rng.choice(["dp", "graphs", "backtracking", "heap"])
        domain, subtopic = PATTERN_TO_DOMAIN.get(pattern_choice, ("dsa", "Dynamic Programming"))
        return domain, subtopic, "hard"

    focus_topic = choose_focus_topic(onboarding, knowledge, target_companies, rng)
    candidate = rank_candidate_topics(
        get_candidate_topics(focus_topic),
        knowledge_nodes or {},
        target_companies,
        rng,
    )
    return focus_topic, candidate["label"], candidate.get("difficulty", "medium")


# --------------------- Mission builder V2 ---------------------

def build_mission_for_user(
    user_id: str,
    onboarding: dict,
    knowledge: List[dict],
    revisions_due: List[dict],
    recent_feedback: Optional[List[dict]] = None,
    extra_practice_count_yesterday: int = 0,
    ds: Optional[str] = None,
    knowledge_nodes: Optional[Dict[str, dict]] = None,
) -> tuple[DailyMission, dict]:
    """Return (mission, adjustment_meta). adjustment_meta describes adaptive decisions."""
    ds = ds or today_date_str()
    rng = _seeded_random(user_id, ds)

    target_companies = onboarding.get("target_companies", []) if onboarding else []
    daily_hours = float(onboarding.get("daily_study_hours", 2)) if onboarding else 2.0
    duration_minutes = int(round(daily_hours * 60))

    # Extra practice yesterday → increase intensity today.
    if extra_practice_count_yesterday >= 2:
        daily_hours = min(daily_hours + 0.5, 8.0)
        duration_minutes = int(round(daily_hours * 60))

    analysis = analyze_recent_feedback(recent_feedback or [])
    mode = determine_mode(analysis)

    focus_topic, subtopic, base_difficulty = select_primary_topic(
        onboarding, knowledge, target_companies, analysis, mode, rng, knowledge_nodes,
    )

    meta = TOPIC_META[focus_topic]

    # Nudge difficulty from experience
    position = (onboarding or {}).get("current_position", "0-1")
    if position in ("3-5", "5+") and base_difficulty == "easy":
        base_difficulty = "medium"

    # Practice count scales with hours
    if daily_hours >= 3:
        practice_count = 3
    elif daily_hours >= 1.5:
        practice_count = 2
    else:
        practice_count = 1

    tasks: List[MissionTask] = []
    inserted_prereqs: List[str] = []
    detected_weaknesses: List[str] = []

    # -------- Root cause: prerequisite revisions (only in revise mode) --------
    if mode == "revise" and analysis["weak_patterns"]:
        seen = set()
        for weak_p in sorted(analysis["weak_patterns"]):  # deterministic order
            for (pre_domain, pre_sub) in prerequisite_revisions_for(weak_p):
                key = (pre_domain, pre_sub)
                if key in seen:
                    continue
                seen.add(key)
                tasks.append(MissionTask(
                    title=f"Revise: {pre_sub} ({TOPIC_META[pre_domain]['label']})",
                    kind="revise",
                    topic=pre_domain,
                ))
                inserted_prereqs.append(f"{pre_domain}::{pre_sub}")
            detected_weaknesses.append(weak_p)
        # cap at 2 prereqs
        if len(tasks) > 2:
            tasks = tasks[:2]

    # -------- Primary task on focus topic --------
    pattern = _pattern_from_subtopic(subtopic)
    if focus_topic == "dsa" and pattern:
        # Real practice: coding problems attached (populated by route caller)
        tasks.append(MissionTask(
            title=f"Solve {practice_count} {subtopic} problems",
            kind="practice",
            topic=focus_topic,
            pattern=pattern,
            problem_count=practice_count,
        ))
    elif focus_topic in ("java", "lld", "hld"):
        tasks.append(MissionTask(
            title=f"Work through: {subtopic}",
            kind="practice",
            topic=focus_topic,
        ))
    else:
        tasks.append(MissionTask(
            title=f"Deep-dive: {subtopic}",
            kind="study",
            topic=focus_topic,
        ))

    # Supporting study task
    support_pool = [t for t in TOPIC_KEYS if t != focus_topic]
    support_topic = rng.choice(support_pool)
    support_meta = TOPIC_META[support_topic]
    support_sub, _ = rng.choice(support_meta["subtopics"])
    tasks.append(MissionTask(
        title=f"Study {support_meta['label']} · {support_sub}",
        kind="study",
        topic=support_topic,
    ))

    if daily_hours >= 3:
        core_topic = rng.choice(["operating_systems", "dbms", "computer_networks"])
        core_meta = TOPIC_META[core_topic]
        core_sub, _ = rng.choice(core_meta["subtopics"])
        tasks.append(MissionTask(
            title=f"Read: {core_meta['label']} · {core_sub}",
            kind="study",
            topic=core_topic,
        ))

    # Revision tasks (from spaced-repetition queue)
    revision_task_ids: List[str] = []
    for rev in revisions_due[:2]:
        rt = MissionTask(
            title=f"Revise: {rev['task_title']}",
            kind="revise",
            topic=rev["topic"],
        )
        tasks.append(rt)
        revision_task_ids.append(rt.id)

    if mode == "revise":
        title = f"Consolidate {subtopic}"
        objective = (
            f"Yesterday's signals showed weak spots — reinforce fundamentals of "
            f"{subtopic} and its prerequisites before advancing."
        )
    elif mode == "advance":
        title = f"Advance: {subtopic}"
        objective = (
            f"Strong performance yesterday. Push into {subtopic} at hard difficulty "
            f"to build interview-grade depth."
        )
    else:
        title = f"Focus on {subtopic}"
        objective = (
            f"Strengthen your {meta['label']} baseline via {subtopic}. "
            f"Consolidate with a supporting {support_meta['label']} concept."
        )

    mission = DailyMission(
        user_id=user_id,
        date=ds,
        title=title,
        focus_area=f"{meta['label']} · {subtopic}",
        focus_topic=focus_topic,
        difficulty=base_difficulty,
        estimated_duration_minutes=duration_minutes,
        learning_objective=objective,
        tasks=tasks,
        revision_task_ids=revision_task_ids,
    )

    adjustment = {
        "mode": mode,
        "reason": _mode_reason(mode, analysis, extra_practice_count_yesterday),
        "detected_weaknesses": detected_weaknesses,
        "inserted_prerequisites": inserted_prereqs,
        "advance": mode == "advance",
    }
    return mission, adjustment


def _mode_reason(mode: str, analysis: dict, extra: int) -> str:
    if mode == "revise":
        return (
            f"Detected weak signals (avg confidence "
            f"{round(analysis['avg_confidence'] or 0, 1)}, "
            f"hint ratio {int(analysis['hint_ratio']*100)}%). "
            f"Inserted prerequisite revisions before advancing."
        )
    if mode == "advance":
        return (
            f"Strong performance yesterday (avg confidence "
            f"{round(analysis['avg_confidence'] or 0, 1)}). "
            f"Progressing into harder patterns."
        )
    if extra >= 2:
        return "Extra practice yesterday — extended today's mission."
    return "Standard progression from baseline."


# --------------------- Spaced repetition ---------------------

REVISION_STAGES_DAYS = [1, 3, 7, 14, 30, 60]


def confidence_modifier_days(confidence: int) -> float:
    """Adjust default interval based on confidence 1-10."""
    if confidence <= 3:
        return 0.4  # revise much sooner
    if confidence <= 5:
        return 0.7
    if confidence >= 9:
        return 1.5  # can wait longer
    if confidence >= 7:
        return 1.2
    return 1.0


def schedule_next_revision(current_stage: int, confidence: int = 6) -> tuple[int, str]:
    """Return (next_stage, next_date_str)."""
    next_stage = min(current_stage + 1, len(REVISION_STAGES_DAYS) - 1)
    days = REVISION_STAGES_DAYS[next_stage] * confidence_modifier_days(confidence)
    days = max(1, round(days))
    d = (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()
    return next_stage, d


def first_revision_date(confidence: int = 6) -> str:
    days = REVISION_STAGES_DAYS[0] * confidence_modifier_days(confidence)
    days = max(1, round(days))
    return (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()


# --------------------- Interview readiness ---------------------

def compute_readiness(knowledge: List[dict], onboarding: dict) -> float:
    baseline = (onboarding or {}).get("self_assessment", {})
    by_topic = {kp["topic"]: kp.get("score", 0.0) for kp in knowledge}
    total = 0.0
    for t, w in DEFAULT_READINESS.items():
        score = by_topic.get(t)
        if score is None:
            score = baseline.get(t, 5) * 10
        total += w * score
    return round(min(max(total, 0.0), 100.0), 1)


def compute_company_readiness(company_id: str, knowledge: List[dict], onboarding: dict) -> float:
    weights = COMPANY_READINESS_WEIGHTS.get(company_id, DEFAULT_READINESS)
    baseline = (onboarding or {}).get("self_assessment", {})
    by_topic = {kp["topic"]: kp.get("score", 0.0) for kp in knowledge}
    total = 0.0
    for t, w in weights.items():
        score = by_topic.get(t)
        if score is None:
            score = baseline.get(t, 5) * 10
        total += w * score
    return round(min(max(total, 0.0), 100.0), 1)


# --------------------- Streak ---------------------

def update_streak_on_completion(streak: Optional[dict]) -> dict:
    today = today_date_str()
    yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    if not streak:
        return {"current_streak": 1, "longest_streak": 1,
                "last_active_date": today,
                "updated_at": datetime.now(timezone.utc).isoformat()}
    if streak.get("last_active_date") == today:
        return streak
    current = streak.get("current_streak", 0)
    if streak.get("last_active_date") == yesterday:
        current += 1
    else:
        current = 1
    longest = max(streak.get("longest_streak", 0), current)
    return {"current_streak": current, "longest_streak": longest,
            "last_active_date": today,
            "updated_at": datetime.now(timezone.utc).isoformat()}


def streak_days_grid(streak: Optional[dict]) -> List[bool]:
    if not streak or not streak.get("last_active_date"):
        return [False] * 7
    last_active = date_cls.fromisoformat(streak["last_active_date"])
    today = datetime.now(timezone.utc).date()
    result = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        start = last_active - timedelta(days=streak.get("current_streak", 0) - 1)
        active = start <= d <= last_active
        result.append(active)
    return result


# --------------------- Knowledge gain ---------------------

def apply_knowledge_gain(current_score: float, difficulty: str, kind: str) -> float:
    base = {"easy": 1.2, "medium": 2.0, "hard": 2.8}[difficulty]
    mult = {"practice": 1.0, "study": 0.6, "revise": 1.4}[kind]
    return round(min(current_score + base * mult, 100.0), 2)


def apply_feedback_gain(current_score: float, confidence: int, solved_status: str) -> float:
    """Bigger gains when solved cleanly; smaller when hints were needed."""
    base = 3.5
    status_mult = {"without_hints": 1.0, "one_hint": 0.7,
                   "multi_hints": 0.35, "could_not_solve": 0.1}[solved_status]
    conf_mult = 0.5 + (confidence / 10.0)  # 0.6 → 1.5
    delta = base * status_mult * conf_mult
    return round(min(current_score + delta, 100.0), 2)
