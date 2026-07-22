"""Mentor Service — the orchestration layer.

Flow for a single `answer()` call:
  1. Load / create the conversation (persisted).
  2. Persist the user's message.
  3. Build the learner context (context_builder).
  4. Load AI config (provider / model / api_key) from user settings.
  5. Assemble system + user turn (mentor_prompt). Two modes:
       - "chat"   → free-form markdown reply
       - "lesson" → strict 9-card JSON, parsed and persisted as structured_content
  6. Call the LLM via `ai_service.complete_json` (reused — no duplication).
  7. Persist the assistant's reply, bump the conversation counters.
  8. Return (conversation, user_msg, assistant_msg, context_preview).

Streaming is not enabled yet but the architecture supports it — replace the
`complete_json` call with a streamed variant later (see `_call_llm`).
Everything else stays identical.
"""
from __future__ import annotations
import json
import logging
import re
from typing import Optional, Tuple

from ai_service import complete_json, AIProviderError

from . import conversation_store as store
from .context_builder import (
    build_context, serialize_context, current_topic_kb_block, public_preview,
)
from .mentor_prompt import (
    build_system_message, build_lesson_system_message,
    build_user_message, summarise_title,
)
from .models import MentorConversation, MentorMessage

log = logging.getLogger(__name__)

_HISTORY_TAIL = 16  # Number of past turns fed to the LLM.


async def _load_ai_config(db, user_id: str) -> dict:
    """Same shape as knowledge_generation._load_ai_config — kept independent
    so the mentor never depends on the KB module internals."""
    doc = await db.settings.find_one({"user_id": user_id}, {"_id": 0, "ai_config": 1}) or {}
    ai = doc.get("ai_config") or {}
    return {
        "provider": ai.get("provider") or "gemini",
        "model_name": ai.get("model_name") or "gemini-flash-latest",
        "api_key": ai.get("api_key") or None,
        "temperature": float(ai.get("temperature") if ai.get("temperature") is not None else 0.6),
    }


async def ensure_conversation(db, *, user_id: str,
                              conversation_id: Optional[str],
                              seed_message: Optional[str] = None,
                              topic_node_id: Optional[str] = None) -> MentorConversation:
    """Return an existing conversation or create a new one with a seed title."""
    if conversation_id:
        existing = await store.get_conversation(
            db, conversation_id=conversation_id, user_id=user_id,
        )
        if existing:
            return existing
    title = summarise_title(seed_message or "New conversation")
    return await store.create_conversation(
        db, user_id=user_id, title=title, topic_node_id=topic_node_id,
    )


async def _call_llm(*, system_message: str, prompt: str, ai_config: dict,
                    session_id: str) -> str:
    """Single LLM hop — reuses the KB-tested `complete_json` provider shim.

    When streaming lands, swap this for `stream_completion(...)` (a future
    generator variant of complete_json) and expose an async generator from
    `answer()`. Route can then be upgraded to Server-Sent Events without
    touching the rest of the stack.
    """
    return await complete_json(
        system_message=system_message,
        prompt=prompt,
        provider=ai_config["provider"],
        model_name=ai_config["model_name"],
        api_key=ai_config["api_key"],
        temperature=ai_config["temperature"],
        session_id=session_id,
    )


async def answer(db, *, user_id: str, user_message: str,
                 conversation_id: Optional[str],
                 topic_node_id: Optional[str] = None,
                 response_style: str = "chat") -> Tuple[
                     MentorConversation, MentorMessage, MentorMessage, dict,
                 ]:
    """The single public entry-point for a mentor turn.

    `response_style="chat"`   → free-form markdown reply (default).
    `response_style="lesson"` → strict 9-card JSON persisted as
        `assistant_msg.structured_content`. `content` still holds the raw JSON
        text so the transcript survives deserialisation issues.

    Any future feature (mock interviews, revision planner, etc.) can call this
    directly — either persistently (with a conversation_id) or ephemerally by
    creating a throwaway conversation.
    """
    style = response_style if response_style in ("chat", "lesson") else "chat"

    # 1. Conversation.
    convo = await ensure_conversation(
        db, user_id=user_id, conversation_id=conversation_id,
        seed_message=user_message, topic_node_id=topic_node_id,
    )
    effective_topic = topic_node_id or convo.topic_node_id

    # 2. Persist user turn immediately.
    user_msg = await store.add_message(
        db, conversation_id=convo.id, user_id=user_id, role="user",
        content=user_message, topic_node_id=effective_topic, style=style,
    )
    await store.touch_conversation(
        db, conversation_id=convo.id, user_id=user_id,
        preview=f"You: {user_message}", delta_count=1,
    )

    # 3. Context.
    context = await build_context(db, user_id=user_id, node_id=effective_topic)
    context_block = serialize_context(context)
    if style == "lesson":
        system_message = build_lesson_system_message(context_block)
    else:
        system_message = build_system_message(context_block)
    kb_block = current_topic_kb_block(context)

    # 4. Config.
    cfg = await _load_ai_config(db, user_id)
    if not cfg["api_key"]:
        raise AIProviderError(
            "Please configure your Gemini API Key in Settings so the mentor can respond.",
            kind="missing_key", status_code=400,
        )

    # 5. Prior transcript (short-term memory) — skip in lesson mode because a
    # lesson is a single-shot structured emit.
    history = []
    if style == "chat":
        history = await store.recent_messages(
            db, conversation_id=convo.id, user_id=user_id, limit=_HISTORY_TAIL,
        )
        history = [m for m in history if m.id != user_msg.id]

    prompt = build_user_message(
        new_message=user_message, history=history, node_kb_block=kb_block,
    )

    # 6. LLM call.
    raw = await _call_llm(
        system_message=system_message, prompt=prompt, ai_config=cfg,
        session_id=f"mentor::{convo.id}",
    )
    reply = (raw or "").strip()
    if not reply:
        raise AIProviderError(
            "Mentor returned an empty reply. Please retry.",
            kind="empty_response", status_code=502,
        )

    structured = None
    if style == "lesson":
        structured = _parse_lesson_json(reply)
        # If parsing failed, fall back to chat mode gracefully — the raw text
        # still gets persisted so the user sees SOMETHING useful.
        if structured is None:
            style = "chat"

    # 7. Persist assistant turn.
    assistant_msg = await store.add_message(
        db, conversation_id=convo.id, user_id=user_id, role="assistant",
        content=reply, topic_node_id=effective_topic, style=style,
        structured_content=structured,
    )
    await store.touch_conversation(
        db, conversation_id=convo.id, user_id=user_id,
        preview=f"Mentor: {reply}", delta_count=1,
    )
    fresh = await store.get_conversation(db, conversation_id=convo.id, user_id=user_id)
    if fresh and fresh.message_count <= 2:
        await store.rename_conversation(
            db, conversation_id=convo.id, user_id=user_id,
            title=summarise_title(user_message),
        )
        fresh = await store.get_conversation(db, conversation_id=convo.id, user_id=user_id)

    return fresh or convo, user_msg, assistant_msg, public_preview(context)


_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _parse_lesson_json(raw: str) -> Optional[dict]:
    """Best-effort JSON parse — Gemini sometimes wraps output in ``` fences."""
    # 1. Direct.
    try:
        return json.loads(raw)
    except Exception:
        pass
    # 2. Extract from fenced block.
    m = _JSON_FENCE.search(raw)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # 3. First-brace to last-brace slice.
    if "{" in raw and "}" in raw:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        try:
            return json.loads(raw[start:end])
        except Exception:
            pass
    log.warning("mentor_service: failed to parse lesson JSON; falling back to chat mode")
    return None
