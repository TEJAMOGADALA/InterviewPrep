"""Iteration 9 — Regression tests guarding against the HTTP 500 leak.

Root cause: a debug patch removed `raise _classify(e)` inside complete_json()'s
`except Exception` block, letting raw provider exceptions escape → FastAPI 500.

These tests lock in:
  1. Source guard: `raise _classify(e)` present in ai_service.py's Exception block.
  2. gemini-1.5-flash (retired model) with valid key -> 404 model_not_found
     with message suggesting gemini-2.5-flash / gemini-2.0-flash. NEVER 500. NEVER 429.
  3. Happy path with gemini-2.5-flash -> 200 with full 7-section payload.
  4. Cache-hit second call -> same generated_at.
  5. Invalid key -> 401 invalid_key.
  6. Missing key -> 400 missing_key.
  7. Untouched-endpoint regression sweep.
"""
import os
import re
import time
import uuid
import pytest
import requests


def _load_backend_url():
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if not v:
        try:
            with open("/app/frontend/.env") as f:
                for line in f:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        v = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass
    return (v or "").rstrip("/")


BASE_URL = _load_backend_url()
EMERGENT_KEY = "sk-emergent-aEa152aE36c979b48F"
GOOD_MODEL = "gemini-2.5-flash"
RETIRED_MODEL = "gemini-1.5-flash"  # Reproduces the user's actual bug report
BAD_KEY = "AIzaBOGUS"

NODE_OS_FS = "os.fs.basics"          # From user's report
NODE_SOLID = "lld.principles.solid"  # Pre-cached from prior iterations


# --- Fixtures --------------------------------------------------------------

@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    email = f"iter9_{uuid.uuid4().hex[:8]}@prepos.io"
    password = "Test@1234"
    r = s.post(f"{BASE_URL}/api/auth/register", json={
        "email": email, "password": password, "name": "Iter9 Test"
    })
    assert r.status_code in (200, 201), r.text
    s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    # Real onboarding shape (per iter8 context)
    s.post(f"{BASE_URL}/api/onboarding", json={
        "target_companies": ["Google"],
        "current_position": "swe",
        "daily_study_hours": 2,
        "self_assessment": {
            "dsa": 3, "java": 3, "lld": 2, "hld": 2,
            "operating_systems": 2, "dbms": 2, "computer_networks": 2,
        },
        "interview_target_date": None,
    })
    return s


def _set_ai(s, *, model=GOOD_MODEL, key=EMERGENT_KEY):
    r = s.patch(f"{BASE_URL}/api/settings", json={
        "ai_config": {"provider": "gemini", "model_name": model,
                      "api_key": key, "temperature": 0.7}
    })
    assert r.status_code == 200, r.text


# --- 1. Source guard (static file inspection) -----------------------------

class TestSourceGuard:
    def test_ai_service_has_raise_classify_in_except_exception(self):
        src = open("/app/backend/ai_service.py").read()
        # Must contain `raise _classify(e)` line
        assert "raise _classify(e)" in src, "ai_service.py missing `raise _classify(e)`"

    def test_no_bare_raise_after_except_exception(self):
        """The only `raise` allowed inside `except Exception` must call _classify."""
        src = open("/app/backend/ai_service.py").read()
        # Find each `except Exception` block and verify its body ends in raise _classify
        # Simple heuristic: look for pattern `except Exception as e:` followed by body,
        # ensure a bare `raise` line (not `raise _classify`, not `raise AIProviderError`)
        # is not present inside complete_json's Exception block.
        m = re.search(
            r"except Exception as e:.*?(?=\n\S|\Z)",
            src, re.DOTALL,
        )
        assert m, "except Exception block not found"
        body = m.group(0)
        # Split into non-blank lines and inspect the last `raise` statement.
        raise_lines = [ln.strip() for ln in body.splitlines() if ln.strip().startswith("raise")]
        assert raise_lines, "no raise in except Exception body"
        for ln in raise_lines:
            assert ln != "raise", f"BARE `raise` found in except Exception body: {body!r}"
            assert "_classify" in ln or "AIProviderError" in ln, f"unexpected raise: {ln}"


# --- 2. User's exact bug: gemini-1.5-flash -> 404 (not 500, not 429) ------

class TestUserBugRegression:
    """The USER'S actual reproduction: retired gemini-1.5-flash model."""

    def test_retired_model_returns_404_never_500(self, session):
        _set_ai(session, model=RETIRED_MODEL, key=EMERGENT_KEY)
        # Use regenerate to force a fresh Gemini call (bypass any cached content)
        r = session.post(
            f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/regenerate"
        )
        assert r.status_code != 500, (
            f"REGRESSION: bare `raise` leaked HTTP 500. Body: {r.text}"
        )
        assert r.status_code != 429, (
            f"REGRESSION: mis-classified as rate_limit 429. Body: {r.text}"
        )
        assert r.status_code == 404, (
            f"Expected 404 model_not_found for retired model, got {r.status_code}: {r.text}"
        )
        detail = r.json().get("detail", {})
        assert detail.get("error") == "model_not_found", detail
        msg = detail.get("message", "")
        # Friendly message MUST guide user to a currently-valid model
        assert ("gemini-2.5-flash" in msg or "gemini-2.0-flash" in msg), (
            f"model_not_found message must suggest current models, got: {msg}"
        )
        # And MUST NOT suggest the broken model back to the user
        assert "gemini-1.5-flash" not in msg, (
            f"message should not suggest deprecated gemini-1.5-flash, got: {msg}"
        )


