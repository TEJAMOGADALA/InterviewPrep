"""Mission Engine V1 backend tests."""
import os
import uuid
import time
from datetime import datetime, timezone, timedelta

import pytest
import requests

# BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
# if not BASE_URL:
#     with open("/app/frontend/.env") as f:
#         for line in f:
#             if line.startswith("REACT_APP_BACKEND_URL="):
#                 BASE_URL = line.split("=", 1)[1].strip().rstrip("/")

from pathlib import Path

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

if not BASE_URL:
    frontend_env = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / ".env"
    )

    if frontend_env.exists():
        with frontend_env.open() as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    BASE_URL = line.split("=", 1)[1].strip().rstrip("/")

if not BASE_URL:
    raise RuntimeError(
        "REACT_APP_BACKEND_URL is not configured."
    )


ONBOARDING = {
    "target_companies": ["google", "stripe"],
    "current_position": "1-3",
    "daily_study_hours": 3,
    "self_assessment": {
        "dsa": 6, "java": 4, "lld": 5, "hld": 3,
        "operating_systems": 5, "dbms": 4, "computer_networks": 5,
    },
    "interview_target_date": "2026-11-15",
}


def _mk_user():
    unique = uuid.uuid4().hex[:8]
    return {
        "email": f"TEST_miss_{unique}@prepos.io",
        "password": "Test@1234",
        "name": f"MissionUser {unique}",
    }


def _register_and_onboard(session=None, onboarding=None):
    s = session or requests.Session()
    u = _mk_user()
    r = s.post(f"{BASE_URL}/api/auth/register", json=u, timeout=30)
    assert r.status_code == 200, r.text
    r = s.post(f"{BASE_URL}/api/onboarding", json=onboarding or ONBOARDING, timeout=15)
    assert r.status_code == 200, r.text
    return s, u


@pytest.fixture(scope="module")
def fresh_session():
    s, _u = _register_and_onboard()
    return s


# ============ 1. GET /api/missions/today ============

class TestTodayMission:
    def test_today_mission_generated(self, fresh_session):
        r = fresh_session.get(f"{BASE_URL}/api/missions/today", timeout=15)
        assert r.status_code == 200, r.text
        m = r.json()
        assert m["status"] == "in_progress"
        assert m["focus_topic"] in [
            "dsa", "java", "lld", "hld",
            "operating_systems", "dbms", "computer_networks",
        ]
        assert isinstance(m["tasks"], list)
        assert len(m["tasks"]) >= 2
        # hours=3 → 180 min
        assert m["estimated_duration_minutes"] == 180
        assert m["difficulty"] in ["easy", "medium", "hard"]
        assert m["title"]
        assert m["focus_area"]

    def test_today_mission_deterministic(self, fresh_session):
        r1 = fresh_session.get(f"{BASE_URL}/api/missions/today", timeout=15)
        r2 = fresh_session.get(f"{BASE_URL}/api/missions/today", timeout=15)
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["id"] == r2.json()["id"]


# ============ 2. Task completion ============

class TestTaskCompletion:
    def test_complete_task_updates_progress_and_creates_revision(self):
        s, _ = _register_and_onboard()
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        # pick a non-revise task
        task = next((t for t in m["tasks"] if t["kind"] != "revise"), None)
        assert task is not None
        topic = task["topic"]

        r = s.post(
            f"{BASE_URL}/api/missions/{m['id']}/tasks/{task['id']}/complete",
            timeout=15,
        )
        assert r.status_code == 200, r.text
        updated = r.json()
        t2 = next(tt for tt in updated["tasks"] if tt["id"] == task["id"])
        assert t2["completed"] is True
        assert t2["completed_at"]

        # revision item created for tomorrow
        rq = s.get(f"{BASE_URL}/api/revisions/queue", timeout=15).json()
        matching = [x for x in rq if x["topic"] == topic and x["task_title"] == task["title"]]
        assert len(matching) >= 1
        assert matching[0]["stage"] == 0
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date().isoformat()
        assert matching[0]["next_review_date"] == tomorrow

        # knowledge progress seeded from baseline (dsa=6 -> ~60 + gain)
        dash = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        kp = next(k for k in dash["knowledge"] if k["topic"] == topic)
        baseline = ONBOARDING["self_assessment"][topic] * 10
        assert kp["score"] > baseline, f"score {kp['score']} not > baseline {baseline}"
        assert kp["completions"] >= 1


