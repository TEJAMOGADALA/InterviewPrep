"""RC1.3.6A Phase 8 — 5-persona validation (temporary, read-only against a
FakeDB — no real database is touched; deleted after use)."""
import asyncio
from datetime import date, timedelta

from roadmap import get_roadmap
from services.progress_engine import seed_knowledge_nodes_from_self_assessment
from services.learning_engine.planner import get_today_learning_node
from services.learning_engine.pacing import compute_pacing_state


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    async def to_list(self, length=None):
        return list(self._rows)


class FakeCollection:
    def __init__(self):
        self._rows = []

    def find(self, query=None, projection=None):
        query = query or {}
        matched = [r for r in self._rows if all(r.get(k) == v for k, v in query.items())]
        return FakeCursor(matched)

    async def insert_many(self, rows):
        self._rows.extend(rows)


class FakeDB:
    def __init__(self):
        self.knowledge_nodes = FakeCollection()


roadmap = get_roadmap()


async def run_persona(name, self_assessment, position, companies, *, interview_date=None, daily_hours=2):
    db = FakeDB()
    await seed_knowledge_nodes_from_self_assessment(db, "user", self_assessment, roadmap)
    pacing_state = None
    if interview_date:
        pacing_state = compute_pacing_state(interview_date, daily_study_hours=daily_hours)
    rec = await get_today_learning_node(
        "user", db=db, position=position, target_companies=companies,
        onboarding={"current_position": position, "self_assessment": self_assessment},
        pacing_state=pacing_state,
    )
    node = roadmap.get(rec["node_id"]) if rec else None
    urgency = (pacing_state or {}).get("urgency", 0.0)
    print(f"=== {name} ===")
    print(f"    position={position} companies={companies} urgency={urgency:.2f}")
    if node:
        print(f"    -> picked: {node['id']}  track={node['track']}  stage={node.get('learning_stage')}  difficulty={node.get('difficulty')}")
    else:
        print("    -> no recommendation")
    print()


async def main():
    await run_persona(
        "1. Student / Google / Low scores", position="student", companies=["google"],
        self_assessment={"dsa": 1, "java": 1, "lld": 1, "hld": 1, "operating_systems": 2, "dbms": 2, "computer_networks": 2},
    )
    await run_persona(
        "2. 1-3yr / Microsoft / Medium scores", position="1-3", companies=["microsoft"],
        self_assessment={"dsa": 5, "java": 5, "lld": 4, "hld": 4, "operating_systems": 5, "dbms": 5, "computer_networks": 5},
    )
    await run_persona(
        "3. 3-5yr / Uber / High scores", position="3-5", companies=["uber"],
        self_assessment={"dsa": 8, "java": 8, "lld": 8, "hld": 8, "operating_systems": 8, "dbms": 8, "computer_networks": 8},
    )
    await run_persona(
        "4. Mixed / Strong Java / Weak DSA", position="1-3", companies=["oracle"],
        self_assessment={"dsa": 2, "java": 9, "lld": 5, "hld": 5, "operating_systems": 5, "dbms": 5, "computer_networks": 5},
    )
    await run_persona(
        "5. All 10s / Interview in 14 days", position="3-5", companies=["google", "uber"],
        self_assessment={"dsa": 10, "java": 10, "lld": 10, "hld": 10, "operating_systems": 10, "dbms": 10, "computer_networks": 10},
        interview_date=(date.today() + timedelta(days=14)).isoformat(), daily_hours=3,
    )


asyncio.run(main())
