
from talentcopilot.ai.provider import generate_json
from talentcopilot.engines.skills_framework import load_skills_framework


def build_framework_prompt(framework):
    lines = []

    for skill, info in framework.items():
        aliases = ", ".join(info.get("aliases", []))
        examples = "; ".join(info.get("evidence_examples", []))

        lines.append(
            f"- {skill} | Category: {info.get('category')} | "
            f"Family: {info.get('family')} | "
            f"Aliases: {aliases} | "
            f"Evidence examples: {examples}"
        )

    return "\n".join(lines)


def build_prompt(cv_text, framework):
    framework_text = build_framework_prompt(framework)

    return f"""
You are TalentCopilot's Competency Extraction Engine.

Your task is to detect competencies from the official Skills Framework only.

Rules:
- Do NOT invent competencies.
- Use only competency names from the framework.
- Evidence must be quoted from the CV.
- If a competency is only weakly implied, lower the confidence.
- detected_level must be one of: None, Beginner, Intermediate, Advanced, Expert.
- confidence must be between 0 and 100.

Official Skills Framework:
{framework_text}

Candidate CV:
{cv_text}

Return ONLY valid JSON in this exact format:
{{
  "competencies": [
    {{
      "competency": "",
      "category": "",
      "family": "",
      "detected_level": "",
      "confidence": 0,
      "evidence": []
    }}
  ]
}}
"""


def extract_competencies(cv_text):
    framework = load_skills_framework()
    prompt = build_prompt(cv_text, framework)
    return generate_json(prompt)
