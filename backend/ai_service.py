"""Thin LLM provider abstraction.

One method surface — `complete_json(system, prompt, provider, model, api_key,
temperature)` — so future providers (OpenAI, Claude) plug in without touching
the generation service. Uses `google.genai` SDK under the hood.

Includes an automatic Emergent LLM key fallback so a user's own-key rate-limit
or deprecated model never turns the app into a paperweight.
"""
from __future__ import annotations
import logging
import os
import json
import re
from google import genai
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

# Emergent LLM key powers the fallback whenever the caller's own key trips a
# quota / rate-limit / deprecated-model wall. This is opt-in per deployment —
# unset the env var to disable the fallback entirely.
_EMERGENT_KEY = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
_EMERGENT_MODEL = (os.environ.get("EMERGENT_LLM_MODEL") or "gemini-2.5-flash").strip()
_FALLBACK_KINDS = {"rate_limit", "quota_exhausted", "model_not_found"}


class AIProviderError(Exception):
    """Wraps provider SDK errors so callers can render a friendly message."""

    def __init__(self, message: str, *, kind: str = "unknown", status_code: Optional[int] = None):
        super().__init__(message)
        self.kind = kind
        self.status_code = status_code


# ---- Precise pattern matching ---------------------------------------------
_INVALID_KEY_PATTERNS = (
    re.compile(r"api[\s_-]*key[^a-z]*(not[\s_]*valid|invalid|missing|rejected)", re.I),
    re.compile(r"api_key_invalid", re.I),
    re.compile(r"authenticationerror", re.I),
    re.compile(r"\bunauthorized\b", re.I),
    re.compile(r"\bpermission[\s_]*denied\b", re.I),
    re.compile(r"\b(401|403)\b"),
)
_RATE_LIMIT_PATTERNS = (
    re.compile(r"rate[\s_]*limit", re.I),
    re.compile(r"\bratelimiterror\b", re.I),
    re.compile(r"quota[\s_]*(exceeded|exhausted)", re.I),
    re.compile(r"\bresource[_\s]*exhausted\b", re.I),
    re.compile(r"\btoo[\s_]*many[\s_]*requests\b", re.I),
    re.compile(r"\b429\b"),
)
_MODEL_MISSING_PATTERNS = (
    re.compile(r"\bnotfounderror\b", re.I),
    re.compile(r"\binvalid[\s_]*model[\s_]*name\b", re.I),
    re.compile(r"model[^a-z]*(not[\s_]*found|does not exist|not available|not supported)", re.I),
    re.compile(r"unknown model", re.I),
    re.compile(r"\b404\b"),
)
_TIMEOUT_PATTERNS = (
    re.compile(r"\btimeout\b", re.I),
    re.compile(r"read[\s_]*timed[\s_]*out", re.I),
)
_NETWORK_PATTERNS = (
    re.compile(r"\bconnection[\s_]*(refused|error|reset|aborted)\b", re.I),
    re.compile(r"name[\s_]*resolution[\s_]*failed", re.I),
    re.compile(r"temporarily[\s_]*unavailable", re.I),
    re.compile(r"\bservice[\s_]*unavailable\b", re.I),
    re.compile(r"\b(502|503|504)\b"),
)


def _match_any(patterns, text: str) -> bool:
    return any(p.search(text) for p in patterns)


