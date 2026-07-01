
from talentcopilot.core.models import Job, JobRequirement
from talentcopilot.ai.provider import generate_json
from talentcopilot.engines.skills_framework import load_skills_framework


def build_framework_prompt(framework):
    lines = []

    for skill, info in framework.items():
        aliases = ", ".join(info.get("aliases", []))
        lines.append(
            f"- {skill} | Category: {info.get('category')} | "
            f"Family: {info.get('family')} | "
            f"Aliases: {aliases} | "
            f"Default weight: {info.get('default_weight')} | "
            f"Default expected level: {info.get('default_expected_level')}"
        )

    return "\\n".join(lines)


def extract_job_requirements(job_text):
    framework = load_skills_framework()
    framework_text = build_framework_prompt(framework)

    prompt = f"""
You are TalentCopilot's Job Requirement Extraction Engine.

Your task is to extract job requirements from the job description using ONLY the official Skills Framework.

Rules:
- Do NOT invent requirements.
- Use only competency names from the framework.
- importance must be one of: Low, Medium, High, Critical.
- expected_level must be one of: Beginner, Intermediate, Advanced, Expert.
- weight must be between 5 and 40.
- Higher weight means the requirement is more important for the job.

Official Skills Framework:
{framework_text}

Job description:
{job_text}

Return ONLY valid JSON in this exact format:
{{
  "job_title": "",
  "requirements": [
    {{
      "name": "",
      "category": "",
      "importance": "",
      "expected_level": "",
      "weight": 0
    }}
  ]
}}
"""

    return generate_json(prompt)


def build_job_from_text(job_text):
    extraction = extract_job_requirements(job_text)

    requirements = []

    for item in extraction.get("requirements", []):
        requirement = JobRequirement(
            name=item.get("name", ""),
            category=item.get("category", "General"),
            importance=item.get("importance", "Medium"),
            expected_level=item.get("expected_level", "Intermediate"),
            weight=item.get("weight", 10)
        )

        requirements.append(requirement)

    job = Job(
        title=extraction.get("job_title", "Untitled Job"),
        description=job_text,
        requirements=requirements
    )

    return job
