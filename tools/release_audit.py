from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from talentcopilot.release_health import load_release_manifest, validate_release_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an installed TalentCopilot release.")
    parser.add_argument("--release", default="1.4")
    args = parser.parse_args()
    manifest = load_release_manifest(REPO, args.release)
    missing = validate_release_files(REPO, manifest)
    print(f"TalentCopilot Release Audit — {manifest.release} {manifest.product_label}")
    if missing:
        print("FAIL: missing required paths")
        for item in missing:
            print(f"- {item}")
        return 1
    tracked_failures = []
    if (REPO / ".git").exists():
        for relative in (*manifest.required_files, *manifest.required_tests):
            result = subprocess.run(["git", "ls-files", "--error-unmatch", relative], cwd=REPO, capture_output=True)
            if result.returncode != 0:
                tracked_failures.append(relative)
    if tracked_failures:
        print("WARN: present but not tracked by Git")
        for item in tracked_failures:
            print(f"- {item}")
        return 2
    print("PASS: required files and tests are present and tracked by Git.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
