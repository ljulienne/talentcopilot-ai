from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReleaseManifest:
    release: str
    product_label: str
    required_files: tuple[str, ...]
    required_tests: tuple[str, ...]


def load_release_manifest(repo: str | Path, release: str = "1.4") -> ReleaseManifest:
    repo_path = Path(repo)
    path = repo_path / "releases" / f"release_{release.replace('.', '_')}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return ReleaseManifest(
        release=str(data["release"]),
        product_label=str(data["product_label"]),
        required_files=tuple(data.get("required_files", ())),
        required_tests=tuple(data.get("required_tests", ())),
    )


def validate_release_files(repo: str | Path, manifest: ReleaseManifest) -> tuple[str, ...]:
    repo_path = Path(repo)
    return tuple(
        relative
        for relative in (*manifest.required_files, *manifest.required_tests)
        if not (repo_path / relative).exists()
    )
