"""Builder for additive learning recommendations."""
from __future__ import annotations

from typing import Optional


def build_learning_recommendation(
    node: dict,
    *,
    progress: Optional[dict] = None,
    support_recommendation: Optional[dict] = None,
) -> dict:
    """Convert a roadmap node into a structured learning recommendation."""
    progress = progress or {}
    confidence = float(progress.get("confidence", 0.0) or 0.0)
    weakness = float(progress.get("weakness_score", 0.0) or 0.0)
    mastery = float(progress.get("mastery", 0.0) or 0.0)

    reason_parts = [
        f"Focus on {node.get('label') or node.get('id')}",
        f"confidence {confidence:.1f}/10",
        f"weakness {weakness:.0f}",
        f"mastery {mastery:.0f}%",
    ]
    recommendation = {
        "node_id": node.get("id"),
        "track": node.get("track"),
        "module": node.get("module"),
        "topic": node.get("topic"),
        "subtopic": node.get("subtopic"),
        "label": node.get("label") or node.get("id"),
        "estimated_minutes": int(node.get("estimated_minutes") or 0),
        "difficulty": node.get("difficulty") or "medium",
        "reason": "; ".join(reason_parts),
        "recommendation_type": "learning",
    }
    if support_recommendation:
        for key in ("support_track", "support_topic", "support_node"):
            if support_recommendation.get(key) is not None:
                recommendation[key] = support_recommendation[key]
    return recommendation
