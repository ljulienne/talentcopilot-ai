from __future__ import annotations

import argparse
import json
from pathlib import Path

from talentcopilot.doctor.engine import TalentCopilotDoctor
from talentcopilot.doctor.models import CheckStatus, DoctorReport


SYMBOLS = {
    CheckStatus.PASS: "OK",
    CheckStatus.WARN: "WARN",
    CheckStatus.FAIL: "FAIL",
}


def render_text(report: DoctorReport) -> str:
    lines = ["TalentCopilot Doctor", "=" * 58]
    for check in report.checks:
        lines.append(f"[{SYMBOLS[check.status]:4}] {check.name}: {check.message}")
        for detail in check.details:
            lines.append(f"       - {detail}")
    lines.extend(
        [
            "=" * 58,
            f"Passed: {len(report.passed)} | Warnings: {len(report.warnings)} | Failures: {len(report.failures)}",
            f"Overall status: {'HEALTHY' if report.healthy else 'UNHEALTHY'}",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate TalentCopilot repository health.")
    parser.add_argument("--repo", default=".", help="Path to the TalentCopilot repository.")
    parser.add_argument("--json", action="store_true", help="Output the report as JSON.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as a non-zero exit status.")
    parser.add_argument("--skip-git", action="store_true", help="Skip Git-related checks.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = Path(args.repo).resolve()
    report = TalentCopilotDoctor(repo).run(include_git=not args.skip_git)
    print(json.dumps(report.to_dict(), indent=2) if args.json else render_text(report))
    if report.failures:
        return 1
    if args.strict and report.warnings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
