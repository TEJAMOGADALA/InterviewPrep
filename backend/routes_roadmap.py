"""Roadmap Engine API + Knowledge Graph endpoints."""
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_current_user
from models import (
    KnowledgeNode, KnowledgeNoteUpdate, KnowledgeConfidenceUpdate,
    KnowledgeStatusUpdate, KnowledgeAttemptUpdate,
)
from roadmap import get_roadmap, CURRENT_VERSION
from problem_bank import problem_by_id
from ai_service import AIProviderError
from knowledge_generation import ensure_content, read_cache, clear_cache

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


# Status vocabulary — normalized public surface.
STATUS_NOT_STARTED = "not_started"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_MASTERED = "mastered"
STATUS_REVISION_DUE = "revision_due"

# Legacy `available` from earlier iterations maps to `not_started` on the
# public surface. We rewrite it on read; older rows keep working untouched.
_LEGACY_STATUS_MAP = {"available": STATUS_NOT_STARTED, "locked": STATUS_NOT_STARTED}


def _normalize_status(raw: Optional[str], next_revision: Optional[str]) -> str:
    st = _LEGACY_STATUS_MAP.get(raw or "", raw) or STATUS_NOT_STARTED
    # Derive `revision_due` when a completed/mastered node has a due date in the past.
    if st in (STATUS_COMPLETED, STATUS_MASTERED) and next_revision:
        try:
            due = datetime.fromisoformat(next_revision.replace("Z", "+00:00"))
            if due <= datetime.now(timezone.utc):
                return STATUS_REVISION_DUE
        except Exception:
            pass
    return st


def _clean(d: dict) -> dict:
    if d:
        d.pop("_id", None)
    return d


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _get_user_version(db, user_id: str) -> str:
    u = await db.users.find_one({"id": user_id}, {"roadmap_version": 1})
    return (u or {}).get("roadmap_version") or CURRENT_VERSION


async def _ensure_user_version(db, user_id: str) -> str:
    """Stamp user with current version if missing."""
    v = await _get_user_version(db, user_id)
    if not v:
        await db.users.update_one({"id": user_id}, {"$set": {"roadmap_version": CURRENT_VERSION}})
        return CURRENT_VERSION
    return v


def _bucket(confidence: float, weakness_score: float) -> str:
    if confidence >= 7 and weakness_score < 30:
        return "green"
    if confidence >= 4:
        return "yellow"
    return "red"


async def _load_user_progress(db, user_id: str) -> dict:
    """Return dict node_id → KnowledgeNode doc."""
    cur = db.knowledge_nodes.find({"user_id": user_id}, {"_id": 0})
    docs = await cur.to_list(length=500)
    return {d["node_id"]: d for d in docs}


def _is_leaf_node(node: dict) -> bool:
    """A node is a leaf if it has no descendants — those are the units we count."""
    return not (node.get("child_ids") or [])


