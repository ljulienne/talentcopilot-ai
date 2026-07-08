from talentcopilot.interview.models import InterviewCompetency, InterviewReadiness


class InterviewReadinessService:
    def calculate(self, fit_score: float, confidence_score: int, competencies: list[InterviewCompetency]) -> InterviewReadiness:
        validation_needed = len([c for c in competencies if c.validate_in_interview])
        strong_evidence = len([c for c in competencies if c.evidence_level.lower() == "high"])
        total = max(1, len(competencies))

        evidence_component = int((strong_evidence / total) * 35)
        confidence_component = int(max(0, min(100, confidence_score)) * 0.35)
        fit_component = int(max(0, min(100, fit_score)) * 0.20)
        gap_penalty = validation_needed * 4

        score = max(0, min(100, evidence_component + confidence_component + fit_component + 10 - gap_penalty))

        if score >= 85:
            status = "Ready for interview"
        elif score >= 65:
            status = "Interview with targeted validation"
        else:
            status = "Needs more evidence before interview"

        drivers = []
        gaps = []
        if strong_evidence:
            drivers.append(f"{strong_evidence} competency area(s) have strong evidence.")
        if confidence_score >= 80:
            drivers.append("AI confidence is high enough for structured interview preparation.")
        if fit_score >= 75:
            drivers.append("Candidate fit is strong enough to justify interview preparation.")
        if validation_needed:
            gaps.append(f"{validation_needed} competency area(s) should be validated during interview.")
        if confidence_score < 65:
            gaps.append("AI confidence is limited; ask evidence-based questions.")

        return InterviewReadiness(score=score, status=status, drivers=drivers, gaps=gaps)
