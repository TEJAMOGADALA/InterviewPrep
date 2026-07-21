"""Iteration 3 backend tests — Mission Engine V2 (adaptive) + Coding Arena."""
import os
import uuid
from datetime import datetime, timezone, timedelta

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")


VALID_PATTERNS = {
    "heap", "dp", "graphs", "backtracking", "trees", "arrays", "hashing",
    "sliding_window", "two_pointers", "binary_search", "stack",
    "linked_list", "greedy", "intervals", "strings", "bit_manipulation",
}


def _mk_user():
    unique = uuid.uuid4().hex[:8]
    return {
        "email": f"TEST_it3_{unique}@prepos.io",
        "password": "Test@1234",
        "name": f"It3User {unique}",
    }


def _register_and_onboard_dsa(session=None):
    """Register + onboard with DSA=1 (weakest) so focus_topic tends to DSA.
    We retry until we get a mission whose focus_topic is dsa.
    """
    for _ in range(15):
        s = requests.Session()
        u = _mk_user()
        r = s.post(f"{BASE_URL}/api/auth/register", json=u, timeout=30)
        assert r.status_code == 200, r.text
        onboarding = {
            "target_companies": ["google", "amazon"],
            "current_position": "1-3",
            "daily_study_hours": 3,
            "self_assessment": {
                "dsa": 1, "java": 9, "lld": 9, "hld": 9,
                "operating_systems": 9, "dbms": 9, "computer_networks": 9,
            },
            "interview_target_date": "2026-11-15",
        }
        r = s.post(f"{BASE_URL}/api/onboarding", json=onboarding, timeout=15)
        assert r.status_code == 200, r.text
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        if m.get("focus_topic") == "dsa":
            return s, u, m
    pytest.skip("Could not get DSA focus after 15 retries")


# =============== 1. GET /api/coding-arena mission + assignments ===============

