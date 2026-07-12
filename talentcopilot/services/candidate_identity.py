from __future__ import annotations

import hashlib
import re
from typing import Any, Dict


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "candidate"


def resolve_candidate_id(candidate: Dict[str, Any]) -> str:
    """Return a stable candidate identifier without relying on display name alone.

    Existing IDs are preserved. For legacy records, a deterministic fallback is
    derived from the most stable available profile attributes. The fallback is
    intentionally deterministic so the same snapshot produces the same ID.
    """
    for key in ("candidate_id", "id", "external_id", "employee_id"):
        value = candidate.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()

    name = str(candidate.get("name") or candidate.get("full_name") or "Candidate").strip()
    title = str(candidate.get("title") or candidate.get("role") or "").strip()
    email = str(candidate.get("email") or "").strip().lower()
    source = str(candidate.get("source") or candidate.get("filename") or "").strip().lower()
    fingerprint = "|".join((name.lower(), title.lower(), email, source))
    digest = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:10]
    return f"cand-{_slug(name)}-{digest}"
