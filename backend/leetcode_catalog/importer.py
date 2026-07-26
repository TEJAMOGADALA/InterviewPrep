"""Production import mechanism for the LeetCode Catalog.

Parses an external JSON or CSV export of the full LeetCode problem set into
`LeetCodeProblem` records. This is the mechanism intended to populate the
*real* catalog (the complete LeetCode problem set) and is intentionally
decoupled from `problem_bank.py` and from the small `data/dev_seed.json`
placeholder used for local development (see repository.py).

Expected external file schema:
    - JSON: either a top-level list of objects, or an object of the form
      `{"problems": [ ... ]}`.
    - CSV: a header row followed by one row per problem.

Column/key names are matched case-insensitively and support common aliases
from typical LeetCode dataset exports:
    - leetcode_id | id | frontend_id | question_id  -> leetcode_id (int)
    - title | question_title                         -> title (str)
    - slug | title_slug                              -> slug (derived from title if absent)
    - difficulty                                     -> difficulty (str)
    - topic_tags | tags                              -> topic_tags (comma-separated in CSV, list in JSON)
    - url | problem_url | leetcode_url               -> url (derived from slug if absent)
"""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path
from typing import List, Optional, Union

from .models import LeetCodeProblem

PathLike = Union[str, Path]

_ALIASES = {
    "leetcode_id": ("leetcode_id", "id", "frontend_id", "question_id"),
    "title": ("title", "question_title"),
    "slug": ("slug", "title_slug"),
    "difficulty": ("difficulty",),
    "topic_tags": ("topic_tags", "tags"),
    "url": ("url", "problem_url", "leetcode_url"),
}


def _pick(row: dict, field: str) -> Optional[object]:
    lowered = {str(k).lower(): v for k, v in row.items()}
    for alias in _ALIASES[field]:
        value = lowered.get(alias)
        if value not in (None, ""):
            return value
    return None


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def _normalize_row(row: dict) -> LeetCodeProblem:
    leetcode_id = _pick(row, "leetcode_id")
    title = _pick(row, "title")
    if leetcode_id is None or title is None:
        raise ValueError(f"Catalog row missing required leetcode_id/title: {row!r}")

    title = str(title)
    slug = _pick(row, "slug") or _slugify(title)
    difficulty = str(_pick(row, "difficulty") or "unknown").lower()

    tags_raw = _pick(row, "topic_tags") or []
    if isinstance(tags_raw, str):
        topic_tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    else:
        topic_tags = [str(t).strip() for t in tags_raw if str(t).strip()]

    url = _pick(row, "url") or f"https://leetcode.com/problems/{slug}/"

    return LeetCodeProblem(
        leetcode_id=int(leetcode_id),
        title=title,
        slug=str(slug),
        difficulty=difficulty,
        topic_tags=topic_tags,
        url=str(url),
    )


def load_from_json(path: PathLike) -> List[LeetCodeProblem]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = raw["problems"] if isinstance(raw, dict) and "problems" in raw else raw
    return [_normalize_row(r) for r in rows]


def load_from_csv(path: PathLike) -> List[LeetCodeProblem]:
    with open(path, newline="", encoding="utf-8") as f:
        return [_normalize_row(r) for r in csv.DictReader(f)]


def import_catalog(path: PathLike) -> List[LeetCodeProblem]:
    """Entry point for the production import — dispatches on file extension."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return load_from_csv(p)
    if suffix == ".json":
        return load_from_json(p)
    raise ValueError(f"Unsupported catalog file type: {suffix!r} (expected .json or .csv)")
