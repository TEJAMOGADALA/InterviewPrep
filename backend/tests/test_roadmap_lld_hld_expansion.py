"""Iteration 6: LLD & HLD roadmap expansion tests (data-only)."""
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

# ---------- 23 GoF patterns ----------
CREATIONAL = ["factory", "abstract_factory", "builder", "singleton", "prototype"]
STRUCTURAL = ["adapter", "bridge", "composite", "decorator", "facade", "flyweight", "proxy"]
BEHAVIORAL = ["chain", "command", "interpreter", "iterator", "mediator", "memento",
              "observer", "state", "strategy", "template", "visitor"]

PATTERN_IDS = (
    [f"lld.patterns.creational.{p}" for p in CREATIONAL]
    + [f"lld.patterns.structural.{p}" for p in STRUCTURAL]
    + [f"lld.patterns.behavioral.{p}" for p in BEHAVIORAL]
)
assert len(PATTERN_IDS) == 23

PATTERN_SUBNODES = ["overview", "uml", "use_cases", "java", "interview"]

# Sample of patterns to verify all 5 sub-learning nodes for
PATTERN_SAMPLE = [
    "lld.patterns.creational.singleton",
    "lld.patterns.creational.factory",
    "lld.patterns.structural.decorator",
    "lld.patterns.structural.flyweight",
    "lld.patterns.behavioral.observer",
    "lld.patterns.behavioral.mediator",
    "lld.patterns.behavioral.memento",
    "lld.patterns.behavioral.interpreter",
]

# ---------- New LLD categorized case-study module leaf ids ----------
LLD_CAT_IDS = [
    "lld.cat.caching.lru", "lld.cat.caching.lfu", "lld.cat.caching.ttl",
    "lld.cat.booking.hotel", "lld.cat.booking.flight", "lld.cat.booking.train", "lld.cat.booking.restaurant",
    "lld.cat.commerce.cart", "lld.cat.commerce.inventory", "lld.cat.commerce.warehouse",
    "lld.cat.commerce.coupon", "lld.cat.commerce.gift_card",
    "lld.cat.communication.whatsapp", "lld.cat.communication.chat_server",
    "lld.cat.communication.email_service", "lld.cat.communication.notification_queue",
    "lld.cat.scheduling.cron", "lld.cat.scheduling.task_scheduler", "lld.cat.scheduling.job_queue",
    "lld.cat.banking.account", "lld.cat.banking.wallet", "lld.cat.banking.upi", "lld.cat.banking.transaction_engine",
    "lld.cat.games.sudoku", "lld.cat.games.minesweeper", "lld.cat.games.blackjack", "lld.cat.games.uno",
    "lld.cat.smart.traffic_signal", "lld.cat.smart.vending_machine", "lld.cat.smart.coffee_machine",
    "lld.cat.smart.printer", "lld.cat.smart.library", "lld.cat.smart.hospital",
    "lld.cat.os.memory_allocator", "lld.cat.os.thread_pool",
    "lld.cat.os.connection_pool", "lld.cat.os.file_system",
]

# ---------- HLD existing cases: 10 mandated subtopics ----------
HLD_CASE_SUBS = ["problem", "func_req", "non_func_req", "capacity", "apis", "db",
                 "components", "scaling", "bottlenecks", "interview"]
HLD_EXISTING_CASES = [
    "hld.cases.url_shortener", "hld.cases.rate_limiter", "hld.cases.chat",
    "hld.cases.uber", "hld.cases.payment", "hld.cases.instagram",
]

