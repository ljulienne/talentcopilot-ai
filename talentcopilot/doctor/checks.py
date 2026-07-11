from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from talentcopilot.doctor.models import CheckStatus, DoctorCheck


CRITICAL_MODULES = (
    "talentcopilot",
    "talentcopilot.intelligence_core",
    "talentcopilot.organization_intelligence",
    "talentcopilot.ui.enterprise_navigation",
)

CRITICAL_TESTS = (
    "tests/stable/test_stable_imports.py",
    "tests/stable/test_stable_navigation.py",
    "tests/stable/test_stable_navigation_cleanup.py",
    "tests/stable/test_stable_intelligence_core.py",
    "tests/stable/test_stable_organization_graph.py",
)


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def check_repository_layout(repo: Path) -> DoctorCheck:
    required = (repo / "app.py", repo / "talentcopilot", repo / "tests")
    missing = tuple(str(path.relative_to(repo)) for path in required if not path.exists())
    if missing:
        return DoctorCheck(
            "Repository layout",
            CheckStatus.FAIL,
            "Required project paths are missing.",
            missing,
        )
    return DoctorCheck("Repository layout", CheckStatus.PASS, "Core project paths are present.")


def check_python_path(repo: Path) -> DoctorCheck:
    resolved = str(repo.resolve())
    if resolved in sys.path or os.environ.get("PYTHONPATH") == resolved:
        return DoctorCheck("Python path", CheckStatus.PASS, "Repository is available on Python path.")
    return DoctorCheck(
        "Python path",
        CheckStatus.WARN,
        "Repository is not explicitly configured in PYTHONPATH.",
        ("Use PYTHONPATH=/content/talentcopilot-ai when running tests in Colab.",),
    )


def check_critical_imports(modules: Iterable[str] = CRITICAL_MODULES) -> DoctorCheck:
    failures: list[str] = []
    for module_name in modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - exact import failures vary by environment
            failures.append(f"{module_name}: {type(exc).__name__}: {exc}")
    if failures:
        return DoctorCheck(
            "Critical imports",
            CheckStatus.FAIL,
            f"{len(failures)} critical import(s) failed.",
            tuple(failures),
        )
    return DoctorCheck("Critical imports", CheckStatus.PASS, "All critical modules import successfully.")


def check_navigation() -> DoctorCheck:
    try:
        from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages
    except Exception as exc:
        return DoctorCheck(
            "Navigation",
            CheckStatus.FAIL,
            "Navigation registry could not be imported.",
            (f"{type(exc).__name__}: {exc}",),
        )

    issues: list[str] = []
    labels: set[str] = set()
    pages = flatten_enterprise_pages()
    for page in pages:
        if page.label in labels:
            issues.append(f"Duplicate label: {page.label}")
        labels.add(page.label)
        try:
            module = importlib.import_module(page.module)
            renderer = getattr(module, page.function)
            if not callable(renderer):
                issues.append(f"Not callable: {page.module}.{page.function}")
        except Exception as exc:
            issues.append(f"{page.label}: {page.module}.{page.function}: {type(exc).__name__}: {exc}")

    if issues:
        return DoctorCheck(
            "Navigation",
            CheckStatus.FAIL,
            f"{len(issues)} navigation issue(s) detected.",
            tuple(issues),
            {"page_count": len(pages)},
        )
    return DoctorCheck(
        "Navigation",
        CheckStatus.PASS,
        f"{len(pages)} visible page(s) resolve to callable renderers.",
        metadata={"page_count": len(pages)},
    )


def check_test_inventory(repo: Path, required: Iterable[str] = CRITICAL_TESTS) -> DoctorCheck:
    missing = tuple(path for path in required if not (repo / path).exists())
    stable_count = len(tuple((repo / "tests" / "stable").glob("test_*.py")))
    if missing:
        return DoctorCheck(
            "Test inventory",
            CheckStatus.WARN,
            f"{len(missing)} recommended critical test file(s) are absent.",
            missing,
            {"stable_test_files": stable_count},
        )
    return DoctorCheck(
        "Test inventory",
        CheckStatus.PASS,
        f"Critical tests are present ({stable_count} stable test files found).",
        metadata={"stable_test_files": stable_count},
    )


def check_release_artifacts(repo: Path) -> DoctorCheck:
    if not (repo / ".git").exists():
        return DoctorCheck(
            "Release artifacts",
            CheckStatus.WARN,
            "Git metadata is unavailable; tracked release artifacts were not checked.",
        )
    result = _run_git(repo, "ls-files", ".release_backups", ".release_*_backup_path")
    tracked = tuple(line for line in result.stdout.splitlines() if line.strip())
    if tracked:
        return DoctorCheck(
            "Release artifacts",
            CheckStatus.WARN,
            "Local installer artifacts are tracked by Git.",
            tracked,
        )
    return DoctorCheck("Release artifacts", CheckStatus.PASS, "No release backup artifacts are tracked.")


def check_git_state(repo: Path) -> DoctorCheck:
    if not (repo / ".git").exists():
        return DoctorCheck("Git state", CheckStatus.WARN, "Git metadata is unavailable.")

    status = _run_git(repo, "status", "--porcelain")
    if status.returncode != 0:
        return DoctorCheck(
            "Git state",
            CheckStatus.WARN,
            "Git status could not be read.",
            (status.stderr.strip() or "Unknown git error",),
        )

    changes = tuple(line for line in status.stdout.splitlines() if line.strip())
    remote = _run_git(repo, "remote", "get-url", "origin")
    remote_url = remote.stdout.strip()
    token_warning = "@github.com" in remote_url and "https://github.com" not in remote_url

    details: list[str] = list(changes[:20])
    if token_warning:
        details.append("The origin URL may contain embedded credentials.")

    if changes or token_warning:
        message = "Working tree has changes." if changes else "Remote URL may expose credentials."
        return DoctorCheck(
            "Git state",
            CheckStatus.WARN,
            message,
            tuple(details),
            {"change_count": len(changes)},
        )
    return DoctorCheck("Git state", CheckStatus.PASS, "Working tree is clean and remote URL is safe.")


def check_executive_copilot_readiness(repo: Path) -> DoctorCheck:
    try:
        from talentcopilot.release_health import load_release_manifest, validate_release_files
        manifest = load_release_manifest(repo, "1.4")
    except Exception as exc:
        return DoctorCheck(
            "Executive Copilot readiness",
            CheckStatus.WARN,
            "Release 1.4 manifest is unavailable.",
            (f"{type(exc).__name__}: {exc}",),
        )

    missing = validate_release_files(repo, manifest)
    if missing:
        return DoctorCheck(
            "Executive Copilot readiness",
            CheckStatus.FAIL,
            f"Release {manifest.release} is incomplete.",
            missing,
            {"release": manifest.release, "missing_count": len(missing)},
        )

    try:
        from talentcopilot.ui.enterprise_navigation import get_page_by_label
        page = get_page_by_label("Executive Copilot")
    except Exception as exc:
        return DoctorCheck(
            "Executive Copilot readiness",
            CheckStatus.FAIL,
            "Executive Copilot navigation could not be validated.",
            (f"{type(exc).__name__}: {exc}",),
        )

    if page is None:
        return DoctorCheck(
            "Executive Copilot readiness",
            CheckStatus.FAIL,
            "Executive Copilot is absent from navigation.",
        )

    return DoctorCheck(
        "Executive Copilot readiness",
        CheckStatus.PASS,
        f"Release {manifest.release} ({manifest.product_label}) is complete and navigable.",
        metadata={"release": manifest.release, "required_file_count": len(manifest.required_files)},
    )
