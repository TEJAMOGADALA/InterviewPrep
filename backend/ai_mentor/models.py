"""Pydantic models for AI Mentor.

Kept lean — the mentor's persisted state is only conversations + messages.
Every reasoning input is derived on the fly by `context_builder` so we never
duplicate data owned by other subsystems.
"""
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


Role = Literal["user", "assistant", "system"]
ResponseStyle = Literal["chat", "lesson"]


class MentorMessage(BaseModel):
    """One message in a mentor conversation.

    Persisted 1:1 to Mongo `mentor_messages`. `structured_content` is populated
    only when the message was produced in `lesson` mode — it holds the parsed
    9-card JSON so the UI can render cards on reload without re-calling Gemini.
    """
    id: str
    conversation_id: str
    user_id: str
    role: Role
    content: str
    topic_node_id: Optional[str] = None
    style: Optional[ResponseStyle] = "chat"
    structured_content: Optional[dict] = None
    created_at: str


class MentorConversation(BaseModel):
    """A user's chat thread. Kept small — messages live in their own collection."""
    id: str
    user_id: str
    title: str
    topic_node_id: Optional[str] = None
    message_count: int = 0
    last_message_preview: Optional[str] = None
    created_at: str
    updated_at: str


# ---------- Route payloads ----------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    conversation_id: Optional[str] = None
    topic_node_id: Optional[str] = None  # If the UI already knows which node the user is on.
    response_style: Optional[ResponseStyle] = "chat"  # chat | lesson (9-card structured)


class NewChatRequest(BaseModel):
    topic_node_id: Optional[str] = None
    seed_title: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: MentorMessage         # The assistant's reply.
    user_message: MentorMessage    # Echoed back so the client can reconcile without another fetch.
    conversation: MentorConversation
    context_summary: Optional[dict] = None  # A compact preview so the UI can show what the mentor saw.


class ConversationListItem(BaseModel):
    id: str
    title: str
    topic_node_id: Optional[str] = None
    message_count: int
    last_message_preview: Optional[str] = None
    updated_at: str


class ConversationDetail(BaseModel):
    conversation: MentorConversation
    messages: List[MentorMessage]
