
from talentcopilot.core.models import MatchResult, MatchDetail, Gap, InterviewQuestion


LEVEL_SCORES = {
    "none": 0,
    "unknown": 0,
    "beginner": 25,
    "intermediate": 60,
    "advanced": 85,
    "expert": 100
}


def normalize_level(level):
    if not level:
        return "unknown"

    level = level.lower().strip()

    for key in LEVEL_SCORES:
        if key in level:
            return key

    return "unknown"


def level_to_score(level):
    return LEVEL_SCORES.get(normalize_level(level), 0)


def find_capability(requirement, candidate):
    requirement_name = requirement.name.lower()

    for capability in candidate.capabilities:
        if capability.name.lower() == requirement_name:
            return capability

    return None


def calculate_requirement_score(requirement, capability):
    if capability is None:
        return 0

    expected_score = level_to_score(requirement.expected_level)
    detected_score = level_to_score(capability.detected_level)

    if expected_score == 0:
        return detected_score

    score = round((detected_score / expected_score) * 100)
    return max(0, min(score, 100))


def create_gap(requirement, capability, score):
    if score >= 80:
        return None

    if capability is None:
        explanation = f"No evidence found for {requirement.name}."
        severity = "High" if requirement.importance in ["High", "Critical"] else "Medium"
    else:
        explanation = (
            f"{requirement.name} is partially demonstrated. "
            f"Expected level: {requirement.expected_level}. "
            f"Detected level: {capability.detected_level}."
        )
        severity = "High" if score < 50 else "Medium"

    return Gap(
        competency=requirement.name,
        severity=severity,
        explanation=explanation,
        recommendation=f"Validate {requirement.name} during the interview."
    )


def create_interview_question(requirement, capability, score):
    if score >= 85:
        priority = "Low"
        question = f"Can you describe a strong example of how you used {requirement.name} in a recent project?"
        purpose = "Confirm the strength of an already well-matched competency."
    elif score >= 50:
        priority = "Medium"
        question = f"Can you explain your practical experience with {requirement.name}?"
        purpose = "Clarify the candidate's real level and depth of experience."
    else:
        priority = "High"
        question = f"The role requires {requirement.name}. Can you share any concrete experience related to this area?"
        purpose = "Validate a potential critical gap."

    return InterviewQuestion(
        question=question,
        purpose=purpose,
        linked_competency=requirement.name,
        priority=priority
    )


def match_candidate_to_job(candidate, job):
    match_details = []
    gaps = []
    interview_questions = []

    total_weight = 0
    weighted_score = 0
    confidence_values = []

    for requirement in job.requirements:
        capability = find_capability(requirement, candidate)
        score = calculate_requirement_score(requirement, capability)

        confidence = capability.confidence if capability else 0
        confidence_values.append(confidence)

        weight = requirement.weight or 10
        total_weight += weight
        weighted_score += score * weight

        if capability is None:
            explanation = f"{requirement.name} was not detected in the candidate CV."
        else:
            explanation = (
                f"{requirement.name}: expected {requirement.expected_level}, "
                f"detected {capability.detected_level}."
            )

        match_details.append(
            MatchDetail(
                requirement=requirement,
                capability=capability,
                score=score,
                confidence=confidence,
                explanation=explanation
            )
        )

        gap = create_gap(requirement, capability, score)
        if gap:
            gaps.append(gap)

        interview_questions.append(
            create_interview_question(requirement, capability, score)
        )

    overall_score = round(weighted_score / total_weight) if total_weight else 0
    confidence_score = round(sum(confidence_values) / len(confidence_values)) if confidence_values else 0

    if overall_score >= 85:
        recommendation = "Strong shortlist"
    elif overall_score >= 70:
        recommendation = "Interview"
    elif overall_score >= 50:
        recommendation = "Maybe"
    else:
        recommendation = "Not recommended"

    executive_summary = (
        f"{candidate.name} has a TalentCopilot match score of {overall_score}% "
        f"for the role {job.title}. Recommendation: {recommendation}."
    )

    return MatchResult(
        candidate=candidate,
        job=job,
        overall_score=overall_score,
        confidence_score=confidence_score,
        recommendation=recommendation,
        match_details=match_details,
        gaps=gaps,
        interview_questions=interview_questions,
        executive_summary=executive_summary
    )
