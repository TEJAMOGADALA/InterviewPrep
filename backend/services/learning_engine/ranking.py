"""Ranking model for additive learning recommendations."""
from __future__ import annotations

from typing import Iterable, List, Optional


def rank_learning_nodes(
    candidates: Iterable[dict],
    progress_map: Optional[dict] = None,
    *,
    target_companies: Optional[Iterable[str]] = None,
) -> List[dict]:
    """Rank nodes by a simple, isolated scoring model.

    Factors include company importance, low confidence, high weakness, low mastery,
    and shorter estimated_minutes for easier pick-ups. The scoring is intentionally
    simple so it can later be replaced by a more advanced model.
    """
    progress_map = progress_map or {}
    companies = [company.lower() for company in (target_companies or [])]

    scored = []
    for node in candidates:
        progress = progress_map.get(node.get("id"), {})
        confidence = float(progress.get("confidence", 0.0) or 0.0)
        weakness = float(progress.get("weakness_score", 100.0) or 100.0)
        mastery = float(progress.get("mastery", 0.0) or 0.0)
        difficulty = (node.get("difficulty") or "medium").lower()
        estimated_minutes = int(node.get("estimated_minutes") or 0)
        company_importance = node.get("company_importance") or {}
        company_score = 0.0
        for company in companies:
            company_score += float(company_importance.get(company, 0) or 0)

        difficulty_penalty = {"easy": 0.0, "medium": 0.2, "hard": 0.4}.get(difficulty, 0.2)
        score = (
            (100.0 - confidence * 10.0) * 0.45
            + weakness * 0.35
            + (100.0 - mastery) * 0.15
            + company_score * 0.05
            - difficulty_penalty * 10.0
            - min(estimated_minutes, 60) * 0.01
        )
        scored.append((score, node))

    return [node for _, node in sorted(scored, key=lambda item: item[0], reverse=True)]
