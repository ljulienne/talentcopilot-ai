from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


TALENT_POOL_DIR = Path("data") / "talent_pool"
TALENT_INDEX_PATH = TALENT_POOL_DIR / "talents.json"


def ensure_talent_pool_exists() -> None:
    TALENT_POOL_DIR.mkdir(parents=True, exist_ok=True)

    if not TALENT_INDEX_PATH.exists():
        TALENT_INDEX_PATH.write_text("[]", encoding="utf-8")


def get_current_timestamp() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def load_talents() -> List[Dict[str, Any]]:
    ensure_talent_pool_exists()

    try:
        return json.loads(TALENT_INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_talents(talents: List[Dict[str, Any]]) -> None:
    ensure_talent_pool_exists()
    TALENT_INDEX_PATH.write_text(
        json.dumps(talents, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def find_talent_by_key(candidate_key: str) -> Optional[Dict[str, Any]]:
    talents = load_talents()

    for talent in talents:
        if talent.get("candidate_key") == candidate_key:
            return talent

    return None


def upsert_talent_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    talents = load_talents()

    candidate_key = profile.get("candidate_key")
    now = get_current_timestamp()

    if not candidate_key:
        raise ValueError("Talent profile requires a candidate_key.")

    for index, existing in enumerate(talents):
        if existing.get("candidate_key") == candidate_key:
            financial_data = existing.get("financial_data")

            existing.update(profile)

            if financial_data and not profile.get("financial_data"):
                existing["financial_data"] = financial_data

            existing["updated_at"] = now
            talents[index] = existing
            save_talents(talents)
            return existing

    profile["created_at"] = now
    profile["updated_at"] = now
    talents.append(profile)
    save_talents(talents)

    return profile


def update_talent_financial_data(
    candidate_key: str,
    financial_data: Dict[str, Any],
) -> Dict[str, Any]:
    talents = load_talents()
    now = get_current_timestamp()

    for index, talent in enumerate(talents):
        if talent.get("candidate_key") == candidate_key:
            talent["financial_data"] = financial_data
            talent["updated_at"] = now
            talents[index] = talent
            save_talents(talents)
            return talent

    raise ValueError(f"Talent not found: {candidate_key}")


def list_talent_profiles() -> List[Dict[str, Any]]:
    talents = load_talents()
    return sorted(
        talents,
        key=lambda item: item.get("updated_at") or "",
        reverse=True,
    )