def _rollup_from_progress(node: dict, progress: dict, roadmap) -> dict:
    """Compute status + mastery + counts for a node from itself or its descendants."""
    prog = progress.get(node["id"])
    if prog:
        status = _normalize_status(prog.get("status"), prog.get("next_revision"))
        mastery = float(prog.get("mastery_percentage", 0.0))
        est_min = int(node.get("estimated_minutes") or 0)
        is_done = status in (STATUS_COMPLETED, STATUS_MASTERED)
        # Only count leaves toward "topic counts" — parent nodes aggregate.
        is_leaf = _is_leaf_node(node)
        completed_topics = 1 if (is_leaf and is_done) else 0
        total_topics = 1 if is_leaf else 0
        remaining_minutes = 0 if is_done else (est_min if is_leaf else 0)
        return {
            "status": status,
            "confidence": round(prog.get("confidence", 0.0), 2),
            "weakness_score": round(prog.get("weakness_score", 0.0), 2),
            "mastery_percentage": round(mastery, 2),
            "revision_bucket": prog.get("revision_bucket", "green"),
            "has_progress": True,
            "bookmarked": bool(prog.get("bookmarked", False)),
            "favorite": bool(prog.get("favorite", False)),
            "attempts": int(prog.get("attempts", 0)),
            "actual_solve_minutes": int(prog.get("actual_solve_minutes", 0)),
            "completion_date": prog.get("completion_date"),
            "last_revision": prog.get("last_revision"),
            "next_revision": prog.get("next_revision"),
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "remaining_topics": total_topics - completed_topics,
            "completion_pct": 100.0 if (is_leaf and is_done) else 0.0,
            "estimated_hours_remaining": round(remaining_minutes / 60.0, 2),
        }
    # No direct record — descend into children.
    kids = node.get("child_ids", []) or []
    if not kids:
        # A leaf with no progress row.
        est_min = int(node.get("estimated_minutes") or 0)
        return {
            "status": STATUS_NOT_STARTED, "confidence": 0.0, "weakness_score": 0.0,
            "mastery_percentage": 0.0, "revision_bucket": "green",
            "has_progress": False, "bookmarked": False, "favorite": False,
            "attempts": 0, "actual_solve_minutes": 0,
            "completion_date": None, "last_revision": None, "next_revision": None,
            "total_topics": 1, "completed_topics": 0, "remaining_topics": 1,
            "completion_pct": 0.0,
            "estimated_hours_remaining": round(est_min / 60.0, 2),
        }
    parts = []
    for cid in kids:
        c = roadmap.get(cid)
        if not c:
            continue
        parts.append(_rollup_from_progress(c, progress, roadmap))
    if not parts:
        return {
            "status": STATUS_NOT_STARTED, "confidence": 0.0, "weakness_score": 0.0,
            "mastery_percentage": 0.0, "revision_bucket": "green",
            "has_progress": False, "bookmarked": False, "favorite": False,
            "attempts": 0, "actual_solve_minutes": 0,
            "completion_date": None, "last_revision": None, "next_revision": None,
            "total_topics": 0, "completed_topics": 0, "remaining_topics": 0,
            "completion_pct": 0.0, "estimated_hours_remaining": 0.0,
        }
    n = len(parts)
    avg_conf = sum(p["confidence"] for p in parts) / n
    avg_mastery = sum(p["mastery_percentage"] for p in parts) / n
    avg_weak = sum(p["weakness_score"] for p in parts) / n
    total_topics = sum(p.get("total_topics", 0) for p in parts)
    completed_topics = sum(p.get("completed_topics", 0) for p in parts)
    hours_remaining = round(sum(p.get("estimated_hours_remaining", 0.0) for p in parts), 2)
    completion_pct = round((completed_topics / total_topics) * 100.0, 2) if total_topics else 0.0
    any_progress = any(p["has_progress"] for p in parts)
    any_bookmarked = any(p.get("bookmarked") for p in parts)
    any_favorite = any(p.get("favorite") for p in parts)
    any_revision_due = any(p.get("status") == STATUS_REVISION_DUE for p in parts)
    all_completed = any_progress and all(
        p.get("status") in (STATUS_COMPLETED, STATUS_MASTERED)
        for p in parts if p.get("has_progress")
    )
    if any_revision_due:
        status = STATUS_REVISION_DUE
    elif all_completed:
        status = STATUS_MASTERED if avg_conf >= 8 else STATUS_COMPLETED
    elif any_progress:
        status = STATUS_IN_PROGRESS
    else:
        status = STATUS_NOT_STARTED
    return {
        "status": status,
        "confidence": round(avg_conf, 2),
        "weakness_score": round(avg_weak, 2),
        "mastery_percentage": round(avg_mastery, 2),
        "revision_bucket": _bucket(avg_conf, avg_weak),
        "has_progress": any_progress,
        "bookmarked": any_bookmarked,
        "favorite": any_favorite,
        "attempts": sum(p.get("attempts", 0) for p in parts),
        "actual_solve_minutes": sum(p.get("actual_solve_minutes", 0) for p in parts),
        "completion_date": None,
        "last_revision": None,
        "next_revision": None,
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "remaining_topics": total_topics - completed_topics,
        "completion_pct": completion_pct,
        "estimated_hours_remaining": hours_remaining,
    }


