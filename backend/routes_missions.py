"""Mission + Dashboard + Coding Arena + Feedback + Knowledge tree routes."""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_current_user
from models import (
    DailyMission, MissionTask, KnowledgeProgress, StudyStreak,
    RevisionItem, ActivityEvent, TOPIC_KEYS, OnboardingPatch, OnboardingRecord,
    ProblemAssignment, ProblemFeedbackPayload, ProblemFeedback, MissionAdjustment,
    WeaknessRecord,
)
from mission_engine import (
    build_mission_for_user, today_date_str, schedule_next_revision,
    first_revision_date, compute_readiness, compute_company_readiness,
    update_streak_on_completion, streak_days_grid, apply_knowledge_gain,
    apply_feedback_gain, TOPIC_META, COMPANY_READINESS_WEIGHTS,
    determine_mode, analyze_recent_feedback,
)
from problem_bank import (
    PROBLEMS, PATTERN_TO_DOMAIN, pattern_counts, problems_by_pattern,
    problem_by_id,
)

router = APIRouter(prefix="/api", tags=["missions"])


def _clean(doc: dict) -> dict:
    if doc:
        doc.pop("_id", None)
    return doc


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _log_activity(db, user_id: str, kind: str, title: str, description: str = None):
    ev = ActivityEvent(user_id=user_id, kind=kind, title=title, description=description)
    await db.activity_events.insert_one(ev.model_dump())


async def _get_streak(db, user_id: str) -> Optional[dict]:
    doc = await db.study_streaks.find_one({"user_id": user_id})
    return _clean(doc) if doc else None


async def _upsert_streak_on_completion(db, user_id: str) -> dict:
    existing = await _get_streak(db, user_id)
    updated_fields = update_streak_on_completion(existing)
    await db.study_streaks.update_one(
        {"user_id": user_id},
        {"$set": {**updated_fields, "user_id": user_id}},
        upsert=True,
    )
    return await _get_streak(db, user_id)


async def _get_onboarding(db, user_id: str) -> Optional[dict]:
    return _clean(await db.onboarding.find_one({"user_id": user_id}))


async def _get_knowledge(db, user_id: str) -> list:
    cur = db.knowledge_progress.find({"user_id": user_id}, {"_id": 0})
    return await cur.to_list(length=100)


async def _get_due_revisions(db, user_id: str) -> list:
    today = today_date_str()
    cur = db.revisions.find(
        {"user_id": user_id, "completed": False, "next_review_date": {"$lte": today}},
        {"_id": 0},
    ).sort("next_review_date", 1)
    return await cur.to_list(length=20)


async def _get_recent_feedback(db, user_id: str, hours: int = 48) -> list:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    cur = db.problem_feedback.find(
        {"user_id": user_id, "submitted_at": {"$gte": since}}, {"_id": 0},
    ).sort("submitted_at", -1).limit(50)
    return await cur.to_list(length=50)


async def _count_extra_practice_yesterday(db, user_id: str) -> int:
    y = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    return await db.problem_assignments.count_documents({
        "user_id": user_id,
        "source": "practice_more",
        "assigned_at": {"$gte": f"{y}T00:00:00", "$lt": f"{y}T23:59:59"},
    })


async def _attach_problems_to_mission(db, mission: DailyMission) -> None:
    """For any practice task with `pattern`, create ProblemAssignment records."""
    for task in mission.tasks:
        if task.kind != "practice" or not task.pattern:
            continue
        count = task.problem_count or 2
        # Pick unseen problems for user in this pattern
        seen_ids = set()
        cur = db.problem_assignments.find(
            {"user_id": mission.user_id, "pattern": task.pattern}, {"problem_id": 1, "_id": 0}
        )
        async for row in cur:
            seen_ids.add(row["problem_id"])
        pool = [p for p in problems_by_pattern(task.pattern) if p["id"] not in seen_ids]
        if not pool:
            # fall back to entire pool
            pool = problems_by_pattern(task.pattern)
        chosen = pool[:count]
        for p in chosen:
            assignment = ProblemAssignment(
                user_id=mission.user_id, problem_id=p["id"],
                mission_id=mission.id, pattern=task.pattern, source="mission",
            )
            await db.problem_assignments.insert_one(assignment.model_dump())


