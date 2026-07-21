"""Thin LLM provider abstraction.

One method surface — `complete_json(system, prompt, provider, model, api_key,
temperature)` — so future providers (OpenAI, Claude) plug in without touching
the generation service. Uses `emergentintegrations.LlmChat` under the hood.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage

log = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Wraps provider SDK errors so callers can render a friendly message."""

    def __init__(self, message: str, *, kind: str = "unknown", status_code: Optional[int] = None):
        super().__init__(message)
        self.kind = kind
        self.status_code = status_code


def _classify(err: Exception) -> AIProviderError:
    """Bucket raw SDK exceptions into user-actionable kinds."""
    msg = str(err) or err.__class__.__name__
    low = msg.lower()
    if any(k in low for k in ("invalid api key", "api key not valid", "unauthorized", "401", "permission denied", "403")):
        return AIProviderError("Your Gemini API key was rejected. Please update it in Settings.",
                                kind="invalid_key", status_code=401)
    if "quota" in low or "rate" in low or "429" in low:
        return AIProviderError("Gemini rate/quota limit reached. Try again in a minute.",
                                kind="rate_limit", status_code=429)
    if any(k in low for k in ("timeout", "connect", "network", "dns", "temporarily unavailable", "503", "500")):
        return AIProviderError("Gemini is temporarily unreachable. Retry in a moment.",
                                kind="upstream", status_code=502)
    return AIProviderError(f"Gemini generation failed: {msg}", kind="unknown", status_code=500)


async def complete_json(
    *,
    system_message: str,
    prompt: str,
    provider: str,
    model_name: str,
    api_key: str,
    temperature: float = 0.7,
    session_id: str = "prepos-knowledge-gen",
) -> str:
    """Fire a single completion and return the raw text response.

    JSON-shape enforcement happens in `prompt_builder.parse_content()` — this
    layer stays provider-agnostic and only worries about I/O + error mapping.
    """
    if not api_key:
        raise AIProviderError(
            "Please configure your Gemini API Key in Settings.",
            kind="missing_key", status_code=400,
        )
    try:
        chat = (
            LlmChat(api_key=api_key, session_id=session_id, system_message=system_message)
            .with_model(provider, model_name)
        )
        # send_message is non-streaming — fine for a JSON one-shot we cache.
        response = await chat.send_message(UserMessage(text=prompt))
    except AIProviderError:
        raise
    except Exception as e:  # noqa: BLE001
        log.warning("LLM provider error (%s/%s): %s", provider, model_name, e)
        raise _classify(e)

    if isinstance(response, str):
        return response
    # emergentintegrations returns a str; but tolerate other shapes defensively.
    return str(response)
