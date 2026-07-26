"""LeetCode Catalog — foundation for Coding Arena search & discovery.

This package is a completely separate component from `problem_bank.py`.
`problem_bank.py` remains the single source of truth for:
    - Mission generation
    - AI Mentor recommendations
    - Progress roadmap
    - Revision roadmap

The LeetCode Catalog exists solely to back future problem search/discovery
features and must not be read by (or write into) any of the systems above.

Public API:
    LeetCodeProblem   — the catalog record model.
    get_by_id()       — look up a problem by its LeetCode numeric ID.
    get_by_title()    — look up a problem by its exact title (case-insensitive).
    search()          — ranked exact/partial/fuzzy title (or numeric id) search.
    count()           — number of problems currently loaded in the catalog.
    reload_catalog()  — drop the cached catalog so it is re-read from disk.
    import_catalog()  — parse an external JSON/CSV export into LeetCodeProblem records.
"""
from .models import LeetCodeProblem
from .repository import get_by_id, get_by_title, search, count, reload_catalog
from .importer import import_catalog, load_from_json, load_from_csv

__all__ = [
    "LeetCodeProblem",
    "get_by_id",
    "get_by_title",
    "search",
    "count",
    "reload_catalog",
    "import_catalog",
    "load_from_json",
    "load_from_csv",
]