def _shape_node(n: dict, progress_view: dict) -> dict:
    """Public shape returned in tree responses (no recursive children objects,
    only ids). Callers can descend using child_ids."""
    return {
        "id": n["id"],
        "label": n["label"],
        "description": n.get("description"),
        "type": n.get("type"),
        "parent_id": n.get("parent_id"),
        "depth": n.get("depth", 0),
        "child_ids": n.get("child_ids", []),
        "pattern": n.get("pattern"),
        "difficulty": n.get("difficulty"),
        "estimated_minutes": n.get("estimated_minutes"),
        "interview_importance": n.get("interview_importance"),
        "interview_frequency": n.get("interview_frequency"),
        "mastery_weight": n.get("mastery_weight"),
        "tags": n.get("tags", []),
        "company_importance": n.get("company_importance") or {},
        "problem_ids": n.get("problem_ids", []),
        "prerequisites": n.get("prerequisites", []),
        "related": n.get("related", []),
        "progress": progress_view,
    }


# ============ Tree ============

@router.get("")
async def get_full_roadmap(user=Depends(get_current_user)):
    """Returns the full roadmap tree with per-user progress rolled up."""
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    progress = await _load_user_progress(db, user["id"])

    tracks = []
    for track in roadmap.tracks():
        track_view = _shape_node(track, _rollup_from_progress(track, progress, roadmap))
        # Build nested modules → topics → subtopics (light)
        def hydrate(n):
            v = _shape_node(n, _rollup_from_progress(n, progress, roadmap))
            v["children"] = [hydrate(roadmap.get(c)) for c in n.get("child_ids", []) if roadmap.get(c)]
            return v
        track_view["children"] = [hydrate(roadmap.get(c)) for c in track["child_ids"] if roadmap.get(c)]
        tracks.append(track_view)

    return {"version": version, "companies": roadmap.tree().get("companies", []), "tracks": tracks}


# ============ Node detail (Deep Topic page) ============

