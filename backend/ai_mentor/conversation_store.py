"""Persistence layer for AI Mentor.

MongoDB-only; two collections:
  * mentor_conversations — one document per chat thread
  * mentor_messages      — one document per turn

Kept as pure CRUD so `mentor_service` never talks to Mongo directly. Makes
future migrations (e.g. move messages to a vector store) painless.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from .models import MentorConversation, MentorMessage

CONV_COLL = "mentor_conversations"
MSG_COLL = "mentor_messages"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


# ---------- Conversations ----------

async def create_conversation(db, *, user_id: str, title: str,
                              topic_node_id: Optional[str] = None) -> MentorConversation:
    now = _now_iso()
    doc = {
        "id": _new_id(),
        "user_id": user_id,
        "title": title or "New conversation",
        "topic_node_id": topic_node_id,
        "message_count": 0,
        "last_message_preview": None,
        "created_at": now,
        "updated_at": now,
    }
    await db[CONV_COLL].insert_one(doc)
    doc.pop("_id", None)
    return MentorConversation(**doc)


async def get_conversation(db, *, conversation_id: str, user_id: str) -> Optional[MentorConversation]:
    doc = await db[CONV_COLL].find_one(
        {"id": conversation_id, "user_id": user_id},
        {"_id": 0},
    )
    return MentorConversation(**doc) if doc else None


async def list_conversations(db, *, user_id: str, limit: int = 40) -> List[MentorConversation]:
    cur = db[CONV_COLL].find(
        {"user_id": user_id},
        {"_id": 0},
    ).sort("updated_at", -1).limit(limit)
    docs = await cur.to_list(length=limit)
    return [MentorConversation(**d) for d in docs]


async def delete_conversation(db, *, conversation_id: str, user_id: str) -> bool:
    res = await db[CONV_COLL].delete_one({"id": conversation_id, "user_id": user_id})
    if res.deleted_count:
        # Cascade-delete the messages too so we don't leak orphans.
        await db[MSG_COLL].delete_many({"conversation_id": conversation_id, "user_id": user_id})
        return True
    return False


async def touch_conversation(db, *, conversation_id: str, user_id: str,
                             preview: str, delta_count: int = 1) -> None:
    """Bump updated_at + message counter + preview snippet."""
    await db[CONV_COLL].update_one(
        {"id": conversation_id, "user_id": user_id},
        {
            "$set": {
                "updated_at": _now_iso(),
                "last_message_preview": preview[:180],
            },
            "$inc": {"message_count": delta_count},
        },
    )


async def rename_conversation(db, *, conversation_id: str, user_id: str, title: str) -> None:
    await db[CONV_COLL].update_one(
        {"id": conversation_id, "user_id": user_id},
        {"$set": {"title": title, "updated_at": _now_iso()}},
    )


# ---------- Messages ----------

async def add_message(db, *, conversation_id: str, user_id: str,
                      role: str, content: str,
                      topic_node_id: Optional[str] = None,
                      style: Optional[str] = "chat",
                      structured_content: Optional[dict] = None) -> MentorMessage:
    doc = {
        "id": _new_id(),
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": role,
        "content": content,
        "topic_node_id": topic_node_id,
        "style": style,
        "structured_content": structured_content,
        "created_at": _now_iso(),
    }
    await db[MSG_COLL].insert_one(doc)
    doc.pop("_id", None)
    return MentorMessage(**doc)


async def list_messages(db, *, conversation_id: str, user_id: str,
                        limit: int = 200) -> List[MentorMessage]:
    cur = db[MSG_COLL].find(
        {"conversation_id": conversation_id, "user_id": user_id},
        {"_id": 0},
    ).sort("created_at", 1).limit(limit)
    docs = await cur.to_list(length=limit)
    return [MentorMessage(**d) for d in docs]


async def recent_messages(db, *, conversation_id: str, user_id: str,
                          limit: int = 20) -> List[MentorMessage]:
    """Chronological tail — used to give the LLM short-term memory."""
    cur = db[MSG_COLL].find(
        {"conversation_id": conversation_id, "user_id": user_id},
        {"_id": 0},
    ).sort("created_at", -1).limit(limit)
    docs = await cur.to_list(length=limit)
    docs.reverse()
    return [MentorMessage(**d) for d in docs]