# ---------- New HLD categorized case-study module leaf ids ----------
HLD_CAT_TOPICS = [
    "hld.cat.storage.google_drive", "hld.cat.storage.dropbox", "hld.cat.storage.s3",
    "hld.cat.messaging.slack", "hld.cat.messaging.discord", "hld.cat.messaging.teams", "hld.cat.messaging.kafka",
    "hld.cat.search.elasticsearch", "hld.cat.search.google_search", "hld.cat.search.autocomplete",
    "hld.cat.streaming.spotify", "hld.cat.streaming.netflix", "hld.cat.streaming.live", "hld.cat.streaming.zoom",
    "hld.cat.finance.upi", "hld.cat.finance.wallet", "hld.cat.finance.payment_gateway", "hld.cat.finance.ledger",
    "hld.cat.infra.api_gateway", "hld.cat.infra.cdn", "hld.cat.infra.distributed_cache",
    "hld.cat.infra.logging", "hld.cat.infra.monitoring", "hld.cat.infra.metrics",
    "hld.cat.social.linkedin", "hld.cat.social.facebook_feed",
    "hld.cat.social.instagram_stories", "hld.cat.social.twitter_timeline",
    "hld.cat.ecommerce.amazon_cart", "hld.cat.ecommerce.inventory",
    "hld.cat.ecommerce.recommendation", "hld.cat.ecommerce.order_service",
    "hld.cat.maps.google_maps_nearby", "hld.cat.maps.uber_dispatch",
    "hld.cat.misc.github", "hld.cat.misc.google_docs",
    "hld.cat.misc.collab_editor", "hld.cat.misc.web_crawler", "hld.cat.misc.online_compiler",
]

# spot-check 2-3 topics per hld.cat with all 10 subtopics
HLD_CAT_SUBTOPIC_SAMPLES = [
    "hld.cat.storage.s3",
    "hld.cat.messaging.kafka",
    "hld.cat.search.elasticsearch",
    "hld.cat.streaming.netflix",
    "hld.cat.finance.payment_gateway",
    "hld.cat.infra.cdn",
    "hld.cat.social.linkedin",
    "hld.cat.ecommerce.order_service",
    "hld.cat.maps.uber_dispatch",
    "hld.cat.misc.github",
]

LEGACY_IDS = [
    "dsa.foundations.arrays.kadane", "java.collections.hashmap",
    "lld.principles.solid", "lld.cases.parking_lot", "lld.cases.book_my_show",
    "lld.patterns.creational.singleton", "lld.patterns.behavioral.observer",
    "hld.cases.url_shortener", "hld.cases.rate_limiter", "hld.cases.uber",
    "os.processes.scheduling", "dbms.relational.acid", "cn.foundations.tcp_ip",
]