def _classify(err: Exception) -> AIProviderError:
    """Bucket raw SDK exceptions into user-actionable kinds."""
    cls_name = err.__class__.__name__ or ""
    msg = str(err) or cls_name

    if cls_name in ("AuthenticationError", "PermissionDeniedError"):
        return AIProviderError(
            "Your Gemini API key was rejected. Please update it in Settings.",
            kind="invalid_key", status_code=401,
        )
    if cls_name in ("NotFoundError",):
        return AIProviderError(
            "The selected Gemini model isn't available for this API key. "
            "Try `gemini-flash-latest` or `gemini-3.6-flash` in Settings.",
            kind="model_not_found", status_code=404,
        )
    if cls_name in ("RateLimitError",):
        return AIProviderError(
            "Gemini rate/quota limit reached. Try again in a minute.",
            kind="rate_limit", status_code=429,
        )
    if cls_name in ("Timeout", "APITimeoutError"):
        return AIProviderError(
            "Gemini timed out. Retry in a moment.",
            kind="timeout", status_code=504,
        )
    if cls_name in ("APIConnectionError", "ServiceUnavailableError"):
        return AIProviderError(
            "Gemini is temporarily unreachable. Retry in a moment.",
            kind="upstream", status_code=502,
        )

    if _match_any(_INVALID_KEY_PATTERNS, msg):
        return AIProviderError(
            "Your Gemini API key was rejected. Please update it in Settings.",
            kind="invalid_key", status_code=401,
        )
    if _match_any(_MODEL_MISSING_PATTERNS, msg):
        return AIProviderError(
            "The selected Gemini model isn't available for this API key. "
            "Try `gemini-flash-latest` or `gemini-3.6-flash` in Settings.",
            kind="model_not_found", status_code=404,
        )
    if _match_any(_RATE_LIMIT_PATTERNS, msg):
        return AIProviderError(
            "Gemini rate/quota limit reached. Try again in a minute.",
            kind="rate_limit", status_code=429,
        )
    if _match_any(_TIMEOUT_PATTERNS, msg):
        return AIProviderError(
            "Gemini timed out. Retry in a moment.",
            kind="timeout", status_code=504,
        )
    if _match_any(_NETWORK_PATTERNS, msg):
        return AIProviderError(
            "Gemini is temporarily unreachable. Retry in a moment.",
            kind="upstream", status_code=502,
        )

    trimmed = msg.strip().split("\n", 1)[0][:180]
    return AIProviderError(
        f"AI generation failed: {trimmed or cls_name or 'unknown error'}",
        kind="unknown", status_code=502,
    )


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
    """Fire a single completion and return the raw text response."""
    if not api_key:
        if _EMERGENT_KEY:
            return await _call_llm(
                api_key=_EMERGENT_KEY,
                model_name=_EMERGENT_MODEL,
                provider=provider or "gemini",
                system_message=system_message,
                prompt=prompt,
                session_id=session_id,
            )
        raise AIProviderError(
            "Please configure your Gemini API Key in Settings.",
            kind="missing_key", status_code=400,
        )
    log.info("LLM request start · provider=%s · model=%s · session=%s", provider, model_name, session_id)
    try:
        return await _call_llm(
            api_key=api_key, model_name=model_name, provider=provider,
            system_message=system_message, prompt=prompt, session_id=session_id,
        )
    except AIProviderError as pe:
        if pe.kind in _FALLBACK_KINDS and _EMERGENT_KEY and api_key != _EMERGENT_KEY:
            log.warning(
                "Falling back to Emergent LLM key · kind=%s · original_model=%s → %s",
                pe.kind, model_name, _EMERGENT_MODEL,
            )
            try:
                out = await _call_llm(
                    api_key=_EMERGENT_KEY, model_name=_EMERGENT_MODEL,
                    provider=provider or "gemini",
                    system_message=system_message, prompt=prompt,
                    session_id=session_id + "::emergent-fallback",
                )
                log.info("Recovered via Emergent fallback · model=%s", _EMERGENT_MODEL)
                return out
            except Exception as fe:  # noqa: BLE001
                log.warning("Emergent fallback also failed: %s", str(fe)[:200])
        raise


async def _call_llm(
    *,
    api_key: str, model_name: str, provider: str,
    system_message: str, prompt: str, session_id: str,
) -> str:
    """Inner LLM invocation using official google-genai SDK. Raises AIProviderError on failure."""
    try:
        client = genai.Client(api_key=api_key)
        
        interaction = client.interactions.create(
            model=model_name,
            input=prompt,
            system_instruction=system_message if system_message else None,
        )
        response = interaction.output_text
    except AIProviderError:
        raise
    except Exception as e:  # noqa: BLE001
        log.exception(
            "LLM provider error · provider=%s · model=%s · class=%s · msg=%s",
            provider, model_name, e.__class__.__name__, str(e)[:600],
        )
        raise _classify(e)
        
    if not response:
        log.warning("LLM returned empty response · provider=%s · model=%s", provider, model_name)
        raise AIProviderError(
            "AI returned an empty response. Please retry.",
            kind="empty_response", status_code=502,
        )
        
    if isinstance(response, str):
        log.info("LLM request ok · provider=%s · model=%s · chars=%d", provider, model_name, len(response))
        return response
    return str(response)