async def _generate_today_mission(db, user_id: str) -> DailyMission:
    onboarding = await _get_onboarding(db, user_id)
    if not onboarding:
        raise HTTPException(status_code=400, detail="Complete onboarding to generate missions.")
    knowledge = await _get_knowledge(db, user_id)
    revisions_due = await _get_due_revisions(db, user_id)
    recent_feedback = await _get_recent_feedback(db, user_id, hours=36)
    extra_yesterday = await _count_extra_practice_yesterday(db, user_id)

    mission, adjustment = build_mission_for_user(
        user_id, onboarding, knowledge, revisions_due,
        recent_feedback=recent_feedback,
        extra_practice_count_yesterday=extra_yesterday,
    )
    await db.daily_missions.insert_one(mission.model_dump())
    await _attach_problems_to_mission(db, mission)

    # Persist adjustment (adaptive audit trail)
    adj = MissionAdjustment(
        user_id=user_id, for_date=mission.date,
        reason=adjustment["reason"],
        detected_weaknesses=adjustment["detected_weaknesses"],
        inserted_prerequisites=adjustment["inserted_prerequisites"],
        advance=adjustment["advance"],
    )
    await db.mission_adjustments.insert_one(adj.model_dump())

    await _log_activity(
        db, user_id, "mission_generated",
        f"Today's mission: {mission.title}",
        description=mission.focus_area,
    )
    return mission


# ============ Today's Mission ============

@router.get("/missions/today", response_model=DailyMission)
async def get_todays_mission(user=Depends(get_current_user)):
    from server import db
    today = today_date_str()
    doc = await db.daily_missions.find_one({"user_id": user["id"], "date": today})
    if doc:
        return DailyMission(**_clean(doc))
    return await _generate_today_mission(db, user["id"])


# ============ Task toggle (replaces one-way complete) ============

