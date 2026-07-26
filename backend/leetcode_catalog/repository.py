"""Repository for the LeetCode Catalog.

Loads `LeetCodeProblem` records either from a configured production import
file (JSON/CSV — see importer.py) or, only when no production file is
configured/found, from the small `data/dev_seed.json` placeholder shipped
for local development. This module is intentionally independent of
`problem_bank.py`, which remains the source of truth for Mission Engine,
AI Mentor, and progress/revision roadmap features.

To populate the real catalog, set the `LEETCODE_CATALOG_PATH` environment
variable to point at a full JSON/CSV export of the LeetCode problem set.
"""
from __future__ import annotations
import difflib
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from .importer import import_catalog
from .models import LeetCodeProblem

logger = logging.getLogger("prepos")

_DATA_DIR = Path(__file__).parent / "data"
_DEV_SEED_PATH = _DATA_DIR / "dev_seed.json"  # dev-only placeholder — never used in production
_CATALOG_PATH_ENV = "LEETCODE_CATALOG_PATH"   # set to the full production import file


@lru_cache(maxsize=1)
def _load_catalog() -> Dict[int, LeetCodeProblem]:
    configured_path = os.environ.get(_CATALOG_PATH_ENV)

    if configured_path and Path(configured_path).exists():
        problems = import_catalog(configured_path)
    else:
        if configured_path:
            logger.warning(
                "LEETCODE_CATALOG_PATH=%s not found; falling back to the dev_seed.json placeholder.",
                configured_path,
            )
        else:
            logger.info(
                "LEETCODE_CATALOG_PATH not set; loading dev_seed.json placeholder catalog. "
                "Set LEETCODE_CATALOG_PATH to a full JSON/CSV export to populate the real catalog."
            )
        problems = import_catalog(_DEV_SEED_PATH)

    return {p.leetcode_id: p for p in problems}


def reload_catalog() -> None:
    """Clear the cached catalog so the next lookup re-reads from disk."""
    _load_catalog.cache_clear()


def get_by_id(leetcode_id: int) -> Optional[LeetCodeProblem]:
    """Look up a catalog entry by its LeetCode numeric ID."""
    return _load_catalog().get(leetcode_id)


def get_by_title(title: str) -> Optional[LeetCodeProblem]:
    """Look up a catalog entry by its exact title (case-insensitive)."""
    needle = title.strip().lower()
    for problem in _load_catalog().values():
        if problem.title.strip().lower() == needle:
            return problem
    return None


def count() -> int:
    """Number of problems currently loaded in the catalog."""
    return len(_load_catalog())


def search(query: str, limit: int = 20) -> List[LeetCodeProblem]:
    """Ranked search across the catalog by numeric id or title.

    Match priority (highest first):
      1. Exact numeric `leetcode_id` match (query is all digits).
      2. Exact title match (case-insensitive).
      3. Title starts with the query.
      4. Query is a substring of the title.
      5. Fuzzy title similarity (stdlib difflib) above a similarity floor.
    """
    needle = (query or "").strip().lower()
    if not needle:
        return []

    catalog = _load_catalog()
    if needle.isdigit() and int(needle) in catalog:
        return [catalog[int(needle)]]

    scored = []
    for problem in catalog.values():
        title_l = problem.title.strip().lower()
        if title_l == needle:
            score = 100.0
        elif title_l.startswith(needle):
            score = 85.0
        elif needle in title_l:
            score = 70.0
        else:
            ratio = difflib.SequenceMatcher(None, needle, title_l).ratio()
            if ratio < 0.55:
                continue
            score = ratio * 60.0
        scored.append((score, problem.leetcode_id, problem))

    scored.sort(key=lambda row: (-row[0], row[1]))
    return [problem for _, _, problem in scored[:limit]]
