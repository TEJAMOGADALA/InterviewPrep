"""Roadmap Engine — the single source of truth for topic hierarchy.

The master roadmap is loaded from `data/roadmap_v{N}.json`. This engine
exposes O(1) node lookup, tree traversal, prerequisite resolution and
company-importance queries. Every other module (Mission Engine, Coding
Arena, Knowledge Base, Company Readiness, future AI Mentor) should read
from here — never redefine topic strings.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, List, Dict, Iterable
from functools import lru_cache

_DATA_DIR = Path(__file__).parent / "data"
CURRENT_VERSION = "v1"


class RoadmapNode(dict):
    """Lightweight dict subclass for readability. Never mutate."""


def _flatten(node: dict, parent_id: Optional[str], depth: int,
             out: Dict[str, dict], type_hint: str) -> None:
    """Walk the roadmap JSON, tagging each node with parent/depth/type/children."""
    node["type"] = type_hint
    node["parent_id"] = parent_id
    node["depth"] = depth
    node["child_ids"] = []

    # Recurse into modules / topics / subtopics / learning_nodes
    for key, child_type in (
        ("modules", "module"),
        ("topics", "topic"),
        ("subtopics", "subtopic"),
        ("learning_nodes", "node"),
    ):
        children = node.get(key)
        if not children:
            continue
        for c in children:
            node["child_ids"].append(c["id"])
            _flatten(c, parent_id=node["id"], depth=depth + 1, out=out, type_hint=child_type)

    out[node["id"]] = node


class RoadmapEngine:
    def __init__(self, version: str = CURRENT_VERSION):
        self.version = version
        self._raw = self._load(version)
        self._index: Dict[str, dict] = {}
        self._by_pattern: Dict[str, List[dict]] = {}
        for track in self._raw["tracks"]:
            _flatten(track, parent_id=None, depth=0, out=self._index, type_hint="track")
        for node in self._index.values():
            pat = node.get("pattern")
            if pat:
                self._by_pattern.setdefault(pat, []).append(node)

    @staticmethod
    def _load(version: str) -> dict:
        f = _DATA_DIR / f"roadmap_{version}.json"
        with open(f, "r", encoding="utf-8") as fh:
            return json.load(fh)

    # ---------- Tree APIs ----------
    def tree(self) -> dict:
        return {
            "version": self.version,
            "companies": self._raw.get("companies", []),
            "tracks": self._raw["tracks"],
        }

    def get(self, node_id: str) -> Optional[dict]:
        return self._index.get(node_id)

    def all_nodes(self) -> Iterable[dict]:
        return self._index.values()

    def children(self, node_id: str) -> List[dict]:
        n = self.get(node_id)
        if not n:
            return []
        return [self._index[c] for c in n.get("child_ids", []) if c in self._index]

    def ancestors(self, node_id: str) -> List[dict]:
        """Root-to-node breadcrumb (excludes the node itself)."""
        path = []
        cur = self.get(node_id)
        while cur and cur.get("parent_id"):
            parent = self.get(cur["parent_id"])
            if parent:
                path.append(parent)
                cur = parent
            else:
                break
        return list(reversed(path))

    def find_track(self, node_id: str) -> Optional[dict]:
        cur = self.get(node_id)
        if not cur:
            return None
        while cur and cur.get("parent_id"):
            cur = self.get(cur["parent_id"])
        return cur

    # ---------- Metadata ----------
    def prerequisites(self, node_id: str) -> List[dict]:
        n = self.get(node_id)
        if not n:
            return []
        result = []
        for pid in n.get("prerequisites", []) or []:
            p = self.get(pid)
            if p:
                result.append(p)
        return result

    def related(self, node_id: str) -> List[dict]:
        n = self.get(node_id)
        if not n:
            return []
        result = []
        for rid in n.get("related", []) or []:
            r = self.get(rid)
            if r:
                result.append(r)
        return result

    def by_pattern(self, pattern: str) -> List[dict]:
        return self._by_pattern.get(pattern, [])

    def topic_for_pattern(self, pattern: str) -> Optional[dict]:
        nodes = self._by_pattern.get(pattern, [])
        return nodes[0] if nodes else None

    def problems_for_node(self, node_id: str) -> List[str]:
        n = self.get(node_id)
        if not n:
            return []
        # Aggregate problem_ids from this node + descendants
        pids: List[str] = list(n.get("problem_ids", []) or [])
        for c_id in n.get("child_ids", []):
            pids.extend(self.problems_for_node(c_id))
        return pids

    def company_importance(self, node_id: str, company_id: str) -> int:
        """Returns 0-5. Falls back to track-level importance."""
        n = self.get(node_id)
        if not n:
            return 0
        track = self.find_track(node_id)
        for src in (n, track):
            if src and (ci := src.get("company_importance")):
                if company_id in ci:
                    return int(ci[company_id])
        return 0

    def tracks(self) -> List[dict]:
        return list(self._raw["tracks"])

    def track_ids(self) -> List[str]:
        return [t["id"] for t in self._raw["tracks"]]


# Singleton
@lru_cache(maxsize=1)
def get_roadmap(version: str = CURRENT_VERSION) -> RoadmapEngine:
    return RoadmapEngine(version)


# ---------- Adapters for backwards compatibility ----------
# The mission engine and other modules used to define TOPIC_META, PATTERN_TO_DOMAIN
# and pattern prerequisites inline. Expose the same shapes derived from roadmap.

def topic_meta() -> Dict[str, Dict]:
    """Return dict shaped like the legacy TOPIC_META: track_id → {label, subtopics: [(name, difficulty)]}"""
    r = get_roadmap()
    result: Dict[str, Dict] = {}
    for track in r.tracks():
        subs = []
        for module in track.get("modules", []) or []:
            for topic in module.get("topics", []) or []:
                subs.append((topic["label"], topic.get("difficulty", "medium")))
        result[track["id"]] = {"label": track["label"], "subtopics": subs}
    return result


def subtopic_to_pattern() -> Dict[str, str]:
    """Legacy SUBTOPIC_TO_PATTERN — label → pattern."""
    r = get_roadmap()
    result: Dict[str, str] = {}
    for n in r.all_nodes():
        pat = n.get("pattern")
        if pat and n.get("type") == "topic":
            result[n["label"]] = pat
    return result


def pattern_to_track() -> Dict[str, str]:
    """pattern → (track_id, track_label) — legacy PATTERN_TO_DOMAIN."""
    r = get_roadmap()
    result = {}
    for pat, nodes in r._by_pattern.items():
        node = nodes[0]
        track = r.find_track(node["id"])
        result[pat] = (track["id"] if track else "dsa", node["label"])
    return result
