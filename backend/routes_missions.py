"""Mission + Dashboard + Revision + Activity routes."""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_current_user
from models import (
    DailyMission, MissionTask, KnowledgeProgress, StudyStreak,
    RevisionItem, ActivityEvent, TOPIC_KEYS, OnboardingPatch, OnboardingRecord,
)
from mission_engine import (
    build_mission_for_user, today_date_str, schedule_next_revision,
    first_revision_date, compute_readiness, update_streak_on_completion,
    streak_days_grid, apply_knowledge_gain, TOPIC_META,
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


async def _generate_today_mission(db, user_id: str) -> DailyMission:
    onboarding = await _get_onboarding(db, user_id)
    if not onboarding:
        raise HTTPException(status_code=400, detail="Complete onboarding to generate missions.")
    knowledge = await _get_knowledge(db, user_id)
    revisions_due = await _get_due_revisions(db, user_id)
    mission = build_mission_for_user(user_id, onboarding, knowledge, revisions_due)
    await db.daily_missions.insert_one(mission.model_dump())
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


# ============ Task completion ============

@router.post("/missions/{mission_id}/tasks/{task_id}/complete", response_model=DailyMission)
async def complete_task(mission_id: str, task_id: str, user=Depends(get_current_user)):
    from server import db
    doc = await db.daily_missions.find_one({"id": mission_id, "user_id": user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Mission not found")
    if doc["status"] in ("completed", "skipped"):
        return DailyMission(**_clean(doc))

    task = next((t for t in doc["tasks"] if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["completed"]:
        return DailyMission(**_clean(doc))

    task["completed"] = True
    task["completed_at"] = _now_iso()

    # Bump knowledge progress
    difficulty = doc["difficulty"]
    kind = task["kind"]
    topic = task["topic"]

    onboarding = await _get_onboarding(db, user["id"])
    baseline_score = (onboarding or {}).get("self_assessment", {}).get(topic, 5) * 10

    kp = await db.knowledge_progress.find_one({"user_id": user["id"], "topic": topic})
    current = float(kp["score"]) if kp else float(baseline_score)
    new_score = apply_knowledge_gain(current, difficulty, kind)
    completions = (kp.get("completions", 0) if kp else 0) + 1
    await db.knowledge_progress.update_one(
        {"user_id": user["id"], "topic": topic},
        {"$set": {
            "user_id": user["id"], "topic": topic,
            "score": new_score, "completions": completions,
            "last_updated": _now_iso(),
        }},
        upsert=True,
    )

    # Schedule spaced repetition for practice/study tasks (not revision)
    if kind != "revise":
        rev = RevisionItem(
            user_id=user["id"],
            task_title=task["title"],
            topic=topic,
            stage=0,
            next_review_date=first_revision_date(),
        )
        await db.revisions.insert_one(rev.model_dump())
    else:
        # Advance existing revision item to next stage if we can match by title+topic
        existing = await db.revisions.find_one({
            "user_id": user["id"], "topic": topic, "completed": False,
        })
        if existing:
            next_stage, next_date = schedule_next_revision(existing.get("stage", 0))
            await db.revisions.update_one(
                {"id": existing["id"]},
                {"$set": {"stage": next_stage, "next_review_date": next_date}},
            )

    await db.daily_missions.update_one({"id": mission_id}, {"$set": {"tasks": doc["tasks"]}})
    await _log_activity(
        db, user["id"], "task_completed",
        f"Completed: {task['title']}",
    )

    updated = await db.daily_missions.find_one({"id": mission_id})
    return DailyMission(**_clean(updated))


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
    # Mark any unfinished tasks as completed too (user is confirming full completion)
    for t in doc["tasks"]:
        if not t["completed"]:
            t["completed"] = True
            t["completed_at"] = now
            # Award small credit for these too
            kp = await db.knowledge_progress.find_one({"user_id": user["id"], "topic": t["topic"]})
            baseline_score = baseline.get(t["topic"], 5) * 10
            current = float(kp["score"]) if kp else float(baseline_score)
            new_score = apply_knowledge_gain(current, doc["difficulty"], t["kind"])
            await db.knowledge_progress.update_one(
                {"user_id": user["id"], "topic": t["topic"]},
                {"$set": {
                    "user_id": user["id"], "topic": t["topic"],
                    "score": new_score,
                    "completions": (kp.get("completions", 0) if kp else 0) + 1,
                    "last_updated": now,
                }},
                upsert=True,
            )

    await db.daily_missions.update_one(
        {"id": mission_id},
        {"$set": {"status": "completed", "completed_at": now, "tasks": doc["tasks"]}},
    )
    await _upsert_streak_on_completion(db, user["id"])
    await _log_activity(
        db, user["id"], "mission_completed",
        f"Mission completed: {doc['title']}",
        description=doc["focus_area"],
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
        f"Mission skipped: {doc['title']}",
        description=doc["focus_area"],
    )
    updated = await db.daily_missions.find_one({"id": mission_id})
    return DailyMission(**_clean(updated))


# ============ History ============

@router.get("/missions/history")
async def get_mission_history(limit: int = 20, user=Depends(get_current_user)):
    from server import db
    cur = db.daily_missions.find(
        {"user_id": user["id"]}, {"_id": 0},
    ).sort("date", -1).limit(limit)
    docs = await cur.to_list(length=limit)
    return [DailyMission(**d) for d in docs]


# ============ Revision queue ============

@router.get("/revisions/queue")
async def get_revision_queue(user=Depends(get_current_user)):
    from server import db
    today = today_date_str()
    cur = db.revisions.find(
        {"user_id": user["id"], "completed": False},
        {"_id": 0},
    ).sort("next_review_date", 1).limit(20)
    items = await cur.to_list(length=20)
    for it in items:
        it["is_due"] = it["next_review_date"] <= today
    return items


# ============ Activity ============

@router.get("/activity")
async def get_activity(limit: int = 20, user=Depends(get_current_user)):
    from server import db
    cur = db.activity_events.find(
        {"user_id": user["id"]}, {"_id": 0},
    ).sort("ts", -1).limit(limit)
    return await cur.to_list(length=limit)


# ============ Aggregated dashboard ============

@router.get("/dashboard")
async def get_dashboard(user=Depends(get_current_user)):
    from server import db
    today = today_date_str()

    onboarding = await _get_onboarding(db, user["id"])
    if not onboarding:
        raise HTTPException(status_code=400, detail="Complete onboarding first.")

    # Ensure today's mission exists
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

    # Streak history (last 7 days)
    streak_grid = streak_days_grid(streak)

    # Upcoming revisions
    cur = db.revisions.find(
        {"user_id": user["id"], "completed": False},
        {"_id": 0},
    ).sort("next_review_date", 1).limit(6)
    revisions = await cur.to_list(length=6)
    for r in revisions:
        r["is_due"] = r["next_review_date"] <= today

    # Knowledge progress with labels
    progress_by_topic = {kp["topic"]: kp for kp in knowledge}
    baseline = onboarding.get("self_assessment", {})
    knowledge_view = []
    for t in TOPIC_KEYS:
        kp = progress_by_topic.get(t)
        if kp:
            score = kp["score"]
        else:
            score = baseline.get(t, 5) * 10  # baseline projection
        knowledge_view.append({
            "topic": t,
            "label": TOPIC_META[t]["label"],
            "score": round(score, 1),
            "completions": kp.get("completions", 0) if kp else 0,
        })

    # Activity (last 6)
    act_cur = db.activity_events.find(
        {"user_id": user["id"]}, {"_id": 0},
    ).sort("ts", -1).limit(6)
    activity = await act_cur.to_list(length=6)

    # Days to target
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
        "knowledge": knowledge_view,
        "revisions": revisions,
        "activity": activity,
        "onboarding": {
            "target_companies": onboarding.get("target_companies", []),
            "current_position": onboarding.get("current_position"),
            "daily_study_hours": onboarding.get("daily_study_hours"),
            "interview_target_date": onboarding.get("interview_target_date"),
            "estimated_prep_days": onboarding.get("estimated_prep_days"),
            "days_to_target": days_to_target,
        },
    }


# ============ Onboarding patch (used by Profile edit) ============

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
            db, user["id"], "profile_updated",
            "Mission profile updated",
            description=", ".join(updates.keys()),
        )

        # Recalculate estimated_prep_days
        from mission_engine import TOPIC_META  # noqa
        merged = {**existing, **updates}
        avg_skill = sum(merged.get("self_assessment", {}).get(t, 5) for t in TOPIC_KEYS) / 7.0
        base = 180 - avg_skill * 12
        hours = float(merged.get("daily_study_hours", 2))
        estimated = max(30, int(base * (4.0 / max(hours, 1)) / 2))
        await db.onboarding.update_one(
            {"user_id": user["id"]}, {"$set": {"estimated_prep_days": estimated}},
        )

        # Regenerate today's mission from the new profile
        today = today_date_str()
        await db.daily_missions.delete_one({
            "user_id": user["id"], "date": today, "status": "in_progress",
        })

    doc = await db.onboarding.find_one({"user_id": user["id"]})
    return OnboardingRecord(**_clean(doc))
