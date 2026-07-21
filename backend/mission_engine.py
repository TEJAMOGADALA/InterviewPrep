"""Mission Engine V1.

Deterministic daily mission generation based on user's onboarding data +
current knowledge progress. Also handles activity logging, streaks, spaced
repetition and interview readiness computation.
"""
import hashlib
import random
from datetime import datetime, timezone, timedelta, date as date_cls
from typing import List, Optional

from models import (
    DailyMission, MissionTask, KnowledgeProgress, StudyStreak,
    RevisionItem, ActivityEvent, TOPIC_KEYS,
)


# --------------------- Content library ---------------------
TOPIC_META = {
    "dsa": {
        "label": "DSA",
        "subtopics": [
            ("Sliding Window", "medium"),
            ("Two Pointers", "easy"),
            ("Dynamic Programming", "hard"),
            ("Trees & Recursion", "medium"),
            ("Graphs · BFS & DFS", "medium"),
            ("Heaps & Priority Queues", "medium"),
            ("Backtracking", "hard"),
            ("Binary Search", "medium"),
        ],
        "practice_verb": "Solve",
        "practice_unit": "problems",
    },
    "java": {
        "label": "Java",
        "subtopics": [
            ("Collections Framework", "easy"),
            ("HashMap Internals", "medium"),
            ("Concurrency & Threads", "hard"),
            ("Streams & Lambdas", "medium"),
            ("JVM Memory Model", "hard"),
        ],
        "practice_verb": "Implement",
        "practice_unit": "exercises",
    },
    "lld": {
        "label": "LLD",
        "subtopics": [
            ("SOLID Principles", "medium"),
            ("Design Patterns · Factory", "medium"),
            ("Observer Pattern", "medium"),
            ("Design a Parking Lot", "medium"),
            ("Design a Chess Game", "hard"),
        ],
        "practice_verb": "Model",
        "practice_unit": "design",
    },
    "hld": {
        "label": "HLD",
        "subtopics": [
            ("URL Shortener", "medium"),
            ("Rate Limiter", "hard"),
            ("News Feed", "hard"),
            ("Chat Application", "hard"),
            ("CDN Design", "medium"),
        ],
        "practice_verb": "Sketch",
        "practice_unit": "system design",
    },
    "operating_systems": {
        "label": "Operating Systems",
        "subtopics": [
            ("Deadlocks", "medium"),
            ("Process Scheduling", "medium"),
            ("Memory Paging", "medium"),
            ("Semaphores & Mutex", "hard"),
        ],
        "practice_verb": "Study",
        "practice_unit": "concept",
    },
    "dbms": {
        "label": "DBMS",
        "subtopics": [
            ("Transactions & ACID", "medium"),
            ("Indexing Strategies", "medium"),
            ("Normalization", "easy"),
            ("Concurrency Control", "hard"),
        ],
        "practice_verb": "Study",
        "practice_unit": "concept",
    },
    "computer_networks": {
        "label": "Computer Networks",
        "subtopics": [
            ("TCP Handshake", "medium"),
            ("HTTP & HTTPS", "easy"),
            ("DNS Resolution", "easy"),
            ("Load Balancing", "medium"),
        ],
        "practice_verb": "Study",
        "practice_unit": "concept",
    },
}

DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3}

# Company weighting bias — how much extra weight to add to each topic per company.
COMPANY_BIAS = {
    "google":      {"dsa": 0.3, "hld": 0.2},
    "microsoft":   {"dsa": 0.25, "lld": 0.2},
    "uber":        {"hld": 0.3, "dsa": 0.15},
    "adobe":       {"lld": 0.25, "dsa": 0.2},
    "atlassian":   {"lld": 0.25, "hld": 0.15},
    "linkedin":    {"hld": 0.25, "dsa": 0.15},
    "stripe":      {"hld": 0.25, "dsa": 0.2},
    "salesforce":  {"java": 0.2, "lld": 0.2},
    "phonepe":     {"hld": 0.2, "dsa": 0.2},
    "flipkart":    {"dsa": 0.25, "lld": 0.2},
    "oracle":      {"dbms": 0.3, "java": 0.2},
    "others":      {},
}


# --------------------- Helpers ---------------------

def today_date_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _seeded_random(user_id: str, ds: str) -> random.Random:
    """Deterministic RNG per (user, date) so today's mission is stable."""
    h = hashlib.sha256(f"{user_id}:{ds}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def choose_focus_topic(
    onboarding: dict, knowledge: List[dict], target_companies: List[str], rng: random.Random,
) -> str:
    """Pick the topic that most needs attention.

    Weight = (10 - normalized_score) + company_bias. Higher = more urgent.
    """
    baseline = onboarding.get("self_assessment", {}) if onboarding else {}
    progress_by_topic = {kp["topic"]: kp.get("score", 0.0) for kp in knowledge}

    weights = {}
    for t in TOPIC_KEYS:
        # Normalize self-assessment (1-10) to 0-100
        base = baseline.get(t, 5) * 10
        score = progress_by_topic.get(t, base)  # if no progress yet, use baseline
        urgency = max(0.0, 100.0 - score)
        weights[t] = urgency

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