EXPECTED_TRACK_MODULE_COUNTS = {
    "dsa": 7, "java": 7, "lld": 13, "hld": 17,
    "os": 3, "dbms": 4, "cn": 3,
}


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
        "email": f"TEST_rm6_{uuid.uuid4().hex[:8]}@prepos.io",
        "password": "Test@1234",
        "name": "Iter6 Tester",
    }
    r = s.post(f"{BASE_URL}/api/auth/register", json=u, timeout=30)
    assert r.status_code == 200, r.text
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
    def test_tracks_and_module_counts(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/roadmap", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["tracks"]) == 10
        # Build map trackId -> module count (children of track)
        for t in data["tracks"]:
            tid = t.get("id")
            expected = EXPECTED_TRACK_MODULE_COUNTS.get(tid)
            if expected is None:
                continue
            mods = t.get("children") or []
            assert len(mods) == expected, f"track {tid}: expected {expected} modules, got {len(mods)}"

    def test_node_count_1000_plus(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/roadmap", timeout=30)
        data = r.json()
        ids = set()
        for t in data["tracks"]:
            _walk(t, ids)
        ids.discard(None)
        assert len(ids) >= 1000, f"Expected >=1000 unique nodes, got {len(ids)}"


class TestGoFPatterns:
    @pytest.mark.parametrize("node_id", PATTERN_IDS)
    def test_pattern_resolves(self, user_session, node_id):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        assert r.status_code == 200, f"{node_id}: {r.status_code} {r.text[:200]}"
        assert r.json()["node"]["id"] == node_id

    @pytest.mark.parametrize("node_id", PATTERN_SAMPLE)
    def test_pattern_has_5_learning_nodes(self, user_session, node_id):
        for sub in PATTERN_SUBNODES:
            sub_id = f"{node_id}.{sub}"
            r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{sub_id}", timeout=15)
            assert r.status_code == 200, f"{sub_id}: {r.status_code} {r.text[:200]}"


class TestLLDCategorizedCases:
    @pytest.mark.parametrize("node_id", LLD_CAT_IDS)
    def test_lld_cat_resolves(self, user_session, node_id):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        assert r.status_code == 200, f"{node_id}: {r.status_code} {r.text[:200]}"


class TestHLDExistingCases10Subs:
    @pytest.mark.parametrize("case_id", HLD_EXISTING_CASES)
    def test_case_has_10_subtopics(self, user_session, case_id):
        for sub in HLD_CASE_SUBS:
            sub_id = f"{case_id}.{sub}"
            r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{sub_id}", timeout=15)
            assert r.status_code == 200, f"{sub_id}: {r.status_code} {r.text[:200]}"


class TestHLDCategorizedCases:
    @pytest.mark.parametrize("node_id", HLD_CAT_TOPICS)
    def test_hld_cat_topic_resolves(self, user_session, node_id):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        assert r.status_code == 200, f"{node_id}: {r.status_code} {r.text[:200]}"

    @pytest.mark.parametrize("node_id", HLD_CAT_SUBTOPIC_SAMPLES)
    def test_hld_cat_topic_has_10_subtopics(self, user_session, node_id):
        for sub in HLD_CASE_SUBS:
            sub_id = f"{node_id}.{sub}"
            r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{sub_id}", timeout=15)
            assert r.status_code == 200, f"{sub_id}: {r.status_code} {r.text[:200]}"


class TestLegacyStillWorks:
    @pytest.mark.parametrize("node_id", LEGACY_IDS)
    def test_legacy(self, user_session, node_id):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        assert r.status_code == 200, f"{node_id}: {r.status_code} {r.text[:200]}"


class TestPrereqLinks:
    @pytest.mark.parametrize("node_id,expected_prereqs", [
        ("lld.cat.caching.lru", ["dsa.linear.linked_list.lru"]),
        ("lld.cat.os.thread_pool", ["java.concurrency.executor"]),
        ("hld.cases.rate_limiter", ["hld.caching.redis", "hld.security.rate_limit"]),
        ("hld.cat.messaging.kafka", ["hld.messaging.kafka"]),
        ("hld.cat.ecommerce.order_service", ["hld.distributed.microservices"]),
    ])
    def test_prereqs_resolve(self, user_session, node_id, expected_prereqs):
        r = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{node_id}", timeout=15)
        assert r.status_code == 200, f"{node_id} did not resolve: {r.text[:200]}"
        prereqs = r.json().get("prerequisites", []) or []
        pids = {p.get("id") for p in prereqs}
        for exp in expected_prereqs:
            assert exp in pids, f"{node_id}: expected prereq {exp} not in {pids}"
            r2 = user_session.get(f"{BASE_URL}/api/roadmap/nodes/{exp}", timeout=15)
            assert r2.status_code == 200, f"prereq {exp} of {node_id} did not resolve"


class TestRegressions:
    def test_missions_today(self, user_session):
        r = user_session.get(f"{BASE_URL}/api/missions/today", timeout=30)
        assert r.status_code < 500, r.text
        assert r.status_code in (200, 404), r.text

    def test_missions_regenerate(self, user_session):
        r = user_session.post(f"{BASE_URL}/api/missions/regenerate", timeout=30)
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

    def test_auth_logout_then_login(self):
        s = requests.Session()
        r = s.post(f"{BASE_URL}/api/auth/login", json=ADMIN, timeout=15)
        assert r.status_code == 200
        r2 = s.post(f"{BASE_URL}/api/auth/logout", timeout=15)
        assert r2.status_code in (200, 204)
