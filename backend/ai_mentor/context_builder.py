"""Context Builder for AI Mentor.

The mentor's power comes from grounding every answer in the learner's actual
state. This module assembles a compact snapshot (~1–2 KB) that fits in the
system prompt without exploding token cost.

Signals collected:
  * User profile (name, target companies, target date, hours/week, skill self-rating)
  * Roadmap version + current node (if the UI passed one)
  * Aggregate progress (completion %, mastery, hours remaining)
  * Weak topics (top 5 by weakness_score / low confidence)
  * Strong topics (top 5 by confidence / mastery)
  * Today's mission (if any)
  * Revision queue (top 5 due)
  * Recent activity (last 6 events)
  * Recently generated KB nodes (last 5) — signal of what user was studying
  * Cached KB content for the CURRENT topic — injected verbatim if node_id given

Everything here is READ-ONLY. No side effects, no writes. Failure of any one
signal degrades gracefully to an empty section — the mentor still works even
if a fresh user has no data yet.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from roadmap import get_roadmap, CURRENT_VERSION
from knowledge_generation import read_cache as read_kb_cache

log = logging.getLogger(__name__)

_TOP_N = 5
_ACTIVITY_LIMIT = 6
_KB_RECENT = 5


async def _load_user_profile(db, user_id: str) -> Dict[str, Any]:
    user = await db.users.find_one(
        {"id": user_id},
        {"_id": 0, "id": 1, "email": 1, "name": 1, "role": 1, "roadmap_version": 1},
    ) or {}
    settings = await db.settings.find_one(
        {"user_id": user_id},
        {"_id": 0, "target_companies": 1, "target_date": 1, "study_hours_per_week": 1,
         "skill_level": 1, "position": 1},
    ) or {}
    onboarding = await db.onboarding.find_one(
        {"user_id": user_id},
        {"_id": 0, "target_companies": 1, "target_date": 1, "study_hours_per_week": 1,
         "skill_level": 1, "position": 1, "focus_areas": 1},
    ) or {}
    return {
        "name": user.get("name"),
        "email": user.get("email"),
        "target_companies": settings.get("target_companies") or onboarding.get("target_companies") or [],
        "position": settings.get("position") or onboarding.get("position"),
        "target_date": settings.get("target_date") or onboarding.get("target_date"),
        "study_hours_per_week": settings.get("study_hours_per_week") or onboarding.get("study_hours_per_week"),
        "skill_level": settings.get("skill_level") or onboarding.get("skill_level"),
        "focus_areas": onboarding.get("focus_areas") or [],
    }


async def _load_progress(db, user_id: str) -> List[Dict[str, Any]]:
    """All `knowledge_nodes` rows for the user."""
    cur = db.knowledge_nodes.find({"user_id": user_id}, {"_id": 0})
    return await cur.to_list(length=1000)


def _weak_and_strong(progress: List[Dict[str, Any]], roadmap) -> Dict[str, List[Dict[str, Any]]]:
    """Split into weak/strong buckets using confidence + mastery.

    Weak = low confidence OR high weakness_score AND has_progress.
    Strong = high confidence + mastery.
    We look up labels from the roadmap so the mentor can refer to them by name.
    """
    def label_for(nid: str) -> str:
        n = roadmap.get(nid)
        return n["label"] if n else nid

    scored = []
    for p in progress:
        conf = float(p.get("confidence") or 0)
        mastery = float(p.get("mastery_percentage") or 0)
        weak = float(p.get("weakness_score") or 0)
        # Skip empty rows.
        if conf == 0 and mastery == 0 and weak == 0 and not p.get("attempts"):
            continue
        scored.append({
            "node_id": p["node_id"],
            "label": label_for(p["node_id"]),
            "confidence": round(conf, 1),
            "mastery": round(mastery, 1),
            "weakness": round(weak, 1),
            "status": p.get("status"),
            "revision_bucket": p.get("revision_bucket"),
        })
    weak = sorted(
        [s for s in scored if s["confidence"] < 6 or s["weakness"] > 50],
        key=lambda s: (s["confidence"], -s["weakness"]),
    )[:_TOP_N]
    strong = sorted(
        [s for s in scored if s["confidence"] >= 7 and s["mastery"] >= 60],
        key=lambda s: (-s["confidence"], -s["mastery"]),
    )[:_TOP_N]
    return {"weak": weak, "strong": strong}


async def _load_todays_mission(db, user_id: str) -> Optional[Dict[str, Any]]:
    today = datetime.now(timezone.utc).date().isoformat()
    doc = await db.daily_missions.find_one(
        {"user_id": user_id, "date": today},
        {"_id": 0, "id": 1, "date": 1, "tasks": 1, "status": 1, "focus_topic": 1},
    )
    if not doc:
        return None
    tasks = doc.get("tasks") or []
    done = sum(1 for t in tasks if t.get("completed"))
    return {
        "date": doc["date"],
        "status": doc.get("status"),
        "focus_topic": doc.get("focus_topic"),
        "tasks_total": len(tasks),
        "tasks_done": done,
        "task_titles": [t.get("title") for t in tasks if t.get("title")][:6],
    }


async def _load_revision_queue(db, user_id: str, roadmap) -> List[Dict[str, Any]]:
    """Top-N nodes whose next_revision is in the past."""
    now = datetime.now(timezone.utc).isoformat()
    cur = db.knowledge_nodes.find(
        {"user_id": user_id, "next_revision": {"$lte": now, "$ne": None}},
        {"_id": 0, "node_id": 1, "next_revision": 1, "confidence": 1},
    ).sort("next_revision", 1).limit(_TOP_N)
    rows = await cur.to_list(length=_TOP_N)
    out = []
    for r in rows:
        n = roadmap.get(r["node_id"])
        out.append({
            "node_id": r["node_id"],
            "label": n["label"] if n else r["node_id"],
            "due": r.get("next_revision"),
            "confidence": r.get("confidence"),
        })
    return out


async def _load_recent_activity(db, user_id: str) -> List[Dict[str, Any]]:
    cur = db.activity_events.find(
        {"user_id": user_id},
        {"_id": 0, "type": 1, "title": 1, "description": 1, "ts": 1},
    ).sort("ts", -1).limit(_ACTIVITY_LIMIT)
    return await cur.to_list(length=_ACTIVITY_LIMIT)


async def _load_recent_kb(db, user_id: str) -> List[Dict[str, Any]]:
    """Most recently GENERATED KB entries — a signal of what the user was studying."""
    cur = db.knowledge_content.find(
        {"generated_by": user_id},
        {"_id": 0, "node_id": 1, "generated_at": 1, "updated_at": 1},
    ).sort("updated_at", -1).limit(_KB_RECENT)
    return await cur.to_list(length=_KB_RECENT)


async def _current_topic_block(db, roadmap, *, node_id: Optional[str],
                               version: str) -> Optional[Dict[str, Any]]:
    """Fetch the roadmap node metadata + cached KB content (if any).

    Returned dict is later stringified into the KB block that gets pushed into
    the user turn of the prompt. Prerequisites/related are shown as labels so
    the model can chain answers ("since you already know X …").
    """
    if not node_id:
        return None
    node = roadmap.get(node_id)
    if not node:
        return None
    kb = await read_kb_cache(db, node_id=node_id, roadmap_version=version) or {}
    track = roadmap.find_track(node_id)
    return {
        "id": node["id"],
        "label": node["label"],
        "description": node.get("description"),
        "track": {"id": track["id"], "label": track["label"]} if track else None,
        "difficulty": node.get("difficulty"),
        "tags": node.get("tags", []),
        "prerequisites": [
            {"id": p["id"], "label": p["label"]}
            for p in roadmap.prerequisites(node_id)
        ],
        "related": [
            {"id": r["id"], "label": r["label"]}
            for r in roadmap.related(node_id)
        ],
        "kb_available": bool(kb.get("theory")),
        "kb": {
            "theory": kb.get("theory"),
            "examples": (kb.get("examples") or [])[:3],
            "interview_tips": (kb.get("interview_tips") or [])[:5],
            "common_mistakes": (kb.get("common_mistakes") or [])[:5],
            "flashcards": (kb.get("flashcards") or [])[:6],
            "related_topics": (kb.get("related_topics") or [])[:5],
            "prerequisites": (kb.get("prerequisites") or [])[:5],
        } if kb.get("theory") else None,
    }


async def _summary_progress(db, user_id: str, roadmap) -> Dict[str, Any]:
    """Cheap overall stats — completion %, hours remaining."""
    progress = await db.knowledge_nodes.count_documents({"user_id": user_id})
    completed = await db.knowledge_nodes.count_documents(
        {"user_id": user_id, "status": {"$in": ["completed", "mastered"]}},
    )
    total_topics = sum(1 for _ in roadmap.all_nodes())
    return {
        "total_roadmap_nodes": total_topics,
        "nodes_touched": progress,
        "nodes_completed": completed,
    }


async def _load_recent_notes(db, user_id: str, roadmap) -> List[Dict[str, Any]]:
    """User's most recent personal notes (from knowledge_nodes.notes)."""
    cur = db.knowledge_nodes.find(
        {"user_id": user_id, "notes": {"$ne": None, "$exists": True}},
        {"_id": 0, "node_id": 1, "notes": 1, "updated_at": 1},
    ).sort("updated_at", -1).limit(_TOP_N)
    rows = await cur.to_list(length=_TOP_N)
    out = []
    for r in rows:
        n = roadmap.get(r["node_id"])
        note = (r.get("notes") or "").strip()
        if not note:
            continue
        out.append({
            "node_id": r["node_id"],
            "label": n["label"] if n else r["node_id"],
            "note_preview": note[:200],
        })
    return out