@router.post("/missions/{mission_id}/tasks/{task_id}/toggle", response_model=DailyMission)
async def toggle_task(mission_id: str, task_id: str, user=Depends(get_current_user)):
    from server import db
    doc = await db.daily_missions.find_one({"id": mission_id, "user_id": user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Mission not found")
    if doc["status"] == "skipped":
        raise HTTPException(status_code=400, detail="Mission was skipped.")

    task = next((t for t in doc["tasks"] if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["completed"]:
        # UNCHECK — reverse
        task["completed"] = False
        task["completed_at"] = None
        # If mission was marked completed, revert to in_progress
        new_status = "in_progress" if doc["status"] == "completed" else doc["status"]
        await db.daily_missions.update_one(
            {"id": mission_id},
            {"$set": {"tasks": doc["tasks"], "status": new_status, "completed_at": None}},
        )
        await _log_activity(db, user["id"], "task_uncompleted", f"Uncompleted: {task['title']}")
    else:
        # CHECK — mark complete + knowledge gain + spaced repetition
        task["completed"] = True
        task["completed_at"] = _now_iso()

        onboarding = await _get_onboarding(db, user["id"])
        baseline_score = (onboarding or {}).get("self_assessment", {}).get(task["topic"], 5) * 10
        kp = await db.knowledge_progress.find_one({"user_id": user["id"], "topic": task["topic"]})
        current = float(kp["score"]) if kp else float(baseline_score)
        new_score = apply_knowledge_gain(current, doc["difficulty"], task["kind"])
        await db.knowledge_progress.update_one(
            {"user_id": user["id"], "topic": task["topic"]},
            {"$set": {
                "user_id": user["id"], "topic": task["topic"],
                "score": new_score,
                "completions": (kp.get("completions", 0) if kp else 0) + 1,
                "last_updated": _now_iso(),
            }},
            upsert=True,
        )

        if task["kind"] != "revise":
            rev = RevisionItem(
                user_id=user["id"], task_title=task["title"], topic=task["topic"],
                stage=0, next_review_date=first_revision_date(),
            )
            await db.revisions.insert_one(rev.model_dump())
        else:
            existing = await db.revisions.find_one({
                "user_id": user["id"], "topic": task["topic"], "completed": False,
            })
            if existing:
                next_stage, next_date = schedule_next_revision(existing.get("stage", 0))
                await db.revisions.update_one(
                    {"id": existing["id"]},
                    {"$set": {"stage": next_stage, "next_review_date": next_date}},
                )

        await db.daily_missions.update_one(
            {"id": mission_id}, {"$set": {"tasks": doc["tasks"]}},
        )
        await _log_activity(db, user["id"], "task_completed", f"Completed: {task['title']}")

    updated = await db.daily_missions.find_one({"id": mission_id})
    return DailyMission(**_clean(updated))


# Backwards-compat one-way complete (kept for API stability)
@router.post("/missions/{mission_id}/tasks/{task_id}/complete", response_model=DailyMission)
async def complete_task(mission_id: str, task_id: str, user=Depends(get_current_user)):
    return await toggle_task(mission_id, task_id, user)


# ============ Mission complete / skip ============

@router.post("/missions/{mission_id}/complete", response_model=DailyMission)
async def complete_mission(mission_id: str, user=Depends(get_current_user)):
    from server import db
    doc = await db.daily_missions.find_one({"id": mission_id, "user_id": user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Mission not found")
    if doc["status"] == "completed":
        return DailyMission(**_clean(doc))

    now = _now_iso()
    onboarding = await _get_onboarding(db, user["id"])
    baseline = (onboarding or {}).get("self_assessment", {})
    for t in doc["tasks"]:
        if not t["completed"]:
            t["completed"] = True
            t["completed_at"] = now
            kp = await db.knowledge_progress.find_one({"user_id": user["id"], "topic": t["topic"]})
            baseline_score = baseline.get(t["topic"], 5) * 10
            current = float(kp["score"]) if kp else float(baseline_score)
            new_score = apply_knowledge_gain(current, doc["difficulty"], t["kind"])
            await db.knowledge_progress.update_one(
                {"user_id": user["id"], "topic": t["topic"]},
                {"$set": {"user_id": user["id"], "topic": t["topic"],
                          "score": new_score,
                          "completions": (kp.get("completions", 0) if kp else 0) + 1,
                          "last_updated": now}},
                upsert=True,
            )

    await db.daily_missions.update_one(
        {"id": mission_id},
        {"$set": {"status": "completed", "completed_at": now, "tasks": doc["tasks"]}},
    )
    await _upsert_streak_on_completion(db, user["id"])
    await _log_activity(
        db, user["id"], "mission_completed",
        f"Mission completed: {doc['title']}", description=doc["focus_area"],
    )
    updated = await db.daily_missions.find_one({"id": mission_id})
    return DailyMission(**_clean(updated))


@router.post("/missions/{mission_id}/skip", response_model=DailyMission)
async def skip_mission(mission_id: str, user=Depends(get_current_user)):
    from server import db
    doc = await db.daily_missions.find_one({"id": mission_id, "user_id": user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Mission not found")
    if doc["status"] != "in_progress":
        return DailyMission(**_clean(doc))
    now = _now_iso()
    await db.daily_missions.update_one(
        {"id": mission_id}, {"$set": {"status": "skipped", "skipped_at": now}},
    )
    await _log_activity(
        db, user["id"], "mission_skipped",
        f"Mission skipped: {doc['title']}", description=doc["focus_area"],
    )
    updated = await db.daily_missions.find_one({"id": mission_id})
    return DailyMission(**_clean(updated))


# ============ History ============

@router.get("/missions/history")
async def get_mission_history(limit: int = 20, user=Depends(get_current_user)):
    from server import db
    cur = db.daily_missions.find({"user_id": user["id"]}, {"_id": 0}).sort("date", -1).limit(limit)
    docs = await cur.to_list(length=limit)
    return [DailyMission(**d) for d in docs]


# ============ Revisions / Activity ============

@router.get("/revisions/queue")
async def get_revision_queue(user=Depends(get_current_user)):
    from server import db
    today = today_date_str()
    cur = db.revisions.find({"user_id": user["id"], "completed": False}, {"_id": 0}).sort("next_review_date", 1).limit(20)
    items = await cur.to_list(length=20)
    for it in items:
        it["is_due"] = it["next_review_date"] <= today
    return items


@router.get("/activity")
async def get_activity(limit: int = 20, user=Depends(get_current_user)):
    from server import db
    cur = db.activity_events.find({"user_id": user["id"]}, {"_id": 0}).sort("ts", -1).limit(limit)
    return await cur.to_list(length=limit)


# ============ Coding Arena ============

@router.get("/problems/patterns")
async def get_pattern_catalog():
    counts = pattern_counts()
    result = []
    for pattern, count in counts.items():
        domain, label = PATTERN_TO_DOMAIN.get(pattern, ("dsa", pattern))
        result.append({
            "pattern": pattern,
            "label": label,
            "domain": domain,
            "count": count,
        })
    result.sort(key=lambda x: -x["count"])
    return result


@router.get("/problems/{problem_id}")
async def get_problem(problem_id: str, user=Depends(get_current_user)):
    p = problem_by_id(problem_id)
    if not p:
        raise HTTPException(status_code=404, detail="Problem not found")
    return p


@router.get("/coding-arena")
async def get_coding_arena(user=Depends(get_current_user)):
    """Returns today's mission problems + user's active pattern + recent history."""
    from server import db
    today = today_date_str()

    # Today's mission
    mission_doc = await db.daily_missions.find_one({"user_id": user["id"], "date": today})
    if not mission_doc:
        # generate on demand
        await _generate_today_mission(db, user["id"])
        mission_doc = await db.daily_missions.find_one({"user_id": user["id"], "date": today})

    mission = DailyMission(**_clean(mission_doc))

    # Assignments for today's mission
    cur = db.problem_assignments.find(
        {"user_id": user["id"], "mission_id": mission.id}, {"_id": 0},
    )
    assignments = await cur.to_list(length=50)

    # Determine primary pattern (first DSA practice task)
    primary_pattern = None
    for t in mission.tasks:
        if t.kind == "practice" and t.pattern:
            primary_pattern = t.pattern
            break

    # Feedback lookup
    fb_cur = db.problem_feedback.find(
        {"user_id": user["id"]}, {"_id": 0},
    ).sort("submitted_at", -1)
    all_feedback = await fb_cur.to_list(length=200)
    fb_by_assignment = {}
    for f in all_feedback:
        if f.get("assignment_id"):
            fb_by_assignment[f["assignment_id"]] = f

    # Enrich assignments with problem detail + feedback
    enriched = []
    for a in assignments:
        p = problem_by_id(a["problem_id"])
        if not p:
            continue
        enriched.append({
            **a,
            "problem": p,
            "feedback": fb_by_assignment.get(a["id"]),
        })
    # Sort: unsolved first, then solved
    enriched.sort(key=lambda x: (x["status"] == "solved", x.get("assigned_at", "")))

    # Recent history (last 15 solved/attempted)
    hist_cur = db.problem_assignments.find(
        {"user_id": user["id"], "status": {"$in": ["solved", "attempted"]}}, {"_id": 0},
    ).sort("completed_at", -1).limit(15)
    history_raw = await hist_cur.to_list(length=15)
    history = []
    for h in history_raw:
        p = problem_by_id(h["problem_id"])
        if not p:
            continue
        history.append({**h, "problem": p, "feedback": fb_by_assignment.get(h["id"])})

    return {
        "mission": mission.model_dump(),
        "primary_pattern": primary_pattern,
        "primary_pattern_label": PATTERN_TO_DOMAIN.get(primary_pattern, ("dsa", primary_pattern or "Practice"))[1] if primary_pattern else None,
        "assignments": enriched,
        "history": history,
    }


@router.post("/coding-arena/practice-more")
async def practice_more(payload: dict, user=Depends(get_current_user)):
    """Pick next unseen problem in given (or today's primary) pattern."""
    from server import db
    pattern = payload.get("pattern")
    today = today_date_str()
    mission_doc = await db.daily_missions.find_one({"user_id": user["id"], "date": today})
    if not mission_doc:
        raise HTTPException(status_code=400, detail="No active mission.")
    mission = DailyMission(**_clean(mission_doc))

    if not pattern:
        # infer from today's mission primary DSA task
        for t in mission.tasks:
            if t.kind == "practice" and t.pattern:
                pattern = t.pattern
                break
    if not pattern:
        raise HTTPException(status_code=400, detail="No pattern specified and none inferable.")

    seen_ids = set()
    cur = db.problem_assignments.find(
        {"user_id": user["id"], "pattern": pattern}, {"problem_id": 1, "_id": 0},
    )
    async for row in cur:
        seen_ids.add(row["problem_id"])
    pool = [p for p in problems_by_pattern(pattern) if p["id"] not in seen_ids]
    if not pool:
        raise HTTPException(status_code=404, detail="You've seen every problem in this pattern.")
    chosen = pool[0]

    assignment = ProblemAssignment(
        user_id=user["id"], problem_id=chosen["id"],
        mission_id=mission.id, pattern=pattern, source="practice_more",
    )
    await db.problem_assignments.insert_one(assignment.model_dump())
    await _log_activity(
        db, user["id"], "practice_more",
        f"Extra practice: {chosen['title']}", description=pattern,
    )
    return {"assignment": assignment.model_dump(), "problem": chosen}


@router.post("/coding-arena/assignments/{assignment_id}/feedback")
async def submit_problem_feedback(
    assignment_id: str, payload: ProblemFeedbackPayload, user=Depends(get_current_user),
):
    from server import db
    a = await db.problem_assignments.find_one({"id": assignment_id, "user_id": user["id"]})
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")

    fb = ProblemFeedback(
        user_id=user["id"], problem_id=a["problem_id"],
        assignment_id=assignment_id, mission_id=a.get("mission_id"),
        pattern=a["pattern"], **payload.model_dump(),
    )
    await db.problem_feedback.insert_one(fb.model_dump())

    # Update assignment status
    new_status = "solved" if payload.solved_status != "could_not_solve" else "attempted"
    await db.problem_assignments.update_one(
        {"id": assignment_id},
        {"$set": {"status": new_status, "completed_at": _now_iso(), "notes": payload.notes}},
    )

    # Update knowledge progress based on feedback
    p = problem_by_id(a["problem_id"])
    if p:
        domain, _ = PATTERN_TO_DOMAIN.get(p["pattern"], ("dsa", ""))
        onboarding = await _get_onboarding(db, user["id"])
        baseline_score = (onboarding or {}).get("self_assessment", {}).get(domain, 5) * 10
        kp = await db.knowledge_progress.find_one({"user_id": user["id"], "topic": domain})
        current = float(kp["score"]) if kp else float(baseline_score)
        new_score = apply_feedback_gain(current, payload.confidence, payload.solved_status)
        await db.knowledge_progress.update_one(
            {"user_id": user["id"], "topic": domain},
            {"$set": {"user_id": user["id"], "topic": domain,
                      "score": new_score,
                      "completions": (kp.get("completions", 0) if kp else 0) + 1,
                      "last_updated": _now_iso()}},
            upsert=True,
        )

    # Schedule revision from confidence
    rev = RevisionItem(
        user_id=user["id"],
        task_title=(p or {}).get("title", "Problem"),
        topic=PATTERN_TO_DOMAIN.get(a["pattern"], ("dsa", ""))[0],
        stage=0,
        next_review_date=first_revision_date(confidence=payload.confidence),
    )
    await db.revisions.insert_one(rev.model_dump())

    # Weakness detection
    if payload.confidence <= 4 or payload.solved_status in ("multi_hints", "could_not_solve"):
        signal = "could_not_solve" if payload.solved_status == "could_not_solve" else \
                 "many_hints" if payload.solved_status == "multi_hints" else "low_confidence"
        w = WeaknessRecord(user_id=user["id"], pattern=a["pattern"], signal=signal)
        await db.weaknesses.insert_one(w.model_dump())

    await _log_activity(
        db, user["id"], "problem_feedback",
        f"Feedback on {(p or {}).get('title', 'problem')}",
        description=f"confidence {payload.confidence}/10 · {payload.solved_status.replace('_',' ')}",
    )
    return {"ok": True, "assignment_id": assignment_id}


# ============ Knowledge tree (drill-down) ============

DOMAIN_ORDER = ["dsa", "java", "lld", "hld", "operating_systems", "dbms", "computer_networks"]


@router.get("/knowledge/tree")
async def get_knowledge_tree(user=Depends(get_current_user)):
    from server import db
    knowledge = await _get_knowledge(db, user["id"])
    onboarding = await _get_onboarding(db, user["id"])
    baseline = (onboarding or {}).get("self_assessment", {})
    by_topic = {k["topic"]: k for k in knowledge}

    # Feedback aggregated by pattern → confidence stats
    fb_cur = db.problem_feedback.find({"user_id": user["id"]}, {"_id": 0})
    all_fb = await fb_cur.to_list(length=500)
    fb_by_pattern = {}
    for f in all_fb:
        fb_by_pattern.setdefault(f["pattern"], []).append(f)

    # Revisions by topic
    rev_cur = db.revisions.find({"user_id": user["id"], "completed": False}, {"_id": 0})
    revs = await rev_cur.to_list(length=200)
    rev_by_topic = {}
    for r in revs:
        rev_by_topic.setdefault(r["topic"], []).append(r)
    today = today_date_str()

    tree = []
    for domain in DOMAIN_ORDER:
        # Domain progress
        kp = by_topic.get(domain)
        domain_score = kp["score"] if kp else (baseline.get(domain, 5) * 10)

        # Sub-topics: for DSA come from PATTERN_TO_DOMAIN filtered by domain
        sub_rows = []
        if domain == "dsa":
            for pattern, (d, label) in PATTERN_TO_DOMAIN.items():
                if d != domain:
                    continue
                fbs = fb_by_pattern.get(pattern, [])
                solved = len([f for f in fbs if f["solved_status"] != "could_not_solve"])
                confs = [f["confidence"] for f in fbs]
                avg_conf = round(sum(confs) / len(confs), 1) if confs else None
                # Simple sub-topic progress derived from solved count (max ~10 solved = 100%)
                progress = min(100.0, round(solved * 12.5, 1))
                revision_status = "fresh"
                due_here = [r for r in rev_by_topic.get(domain, []) if r["next_review_date"] <= today]
                if due_here:
                    revision_status = "due"
                elif avg_conf and avg_conf >= 8:
                    revision_status = "mastered"
                sub_rows.append({
                    "pattern": pattern,
                    "label": label,
                    "progress": progress,
                    "problems_solved": solved,
                    "avg_confidence": avg_conf,
                    "revision_status": revision_status,
                })
            sub_rows.sort(key=lambda x: -x["progress"])
        else:
            # For other domains, subtopics come from TOPIC_META
            meta = TOPIC_META.get(domain, {"subtopics": [], "label": domain})
            for sub, _ in meta["subtopics"]:
                sub_rows.append({
                    "pattern": None,
                    "label": sub,
                    "progress": round(domain_score, 1),
                    "problems_solved": 0,
                    "avg_confidence": None,
                    "revision_status": "fresh",
                })

        tree.append({
            "domain": domain,
            "label": TOPIC_META.get(domain, {}).get("label", domain),
            "score": round(domain_score, 1),
            "completions": kp.get("completions", 0) if kp else 0,
            "subtopics": sub_rows,
        })
    return tree


# ============ Company readiness ============

@router.get("/readiness/companies")
async def get_company_readiness(user=Depends(get_current_user)):
    from server import db
    onboarding = await _get_onboarding(db, user["id"])
    if not onboarding:
        return []
    knowledge = await _get_knowledge(db, user["id"])
    target_companies = onboarding.get("target_companies", [])
    # Show target companies first; then all known companies
    known = list(COMPANY_READINESS_WEIGHTS.keys())
    ordered = [c for c in target_companies if c in known] + [c for c in known if c not in target_companies]
    result = []
    for c in ordered:
        result.append({
            "company_id": c,
            "score": compute_company_readiness(c, knowledge, onboarding),
            "is_target": c in target_companies,
        })
    return result


# ============ Aggregated dashboard ============

@router.get("/dashboard")
async def get_dashboard(user=Depends(get_current_user)):
    from server import db
    today = today_date_str()

    onboarding = await _get_onboarding(db, user["id"])
    if not onboarding:
        raise HTTPException(status_code=400, detail="Complete onboarding first.")

    mission_doc = await db.daily_missions.find_one({"user_id": user["id"], "date": today})
    if not mission_doc:
        await _generate_today_mission(db, user["id"])
        mission_doc = await db.daily_missions.find_one({"user_id": user["id"], "date": today})
    mission = DailyMission(**_clean(mission_doc))

    # Daily login activity (once per day)
    login_today = await db.activity_events.find_one({
        "user_id": user["id"], "kind": "daily_login",
        "ts": {"$gte": f"{today}T00:00:00"},
    })
    if not login_today:
        await _log_activity(db, user["id"], "daily_login", "Signed in")

    knowledge = await _get_knowledge(db, user["id"])
    streak = await _get_streak(db, user["id"])
    readiness = compute_readiness(knowledge, onboarding)
    streak_grid = streak_days_grid(streak)

    cur = db.revisions.find({"user_id": user["id"], "completed": False}, {"_id": 0}).sort("next_review_date", 1).limit(6)
    revisions = await cur.to_list(length=6)
    for r in revisions:
        r["is_due"] = r["next_review_date"] <= today

    baseline = onboarding.get("self_assessment", {})
    progress_by_topic = {kp["topic"]: kp for kp in knowledge}
    knowledge_view = []
    for t in TOPIC_KEYS:
        kp = progress_by_topic.get(t)
        score = kp["score"] if kp else (baseline.get(t, 5) * 10)
        knowledge_view.append({
            "topic": t,
            "label": TOPIC_META[t]["label"],
            "score": round(score, 1),
            "completions": kp.get("completions", 0) if kp else 0,
        })

    # LIMIT to latest 5 activities
    act_cur = db.activity_events.find({"user_id": user["id"]}, {"_id": 0}).sort("ts", -1).limit(5)
    activity = await act_cur.to_list(length=5)

    # Company readiness (targets first, top-6 total)
    target_companies = onboarding.get("target_companies", [])
    company_readiness = []
    known = list(COMPANY_READINESS_WEIGHTS.keys())
    ordered = [c for c in target_companies if c in known] + [c for c in known if c not in target_companies][:5]
    for c in ordered[:6]:
        company_readiness.append({
            "company_id": c,
            "score": compute_company_readiness(c, knowledge, onboarding),
            "is_target": c in target_companies,
        })

    # Latest mission adjustment (sort desc so newest adaptive decision wins)
    adj_cursor = db.mission_adjustments.find(
        {"user_id": user["id"], "for_date": today}, {"_id": 0},
    ).sort("created_at", -1).limit(1)
    adj_list = await adj_cursor.to_list(length=1)
    adj_doc = adj_list[0] if adj_list else None

    days_to_target = None
    try:
        target = datetime.fromisoformat(onboarding["interview_target_date"].replace("Z", "+00:00"))
        days_to_target = max(0, (target.date() - datetime.now(timezone.utc).date()).days)
    except Exception:
        pass

    return {
        "today": today,
        "mission": mission.model_dump(),
        "streak": {
            "current": (streak or {}).get("current_streak", 0),
            "longest": (streak or {}).get("longest_streak", 0),
            "last_active_date": (streak or {}).get("last_active_date"),
            "week_grid": streak_grid,
        },
        "readiness": readiness,
        "company_readiness": company_readiness,
        "knowledge": knowledge_view,
        "revisions": revisions,
        "activity": activity,
        "adjustment": adj_doc,
        "onboarding": {
            "target_companies": onboarding.get("target_companies", []),
            "current_position": onboarding.get("current_position"),
            "daily_study_hours": onboarding.get("daily_study_hours"),
            "interview_target_date": onboarding.get("interview_target_date"),
            "estimated_prep_days": onboarding.get("estimated_prep_days"),
            "days_to_target": days_to_target,
        },
    }


# ============ Onboarding patch ============

@router.patch("/onboarding", response_model=OnboardingRecord)
async def patch_onboarding(payload: OnboardingPatch, user=Depends(get_current_user)):
    from server import db
    existing = await db.onboarding.find_one({"user_id": user["id"]})
    if not existing:
        raise HTTPException(status_code=404, detail="Onboarding record not found.")

    updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if updates:
        updates["updated_at"] = _now_iso()
        await db.onboarding.update_one({"user_id": user["id"]}, {"$set": updates})
        await _log_activity(
            db, user["id"], "profile_updated", "Mission profile updated",
            description=", ".join(updates.keys()),
        )
        merged = {**existing, **updates}
        avg_skill = sum(merged.get("self_assessment", {}).get(t, 5) for t in TOPIC_KEYS) / 7.0
        base = 180 - avg_skill * 12
        hours = float(merged.get("daily_study_hours", 2))
        estimated = max(30, int(base * (4.0 / max(hours, 1)) / 2))
        await db.onboarding.update_one(
            {"user_id": user["id"]}, {"$set": {"estimated_prep_days": estimated}},
        )
        today = today_date_str()
        await db.daily_missions.delete_one({
            "user_id": user["id"], "date": today, "status": "in_progress",
        })

    doc = await db.onboarding.find_one({"user_id": user["id"]})
    return OnboardingRecord(**_clean(doc))
