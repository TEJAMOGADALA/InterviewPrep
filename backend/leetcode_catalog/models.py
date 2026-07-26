"""Data model for the LeetCode Catalog.

Deliberately separate from any model in `models.py` / `problem_bank.py` —
this record shape mirrors LeetCode's own problem metadata, not the internal
Mission Engine problem shape.
"""
from pydantic import BaseModel, Field
from typing import List


class LeetCodeProblem(BaseModel):
    """A single catalog entry, keyed by `leetcode_id`."""
    leetcode_id: int
    title: str
    slug: str
    difficulty: str  # easy | medium | hard
    topic_tags: List[str] = Field(default_factory=list)
    url: str
