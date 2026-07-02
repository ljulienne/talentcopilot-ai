from __future__ import annotations

import re
from typing import Any, Dict


def normalize_candidate_name(name: str) -> str:
    cleaned = name.lower().strip()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def build_candidate_key(candidate: Dict[str, Any]) -> str:
    name = candidate.get("name") or "unknown-candidate"
    return normalize_candidate_name(name).replace(" ", "-")