# ---------- Serialisers ----------

def _fmt_list(items: List[str]) -> str:
    return ", ".join(items) if items else "—"


def _fmt_kb_block(current_topic: Optional[Dict[str, Any]]) -> Optional[str]:
    """Serialise the current-topic KB content as a compact markdown block."""
    if not current_topic or not current_topic.get("kb"):
        return None
    kb = current_topic["kb"]
    lines: List[str] = [
        f"**Topic**: {current_topic['label']}  ({current_topic.get('difficulty') or 'unknown difficulty'})",
    ]
    if kb.get("theory"):
        theory = kb["theory"]
        if isinstance(theory, dict):
            beg = (theory.get("beginner") or "").strip()
            deep = (theory.get("deep") or "").strip()
            if beg:
                lines.append(f"**Beginner theory**: {beg[:900]}")
            if deep:
                lines.append(f"**Deep theory**: {deep[:1200]}")
        elif isinstance(theory, str):
            lines.append(f"**Theory**: {theory[:1500]}")
    if kb.get("interview_tips"):
        tips = [str(t).strip() for t in kb["interview_tips"] if t][:5]
        if tips:
            lines.append("**Interview tips**: " + " | ".join(tips))
    if kb.get("common_mistakes"):
        mistakes = [str(m).strip() for m in kb["common_mistakes"] if m][:4]
        if mistakes:
            lines.append("**Common mistakes**: " + " | ".join(mistakes))
    if kb.get("examples"):
        ex = [str(e).strip()[:180] for e in kb["examples"] if e][:2]
        if ex:
            lines.append("**Examples**: " + " ; ".join(ex))
    if kb.get("flashcards"):
        cards: List[str] = []
        for c in kb["flashcards"][:4]:
            if isinstance(c, dict):
                q = (c.get("question") or c.get("q") or "").strip()
                a = (c.get("answer") or c.get("a") or "").strip()
                if q and a:
                    cards.append(f"Q: {q[:80]} → A: {a[:120]}")
        if cards:
            lines.append("**Flashcards**: " + " | ".join(cards))
    return "\n".join(lines)


