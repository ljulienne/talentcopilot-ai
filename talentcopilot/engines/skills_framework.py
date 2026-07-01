
import json


def load_skills_framework():
    with open("talentcopilot/skills_framework.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_skill_info(skill_name):
    framework = load_skills_framework()
    return framework.get(skill_name)


def get_default_weight(skill_name):
    info = get_skill_info(skill_name)
    if not info:
        return 10
    return info.get("default_weight", 10)


def get_default_expected_level(skill_name):
    info = get_skill_info(skill_name)
    if not info:
        return "Intermediate"
    return info.get("default_expected_level", "Intermediate")


def list_skills():
    return list(load_skills_framework().keys())
