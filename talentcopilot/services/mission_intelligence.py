from __future__ import annotations

import re
from dataclasses import dataclass

from talentcopilot.models.mission import MissionCanvas, MissionDomain


@dataclass(frozen=True)
class _MissionRule:
    domain: MissionDomain
    terms: tuple[str, ...]
    title: str
    objective: str
    required_inputs: tuple[str, ...]
    workflow: tuple[str, ...]
    target_page: str | None


_RULES = (
    _MissionRule(
        MissionDomain.RECRUITMENT,
        ("recruit", "hire", "candidate", "cv", "resume", "interview", "job", "position", "role"),
        "Recruit the right person",
        "Identify the strongest candidate and prepare an explainable hiring decision.",
        ("Job description or role requirements", "Candidate CVs", "Business priorities and mandatory criteria"),
        ("Clarify the role", "Upload job description", "Upload candidate CVs", "Analyse evidence", "Compare candidates", "Prepare interviews", "Review hiring recommendation"),
        "Recruitment Workspace",
    ),
    _MissionRule(
        MissionDomain.ORGANIZATION,
        ("organization", "organisation", "reorganization", "reorganisation", "structure", "department", "team", "turnover", "span of control"),
        "Understand the organization",
        "Identify structural risks, capability gaps and priority actions.",
        ("Employee or HRIS export", "Organization structure", "Business context"),
        ("Clarify the organizational question", "Upload workforce data", "Assess data maturity", "Analyse structural signals", "Review risks and recommendations"),
        "Organization Intelligence",
    ),
    _MissionRule(
        MissionDomain.SUCCESSION,
        ("succession", "successor", "replace", "critical role", "retirement", "future leader", "leadership pipeline"),
        "Prepare succession",
        "Assess critical-role coverage and identify evidence-based successor options.",
        ("Critical roles", "Employee profiles", "Performance and potential evidence", "Career aspirations and mobility constraints"),
        ("Define critical roles", "Collect talent evidence", "Assess readiness", "Compare successor scenarios", "Build development actions"),
        None,
    ),
    _MissionRule(
        MissionDomain.SKILLS,
        ("skill", "skills", "competency", "competencies", "capability", "training", "upskill", "reskill", "certification"),
        "Build critical capabilities",
        "Understand current capabilities and prioritize the most valuable build, buy or mobility actions.",
        ("Skills inventory or CV data", "Job or capability requirements", "Business priorities", "Learning history when available"),
        ("Define target capabilities", "Import available skills evidence", "Normalize skills", "Identify gaps", "Compare recruit, upskill and mobility options"),
        None,
    ),
    _MissionRule(
        MissionDomain.WORKFORCE,
        ("workforce", "headcount", "capacity", "forecast", "planning", "hiring plan", "attrition"),
        "Plan the workforce",
        "Estimate future capacity needs and compare workforce scenarios.",
        ("Current workforce", "Historical movements", "Business scenarios", "Planning horizon"),
        ("Define the planning horizon", "Upload workforce history", "Set scenarios", "Forecast capacity", "Compare workforce actions"),
        None,
    ),
    _MissionRule(
        MissionDomain.COLLABORATION,
        ("collaboration", "collaborate", "silo", "network", "ona", "relationship", "communication flow"),
        "Understand collaboration",
        "Assess collaboration patterns only to the level supported by available relational evidence.",
        ("Relationship survey or collaboration metadata", "Employee and team identifiers", "Analysis purpose and governance approval"),
        ("Confirm data suitability", "Collect relational evidence", "Assess network maturity", "Analyse collaboration patterns", "Review limitations and actions"),
        "Organization Intelligence",
    ),
    _MissionRule(
        MissionDomain.KNOWLEDGE,
        ("knowledge", "expertise", "know-how", "key person", "single point of failure", "knowledge transfer"),
        "Protect critical knowledge",
        "Identify concentrated expertise and prioritize knowledge-transfer actions.",
        ("Roles and employees", "Skills or expertise evidence", "Retirement or departure risks", "Critical business capabilities"),
        ("Define critical knowledge", "Import expertise evidence", "Detect concentration", "Assess business impact", "Create transfer priorities"),
        None,
    ),
    _MissionRule(
        MissionDomain.INTERNAL_MOBILITY,
        ("mobility", "internal candidate", "career move", "career path", "internal talent", "redeploy"),
        "Develop internal mobility",
        "Identify credible internal opportunities while respecting skills evidence and employee aspirations.",
        ("Open roles", "Employee profiles", "Skills evidence", "Career aspirations and mobility preferences"),
        ("Define target opportunities", "Import role and employee evidence", "Identify transferable capabilities", "Assess gaps", "Recommend development or mobility actions"),
        None,
    ),
)

