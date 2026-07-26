"""LeetCode Catalog search routes — manual search & discovery ONLY.

These endpoints are backed exclusively by the `leetcode_catalog` package
(`get_by_id` / `get_by_title`) and MUST NOT import from or depend on
`problem_bank.py`. They are not read by, and do not affect, the Mission
Engine, Today's Mission, Practice More, AI Mentor, Progress, Roadmap, or
Revision systems — `problem_bank.py` remains the sole source of truth for
those.
"""
from fastapi import APIRouter, Depends, HTTPException

from auth_utils import get_current_user
from leetcode_catalog import get_by_id, get_by_title, search

router = APIRouter(prefix="/api/leetcode", tags=["leetcode-catalog"])


@router.get("/problems/search")
async def search_catalog_problems(q: str, limit: int = 20, user=Depends(get_current_user)):
    """Ranked exact/partial/fuzzy title search (numeric queries match by id)."""
    limit = max(1, min(limit, 50))
    if not q or not q.strip():
        return []
    return search(q, limit=limit)


@router.get("/problems/title/{title}")
async def get_catalog_problem_by_title(title: str, user=Depends(get_current_user)):
    problem = get_by_title(title)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.get("/problems/{leetcode_id}")
async def get_catalog_problem_by_id(leetcode_id: int, user=Depends(get_current_user)):
    problem = get_by_id(leetcode_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem
