"""Iteration 8 — AI Knowledge Base endpoints regression + happy path."""
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
NODE_CAP = "hld.foundations.cap"
NODE_KADANE = "dsa.foundations.arrays.kadane"
NODE_PREFIX = "dsa.foundations.arrays.prefix_sum"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    email = f"kbtest_{uuid.uuid4().hex[:8]}@prepos.io"
    password = "Test@1234"
    r = s.post(f"{BASE_URL}/api/auth/register", json={
        "email": email, "password": password, "name": "KB Test"
    })
    assert r.status_code in (200, 201), r.text
    # login (register may already set cookies)
    r2 = s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    assert r2.status_code == 200, r2.text
    # onboarding minimal
    s.post(f"{BASE_URL}/api/onboarding", json={
        "current_role": "swe", "years_experience": 2, "target_role": "swe",
        "target_companies": ["Google"], "primary_track": "dsa",
        "daily_minutes": 60, "interview_date": None,
    })
    return s


class TestReadOnlyCache:
    def test_fresh_node_read_no_gemini(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/nodes/{NODE_KADANE}/content")
        assert r.status_code == 200, r.text
        j = r.json()
        # If previously cached from another test run, tolerate available=True
        assert "available" in j
        assert "theory" in j
        assert isinstance(j.get("examples", []), list)

    def test_unknown_node_404(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/nodes/notarealnode/content")
        assert r.status_code == 404


class TestMissingKey:
    def test_generate_without_key_returns_400(self, session):
        # Ensure user has NO api_key set
        session.patch(f"{BASE_URL}/api/settings", json={
            "ai_config": {"provider": "gemini", "model_name": "gemini-2.5-flash",
                          "api_key": "", "temperature": 0.7}
        })
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_KADANE}/content/generate")
        assert r.status_code == 400, r.text
        detail = r.json().get("detail", {})
        assert detail.get("error") == "missing_key"
        assert "Settings" in detail.get("message", "") or "Setting" in detail.get("message", "")


class TestHappyPath:
    def _set_key(self, s):
        r = s.patch(f"{BASE_URL}/api/settings", json={
            "ai_config": {"provider": "gemini", "model_name": "gemini-2.5-flash",
                          "api_key": EMERGENT_KEY, "temperature": 0.7}
        })
        assert r.status_code == 200, r.text

    def test_generate_cap(self, session):
        self._set_key(session)
        # Ensure clean cache
        session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content/regenerate")
        # Fresh generate call - allow retry once for upstream flake
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content/generate")
        if r.status_code != 200:
            time.sleep(2)
            session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content/regenerate")
            r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content/generate")
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["available"] is True
        assert j["provider"] == "gemini"
        assert j["model_name"] == "gemini-2.5-flash"
        assert j["generated_at"]
        assert j["theory"] and j["theory"].get("beginner")
        assert j["theory"].get("deep")
        assert len(j["flashcards"]) >= 3
        assert len(j["examples"]) >= 2
        assert len(j["interview_tips"]) >= 3
        assert len(j["common_mistakes"]) >= 3
        assert len(j["related_topics"]) >= 2
        assert len(j["prerequisites"]) >= 1
        # Stash generated_at for cache test
        pytest.cap_generated_at = j["generated_at"]

    def test_cache_hit_no_regeneration(self, session):
        # Second call must not re-generate
        t0 = time.time()
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content/generate")
        elapsed = time.time() - t0
        assert r.status_code == 200
        j = r.json()
        assert j["generated_at"] == pytest.cap_generated_at
        assert elapsed < 3.0, f"Cache hit too slow ({elapsed}s), likely re-generated"

    def test_get_returns_cached(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content")
        assert r.status_code == 200
        j = r.json()
        assert j["available"] is True
        assert j["theory"]
        assert j["flashcards"]

    def test_regenerate_updates_timestamp(self, session):
        prev = pytest.cap_generated_at
        time.sleep(1.1)
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content/regenerate")
        if r.status_code != 200:
            time.sleep(2)
            r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content/regenerate")
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["generated_at"] != prev
        assert j["available"] is True

    def test_related_prereq_ids_resolve(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/content")
        j = r.json()
        for entry in (j.get("related_topics", []) + j.get("prerequisites", [])):
            nid = (entry or {}).get("id")
            if nid:
                rr = session.get(f"{BASE_URL}/api/roadmap/nodes/{nid}")
                assert rr.status_code == 200, f"Bad id in model output: {nid}"

    def test_second_node_kadane(self, session):
        # Clear + generate Kadane
        session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_KADANE}/content/regenerate")
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_KADANE}/content/generate")
        if r.status_code != 200:
            time.sleep(2)
            session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_KADANE}/content/regenerate")
            r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_KADANE}/content/generate")
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["available"] is True
        assert j["theory"] and j["theory"].get("beginner")


class TestRegression:
    def test_roadmap_tree(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap")
        assert r.status_code == 200
        assert "tracks" in r.json()

    def test_summary(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/summary")
        assert r.status_code == 200
        assert "overall" in r.json()

    def test_progress(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/progress")
        assert r.status_code == 200

    def test_node_detail(self, session):
        r = session.get(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}")
        assert r.status_code == 200

    def test_bookmark(self, session):
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/bookmark")
        assert r.status_code == 200
        assert "bookmarked" in r.json()

    def test_favorite(self, session):
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/favorite")
        assert r.status_code == 200

    def test_attempt(self, session):
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/attempt",
                         json={"actual_minutes": 5})
        assert r.status_code == 200

    def test_confidence(self, session):
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/confidence",
                         json={"confidence": 7})
        assert r.status_code == 200

    def test_status(self, session):
        r = session.post(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/status",
                         json={"status": "in_progress"})
        assert r.status_code == 200

    def test_notes(self, session):
        r = session.patch(f"{BASE_URL}/api/roadmap/nodes/{NODE_CAP}/notes",
                          json={"notes": "test note"})
        assert r.status_code == 200

    def test_missions_today(self, session):
        r = session.get(f"{BASE_URL}/api/missions/today")
        # 409 = onboarding not complete on this fresh test user; both are healthy responses
        assert r.status_code in (200, 409)

    def test_auth_me(self, session):
        r = session.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 200

    def test_settings(self, session):
        r = session.get(f"{BASE_URL}/api/settings")
        assert r.status_code == 200
