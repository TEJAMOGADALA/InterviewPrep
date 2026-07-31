"""Recommendation Insight — the single explainable object built from the same
signals `ranking.py` used to pick today's mission.

Never hardcode explanations: every sentence and highlight here is assembled
from the actual score breakdown (`ranking.score_learning_node`), the
roadmap-graph ROI (its `roi` sub-dict) and the pacing/forecast state — so the
explanation can never contradict the ranking that produced it.

Single source of truth: consumed via `DailyMission.recommendation_insight`
(Mission Control). AI Mentor's context builder reads the same
`daily_missions` document, so it gets the identical object for free. Future
Analytics and a mobile app should read this same field rather than
recomputing an explanation independently.
"""
from __future__ import annotations

from typing import Iterable, List, Optional

from roadmap import get_roadmap

_WEAK_CONFIDENCE_THRESHOLD = 4.0
_WEAK_WEAKNESS_THRESHOLD = 50.0
_FREQUENT_THRESHOLD = 4.0


def _company_relevance(node: dict, breakdown: dict, target_companies: Optional[Iterable[str]]) -> dict:
    companies = [c.lower() for c in (target_companies or [])]
    if not companies:
        return {"target_companies": [], "score": 0.0, "per_company": {}, "top_company": None}

    roadmap = get_roadmap()
    company_key = node.get("track") or node.get("id")
    per_company = {c: roadmap.company_importance(company_key, c) for c in companies}
    top_company = max(per_company, key=per_company.get) if per_company else None
    return {
        "target_companies": companies,
        "score": breakdown.get("company_score", 0.0),
        "per_company": per_company,
        "top_company": top_company,
    }


def _highlights(breakdown: dict, company_relevance: dict, fits_today: Optional[bool]) -> List[str]:
    highlights: List[str] = []
    if breakdown.get("weakness", 0.0) >= _WEAK_WEAKNESS_THRESHOLD or breakdown.get("confidence", 10.0) <= _WEAK_CONFIDENCE_THRESHOLD:
        highlights.append("Weak topic")
    if company_relevance.get("score", 0.0) > 0:
        top = company_relevance.get("top_company")
        highlights.append(f"High relevance to {top}" if top else "High company relevance")
    if breakdown.get("interview_frequency", 0.0) >= _FREQUENT_THRESHOLD:
        highlights.append("Frequently asked in interviews")
    roi = breakdown.get("roi") or {}
    if roi.get("direct_unlocks", 0) > 0:
        count = roi["direct_unlocks"]
        highlights.append(f"Unlocks {count} future topic{'s' if count != 1 else ''}")
    if fits_today:
        highlights.append("Fits today's study time")
    return highlights


def _explanation(
    node: dict,
    breakdown: dict,
    company_relevance: dict,
    *,
    fits_today: Optional[bool] = None,
    daily_capacity_minutes: Optional[float] = None,
) -> str:
    """Build a readable, bulleted "why this was picked" explanation.

    Every bullet is derived straight from `breakdown` / `company_relevance` /
    the pacing state already computed for this recommendation — the same
    signals `ranking.py` used to pick it — so this can never assert
    something the ranking didn't actually consider. Falls back to a plain
    one-line sentence when none of the richer signals apply (e.g. a cold
    start with no target companies and no pacing data yet).
    """
    label = node.get("label") or node.get("id")
    confidence = breakdown.get("confidence", 0.0)
    weakness = breakdown.get("weakness", 0.0)
    mastery = breakdown.get("mastery", 0.0)

    bullets: List[str] = [
        f"confidence {confidence:.1f}/10, weakness {weakness:.0f}, mastery {mastery:.0f}%"
    ]
    if confidence <= _WEAK_CONFIDENCE_THRESHOLD:
        bullets.append(f"your confidence is low ({confidence:.0f}/10)")
    elif confidence >= 8.0:
        bullets.append(f"you're already confident here ({confidence:.0f}/10) \u2014 time to push further")

    if node.get("prerequisites"):
        bullets.append("prerequisite topics are complete")

    roi = breakdown.get("roi") or {}
    if roi.get("direct_unlocks"):
        count = roi["direct_unlocks"]
        bullets.append(f"it unlocks {count} downstream topic{'s' if count != 1 else ''}")

    top_company = company_relevance.get("top_company")
    if company_relevance.get("score", 0.0) > 0 and top_company:
        bullets.append(f"{top_company.title()} frequently asks this pattern")

    if breakdown.get("urgency", 0.0) > 0:
        bullets.append("prioritized to keep you on pace for your interview date")

    if fits_today and daily_capacity_minutes:
        hours = daily_capacity_minutes / 60.0
        hours_label = f"{hours:.0f}" if hours == int(hours) else f"{hours:.1f}"
        bullets.append(f"it fits today's {hours_label}-hour study window")

    if not bullets:
        return f'Selected "{label}" as today\'s best next step.'
    return f'This topic was selected because:\n' + "\n".join(f"\u2022 {b}" for b in bullets)


def build_recommendation_insight(
    node: dict,
    *,
    score_breakdown: dict,
    target_companies: Optional[Iterable[str]] = None,
    pacing_state: Optional[dict] = None,
    forecast: Optional[dict] = None,
) -> dict:
    """Assemble the structured, explainable Recommendation Insight for one node.

    Pure function over already-computed signals (`score_breakdown` from
    `ranking.score_learning_node`, `pacing_state` from
    `pacing.compute_pacing_state`, `forecast` from `pacing.forecast_completion`)
    — it derives an explanation and highlights, it never re-derives a score.
    """
    pacing_state = pacing_state or {}
    company_relevance = _company_relevance(node, score_breakdown, target_companies)

    estimated_minutes = int(node.get("estimated_minutes") or 0)
    daily_capacity = pacing_state.get("daily_capacity_minutes")
    fits_today = estimated_minutes <= daily_capacity if daily_capacity is not None else None

    highlights = _highlights(score_breakdown, company_relevance, fits_today)
    explanation = _explanation(
        node, score_breakdown, company_relevance,
        fits_today=fits_today, daily_capacity_minutes=daily_capacity,
    )

    return {
        "node_id": node.get("id"),
        "label": node.get("label") or node.get("id"),
        "track": node.get("track"),
        "overall_score": round(score_breakdown.get("total_score", 0.0), 2),
        "estimated_study_minutes": estimated_minutes,
        "fits_today_study_time": fits_today,
        "confidence": score_breakdown.get("confidence"),
        "weakness": score_breakdown.get("weakness"),
        "mastery": score_breakdown.get("mastery"),
        "interview_frequency": score_breakdown.get("interview_frequency"),
        "company_relevance": company_relevance,
        "roi": score_breakdown.get("roi"),
        "pacing": {
            "mode": pacing_state.get("pacing_mode"),
            "urgency": pacing_state.get("urgency", 0.0),
            "remaining_days": pacing_state.get("remaining_days"),
        },
        "forecast": forecast,
        "ranking_factors": score_breakdown,
        "highlights": highlights,
        "explanation": explanation,
    }
