"""Roadmap Engine API + Knowledge Graph endpoints."""
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_current_user
from models import KnowledgeNode, KnowledgeNoteUpdate, KnowledgeConfidenceUpdate
from roadmap import get_roadmap, CURRENT_VERSION
from problem_bank import problem_by_id

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


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


def _rollup_from_progress(node: dict, progress: dict, roadmap) -> dict:
    """Compute status + mastery for a node from itself or its descendants."""
    prog = progress.get(node["id"])
    if prog:
        return {
            "status": prog.get("status", "available"),
            "confidence": round(prog.get("confidence", 0.0), 2),
            "weakness_score": round(prog.get("weakness_score", 0.0), 2),
            "mastery_percentage": round(prog.get("mastery_percentage", 0.0), 2),
            "revision_bucket": prog.get("revision_bucket", "green"),
            "has_progress": True,
        }
    # No direct record — average descendants
    kids = node.get("child_ids", []) or []
    if not kids:
        return {"status": "available", "confidence": 0.0, "weakness_score": 0.0,
                "mastery_percentage": 0.0, "revision_bucket": "green",
                "has_progress": False}
    parts = []
    for cid in kids:
        c = roadmap.get(cid)
        if not c: continue
        parts.append(_rollup_from_progress(c, progress, roadmap))
    if not parts:
        return {"status": "available", "confidence": 0.0, "weakness_score": 0.0,
                "mastery_percentage": 0.0, "revision_bucket": "green",
                "has_progress": False}
    n = len(parts)
    avg_conf = sum(p["confidence"] for p in parts) / n
    avg_mastery = sum(p["mastery_percentage"] for p in parts) / n
    avg_weak = sum(p["weakness_score"] for p in parts) / n
    any_progress = any(p["has_progress"] for p in parts)
    all_completed = any_progress and all(p.get("status") in ("completed", "mastered") for p in parts if p.get("has_progress"))
    status = "in_progress" if any_progress else "available"
    if all_completed: status = "mastered" if avg_conf >= 8 else "completed"
    return {
        "status": status,
        "confidence": round(avg_conf, 2),
        "weakness_score": round(avg_weak, 2),
        "mastery_percentage": round(avg_mastery, 2),
        "revision_bucket": _bucket(avg_conf, avg_weak),
        "has_progress": any_progress,
    }


def _shape_node(n: dict, progress_view: dict) -> dict:
    """Public shape returned in tree responses (no recursive children objects,
    only ids). Callers can descend using child_ids."""
    return {
        "id": n["id"],
        "label": n["label"],
        "type": n.get("type"),
        "parent_id": n.get("parent_id"),
        "depth": n.get("depth", 0),
        "child_ids": n.get("child_ids", []),
        "pattern": n.get("pattern"),
        "difficulty": n.get("difficulty"),
        "estimated_minutes": n.get("estimated_minutes"),
        "interview_importance": n.get("interview_importance"),
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
    # Roll up per track and per module
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
            "id": track["id"], "label": track["label"],
            "progress": _rollup_from_progress(track, progress_map, roadmap),
            "modules": modules,
        })
    return {"version": version, "tracks": result}


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
    status = "mastered" if conf >= 9 else "in_progress" if conf > 0 else "available"
    bucket = _bucket(conf, weakness)

    await db.knowledge_nodes.update_one(
        {"user_id": user["id"], "node_id": node_id, "roadmap_version": version},
        {"$set": {
            "user_id": user["id"], "node_id": node_id, "roadmap_version": version,
            "confidence": conf, "weakness_score": weakness,
            "mastery_percentage": mastery,
            "status": status, "revision_bucket": bucket,
            "updated_at": _now_iso(),
        }},
        upsert=True,
    )
    return {"ok": True, "node_id": node_id, "confidence": conf}


# ============ Version + Migration status ============

@router.get("/version")
async def get_version(user=Depends(get_current_user)):
    from server import db
    version = await _ensure_user_version(db, user["id"])
    return {"user_version": version, "current_version": CURRENT_VERSION}
