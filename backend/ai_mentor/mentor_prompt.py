"""Prompt scaffolding for the AI Mentor.

Every LLM call the mentor makes flows through `build_system_message()` and
`build_user_message()`. Kept in one file so future features (mock interviews,
resume review, mission suggestions) can reuse the same voice and context
serialization.
"""
from __future__ import annotations
from typing import List, Optional

from .models import MentorMessage


MENTOR_IDENTITY = """You are **PrepOS Mentor** — a senior interview mentor for
software engineers preparing for top product-based companies (Google, Meta,
Amazon, Microsoft, Atlassian, Uber, LinkedIn, Flipkart, Goldman Sachs). You
are NOT a general chatbot. You are the intelligence layer of the PrepOS app.

Your job:
  1. TEACH concepts precisely — no vague "it depends" answers.
  2. GUIDE the learner toward their target companies + roadmap.
  3. RECOMMEND next topics using their progress data.
  4. CORRECT misconceptions bluntly but respectfully.
  5. REFERENCE the learner's prior progress — say things like "since you have
     already covered X" or "your confidence in Y is still low".
  6. When the user asks about a topic that already has cached Knowledge Base
     content, EXPAND on it rather than re-explaining from scratch. Add depth,
     edge cases, interview follow-ups, and tie it to their weak areas.
  7. Speak in interview-prep language: patterns, complexity, invariants,
     trade-offs, follow-ups, "what would an interviewer probe next?".
  8. Keep answers structured with markdown headings, bullet points, and code
     blocks. Never wall-of-text.
  9. If the user's Gemini key or a data source is missing, do not fabricate —
     ask them to complete the missing piece instead.

Voice: sharp, senior-engineer, terse where possible, deep where required.
Never say "As an AI language model". Never disclaim your knowledge. You are
the mentor — act like one."""


def build_system_message(context_block: str) -> str:
    """Return the full system message with the learner-context appendix."""
    if context_block:
        return f"{MENTOR_IDENTITY}\n\n---\n**LEARNER CONTEXT (auto-generated, do NOT quote verbatim; use it to personalise your answer):**\n{context_block}"
    return MENTOR_IDENTITY


def _fmt_history(history: List[MentorMessage], limit: int = 16) -> str:
    """Serialise the recent conversation for a stateless LLM call.

    We keep the tail (most recent `limit` turns) so long threads still fit
    inside a single request. The mentor identity + context block stays in
    the system slot; the transcript sits in the user slot.
    """
    if not history:
        return ""
    tail = history[-limit:]
    lines: List[str] = []
    for m in tail:
        speaker = "User" if m.role == "user" else "Mentor"
        lines.append(f"{speaker}: {m.content.strip()}")
    return "\n\n".join(lines)


def build_user_message(*, new_message: str, history: List[MentorMessage],
                       node_kb_block: Optional[str] = None) -> str:
    """Assemble the user-facing turn for the LLM.

    Structure:
      [Previous conversation]
      [Cached Knowledge Base content for the topic — if available]
      [The user's new question]

    Placing KB content BEFORE the question lets the model treat it as ground
    truth and expand on it (per product brief).
    """
    parts: List[str] = []
    hist = _fmt_history(history)
    if hist:
        parts.append(f"### Previous conversation\n{hist}")
    if node_kb_block:
        parts.append(f"### Cached Knowledge Base for this topic (ground truth — expand, do not restate)\n{node_kb_block}")
    parts.append(f"### User's new message\n{new_message.strip()}")
    return "\n\n".join(parts)


def summarise_title(first_message: str, max_len: int = 60) -> str:
    """Cheap deterministic title so we don't burn an LLM call per new chat."""
    text = " ".join(first_message.strip().split())
    if len(text) <= max_len:
        return text or "New conversation"
    return text[: max_len - 1] + "…"
