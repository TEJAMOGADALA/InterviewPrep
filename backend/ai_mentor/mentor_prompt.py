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

**PREREQUISITE-AWARE REASONING — HARD RULE**:
Before recommending ANY next topic you MUST check the learner's prerequisite
chain (provided in the LEARNER CONTEXT block).
  • If prerequisites are incomplete, recommend the FIRST INCOMPLETE prerequisite,
    NOT the advanced topic.
  • Never leap over the roadmap. Example:
      – WRONG: Arrays → Trees (skips Prefix Sum, Sliding Window, Two Pointers,
        Hashing, Binary Search, Stack/Queue, Linked List).
      – RIGHT: Arrays → Prefix Sum → Sliding Window → Two Pointers → Strings →
        Hashing → Binary Search → Stack → Queue → Linked List → Trees.
  • Example (LLD):
      – WRONG: LLD confidence low → jump to Chess Design.
      – RIGHT: OOP Basics → Classes/Objects → Inheritance → Composition →
        Abstraction → Polymorphism → SOLID → UML → Design Patterns →
        Parking Lot → Library → Chess.
  • When you list what to study next, ALWAYS anchor to the recommended path
     already computed for the learner (see "RECOMMENDED NEXT STEP" in context).

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


# ---------------------------------------------------------------------------
# Structured "lesson" mode — the 9-card format specified in the product brief.
# ---------------------------------------------------------------------------

LESSON_JSON_SCHEMA_HINT = """
{
  "executive_summary": {
    "why_it_matters": "string — why this topic matters for the learner right now",
    "target_company_relevance": "string — how it maps to their target companies",
    "why_next": "string — why this is the correct next step given their progress"
  },
  "core_concept": {
    "definition": "string — one-line precise definition",
    "explanation": "string — 3-6 sentences",
    "visualization": "string — describe a mental model or diagram in words (ASCII allowed)"
  },
  "internal_working": {
    "flow": "string — step by step how it works internally",
    "architecture": "string — components / data structures / invariants"
  },
  "implementation": {
    "language": "Java",
    "code": "string — clean idiomatic Java snippet (no dependencies)",
    "explanation": "string — 2-4 lines of what the code does"
  },
  "complexity": {
    "time": "string — Big-O with justification",
    "space": "string — Big-O with justification",
    "tradeoffs": "string — 2-3 tradeoffs vs alternatives"
  },
  "interview_insights": {
    "companies": [
      {"name": "Google", "signal": "what a Google interviewer probes"},
      {"name": "Amazon", "signal": "what an Amazon interviewer probes"}
    ],
    "common_questions": ["string", "string", "string"]
  },
  "common_mistakes": {
    "mistakes": ["string", "string", "string"],
    "edge_cases": ["string", "string"]
  },
  "practice_plan": {
    "easy":   [{"title": "problem name", "why": "why this problem"}],
    "medium": [{"title": "problem name", "why": "why this problem"}],
    "hard":   [{"title": "problem name", "why": "why this problem"}]
  },
  "next_learning_path": {
    "next_topic": {"label": "string", "node_id": "string or null"},
    "reason": "string — why this is next based on roadmap + progress",
    "sequence": ["Topic A", "Topic B", "Topic C"]
  }
}
""".strip()


LESSON_INSTRUCTION = f"""**RESPOND WITH VALID JSON ONLY** — no prose before or
after. Match this schema EXACTLY (all keys required, empty arrays / short
strings allowed but keys must be present):

{LESSON_JSON_SCHEMA_HINT}

Guidance while filling in the cards:
  * Ground every recommendation in the LEARNER CONTEXT block above — quote
    weak topics, mission focus, recent activity by name.
  * The `next_learning_path` MUST respect the prerequisite chain. If the
    learner has an incomplete prerequisite, that IS the next step (not the
    advanced topic they asked about).
  * `implementation.code` should be idiomatic Java. Runnable is a bonus but
    not required.
  * `practice_plan` entries must be real interview-style problems.
  * `interview_insights.companies` should highlight ONLY companies the learner
    is targeting when possible; fall back to Google/Amazon/Meta otherwise.
  * Keep every string tight — one sentence unless the field explicitly needs
    more. This is a lesson card, not a blog post.
""".strip()


def build_lesson_system_message(context_block: str) -> str:
    """System prompt for structured-lesson mode. Same identity + prereq rules
    but with strict JSON-output instruction appended."""
    core = build_system_message(context_block)
    return core + "\n\n---\n" + LESSON_INSTRUCTION