def build_mission_for_user(
    user_id: str,
    onboarding: dict,
    knowledge: List[dict],
    revisions_due: List[dict],
    ds: Optional[str] = None,
) -> DailyMission:
    ds = ds or today_date_str()
    rng = _seeded_random(user_id, ds)

    target_companies = onboarding.get("target_companies", []) if onboarding else []
    daily_hours = float(onboarding.get("daily_study_hours", 2)) if onboarding else 2.0
    duration_minutes = int(round(daily_hours * 60))

    focus_topic = choose_focus_topic(onboarding, knowledge, target_companies, rng)
    meta = TOPIC_META[focus_topic]
    subtopic, base_difficulty = rng.choice(meta["subtopics"])

    # Nudge difficulty from experience level
    position = (onboarding or {}).get("current_position", "0-1")
    if position in ("3-5", "5+") and base_difficulty == "easy":
        base_difficulty = "medium"

    # Practice count scales with hours
    practice_count = 3 if daily_hours >= 3 else 2 if daily_hours >= 1.5 else 1

    tasks: List[MissionTask] = []

    # Primary practice task on focus topic
    if focus_topic in ("dsa", "java", "lld", "hld"):
        tasks.append(MissionTask(
            title=f"{meta['practice_verb']} {practice_count} {subtopic} {meta['practice_unit']}",
            kind="practice",
            topic=focus_topic,
        ))
    else:
        tasks.append(MissionTask(
            title=f"Deep-dive: {subtopic}",
            kind="study",
            topic=focus_topic,
        ))

    # Secondary study task on a supporting topic (rotate)
    support_pool = [t for t in TOPIC_KEYS if t != focus_topic]
    support_topic = rng.choice(support_pool)
    support_meta = TOPIC_META[support_topic]
    support_sub, _ = rng.choice(support_meta["subtopics"])
    tasks.append(MissionTask(
        title=f"Study {support_meta['label']} · {support_sub}",
        kind="study",
        topic=support_topic,
    ))

    # Optional tertiary reading if enough hours
    if daily_hours >= 3:
        core_topic = rng.choice(["operating_systems", "dbms", "computer_networks"])
        core_meta = TOPIC_META[core_topic]
        core_sub, _ = rng.choice(core_meta["subtopics"])
        tasks.append(MissionTask(
            title=f"Read: {core_meta['label']} · {core_sub}",
            kind="study",
            topic=core_topic,
        ))

    # Revision tasks (up to 2 due items)
    revision_task_ids: List[str] = []
    for rev in revisions_due[:2]:
        rt = MissionTask(
            title=f"Revise: {rev['task_title']}",
            kind="revise",
            topic=rev["topic"],
        )
        tasks.append(rt)
        revision_task_ids.append(rt.id)

    title = f"Focus on {subtopic}"
    objective = (
        f"Strengthen your {meta['label']} baseline by working through "
        f"{subtopic}. Consolidate with a supporting {support_meta['label']} concept."
    )

    return DailyMission(
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


# --------------------- Spaced repetition ---------------------

REVISION_STAGES_DAYS = [1, 3, 7, 14, 30]


def schedule_next_revision(current_stage: int) -> tuple[int, str]:
    """Return (next_stage, next_date_str). If already at final stage, cap it."""
    next_stage = min(current_stage + 1, len(REVISION_STAGES_DAYS) - 1)
    days = REVISION_STAGES_DAYS[next_stage]
    d = (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()
    return next_stage, d


def first_revision_date() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=REVISION_STAGES_DAYS[0])).date().isoformat()


# --------------------- Interview readiness ---------------------

READINESS_WEIGHTS = {
    "dsa": 0.35,
    "java": 0.15,
    "lld": 0.15,
    "hld": 0.15,
    "operating_systems": 0.0667,
    "dbms": 0.0667,
    "computer_networks": 0.0666,
}


def compute_readiness(knowledge: List[dict], onboarding: dict) -> float:
    baseline = (onboarding or {}).get("self_assessment", {})
    by_topic = {kp["topic"]: kp.get("score", 0.0) for kp in knowledge}
    total = 0.0
    for t, w in READINESS_WEIGHTS.items():
        score = by_topic.get(t)
        if score is None:
            # No progress recorded → use baseline as starting point
            score = baseline.get(t, 5) * 10
        total += w * score
    return round(min(max(total, 0.0), 100.0), 1)


# --------------------- Streak ---------------------

def update_streak_on_completion(streak: Optional[dict]) -> dict:
    today = today_date_str()
    yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    if not streak:
        return {
            "current_streak": 1,
            "longest_streak": 1,
            "last_active_date": today,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    if streak.get("last_active_date") == today:
        return streak  # already counted
    current = streak.get("current_streak", 0)
    if streak.get("last_active_date") == yesterday:
        current += 1
    else:
        current = 1
    longest = max(streak.get("longest_streak", 0), current)
    return {
        "current_streak": current,
        "longest_streak": longest,
        "last_active_date": today,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def streak_days_grid(streak: Optional[dict]) -> List[bool]:
    """Return last 7 days as bool (True if active). Deterministic from last_active_date + current_streak."""
    if not streak or not streak.get("last_active_date"):
        return [False] * 7
    last_active = date_cls.fromisoformat(streak["last_active_date"])
    today = datetime.now(timezone.utc).date()
    result = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        # active if within [last_active - (streak-1), last_active]
        start = last_active - timedelta(days=streak.get("current_streak", 0) - 1)
        active = start <= d <= last_active
        result.append(active)
    return result


# --------------------- Knowledge progress update ---------------------

def apply_knowledge_gain(current_score: float, difficulty: str, kind: str) -> float:
    """Small gain per task completion. Practice/hard gives more."""
    base = {"easy": 1.2, "medium": 2.0, "hard": 2.8}[difficulty]
    mult = {"practice": 1.0, "study": 0.6, "revise": 1.4}[kind]
    gain = base * mult
    return round(min(current_score + gain, 100.0), 2)
