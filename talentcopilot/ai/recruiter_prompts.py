from __future__ import annotations

from typing import Dict

from talentcopilot.ai.recruiter_context import format_context_for_prompt


SYSTEM_PROMPT = """
You are TalentCopilot, an Enterprise AI Recruitment Intelligence assistant.

You answer as a senior recruitment and HR technology expert.
Your role is to help recruiters make better, faster and more transparent hiring decisions.

You must:
- stay factual
- use only the provided TalentCopilot context
- avoid inventing candidate information
- clearly separate strengths, risks and recommendations
- mention when data is missing
- provide practical next steps
""".strip()


PROMPT_TEMPLATES: Dict[str, str] = {
    "general": """
Use the TalentCopilot context below to answer the recruiter question.

Structure your response with:
1. Direct answer
2. Evidence from TalentCopilot
3. Risks or missing data
4. Recommended next step

Context:
{context}
""".strip(),

    "comparison": """
Use the TalentCopilot context below to compare the relevant talents.

Structure your response with:
1. Comparison summary
2. Strengths of each talent
3. Risks or gaps
4. Recommendation
5. Suggested next step

Context:
{context}
""".strip(),

    "budget": """
Use the TalentCopilot context below to assess budget and salary alignment.

Structure your response with:
1. Financial assessment
2. Candidates within budget
3. Candidates above budget
4. Risks
5. Recommendation

Context:
{context}
""".strip(),

    "interview": """
Use the TalentCopilot context below to recommend interview priorities.

Structure your response with:
1. Who to interview first
2. Why
3. Interview focus areas
4. Risks to validate
5. Suggested interview plan

Context:
{context}
""".strip(),

    "skills": """
Use the TalentCopilot context below to analyze skills across the Talent Pool.

Structure your response with:
1. Key available skills
2. Strongest talents by skill
3. Skill gaps
4. Hiring implications
5. Recommended next step

Context:
{context}
""".strip(),
}


def detect_prompt_type(question: str) -> str:
    q = question.lower().strip()

    if any(keyword in q for keyword in ["compare", "versus", "vs"]):
        return "comparison"

    if any(keyword in q for keyword in ["budget", "salary", "cost", "financial", "offer"]):
        return "budget"

    if any(keyword in q for keyword in ["interview", "meet", "shortlist"]):
        return "interview"

    if any(keyword in q for keyword in ["skill", "skills", "competence", "competencies", "experience"]):
        return "skills"

    return "general"


def build_recruiter_prompt(context: dict) -> dict:
    question = context.get("question", "")
    prompt_type = detect_prompt_type(question)
    formatted_context = format_context_for_prompt(context)

    user_prompt = PROMPT_TEMPLATES[prompt_type].format(context=formatted_context)

    return {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "prompt_type": prompt_type,
    }
