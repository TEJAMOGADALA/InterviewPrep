"""Iteration 8 STABILIZATION — regression tests for the AI classify bug fix.

Root cause: naked substring `if "rate" in low` was matching the word "generate"
in litellm error messages, so every 4xx was being mis-labelled 429/rate_limit.
Also `"500" in low` was over-matching.

These tests lock in:
  1. model_not_found -> 404 (bogus model name w/ valid key)
  2. invalid_key    -> 401 (valid model, junk key)
  3. missing_key    -> 400 (empty key)
  4. happy path     -> 200 with all 7 populated sections
  5. cache-hit no-op (generated_at unchanged on 2nd generate)
  6. regenerate refreshes generated_at
"""
import os
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
BAD_MODEL = "gemini-nonexistent-model"
BAD_KEY = "AIzaBOGUSKEY_bad_1234567890"

NODE_SINGLETON = "lld.patterns.creational.singleton"
NODE_HAPPY = "dsa.linear.linked_list.lru"
NODE_SOLID = "lld.principles.solid"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    email = f"stab_{uuid.uuid4().hex[:8]}@prepos.io"
    password = "Test@1234"
    r = s.post(f"{BASE_URL}/api/auth/register", json={
        "email": email, "password": password, "name": "Stab Test"
    })
    assert r.status_code in (200, 201), r.text
    s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    s.post(f"{BASE_URL}/api/onboarding", json={
        "current_role": "swe", "years_experience": 2, "target_role": "swe",
        "target_companies": ["Google"], "primary_track": "dsa",
        "daily_minutes": 60, "interview_date": None,
    })
    return s


def _set_ai(s, *, model=GOOD_MODEL, key=EMERGENT_KEY):
    r = s.patch(f"{BASE_URL}/api/settings", json={
        "ai_config": {"provider": "gemini", "model_name": model,
                      "api_key": key, "temperature": 0.7}
    })
    assert r.status_code == 200, r.text


# --- BUG FIX: error classification ---------------------------------------


class TestClassifyBugFix:
    def test_model_not_found_returns_404_not_429(self, session):
        _set_ai(session, model=BAD_MODEL, key=EMERGENT_KEY)
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_SINGLETON}/content/generate")
        assert r.status_code == 404, f"Expected 404 model_not_found, got {r.status_code}: {r.text}"
        detail = r.json().get("detail", {})
        assert detail.get("error") == "model_not_found", detail
        msg = detail.get("message", "").lower()
        assert ("gemini-2.5-flash" in msg or "gemini-1.5-flash" in msg), msg
        # CRITICAL regression guard: must NOT be mis-classified as rate_limit
        assert detail.get("error") != "rate_limit"

    def test_invalid_key_returns_401_not_429(self, session):
        _set_ai(session, model=GOOD_MODEL, key=BAD_KEY)
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_SINGLETON}/content/generate")
        assert r.status_code == 401, f"Expected 401 invalid_key, got {r.status_code}: {r.text}"
        detail = r.json().get("detail", {})
        assert detail.get("error") == "invalid_key", detail
        assert detail.get("error") != "rate_limit"

    def test_missing_key_returns_400(self, session):
        _set_ai(session, model=GOOD_MODEL, key="")
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_SINGLETON}/content/generate")
        assert r.status_code == 400, r.text
        detail = r.json().get("detail", {})
        assert detail.get("error") == "missing_key", detail


# --- HAPPY PATH + CACHE ----------------------------------------------------


class TestHappyPathAndCache:
    def test_happy_path_generate_full_shape(self, session):
        _set_ai(session, model=GOOD_MODEL, key=EMERGENT_KEY)
        # Ensure fresh
        session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_HAPPY}/content/regenerate")
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_HAPPY}/content/generate")
        if r.status_code != 200:
            time.sleep(2)
            session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_HAPPY}/content/regenerate")
            r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_HAPPY}/content/generate")
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["available"] is True
        assert j["generated_at"]
        assert j["theory"].get("beginner")
        assert j["theory"].get("deep")
        assert len(j["interview_tips"]) >= 3
        assert len(j["common_mistakes"]) >= 3
        assert len(j["flashcards"]) >= 5
        assert len(j["related_topics"]) >= 1
        assert len(j["prerequisites"]) >= 1
        assert len(j["examples"]) >= 1
        # verify example shape
        ex = j["examples"][0]
        assert "title" in ex and ("scenario" in ex or "walkthrough" in ex)
        # verify mistake shape
        m = j["common_mistakes"][0]
        assert "mistake" in m
        pytest.happy_generated_at = j["generated_at"]

    def test_cache_hit_second_call_same_timestamp(self, session):
        t0 = time.time()
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_HAPPY}/content/generate")
        elapsed = time.time() - t0
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["generated_at"] == pytest.happy_generated_at, "cache miss - was regenerated"
        assert elapsed < 3.0, f"Cache hit too slow ({elapsed:.2f}s)"

    def test_regenerate_updates_timestamp(self, session):
        _set_ai(session, model=GOOD_MODEL, key=EMERGENT_KEY)
        prev = pytest.happy_generated_at
        time.sleep(1.1)
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_HAPPY}/content/regenerate")
        if r.status_code != 200:
            time.sleep(2)
            r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_HAPPY}/content/regenerate")
        assert r.status_code == 200, r.text
        assert r.json()["generated_at"] != prev


# --- REGRESSION ------------------------------------------------------------


class TestRegression:
    def test_roadmap_tree(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap").status_code == 200

    def test_summary(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap/summary").status_code == 200

    def test_progress(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap/progress").status_code == 200

    def test_node_detail(self, session):
        assert session.get(f"{BASE_URL}/api/roadmap/nodes/{NODE_SOLID}").status_code == 200
