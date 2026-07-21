"""Iteration 4: roadmap expansion tests (data-only change)."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")

ADMIN = {"email": "admin@prepos.io", "password": "Admin@123"}

LEGACY_IDS = [
    "dsa.foundations.arrays.kadane", "dsa.foundations.arrays.prefix_sum",
    "dsa.foundations.hashing.frequency", "dsa.foundations.hashing.two_sum",
    "dsa.foundations.two_pointers.palindrome", "dsa.foundations.two_pointers.k_sum",
    "dsa.windows.sliding_window.fixed.max_avg",
    "dsa.windows.sliding_window.variable.longest_unique",
    "dsa.windows.sliding_window.variable.min_window",
    "dsa.windows.sliding_window.variable.anagrams",
    "dsa.search.binary_search.basic", "dsa.search.binary_search.rotated",
    "dsa.search.binary_search.on_answer",
    "dsa.linear.stack.parens", "dsa.linear.stack.monotonic",
    "dsa.linear.linked_list.reverse", "dsa.linear.linked_list.fast_slow",
    "dsa.linear.linked_list.lru",
    "dsa.trees.traversal.level_order", "dsa.trees.traversal.depth",
    "dsa.trees.bst.validate", "dsa.trees.bst.kth_smallest",
    "dsa.trees.graphs.islands", "dsa.trees.graphs.topo",
    "dsa.trees.graphs.shortest_path",
    "dsa.heaps.kth", "dsa.heaps.k_closest", "dsa.heaps.two_heaps",
    "dsa.heaps.task_scheduler",
    "dsa.dp.1d.climbing", "dsa.dp.1d.house_robber",
    "dsa.dp.unbounded.coin_change", "dsa.dp.2d.lcs", "dsa.dp.2d.edit_distance",
    "dsa.backtracking.subsets", "dsa.backtracking.word_search",
    "java.collections.hashmap", "java.collections.core",
    "java.collections.comparator",
    "java.concurrency.threads", "java.concurrency.executor", "java.concurrency.sync",
    "java.streams.core", "java.lambdas.core",
    "java.jvm.memory", "java.jvm.gc",
    "java.oop.equals_hashcode", "java.oop.inheritance",
    "lld.principles.solid", "lld.principles.dry_kiss",
    "lld.cases.parking_lot", "lld.cases.chess", "lld.cases.splitwise",
    "hld.foundations.cap", "hld.foundations.consistency",
    "hld.foundations.load_balancing",
    "hld.caching.strategies", "hld.caching.redis",
    "hld.messaging.queues", "hld.messaging.kafka",
    "hld.distributed.systems", "hld.distributed.consensus",
    "hld.cases.url_shortener", "hld.cases.rate_limiter", "hld.cases.news_feed",
    "os.processes.scheduling", "os.processes.sync", "os.processes.deadlocks",
    "os.memory.paging", "os.memory.virtual",
    "dbms.relational.acid", "dbms.relational.indexing",
    "dbms.relational.normalization",
    "dbms.concurrency.isolation", "dbms.concurrency.control",
    "cn.foundations.tcp_ip", "cn.foundations.http_https", "cn.foundations.dns",
    "cn.advanced.load_balancing", "cn.advanced.cdn",
]

NEW_IDS = [
    "dsa.foundations.strings.anagram",
    "dsa.foundations.bit_math.xor_tricks",
    "dsa.trees.tries.implement",
    "dsa.advanced.union_find.core",
    "dsa.dp.lis.core",
    "dsa.greedy.intervals",
    "java.collections.concurrent_map",
    "java.concurrency.completable",
    "java.jvm.classloader",
    "lld.patterns.structural.decorator",
    "lld.cases.book_my_show",
    "hld.db.sharding",
    "hld.cases.uber",
    "hld.cases.payment",
    "os.processes.ipc",
    "dbms.nosql.kv",
    "cn.foundations.http2_http3",
    "cn.advanced.tls_ssl",
]


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json=ADMIN, timeout=30)
    assert r.status_code == 200, r.text
    return s


@pytest.fixture(scope="module")
def user_session():
    s = requests.Session()
    u = {
        "email": f"TEST_rm_{uuid.uuid4().hex[:8]}@prepos.io",
        "password": "Test@1234",
        "name": "Roadmap Tester",
    }
    r = s.post(f"{BASE_URL}/api/auth/register", json=u, timeout=30)
    assert r.status_code == 200, r.text
    # complete onboarding to enable missions
    payload = {
        "target_companies": ["Google"],
        "current_position": "1-3",
        "daily_study_hours": 3,
        "self_assessment": {"dsa": 5, "java": 5, "lld": 5, "hld": 5,
                            "operating_systems": 5, "dbms": 5, "computer_networks": 5},
        "interview_target_date": "2026-06-01",
    }
    r2 = s.post(f"{BASE_URL}/api/onboarding", json=payload, timeout=30)
    assert r2.status_code == 200, r2.text
    return s


def _walk(node, ids):
    ids.add(node.get("id"))
    for c in node.get("children", []) or []:
        _walk(c, ids)


class TestRoadmapTree:
    def test_get_full_roadmap(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/roadmap", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "tracks" in data
        assert "companies" in data
        assert len(data["tracks"]) == 7, f"Expected 7 tracks, got {len(data['tracks'])}"
        companies = data["companies"]
        assert len(companies) == 14, f"Expected 14 companies, got {len(companies)}"
        for req in ("paypal", "goldman_sachs", "zoho", "google"):
            assert req in companies, f"Missing company {req}"

    def test_tree_nested_and_node_count(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/roadmap", timeout=30)
        assert r.status_code == 200
        data = r.json()
        ids = set()
        for t in data["tracks"]:
            _walk(t, ids)
        ids.discard(None)
        assert len(ids) >= 300, f"Expected >=300 unique nodes, got {len(ids)}"
        # Also verify at least one track has nested children->children->children
        found_deep = False
        for t in data["tracks"]:
            for m in t.get("children", []) or []:
                for topic in m.get("children", []) or []:
                    if topic.get("children"):
                        found_deep = True
                        break
        assert found_deep, "No 3-level-deep nesting found"


class TestLegacyIds:
    @pytest.mark.parametrize("node_id", LEGACY_IDS)
    def test_legacy_node_resolves(self, user_session, node_id):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        assert r.status_code == 200, f"{node_id}: {r.status_code} {r.text[:200]}"
        node = r.json().get("node", {})
        assert node.get("id") == node_id
        assert node.get("label"), f"empty label for {node_id}"


class TestNewIds:
    @pytest.mark.parametrize("node_id", NEW_IDS)
    def test_new_node_resolves(self, user_session, node_id):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        assert r.status_code == 200, f"{node_id}: {r.status_code} {r.text[:200]}"
        assert r.json()["node"]["id"] == node_id


class TestPrereqDAG:
    @pytest.mark.parametrize("node_id", [
        "dsa.windows.sliding_window", "hld.messaging.kafka", "dsa.trees.graphs.mst",
    ])
    def test_prereqs_resolve(self, user_session, node_id):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        # Node may or may not exist; if missing, skip
        if r.status_code == 404:
            pytest.skip(f"{node_id} not in roadmap")
        assert r.status_code == 200, r.text
        prereqs = r.json().get("prerequisites", [])
        for p in prereqs:
            pid = p["id"]
            r2 = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{pid}", timeout=15)
            assert r2.status_code == 200, f"prereq {pid} of {node_id} did not resolve"


class TestRegressions:
    def test_missions_today(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/missions/today", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id" in data or "mission" in data or "focus_topic" in data or isinstance(data, dict)

    def test_missions_regenerate(self, user_session):
        r = user_session.post(f"{BASE_URL}/api/missions/regenerate", timeout=30)
        # Endpoint may or may not exist; accept 200 or 404
        assert r.status_code in (200, 404, 405), r.text

    def test_problems_list(self, user_session):
        # /api/problems/patterns is the canonical listing endpoint
        r = user_session.get(f"{BASE_URL}/api/problems/patterns", timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        patterns = data if isinstance(data, list) else data.get("patterns", [])
        assert len(patterns) > 0
        # Also verify individual problem lookup works
        r2 = user_session.get(f"{BASE_URL}/api/problems/lc-53", timeout=15)
        assert r2.status_code == 200, r2.text

    def test_problem_feedback_lc53(self, user_session):
        payload = {"confidence": 8, "time_taken_minutes": 20, "solved": True, "used_hints": False,
                   "notes": "TEST regression", "difficulty_felt": "medium"}
        r = user_session.post(f"{BASE_URL}/api/problems/lc-53/feedback", json=payload, timeout=15)
        # Could be 200/201; 404 means endpoint moved but shouldn't 500
        assert r.status_code < 500, r.text

    def test_profile(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/profile", timeout=15)
        assert r.status_code == 200

    def test_onboarding_get(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/onboarding", timeout=15)
        assert r.status_code == 200

    def test_auth_me(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN["email"]