def _serialize_context(context: Dict[str, Any]) -> str:
    """Pack the context dict into a compact markdown block for the system prompt."""
    p = context.get("profile") or {}
    s = context.get("summary") or {}
    ws = context.get("focus") or {}
    mission = context.get("todays_mission")
    revisions = context.get("revision_queue") or []
    activity = context.get("recent_activity") or []
    recent_kb = context.get("recent_kb") or []
    current = context.get("current_topic")
    notes = context.get("recent_notes") or []

    lines: List[str] = []

    # Profile
    lines.append(
        f"* **Learner**: {p.get('name') or 'Unknown'}"
        f" · Position: {p.get('position') or 'n/a'}"
        f" · Skill self-rating: {p.get('skill_level') or 'n/a'}/10"
        f" · Hours/week: {p.get('study_hours_per_week') or 'n/a'}"
        f" · Target date: {p.get('target_date') or 'n/a'}"
    )
    tc = p.get("target_companies") or []
    lines.append(f"* **Target companies**: {_fmt_list(tc)}")
    if p.get("focus_areas"):
        lines.append(f"* **Declared focus areas**: {_fmt_list(p['focus_areas'])}")

    # Summary
    lines.append(
        f"* **Roadmap progress**: {s.get('nodes_completed', 0)} completed · "
        f"{s.get('nodes_touched', 0)} touched · "
        f"{s.get('total_roadmap_nodes', 0)} total nodes"
    )

    # Weak / strong
    weak = ws.get("weak") or []
    strong = ws.get("strong") or []
    if weak:
        lines.append("* **Weak topics** (call these out when relevant): " +
                     ", ".join(f"{w['label']} (conf {w['confidence']})" for w in weak))
    if strong:
        lines.append("* **Strong topics** (safe to build on): " +
                     ", ".join(f"{w['label']} (conf {w['confidence']})" for w in strong))

    # Mission
    if mission:
        lines.append(
            f"* **Today's mission**: {mission.get('tasks_done', 0)}/{mission.get('tasks_total', 0)} tasks"
            f" · focus: {mission.get('focus_topic') or 'general'}"
            f" · titles: {_fmt_list(mission.get('task_titles') or [])}"
        )
    else:
        lines.append("* **Today's mission**: not yet generated")

    # Revision queue
    if revisions:
        lines.append(
            "* **Revision queue** (due now): " +
            ", ".join(f"{r['label']}" for r in revisions)
        )

    # Recent activity
    if activity:
        rec = [f"{a.get('title') or a.get('type') or 'event'}" for a in activity][:5]
        lines.append("* **Recent activity**: " + _fmt_list(rec))

    # Recent KB
    if recent_kb:
        rec_kb_lbl: List[str] = []
        for r in recent_kb:
            rec_kb_lbl.append(r.get("node_id"))
        lines.append("* **Recently studied (KB generated)**: " + _fmt_list(rec_kb_lbl))

    # Notes
    if notes:
        note_lines = [f"{n['label']}: {n['note_preview']}" for n in notes][:3]
        lines.append("* **Recent personal notes**: " + " ; ".join(note_lines))

    # Current topic
    if current:
        lines.append(
            f"* **Current topic in view**: {current['label']} (id `{current['id']}`)"
            f" · track: {(current.get('track') or {}).get('label') or 'n/a'}"
            f" · KB cached: {'yes' if current.get('kb_available') else 'no'}"
        )
        pre = [p["label"] for p in (current.get("prerequisites") or [])][:5]
        rel = [r["label"] for r in (current.get("related") or [])][:5]
        if pre:
            lines.append("  * Prerequisites: " + _fmt_list(pre))
        if rel:
            lines.append("  * Related topics: " + _fmt_list(rel))

    return "\n".join(lines)