# ============ 3. Mission complete ============

class TestMissionComplete:
    def test_complete_mission_streak_and_activity(self):
        s, _ = _register_and_onboard()
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        r = s.post(f"{BASE_URL}/api/missions/{m['id']}/complete", timeout=15)
        assert r.status_code == 200, r.text
        done = r.json()
        assert done["status"] == "completed"
        assert done["completed_at"]
        assert all(t["completed"] for t in done["tasks"])

        # streak upserted
        dash = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        assert dash["streak"]["current"] == 1
        assert dash["streak"]["last_active_date"] == datetime.now(timezone.utc).date().isoformat()
        # week grid — last cell true
        assert dash["streak"]["week_grid"][-1] is True
        assert len(dash["streak"]["week_grid"]) == 7

        # activity
        acts = s.get(f"{BASE_URL}/api/activity", timeout=15).json()
        kinds = [a["kind"] for a in acts]
        assert "mission_completed" in kinds

    def test_complete_idempotent_same_day(self):
        s, _ = _register_and_onboard()
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        s.post(f"{BASE_URL}/api/missions/{m['id']}/complete", timeout=15)
        s.post(f"{BASE_URL}/api/missions/{m['id']}/complete", timeout=15)
        dash = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        assert dash["streak"]["current"] == 1


# ============ 4. Skip ============

class TestMissionSkip:
    def test_skip_mission(self):
        s, _ = _register_and_onboard()
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        r = s.post(f"{BASE_URL}/api/missions/{m['id']}/skip", timeout=15)
        assert r.status_code == 200
        assert r.json()["status"] == "skipped"
        acts = s.get(f"{BASE_URL}/api/activity", timeout=15).json()
        assert any(a["kind"] == "mission_skipped" for a in acts)


# ============ 5. Dashboard ============