@router.get("/nodes/{node_id}")
async def get_node_detail(node_id: str, user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    node = roadmap.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    progress_map = await _load_user_progress(db, user["id"])
    node_progress = _rollup_from_progress(node, progress_map, roadmap)

    breadcrumb = [{"id": a["id"], "label": a["label"], "type": a.get("type")}
                  for a in roadmap.ancestors(node_id)]

    prereqs = [{
        "id": p["id"], "label": p["label"], "type": p.get("type"),
        "progress": _rollup_from_progress(p, progress_map, roadmap),
    } for p in roadmap.prerequisites(node_id)]

    related = [{
        "id": r["id"], "label": r["label"], "type": r.get("type"),
    } for r in roadmap.related(node_id)]

    # Linked problems (aggregate from this + descendants)
    problem_ids = roadmap.problems_for_node(node_id)
    problems = []
    for pid in problem_ids[:20]:
        p = problem_by_id(pid)
        if p:
            problems.append(p)

    # Assignments/feedback for this node's problems
    if problem_ids:
        cur = db.problem_assignments.find(
            {"user_id": user["id"], "problem_id": {"$in": problem_ids}}, {"_id": 0},
        ).sort("assigned_at", -1).limit(40)
        assignments = await cur.to_list(length=40)
    else:
        assignments = []

    fb_cur = db.problem_feedback.find(
        {"user_id": user["id"], "problem_id": {"$in": problem_ids} if problem_ids else {"$exists": False}},
        {"_id": 0},
    ).sort("submitted_at", -1).limit(20)
    feedback = await fb_cur.to_list(length=20)

    # Personal notes come from the direct KnowledgeNode row (if present)
    direct = progress_map.get(node_id) or {}
    notes = direct.get("notes")

    # Recent activity referencing this node (via description/title matches). Best-effort.
    activity_cur = db.activity_events.find(
        {"user_id": user["id"], "$or": [
            {"description": {"$regex": node["label"], "$options": "i"}},
            {"title": {"$regex": node["label"], "$options": "i"}},
        ]}, {"_id": 0},
    ).sort("ts", -1).limit(10)
    activity = await activity_cur.to_list(length=10)

    # Company importance
    companies = roadmap.tree().get("companies", [])
    company_importance = {c: roadmap.company_importance(node_id, c) for c in companies}

    # Track
    track = roadmap.find_track(node_id)

    return {
        "node": _shape_node(node, node_progress),
        "track": {"id": track["id"], "label": track["label"]} if track else None,
        "breadcrumb": breadcrumb,
        "prerequisites": prereqs,
        "related": related,
        "problems": [{
            **p,
            "assignment": next((a for a in assignments if a["problem_id"] == p["id"]), None),
            "feedback": next((f for f in feedback if f["problem_id"] == p["id"]), None),
        } for p in problems],
        "notes": notes,
        "company_importance": company_importance,
        "activity": activity,
        "assignments_count": len(assignments),
    }


# ============ Progress ============

@router.get("/progress")
async def get_progress(user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    progress_map = await _load_user_progress(db, user["id"])
    # Roll up per track and per module (progress now includes topic counts + hours).
    result = []
    for track in roadmap.tracks():
        modules = []
        for module in track.get("modules", []) or []:
            modules.append({
                "id": module["id"], "label": module["label"],
                "progress": _rollup_from_progress(module, progress_map, roadmap),
                "topic_count": len(module.get("topics", []) or []),
            })
        result.append({
            "id": track["id"], "label": track["label"], "icon": track.get("icon"),
            "progress": _rollup_from_progress(track, progress_map, roadmap),
            "modules": modules,
        })
    return {"version": version, "tracks": result}


# ============ Dashboard summary ============

@router.get("/summary")
async def get_summary(user=Depends(get_current_user)):
    """Compact rollup for the Mission Control dashboard strip.

    Returns overall percentages and topic counts across every track — this
    is what powers the "Overall DSA %, LLD %, HLD %" tiles without needing
    the caller to walk the full tree.
    """
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    progress_map = await _load_user_progress(db, user["id"])

    today = datetime.now(timezone.utc).date().isoformat()
    tracks_summary = []
    total_topics = 0
    total_completed = 0
    total_hours_remaining = 0.0
    weighted_readiness_num = 0.0
    weighted_readiness_den = 0.0

    for track in roadmap.tracks():
        roll = _rollup_from_progress(track, progress_map, roadmap)
        weight = float(track.get("mastery_weight") or track.get("interview_importance") or 3)
        tracks_summary.append({
            "id": track["id"], "label": track["label"], "icon": track.get("icon"),
            "completion_pct": roll["completion_pct"],
            "mastery_percentage": roll["mastery_percentage"],
            "completed_topics": roll["completed_topics"],
            "total_topics": roll["total_topics"],
            "remaining_topics": roll["remaining_topics"],
            "estimated_hours_remaining": roll["estimated_hours_remaining"],
            "status": roll["status"],
            "revision_bucket": roll["revision_bucket"],
        })
        total_topics += roll["total_topics"]
        total_completed += roll["completed_topics"]
        total_hours_remaining += roll["estimated_hours_remaining"]
        weighted_readiness_num += roll["mastery_percentage"] * weight
        weighted_readiness_den += weight

    overall_completion = round((total_completed / total_topics) * 100.0, 2) if total_topics else 0.0
    overall_readiness = round(weighted_readiness_num / weighted_readiness_den, 2) if weighted_readiness_den else 0.0

    # Today's completed topics — count knowledge_nodes whose completion_date is today.
    today_completed_ids: list[str] = []
    for nid, prog in progress_map.items():
        cd = prog.get("completion_date")
        if cd and cd[:10] == today:
            today_completed_ids.append(nid)

    revision_due_count = sum(
        1 for _, p in progress_map.items()
        if _normalize_status(p.get("status"), p.get("next_revision")) == STATUS_REVISION_DUE
    )
    bookmarked_count = sum(1 for _, p in progress_map.items() if p.get("bookmarked"))
    favorite_count = sum(1 for _, p in progress_map.items() if p.get("favorite"))

    return {
        "version": version,
        "tracks": tracks_summary,
        "overall": {
            "completion_pct": overall_completion,
            "readiness": overall_readiness,
            "total_topics": total_topics,
            "completed_topics": total_completed,
            "remaining_topics": total_topics - total_completed,
            "estimated_hours_remaining": round(total_hours_remaining, 2),
        },
        "today": {
            "completed_count": len(today_completed_ids),
            "completed_ids": today_completed_ids[:50],
        },
        "counts": {
            "revision_due": revision_due_count,
            "bookmarked": bookmarked_count,
            "favorite": favorite_count,
        },
    }


# ============ Notes ============

@router.patch("/nodes/{node_id}/notes")
async def update_notes(node_id: str, payload: KnowledgeNoteUpdate, user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    if not roadmap.get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")

    await db.knowledge_nodes.update_one(
        {"user_id": user["id"], "node_id": node_id, "roadmap_version": version},
        {"$set": {"notes": payload.notes, "updated_at": _now_iso(),
                  "user_id": user["id"], "node_id": node_id, "roadmap_version": version}},
        upsert=True,
    )
    return {"ok": True, "node_id": node_id}


# ============ Confidence update ============

@router.post("/nodes/{node_id}/confidence")
async def update_confidence(node_id: str, payload: KnowledgeConfidenceUpdate, user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    if not roadmap.get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")

    conf = float(payload.confidence)
    weakness = max(0.0, 100 - conf * 10)
    mastery = min(100.0, conf * 10)
    # Use the normalized status vocabulary.
    if conf >= 9:
        status = STATUS_MASTERED
    elif conf > 0:
        status = STATUS_IN_PROGRESS
    else:
        status = STATUS_NOT_STARTED
    bucket = _bucket(conf, weakness)

    set_doc = {
        "user_id": user["id"], "node_id": node_id, "roadmap_version": version,
        "confidence": conf, "weakness_score": weakness,
        "mastery_percentage": mastery,
        "status": status, "revision_bucket": bucket,
        "updated_at": _now_iso(),
    }
    # Stamp completion_date when transitioning into completed/mastered.
    if status in (STATUS_COMPLETED, STATUS_MASTERED):
        set_doc["completion_date"] = _now_iso()
    await db.knowledge_nodes.update_one(
        {"user_id": user["id"], "node_id": node_id, "roadmap_version": version},
        {"$set": set_doc},
        upsert=True,
    )
    return {"ok": True, "node_id": node_id, "confidence": conf, "status": status}


# ============ Explicit status ============

@router.post("/nodes/{node_id}/status")
async def update_status(node_id: str, payload: KnowledgeStatusUpdate, user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    if not roadmap.get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")

    status = payload.status
    now = _now_iso()
    set_doc = {
        "user_id": user["id"], "node_id": node_id, "roadmap_version": version,
        "status": status, "updated_at": now,
    }
    # When marking completed/mastered, snap sensible defaults if the row was empty.
    if status in (STATUS_COMPLETED, STATUS_MASTERED):
        set_doc["completion_date"] = now
        # Schedule a first revision 3 days out — spaced-repetition friendly default.
        set_doc["next_revision"] = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        # Bump mastery baseline if none yet.
        existing = await db.knowledge_nodes.find_one(
            {"user_id": user["id"], "node_id": node_id, "roadmap_version": version},
            {"mastery_percentage": 1, "confidence": 1},
        ) or {}
        if not existing.get("mastery_percentage"):
            set_doc["mastery_percentage"] = 100.0 if status == STATUS_MASTERED else 80.0
        if not existing.get("confidence"):
            set_doc["confidence"] = 9.0 if status == STATUS_MASTERED else 7.0
    elif status == STATUS_REVISION_DUE:
        set_doc["next_revision"] = now
    await db.knowledge_nodes.update_one(
        {"user_id": user["id"], "node_id": node_id, "roadmap_version": version},
        {"$set": set_doc},
        upsert=True,
    )
    return {"ok": True, "node_id": node_id, "status": status}


# ============ Bookmark / Favorite toggles ============

async def _toggle_flag(db, user_id: str, version: str, node_id: str, field: str) -> bool:
    existing = await db.knowledge_nodes.find_one(
        {"user_id": user_id, "node_id": node_id, "roadmap_version": version},
        {field: 1},
    ) or {}
    new_val = not bool(existing.get(field, False))
    await db.knowledge_nodes.update_one(
        {"user_id": user_id, "node_id": node_id, "roadmap_version": version},
        {"$set": {
            "user_id": user_id, "node_id": node_id, "roadmap_version": version,
            field: new_val, "updated_at": _now_iso(),
        }},
        upsert=True,
    )
    return new_val


@router.post("/nodes/{node_id}/bookmark")
async def toggle_bookmark(node_id: str, user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    if not roadmap.get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    val = await _toggle_flag(db, user["id"], version, node_id, "bookmarked")
    return {"ok": True, "node_id": node_id, "bookmarked": val}


@router.post("/nodes/{node_id}/favorite")
async def toggle_favorite(node_id: str, user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    if not roadmap.get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    val = await _toggle_flag(db, user["id"], version, node_id, "favorite")
    return {"ok": True, "node_id": node_id, "favorite": val}


# ============ Attempt logging ============

@router.post("/nodes/{node_id}/attempt")
async def record_attempt(node_id: str, payload: KnowledgeAttemptUpdate, user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    roadmap = get_roadmap(version)
    if not roadmap.get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")

    inc_doc = {"attempts": 1}
    if payload.actual_minutes:
        inc_doc["actual_solve_minutes"] = int(payload.actual_minutes)

    await db.knowledge_nodes.update_one(
        {"user_id": user["id"], "node_id": node_id, "roadmap_version": version},
        {
            "$inc": inc_doc,
            "$set": {
                "user_id": user["id"], "node_id": node_id, "roadmap_version": version,
                "updated_at": _now_iso(),
            },
            # If this is a brand-new row, seed status to in_progress.
            "$setOnInsert": {"status": STATUS_IN_PROGRESS},
        },
        upsert=True,
    )
    row = await db.knowledge_nodes.find_one(
        {"user_id": user["id"], "node_id": node_id, "roadmap_version": version},
        {"_id": 0, "attempts": 1, "actual_solve_minutes": 1},
    ) or {}
    return {
        "ok": True, "node_id": node_id,
        "attempts": int(row.get("attempts", 0)),
        "actual_solve_minutes": int(row.get("actual_solve_minutes", 0)),
    }


# ============ Version + Migration status ============

@router.get("/version")
async def get_version(user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    return {"user_version": version, "current_version": CURRENT_VERSION}


# ============ AI-generated Knowledge Base content ============

def _content_view(doc: Optional[dict]) -> dict:
    """Shape a cached KnowledgeContent document for API consumers.

    Missing sections come back as empty lists / None so the frontend can render
    without null-guards. `available` is a convenience flag for lazy UIs."""
    if not doc:
        return {
            "available": False,
            "theory": None,
            "examples": [],
            "interview_tips": [],
            "common_mistakes": [],
            "flashcards": [],
            "related_topics": [],
            "prerequisites": [],
            "provider": None, "model_name": None,
            "generated_at": None, "updated_at": None,
        }
    return {
        "available": bool(doc.get("theory")),
        "theory": doc.get("theory"),
        "examples": doc.get("examples") or [],
        "interview_tips": doc.get("interview_tips") or [],
        "common_mistakes": doc.get("common_mistakes") or [],
        "flashcards": doc.get("flashcards") or [],
        "related_topics": doc.get("related_topics") or [],
        "prerequisites": doc.get("prerequisites") or [],
        "provider": doc.get("provider"),
        "model_name": doc.get("model_name"),
        "generated_at": doc.get("generated_at"),
        "updated_at": doc.get("updated_at"),
    }


def _ai_error_to_http(err: AIProviderError) -> HTTPException:
    return HTTPException(
        status_code=err.status_code or 500,
        detail={"error": err.kind, "message": str(err)},
    )


@router.get("/nodes/{node_id}/content")
async def get_node_content(node_id: str, user=Depends(get_current_user)):
    """Return cached AI content for a node — never triggers generation.
    Frontend calls this on tab open and only prompts the user to generate
    when `available` is false."""
    from server import db
    version = await _ensure_user_version(db, user["id"])
    if not get_roadmap(version).get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    doc = await read_cache(db, node_id=node_id, roadmap_version=version)
    return _content_view(doc)


@router.post("/nodes/{node_id}/content/generate")
async def generate_node_content(node_id: str, user=Depends(get_current_user)):
    """Generate + cache AI content for a node. Idempotent on a cache hit
    (returns the existing doc without a new Gemini call)."""
    from server import db
    version = await _ensure_user_version(db, user["id"])
    if not get_roadmap(version).get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        doc = await ensure_content(
            db, node_id=node_id, roadmap_version=version, user_id=user["id"], force=False,
        )
    except AIProviderError as e:
        raise _ai_error_to_http(e)
    return _content_view(doc)


@router.post("/nodes/{node_id}/content/regenerate")
async def regenerate_node_content(node_id: str, user=Depends(get_current_user)):
    """Explicit re-generation. Clears the cache row and calls Gemini again."""
    from server import db
    version = await _ensure_user_version(db, user["id"])
    if not get_roadmap(version).get(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        await clear_cache(db, node_id=node_id, roadmap_version=version)
        doc = await ensure_content(
            db, node_id=node_id, roadmap_version=version, user_id=user["id"], force=True,
        )
    except AIProviderError as e:
        raise _ai_error_to_http(e)
    return _content_view(doc)

