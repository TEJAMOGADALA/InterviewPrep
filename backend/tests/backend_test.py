"""PrepOS backend API tests."""
import os
import uuid
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback to frontend/.env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")

ADMIN_EMAIL = "admin@prepos.io"
ADMIN_PASSWORD = "Admin@123"


def _mk_user():
    unique = uuid.uuid4().hex[:8]
    return {
        "email": f"TEST_user_{unique}@prepos.io",
        "password": "Test@1234",
        "name": f"Test User {unique}",
    }


@pytest.fixture(scope="module")
def new_user():
    return _mk_user()


@pytest.fixture(scope="module")
def user_session(new_user):
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/register", json=new_user, timeout=30)
    assert r.status_code == 200, f"register failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    return s


# ------------ Health ------------

class TestHealth:
    def test_root(self):
        r = requests.get(f"{BASE_URL}/api/", timeout=15)
        assert r.status_code == 200
        assert "PrepOS" in r.json().get("message", "")

    def test_health(self):
        r = requests.get(f"{BASE_URL}/api/health", timeout=15)
        assert r.status_code == 200
        assert r.json().get("status") == "ok"


# ------------ Auth ------------

class TestAuth:
    def test_register_new(self):
        u = _mk_user()
        r = requests.post(f"{BASE_URL}/api/auth/register", json=u, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["email"] == u["email"].lower()
        assert data["onboarding_completed"] is False
        # Cookies set
        assert "access_token" in r.cookies
        assert "refresh_token" in r.cookies

    def test_register_duplicate(self, new_user, user_session):
        r = requests.post(f"{BASE_URL}/api/auth/register", json=new_user, timeout=30)
        assert r.status_code == 400

    def test_login_admin(self, admin_session):
        # Verified in fixture; also check /me
        r = admin_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN_EMAIL

    def test_login_wrong_password(self):
        r = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": "WrongPass!!"},
            timeout=15,
        )
        assert r.status_code == 401

    def test_me_without_cookies(self):
        r = requests.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 401

    def test_refresh(self, user_session):
        r = user_session.post(f"{BASE_URL}/api/auth/refresh", timeout=15)
        assert r.status_code == 200

    def test_forgot_password_always_200(self):
        r = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "nonexistent_xyz@prepos.io"},
            timeout=15,
        )
        assert r.status_code == 200
        r2 = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": ADMIN_EMAIL},
            timeout=15,
        )
        assert r2.status_code == 200

    def test_logout(self):
        s = requests.Session()
        u = _mk_user()
        r = s.post(f"{BASE_URL}/api/auth/register", json=u, timeout=30)
        assert r.status_code == 200
        r = s.post(f"{BASE_URL}/api/auth/logout", timeout=15)
        assert r.status_code == 200
        # After logout, /me should be 401
        # Note: requests session may still have expired cookies but server should reject
        r2 = s.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r2.status_code == 401


# ------------ Onboarding ------------

class TestOnboarding:
    def test_submit_and_get(self, user_session):
        payload = {
            "target_companies": ["Google", "Amazon"],
            "current_position": "1-3",
            "daily_study_hours": 4,
            "self_assessment": {
                "dsa": 6, "java": 7, "lld": 5, "hld": 4,
                "operating_systems": 6, "dbms": 7, "computer_networks": 5,
            },
            "interview_target_date": "2026-06-01",
        }
        r = user_session.post(f"{BASE_URL}/api/onboarding", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["target_companies"] == ["Google", "Amazon"]
        assert isinstance(data["estimated_prep_days"], int)
        assert data["estimated_prep_days"] > 0

        # /me should reflect onboarding_completed
        r_me = user_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r_me.status_code == 200
        assert r_me.json()["onboarding_completed"] is True

        # GET returns saved record
        r_get = user_session.get(f"{BASE_URL}/api/onboarding", timeout=15)
        assert r_get.status_code == 200
        got = r_get.json()
        assert got["current_position"] == "1-3"
        assert got["self_assessment"]["dsa"] == 6


# ------------ Profile ------------

class TestProfile:
    def test_get_profile(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/profile", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "password_hash" not in data
        assert data["email"].startswith("test_user_")

    def test_patch_profile(self, user_session):
        r = user_session.patch(
            f"{BASE_URL}/api/profile",
            json={"name": "Updated Name", "headline": "Test Headline", "bio": "hello"},
            timeout=15,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["name"] == "Updated Name"
        # Verify persistence
        r2 = user_session.get(f"{BASE_URL}/api/profile", timeout=15)
        assert r2.json()["name"] == "Updated Name"


# ------------ Settings ------------

class TestSettings:
    def test_get_default_settings(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/settings", timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["theme"] == "dark"
        assert data["ai_config"]["provider"] == "gemini"
        assert "notification_prefs" in data

    def test_patch_settings(self, user_session):
        r = user_session.patch(
            f"{BASE_URL}/api/settings",
            json={
                "theme": "light",
                "ai_config": {
                    "provider": "openai",
                    "model_name": "gpt-4o",
                    "api_key": "sk-test",
                    "temperature": 0.5,
                },
            },
            timeout=15,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["theme"] == "light"
        assert data["ai_config"]["provider"] == "openai"
        assert data["ai_config"]["temperature"] == 0.5
        # Persist check
        r2 = user_session.get(f"{BASE_URL}/api/settings", timeout=15)
        assert r2.json()["theme"] == "light"