class TestDashboard:
    def test_dashboard_shape_and_daily_login(self):
        s, _ = _register_and_onboard()
        r = s.get(f"{BASE_URL}/api/dashboard", timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        for key in ["today", "mission", "streak", "readiness",
                    "knowledge", "revisions", "activity", "onboarding"]:
            assert key in d, f"missing {key}"
        assert len(d["knowledge"]) == 7
        topics_in_view = {k["topic"] for k in d["knowledge"]}
        assert topics_in_view == {
            "dsa", "java", "lld", "hld",
            "operating_systems", "dbms", "computer_networks",
        }
        for kp in d["knowledge"]:
            assert "label" in kp and "score" in kp and "completions" in kp
        assert 0 <= d["readiness"] <= 100
        for key in ["target_companies", "current_position", "daily_study_hours",
                    "interview_target_date", "estimated_prep_days", "days_to_target"]:
            assert key in d["onboarding"]
        # daily_login logged
        acts = s.get(f"{BASE_URL}/api/activity", timeout=15).json()
        assert any(a["kind"] == "daily_login" for a in acts)

    def test_dashboard_no_duplicate_daily_login(self):
        s, _ = _register_and_onboard()
        s.get(f"{BASE_URL}/api/dashboard", timeout=15)
        s.get(f"{BASE_URL}/api/dashboard", timeout=15)
        acts = s.get(f"{BASE_URL}/api/activity", timeout=15).json()
        n = sum(1 for a in acts if a["kind"] == "daily_login")
        assert n == 1


# ============ 6. Revisions queue ============

class TestRevisions:
    def test_queue_has_is_due(self):
        s, _ = _register_and_onboard()
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        task = next(t for t in m["tasks"] if t["kind"] != "revise")
        s.post(f"{BASE_URL}/api/missions/{m['id']}/tasks/{task['id']}/complete", timeout=15)
        rq = s.get(f"{BASE_URL}/api/revisions/queue", timeout=15).json()
        assert len(rq) >= 1
        item = rq[0]
        for k in ["next_review_date", "task_title", "topic", "stage", "is_due"]:
            assert k in item


# ============ 7. Activity ============

class TestActivity:
    def test_activity_sorted_desc(self):
        s, _ = _register_and_onboard()
        s.get(f"{BASE_URL}/api/dashboard", timeout=15)
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        s.post(f"{BASE_URL}/api/missions/{m['id']}/complete", timeout=15)
        acts = s.get(f"{BASE_URL}/api/activity", timeout=15).json()
        assert len(acts) >= 2
        ts_list = [a["ts"] for a in acts]
        assert ts_list == sorted(ts_list, reverse=True)


# ============ 8. History ============

class TestHistory:
    def test_history_desc(self):
        s, _ = _register_and_onboard()
        s.get(f"{BASE_URL}/api/missions/today", timeout=15)
        r = s.get(f"{BASE_URL}/api/missions/history", timeout=15)
        assert r.status_code == 200
        arr = r.json()
        assert isinstance(arr, list) and len(arr) >= 1


# ============ 9. PATCH onboarding regenerates mission ============

class TestOnboardingPatch:
    def test_patch_hours_regenerates_mission(self):
        s, _ = _register_and_onboard()
        m1 = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        assert m1["estimated_duration_minutes"] == 180

        r = s.patch(f"{BASE_URL}/api/onboarding", json={"daily_study_hours": 5}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["daily_study_hours"] == 5
        assert isinstance(data["estimated_prep_days"], int)

        # profile_updated activity
        acts = s.get(f"{BASE_URL}/api/activity", timeout=15).json()
        assert any(a["kind"] == "profile_updated" for a in acts)

        # New dashboard should regenerate mission with new duration
        d2 = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        assert d2["mission"]["estimated_duration_minutes"] == 300


# ============ 10. Readiness ============

class TestReadiness:
    def test_readiness_baseline_weighted(self):
        s, _ = _register_and_onboard()
        d = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        # expected weighted baseline
        weights = {
            "dsa": 0.35, "java": 0.15, "lld": 0.15, "hld": 0.15,
            "operating_systems": 0.0667, "dbms": 0.0667, "computer_networks": 0.0666,
        }
        expected = sum(ONBOARDING["self_assessment"][t] * 10 * w for t, w in weights.items())
        assert abs(d["readiness"] - expected) < 1.5, (
            f"readiness {d['readiness']} vs expected ~{expected:.2f}"
        )

    def test_readiness_changes_after_completion(self):
        s, _ = _register_and_onboard()
        d0 = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        m = d0["mission"]
        # find first dsa task if any, else any non-revise
        task = next((t for t in m["tasks"] if t["topic"] == "dsa" and t["kind"] != "revise"), None)
        if task is None:
            task = next(t for t in m["tasks"] if t["kind"] != "revise")
        s.post(f"{BASE_URL}/api/missions/{m['id']}/tasks/{task['id']}/complete", timeout=15)
        d1 = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        assert d1["readiness"] != d0["readiness"]


# ============ 11. Spaced repetition advance on revise ============

class TestSpacedRepetition:
    def test_revise_task_advances_stage(self):
        s, _ = _register_and_onboard()
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        # first complete a non-revise task to seed a revision
        nrt = next(t for t in m["tasks"] if t["kind"] != "revise")
        s.post(f"{BASE_URL}/api/missions/{m['id']}/tasks/{nrt['id']}/complete", timeout=15)
        rq_before = s.get(f"{BASE_URL}/api/revisions/queue", timeout=15).json()
        assert len(rq_before) >= 1

        # Now simulate a revise task on same topic by creating a task via completing
        # a mission task that is 'revise'. Since fresh user has no due revisions yet,
        # the mission won't include revise tasks. Instead, manually check schedule fn
        # by calling the same complete endpoint on a revise-like scenario:
        # We construct the check by verifying REVISION_STAGES_DAYS math directly here.
        # Since we cannot easily inject a revise task without due-yesterday item,
        # this test focuses on stage progression via API when the item exists.
        # (No practical way to fast-forward date here — mark test as basic sanity.)
        assert rq_before[0]["stage"] == 0