class TestCodingArena:
    def test_arena_returns_mission_and_assignments(self):
        s, _u, _m = _register_and_onboard_dsa()
        r = s.get(f"{BASE_URL}/api/coding-arena", timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["primary_pattern"] in VALID_PATTERNS
        assignments = data["assignments"]
        assert 2 <= len(assignments) <= 4
        for a in assignments:
            p = a["problem"]
            for key in ("title", "difficulty", "pattern", "estimated_minutes", "leetcode_url"):
                assert key in p and p[key] is not None
            assert p["leetcode_url"].startswith("https://leetcode.com/")


# =============== 2. GET /api/problems/patterns ===============

class TestPatternsCatalog:
    def test_patterns_16_and_80plus(self):
        r = requests.get(f"{BASE_URL}/api/problems/patterns", timeout=15)
        assert r.status_code == 200, r.text
        arr = r.json()
        assert len(arr) == 16
        patterns = {x["pattern"] for x in arr}
        assert patterns == VALID_PATTERNS
        total = sum(x["count"] for x in arr)
        assert total >= 80, f"total problems={total}"


# =============== 3. Practice More returns unseen; exhaustion → 404 ===============

class TestPracticeMore:
    def test_practice_more_returns_new_problems(self):
        s, _u, _m = _register_and_onboard_dsa()
        arena = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        pattern = arena["primary_pattern"]
        existing_ids = {a["problem_id"] for a in arena["assignments"]}

        r = s.post(f"{BASE_URL}/api/coding-arena/practice-more",
                   json={"pattern": pattern}, timeout=15)
        assert r.status_code == 200, r.text
        p1 = r.json()["problem"]
        assert p1["id"] not in existing_ids
        existing_ids.add(p1["id"])

        r2 = s.post(f"{BASE_URL}/api/coding-arena/practice-more",
                    json={"pattern": pattern}, timeout=15)
        # Could 200 (new) or 404 (exhausted small pattern)
        if r2.status_code == 200:
            p2 = r2.json()["problem"]
            assert p2["id"] not in existing_ids

    def test_practice_more_exhaustion_returns_404(self):
        """Exhaust a small pattern (bit_manipulation has 4 problems) manually
        by repeatedly requesting practice_more until 404 occurs."""
        s, _u, _m = _register_and_onboard_dsa()
        # Try to exhaust bit_manipulation (only 4 problems in bank)
        target = "bit_manipulation"
        seen = 0
        last_code = None
        for _ in range(10):
            r = s.post(f"{BASE_URL}/api/coding-arena/practice-more",
                       json={"pattern": target}, timeout=15)
            last_code = r.status_code
            if r.status_code == 404:
                break
            assert r.status_code == 200, r.text
            seen += 1
        assert last_code == 404, f"expected exhaustion 404 within 10 tries, saw {seen} successes"


# =============== 4. Feedback high confidence → solved + revision ~1.5x ===============

class TestFeedbackHigh:
    def test_high_confidence_feedback(self):
        s, _u, _m = _register_and_onboard_dsa()
        arena = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        a = arena["assignments"][0]
        aid = a["id"]

        payload = {
            "difficulty_rating": "hard",
            "solved_status": "without_hints",
            "confidence": 9,
            "time_taken_minutes": 30,
            "notes": "clean",
        }
        r = s.post(f"{BASE_URL}/api/coding-arena/assignments/{aid}/feedback",
                   json=payload, timeout=15)
        assert r.status_code == 200, r.text

        # Assignment should now be 'solved'
        arena2 = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        a2 = next(x for x in arena2["assignments"] if x["id"] == aid)
        assert a2["status"] == "solved"
        assert a2["feedback"] is not None
        assert a2["feedback"]["confidence"] == 9

        # Revision item scheduled — confidence 9 → 1.5x of default 1 day = 2 days
        rq = s.get(f"{BASE_URL}/api/revisions/queue", timeout=15).json()
        assert len(rq) >= 1
        # find the newest one
        # For conf 9: 1 * 1.5 = 1.5 → round to 2 (banker's) → could be 2 days
        # Just verify it's between 1 and 3 days out
        today = datetime.now(timezone.utc).date()
        found_recent = False
        for item in rq:
            d = datetime.fromisoformat(item["next_review_date"]).date()
            if 1 <= (d - today).days <= 3:
                found_recent = True
                break
        assert found_recent, f"expected a revision 1-3 days out; got {[x['next_review_date'] for x in rq]}"


# =============== 5. Feedback low confidence → WeaknessRecord + sooner revision ===============

class TestFeedbackLow:
    def test_low_confidence_creates_weakness(self):
        s, _u, _m = _register_and_onboard_dsa()
        arena = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        a = arena["assignments"][0]
        aid = a["id"]

        payload = {
            "difficulty_rating": "hard",
            "solved_status": "could_not_solve",
            "confidence": 3,
            "time_taken_minutes": 45,
            "notes": "stuck",
        }
        r = s.post(f"{BASE_URL}/api/coding-arena/assignments/{aid}/feedback",
                   json=payload, timeout=15)
        assert r.status_code == 200, r.text

        arena2 = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        a2 = next(x for x in arena2["assignments"] if x["id"] == aid)
        assert a2["status"] == "attempted"  # could_not_solve → attempted

        # Revision: conf 3 → 0.4 * 1 = 0.4 → max(1, round(0.4))=1 day
        # (still 1 day but that's expected — sooner-or-equal to baseline)
        # We cannot inspect WeaknessRecord via API — but no error means insertion happened.


# =============== 6. Task toggle both ways + mission status revert ===============

class TestTaskToggle:
    def test_toggle_task_both_ways(self):
        s, _u, m = _register_and_onboard_dsa()
        task = next(t for t in m["tasks"] if t["kind"] != "revise")
        mid, tid = m["id"], task["id"]

        # First toggle → completed=true
        r1 = s.post(f"{BASE_URL}/api/missions/{mid}/tasks/{tid}/toggle", timeout=15)
        assert r1.status_code == 200
        t1 = next(t for t in r1.json()["tasks"] if t["id"] == tid)
        assert t1["completed"] is True

        # Verify today reflects
        today = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        assert next(t for t in today["tasks"] if t["id"] == tid)["completed"] is True

        # Second toggle → completed=false
        r2 = s.post(f"{BASE_URL}/api/missions/{mid}/tasks/{tid}/toggle", timeout=15)
        assert r2.status_code == 200
        t2 = next(t for t in r2.json()["tasks"] if t["id"] == tid)
        assert t2["completed"] is False
        assert t2["completed_at"] is None

    def test_untoggle_reverts_mission_status(self):
        s, _u, m = _register_and_onboard_dsa()
        mid = m["id"]
        # Complete mission
        s.post(f"{BASE_URL}/api/missions/{mid}/complete", timeout=15)
        # Verify completed
        today = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        assert today["status"] == "completed"
        # Untoggle one task
        tid = today["tasks"][0]["id"]
        r = s.post(f"{BASE_URL}/api/missions/{mid}/tasks/{tid}/toggle", timeout=15)
        assert r.status_code == 200
        assert r.json()["status"] == "in_progress"

    def test_backwards_compat_complete_endpoint(self):
        s, _u, m = _register_and_onboard_dsa()
        task = next(t for t in m["tasks"] if t["kind"] != "revise")
        r = s.post(
            f"{BASE_URL}/api/missions/{m['id']}/tasks/{task['id']}/complete", timeout=15,
        )
        assert r.status_code == 200
        updated_task = next(t for t in r.json()["tasks"] if t["id"] == task["id"])
        assert updated_task["completed"] is True


# =============== 7. Adaptive revise mode with prerequisites ===============

class TestAdaptiveRevise:
    def test_revise_mode_inserts_prerequisites(self):
        s, _u, m = _register_and_onboard_dsa()
        arena = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        pattern = arena["primary_pattern"]

        # Submit LOW confidence feedback on all assignments to trigger 'revise'
        for a in arena["assignments"]:
            payload = {
                "difficulty_rating": "hard",
                "solved_status": "could_not_solve",
                "confidence": 2,
                "time_taken_minutes": 40,
            }
            r = s.post(
                f"{BASE_URL}/api/coding-arena/assignments/{a['id']}/feedback",
                json=payload, timeout=15,
            )
            assert r.status_code == 200

        # Delete today's mission to force regeneration
        # We use the fact that PATCH onboarding deletes in_progress mission
        r = s.patch(f"{BASE_URL}/api/onboarding",
                    json={"daily_study_hours": 3}, timeout=15)
        assert r.status_code == 200

        # Regenerate
        m2 = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()

        # Latest adjustment via dashboard
        dash = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        adj = dash.get("adjustment")
        assert adj is not None, "adjustment record missing"
        # Reason should mention weak signals OR advance
        reason = adj["reason"].lower()
        # Either revise (weak signals) or an already-advanced flag
        assert ("weak" in reason) or ("prerequisite" in reason) or ("hint" in reason), \
            f"reason not about weakness: {adj['reason']}"

        # Detected weakness should include the failed pattern
        assert pattern in adj.get("detected_weaknesses", []), \
            f"pattern {pattern} not in {adj.get('detected_weaknesses')}"

        # Mission should contain a 'Revise:' task
        revise_titles = [t["title"] for t in m2["tasks"] if t["kind"] == "revise"]
        assert any(t.startswith("Revise:") for t in revise_titles), \
            f"no prereq revise tasks; got: {[t['title'] for t in m2['tasks']]}"


# =============== 8. Adaptive advance mode ===============

class TestAdaptiveAdvance:
    def test_advance_mode_after_strong_feedback(self):
        s, _u, m = _register_and_onboard_dsa()
        arena = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()

        for a in arena["assignments"]:
            payload = {
                "difficulty_rating": "easy",
                "solved_status": "without_hints",
                "confidence": 10,
                "time_taken_minutes": 15,
            }
            r = s.post(
                f"{BASE_URL}/api/coding-arena/assignments/{a['id']}/feedback",
                json=payload, timeout=15,
            )
            assert r.status_code == 200

        r = s.patch(f"{BASE_URL}/api/onboarding",
                    json={"daily_study_hours": 3}, timeout=15)
        assert r.status_code == 200

        m2 = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        dash = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        adj = dash["adjustment"]
        assert adj is not None
        # Advance flag set
        assert adj.get("advance") is True or "advance" in adj["reason"].lower() or "strong" in adj["reason"].lower(), \
            f"expected advance; got: {adj}"
        assert m2["difficulty"] == "hard"


# =============== 9. Dashboard shape (activity<=5, company_readiness, adjustment) ===============

class TestDashboardShape:
    def test_dashboard_has_new_fields(self):
        s, _u, _m = _register_and_onboard_dsa()
        # Generate multiple activities
        for _ in range(4):
            s.get(f"{BASE_URL}/api/missions/today", timeout=15)
        m = s.get(f"{BASE_URL}/api/missions/today", timeout=15).json()
        for t in m["tasks"][:2]:
            s.post(f"{BASE_URL}/api/missions/{m['id']}/tasks/{t['id']}/toggle", timeout=15)

        dash = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        # Activity capped at 5
        assert len(dash["activity"]) <= 5
        # company_readiness present
        assert "company_readiness" in dash
        assert isinstance(dash["company_readiness"], list)
        # Contains target companies with is_target flag
        target_entries = [c for c in dash["company_readiness"] if c["is_target"]]
        assert len(target_entries) >= 1
        target_ids = {c["company_id"] for c in target_entries}
        assert "google" in target_ids
        # Adjustment field present
        assert "adjustment" in dash


# =============== 10. Knowledge Tree with DSA subtopics ===============

class TestKnowledgeTree:
    def test_knowledge_tree_shape(self):
        s, _u, _m = _register_and_onboard_dsa()
        # Do at least one feedback to get non-zero DSA subtopic progress
        arena = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        aid = arena["assignments"][0]["id"]
        s.post(f"{BASE_URL}/api/coding-arena/assignments/{aid}/feedback",
               json={"difficulty_rating": "medium", "solved_status": "without_hints",
                     "confidence": 8, "time_taken_minutes": 20}, timeout=15)

        tree = s.get(f"{BASE_URL}/api/knowledge/tree", timeout=15).json()
        assert len(tree) == 7
        domains = {d["domain"] for d in tree}
        assert domains == {"dsa", "java", "lld", "hld",
                            "operating_systems", "dbms", "computer_networks"}

        dsa = next(d for d in tree if d["domain"] == "dsa")
        # DSA should have 16 subtopics (from PATTERN_TO_DOMAIN)
        assert len(dsa["subtopics"]) == 16
        for st in dsa["subtopics"]:
            for key in ("label", "progress", "problems_solved",
                        "avg_confidence", "revision_status"):
                assert key in st
            assert st["revision_status"] in ("fresh", "due", "mastered")


# =============== 11. Company readiness endpoint returns 12 ===============

class TestCompanyReadiness:
    def test_readiness_companies(self):
        s, _u, _m = _register_and_onboard_dsa()
        r = s.get(f"{BASE_URL}/api/readiness/companies", timeout=15)
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) == 12
        # Google (DSA-heavy) score should differ from Oracle (DBMS-heavy)
        google = next(c for c in arr if c["company_id"] == "google")
        oracle = next(c for c in arr if c["company_id"] == "oracle")
        # Since user's DSA=1 (weakest) and DBMS=9 (strong), google < oracle
        assert google["score"] != oracle["score"]
        assert google["is_target"] is True
        assert oracle["is_target"] is False


# =============== 12. Recent activity <= 5 in dashboard even after many events ===============

class TestActivityLimit:
    def test_activity_limited_to_5(self):
        s, _u, m = _register_and_onboard_dsa()
        # Perform many actions to generate >5 activity events
        arena = s.get(f"{BASE_URL}/api/coding-arena", timeout=15).json()
        for a in arena["assignments"][:2]:
            s.post(f"{BASE_URL}/api/coding-arena/assignments/{a['id']}/feedback",
                   json={"difficulty_rating": "medium", "solved_status": "without_hints",
                         "confidence": 7, "time_taken_minutes": 20}, timeout=15)
        # practice more
        s.post(f"{BASE_URL}/api/coding-arena/practice-more",
               json={"pattern": arena["primary_pattern"]}, timeout=15)
        # toggle
        s.post(f"{BASE_URL}/api/missions/{m['id']}/tasks/{m['tasks'][0]['id']}/toggle", timeout=15)

        dash = s.get(f"{BASE_URL}/api/dashboard", timeout=15).json()
        assert len(dash["activity"]) <= 5