# --- 3. Happy path --------------------------------------------------------

class TestHappyPath:
    def test_happy_path_generate_full_shape(self, session):
        _set_ai(session, model=GOOD_MODEL, key=EMERGENT_KEY)
        # Ensure fresh — regenerate first
        session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/regenerate")
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/generate")
        if r.status_code != 200:
            time.sleep(2)
            session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/regenerate")
            r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/generate")
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["available"] is True
        assert j["generated_at"]
        theory = j.get("theory", {})
        # theory can be dict{beginner,deep} OR simple string in some shapes; accept dict
        assert theory.get("beginner") or theory.get("deep") or isinstance(theory, str), theory
        assert len(j["examples"]) >= 2, f"examples: {len(j['examples'])}"
        assert len(j["interview_tips"]) >= 3
        assert len(j["common_mistakes"]) >= 3
        assert len(j["flashcards"]) >= 5
        assert len(j["related_topics"]) >= 1
        assert len(j["prerequisites"]) >= 1
        pytest.iter9_generated_at = j["generated_at"]

    def test_cache_hit_second_call_same_timestamp(self, session):
        t0 = time.time()
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/generate")
        elapsed = time.time() - t0
        assert r.status_code == 200, r.text
        assert r.json()["generated_at"] == pytest.iter9_generated_at, "cache miss"
        assert elapsed < 3.0, f"cache hit too slow: {elapsed:.2f}s"


# --- 4. Cleanly-mapped auth/config errors ---------------------------------

class TestCleanErrorMapping:
    def test_invalid_key_401(self, session):
        # Use /regenerate to bypass cache (os.fs.basics was cached by happy path)
        _set_ai(session, model=GOOD_MODEL, key=BAD_KEY)
        r = session.post(
            f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/regenerate"
        )
        assert r.status_code != 500, f"500 leaked for bad key: {r.text}"
        assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
        assert r.json().get("detail", {}).get("error") == "invalid_key"

    def test_missing_key_400(self, session):
        _set_ai(session, model=GOOD_MODEL, key="")
        r = session.post(
            f"{BASE_URL}/api/roadmap/nodes/{NODE_OS_FS}/content/regenerate"
        )
        assert r.status_code == 400, r.text
        assert r.json().get("detail", {}).get("error") == "missing_key"


# --- 5. Broad regression sweep of untouched endpoints ---------------------

class TestUntouchedEndpointsRegression:
    def test_roadmap_tree(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap").status_code == 200

    def test_roadmap_summary(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap/summary").status_code == 200

    def test_roadmap_progress(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap/progress").status_code == 200

    def test_node_detail(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap/nodes/{NODE_SOLID}").status_code == 200

    def test_content_get_cached_solid(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/nodes/{NODE_SOLID}/content")
        assert r.status_code == 200, r.text
        j = r.json()
        # Cached from iter8 — available should be true
        assert j.get("available") is True, j

    def test_status_bookmark_favorite_notes_confidence(self, session):
        base = f"{BASE_URL}/api/roadmap/nodes/{NODE_SOLID}"
        assert session.post(f"{base}/status", json={"status": "in_progress"}).status_code in (200, 201)
        assert session.post(f"{base}/bookmark", json={"bookmarked": True}).status_code in (200, 201)
        assert session.post(f"{base}/favorite", json={"favorite": True}).status_code in (200, 201)
        # Notes is PATCH not POST
        assert session.patch(f"{base}/notes", json={"notes": "iter9 test"}).status_code in (200, 201)
        assert session.post(f"{base}/confidence", json={"confidence": 3}).status_code in (200, 201)

    def test_attempt(self, session):
        r = session.post(
            f"{BASE_URL}/api/roadmap/nodes/{NODE_SOLID}/attempt",
            json={"outcome": "solved", "time_minutes": 15}
        )
        assert r.status_code in (200, 201), r.text

    def test_missions_today(self, session):
        r = session.get(f"{BASE_URL}/api/missions/today")
        # 409 is acceptable IF onboarding row missing (unrelated to this fix).
        # Critical: it must NOT be 500.
        assert r.status_code != 500, r.text
        assert r.status_code in (200, 409), r.text

    def test_settings(self, session):
        assert session.get(f"{BASE_URL}/api/settings").status_code == 200

    def test_onboarding_get(self, session):
        assert session.get(f"{BASE_URL}/api/onboarding").status_code == 200

    def test_auth_me(self, session):
        assert session.get(f"{BASE_URL}/api/auth/me").status_code == 200
