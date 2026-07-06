import json
from pathlib import Path


ENTERPRISE_DEMO_PATH = Path("data/enterprise_demo")


def _load_json(filename, default):
    path = ENTERPRISE_DEMO_PATH / filename

    if not path.exists():
        return default

    return json.loads(path.read_text(encoding="utf-8"))


def load_enterprise_demo():
    return {
        "organizations": _load_json("organizations.json", []),
        "recruiters": _load_json("recruiters.json", []),
        "jobs": _load_json("jobs.json", []),
        "candidates": _load_json("candidates.json", []),
        "applications": _load_json("applications.json", []),
        "skills": _load_json("skills.json", []),
        "certifications": _load_json("certifications.json", []),
        "languages": _load_json("languages.json", []),
        "analytics": _load_json("analytics.json", {}),
    }