_CONSTRAINT_PATTERNS = (
    (r"\bmandatory\b|\brequired\b|\bmust\b", "Mandatory criteria mentioned"),
    (r"\bwithin\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|twelve)\s+(?:day|days|week|weeks|month|months)\b|\burgent\b|\basap\b", "Time constraint detected"),
    (r"\bremote\b|\bhybrid\b|\bon-site\b|\bonsite\b", "Work-location constraint detected"),
    (r"\bbudget\b|\bsalary\b|\bcost\b", "Budget or compensation constraint detected"),
    (r"\bglobal\b|\binternational\b|\bapac\b|\bemea\b|\bamericas\b", "International scope detected"),
)


def _normalize(text: str) -> str:
    return " ".join(str(text or "").strip().split())


def _score_rule(lowered: str, rule: _MissionRule) -> int:
    strong_terms = {
        "recruit", "hire", "succession", "successor", "ona",
        "collaboration", "workforce", "mobility", "knowledge transfer",
    }
    score = 0
    for term in rule.terms:
        if term in lowered:
            score += 2 if term in strong_terms else 1
    return score


def _extract_context(request: str) -> str:
    if len(request) <= 220:
        return request
    return request[:217].rstrip() + "..."


def _extract_constraints(lowered: str) -> tuple[str, ...]:
    matches = [label for pattern, label in _CONSTRAINT_PATTERNS if re.search(pattern, lowered)]
    return tuple(dict.fromkeys(matches))


def understand_mission(request: str) -> MissionCanvas:
    cleaned = _normalize(request)
    if not cleaned:
        return MissionCanvas(
            raw_request="",
            domain=MissionDomain.UNKNOWN,
            mission_title="Describe your mission",
            objective="TalentCopilot needs a business objective before it can prepare an analysis.",
            context="No mission has been provided yet.",
            required_inputs=("Business objective", "Available data", "Decision deadline"),
            recommended_workflow=("Describe the mission", "Confirm the decision to support", "Provide the minimum useful evidence"),
            confidence="Limited",
        )

    lowered = cleaned.lower()
    score, selected = max(((_score_rule(lowered, rule), rule) for rule in _RULES), key=lambda item: item[0])

    if score == 0:
        return MissionCanvas(
            raw_request=cleaned,
            domain=MissionDomain.UNKNOWN,
            mission_title="Clarify the talent decision",
            objective="Translate the request into one clear people or workforce decision.",
            context=_extract_context(cleaned),
            required_inputs=("Decision to support", "People or teams concerned", "Available evidence", "Expected outcome"),
            recommended_workflow=("Clarify the business question", "Choose the relevant Studio", "Collect only the evidence needed", "Run an explainable analysis"),
            confidence="Limited",
            limitation="The current wording does not identify a single TalentCopilot Studio with sufficient confidence.",
        )

    confidence = "High" if score >= 3 else "Medium" if score >= 2 else "Limited"
    limitation = (
        "Mission routing is based on the business language provided. The final analysis remains limited by the quality and completeness of uploaded evidence."
        if confidence != "Limited"
        else "The mission can be routed, but more context is recommended before analysis."
    )
    constraints = _extract_constraints(lowered)
    success_criteria = (
        "A clear, explainable recommendation",
        "Evidence and limitations visible",
        "A practical next action for the accountable human decision-maker",
    )
    return MissionCanvas(
        raw_request=cleaned,
        domain=selected.domain,
        mission_title=selected.title,
        objective=selected.objective,
        context=_extract_context(cleaned),
        constraints=constraints,
        success_criteria=success_criteria,
        required_inputs=selected.required_inputs,
        recommended_workflow=selected.workflow,
        target_page=selected.target_page,
        confidence=confidence,
        limitation=limitation,
    )
