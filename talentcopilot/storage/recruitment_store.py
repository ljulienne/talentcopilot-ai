from __future__ import annotations

import json
import logging
import os
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from talentcopilot.talent_pool.talent_profile import index_recruitment_talents

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("TALENTCOPILOT_DATA_DIR", "data"))
RECRUITMENTS_DIR = DATA_DIR / "recruitments"


def ensure_storage_exists() -> None:
    RECRUITMENTS_DIR.mkdir(parents=True, exist_ok=True)


def get_current_timestamp() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def generate_recruitment_id() -> str:
    return f"REC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def get_recruitment_path(recruitment_id: str) -> Path:
    return RECRUITMENTS_DIR / f"{recruitment_id.strip()}.json"


def make_json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    if is_dataclass(value):
        return make_json_safe(asdict(value))

    if hasattr(value, "model_dump"):
        return make_json_safe(value.model_dump())

    if hasattr(value, "dict"):
        try:
            return make_json_safe(value.dict())
        except Exception:
            pass

    if isinstance(value, dict):
        return {str(key): make_json_safe(val) for key, val in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]

    if hasattr(value, "__dict__"):
        return make_json_safe(vars(value))

    return str(value)


def update_talent_pool_if_needed(recruitment_data: Dict[str, Any]) -> None:
    analysis_batch = recruitment_data.get("analysis_batch")

    if not analysis_batch:
        return

    try:
        indexed_profiles = index_recruitment_talents(recruitment_data)
        logger.info("Talent Pool updated with %s talent(s).", len(indexed_profiles))

    except Exception as exc:
        logger.exception("Talent Pool update failed: %s", exc)


def save_recruitment(recruitment_data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_storage_exists()

    data = deepcopy(recruitment_data)

    if not data.get("id"):
        data["id"] = generate_recruitment_id()

    now = get_current_timestamp()

    if not data.get("created_at"):
        data["created_at"] = now

    data["updated_at"] = now

    if not data.get("title"):
        data["title"] = "Untitled Recruitment"

    safe_data = make_json_safe(data)
    file_path = get_recruitment_path(safe_data["id"])

    try:
        temporary_path = file_path.with_suffix(file_path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(safe_data, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, file_path)

        logger.info("Recruitment saved: %s", file_path)

        update_talent_pool_if_needed(safe_data)

        return safe_data

    except Exception as exc:
        logger.exception("Failed to save recruitment: %s", safe_data.get("id"))
        raise RuntimeError(f"Failed to save recruitment: {exc}") from exc


def load_recruitment(recruitment_id: str) -> Dict[str, Any]:
    ensure_storage_exists()

    file_path = get_recruitment_path(recruitment_id)

    if not file_path.exists():
        raise FileNotFoundError(f"Recruitment not found: {recruitment_id}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def list_recruitments() -> List[Dict[str, Any]]:
    ensure_storage_exists()

    recruitments: List[Dict[str, Any]] = []

    for file_path in RECRUITMENTS_DIR.glob("*.json"):
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            recruitments.append(
                {
                    "id": data.get("id", file_path.stem),
                    "title": data.get("title", "Untitled Recruitment"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "language": data.get("language"),
                    "candidate_count": int(
                        data.get("candidate_count")
                        or len(data.get("candidates", []) or [])
                        or len(data.get("analysis_batch", {}).get("results", []) or [])
                    ),
                    "analyzed_count": int(
                        data.get("analyzed_count")
                        or len(data.get("analyses", []) or [])
                        or len(data.get("analysis_batch", {}).get("results", []) or [])
                    ),
                    "status": data.get("status"),
                    "schema_version": data.get("schema_version"),
                    "job": data.get("job") if isinstance(data.get("job"), dict) else {},
                    "location": (
                        data.get("job", {}).get("location")
                        if isinstance(data.get("job"), dict)
                        else None
                    ),
                    "metadata": data.get("metadata") if isinstance(data.get("metadata"), dict) else {},
                    "workflow_context": (
                        data.get("workflow_context")
                        if isinstance(data.get("workflow_context"), dict)
                        else {}
                    ),
                    "file_path": str(file_path),
                }
            )

        except Exception as exc:
            logger.warning("Skipping invalid recruitment file %s: %s", file_path, exc)

    return sorted(
        recruitments,
        key=lambda item: item.get("updated_at") or "",
        reverse=True,
    )


def delete_recruitment(recruitment_id: str) -> bool:
    ensure_storage_exists()

    file_path = get_recruitment_path(recruitment_id)

    if not file_path.exists():
        return False

    file_path.unlink()
    return True


def update_recruitment(recruitment_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    data = load_recruitment(recruitment_id)

    for key, value in updates.items():
        if key not in {"id", "created_at"}:
            data[key] = value

    return save_recruitment(data)


def duplicate_recruitment(
    recruitment_id: str,
    new_title: Optional[str] = None,
) -> Dict[str, Any]:
    original = load_recruitment(recruitment_id)
    duplicate = deepcopy(original)

    duplicate["id"] = generate_recruitment_id()
    duplicate["title"] = new_title or f"{original.get('title', 'Untitled Recruitment')} - Copy"
    duplicate["created_at"] = get_current_timestamp()
    duplicate["updated_at"] = get_current_timestamp()

    return save_recruitment(duplicate)
