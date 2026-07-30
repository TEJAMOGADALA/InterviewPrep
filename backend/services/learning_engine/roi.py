"""Learning ROI — derived purely from the roadmap's existing prerequisite graph.

Never stored: every value here is recomputed on demand from `roadmap.py`'s
node index (specifically each node's existing `prerequisites` list, inverted),
so it can never drift from the roadmap it describes. This is the "future
nodes unlocked / prerequisite importance / dependency count" signal consumed
by `ranking.py` (as an additional scoring term) and by `insight.py` (for the
human-readable Recommendation Insight).
"""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Set

from roadmap import get_roadmap


@lru_cache(maxsize=1)
def _reverse_dependents() -> Dict[str, List[str]]:
    """node_id -> ids of learning nodes that list it as a direct prerequisite."""
    roadmap = get_roadmap()
    reverse: Dict[str, List[str]] = {}
    for node in roadmap.get_learning_nodes():
        for prereq_id in node.get("prerequisites", []) or []:
            reverse.setdefault(prereq_id, []).append(node["id"])
    return reverse


def _downstream_closure(node_id: str) -> Set[str]:
    """Every node transitively reachable from `node_id` in the reverse-prerequisite
    graph — i.e. the full long-term curriculum value of completing it."""
    reverse = _reverse_dependents()
    seen: Set[str] = set()
    queue = list(reverse.get(node_id, []))
    while queue:
        current = queue.pop()
        if current in seen:
            continue
        seen.add(current)
        queue.extend(reverse.get(current, []))
    return seen


def compute_learning_roi(node_id: str) -> dict:
    """Return the roadmap-graph ROI signal for one learning node.

    - direct_unlocks: nodes that list this node as a direct prerequisite.
    - total_downstream_unlocks: full transitive reach in the dependency graph.
    - dependency_count: how many prerequisites this node itself needs (a
      shallow, cheap-to-reach node scores higher ROI than a deep, costly one).
    - roi_score: 0-100, direct unlocks weighted highest, downstream reach
      lightly, deep prerequisite chains lightly penalized.
    """
    roadmap = get_roadmap()
    node = roadmap.get_learning_node(node_id) if node_id else None
    if node is None:
        return {"direct_unlocks": 0, "total_downstream_unlocks": 0, "dependency_count": 0, "roi_score": 0.0}

    direct_unlocks = len(_reverse_dependents().get(node_id, []))
    total_downstream_unlocks = len(_downstream_closure(node_id))
    dependency_count = len(node.get("prerequisites", []) or [])

    raw = direct_unlocks * 6.0 + total_downstream_unlocks * 1.5 - dependency_count * 1.0
    roi_score = max(0.0, min(100.0, raw))

    return {
        "direct_unlocks": direct_unlocks,
        "total_downstream_unlocks": total_downstream_unlocks,
        "dependency_count": dependency_count,
        "roi_score": round(roi_score, 2),
    }