# ---------- Public API ----------

async def build_context(db, *, user_id: str, node_id: Optional[str] = None) -> Dict[str, Any]:
    """Assemble the full mentor context.

    Returns a structured dict — one caller (`mentor_service`) serialises it
    for the system prompt, another caller (route) sends a slim preview back
    to the UI so users can see what the mentor knows about them.
    """
    # Version + roadmap engine.
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "roadmap_version": 1}) or {}
    version = user.get("roadmap_version") or CURRENT_VERSION
    roadmap = get_roadmap(version)

    # Parallel-ish loads (motor is async, but await sequentially since motor
    # already dispatches on a single event loop).
    profile = await _load_user_profile(db, user_id)
    progress = await _load_progress(db, user_id)
    focus = _weak_and_strong(progress, roadmap)
    mission = await _load_todays_mission(db, user_id)
    revisions = await _load_revision_queue(db, user_id, roadmap)
    activity = await _load_recent_activity(db, user_id)
    recent_kb = await _load_recent_kb(db, user_id)
    current = await _current_topic_block(db, roadmap, node_id=node_id, version=version)
    summary = await _summary_progress(db, user_id, roadmap)
    notes = await _load_recent_notes(db, user_id, roadmap)

    return {
        "version": version,
        "profile": profile,
        "summary": summary,
        "focus": focus,
        "todays_mission": mission,
        "revision_queue": revisions,
        "recent_activity": activity,
        "recent_kb": recent_kb,
        "current_topic": current,
        "recent_notes": notes,
    }


def serialize_context(context: Dict[str, Any]) -> str:
    """Public: turn the context dict into the markdown block for the LLM."""
    return _serialize_context(context)


def current_topic_kb_block(context: Dict[str, Any]) -> Optional[str]:
    """Public: extract the current-topic KB block (goes in the user turn)."""
    return _fmt_kb_block(context.get("current_topic"))


def public_preview(context: Dict[str, Any]) -> Dict[str, Any]:
    """A slim snapshot the frontend can render as "mentor knows about you"."""
    profile = context.get("profile") or {}
    focus = context.get("focus") or {}
    mission = context.get("todays_mission")
    current = context.get("current_topic")
    return {
        "name": profile.get("name"),
        "target_companies": profile.get("target_companies") or [],
        "position": profile.get("position"),
        "weak_topics": [w["label"] for w in (focus.get("weak") or [])],
        "strong_topics": [w["label"] for w in (focus.get("strong") or [])],
        "todays_mission": {
            "focus_topic": (mission or {}).get("focus_topic"),
            "progress": f"{(mission or {}).get('tasks_done', 0)}/{(mission or {}).get('tasks_total', 0)}" if mission else None,
        } if mission else None,
        "current_topic": {
            "id": current["id"], "label": current["label"], "kb_available": current.get("kb_available"),
        } if current else None,
        "revision_due_count": len(context.get("revision_queue") or []),
    }
