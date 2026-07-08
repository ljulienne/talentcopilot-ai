import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

@dataclass
class CacheLookupResult:
    hit: bool
    key: str
    path: Path

class LLMExtractionCache:
    def __init__(self, cache_dir: str | Path | None = None):
        self.cache_dir = Path(cache_dir or ".talentcopilot_cache/llm_extraction")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def key(self, extraction_type: str, text: str, model: str = "default") -> str:
        return hashlib.sha256(f"{extraction_type}::{model}::{text or ''}".encode("utf-8")).hexdigest()

    def path_for(self, extraction_type: str, text: str, model: str = "default") -> Path:
        return self.cache_dir / f"{self.key(extraction_type, text, model)}.json"

    def lookup(self, extraction_type: str, text: str, model: str = "default") -> CacheLookupResult:
        key = self.key(extraction_type, text, model)
        path = self.cache_dir / f"{key}.json"
        return CacheLookupResult(hit=path.exists(), key=key, path=path)

    def get(self, extraction_type: str, text: str, schema: Type[T], model: str = "default") -> T | None:
        lookup = self.lookup(extraction_type, text, model)
        if not lookup.hit:
            return None
        try:
            return schema.model_validate(json.loads(lookup.path.read_text(encoding="utf-8")))
        except Exception:
            return None

    def set(self, extraction_type: str, text: str, value: BaseModel, model: str = "default") -> Path:
        path = self.path_for(extraction_type, text, model)
        path.write_text(json.dumps(value.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def stats(self) -> dict:
        files = list(self.cache_dir.glob("*.json"))
        return {"cache_dir": str(self.cache_dir), "entries": len(files), "size_bytes": sum(p.stat().st_size for p in files)}

    def clear(self) -> int:
        files = list(self.cache_dir.glob("*.json"))
        for path in files:
            path.unlink()
        return len(files)
