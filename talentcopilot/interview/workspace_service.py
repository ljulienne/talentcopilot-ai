from talentcopilot.interview.evaluation_service import InterviewEvaluationService
from talentcopilot.interview.models import InterviewCompetency, InterviewWorkspaceReport
from talentcopilot.interview.plan_service import InterviewPlanService
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.readiness_service import InterviewReadinessService


class InterviewWorkspaceService:
    def build_all(self, session=None) -> list[InterviewWorkspaceReport]:
        if session is None or not getattr(session, "ranked_analyses", None):
            return []

        candidates_by_name = {}
        for candidate in getattr(session, "candidates", []) or []:
            name = candidate.get("name")
            if name:
                candidates_by_name[name] = candidate

        reports = []
        for analysis in session.ranked_analyses:
            candidate = candidates_by_name.get(analysis.candidate_name, {})
            reports.append(self.build_one(analysis, candidate, getattr(session, "role_title", "Recruitment")))
        return reports

    def build_one(self, analysis, candidate: dict, role_title: str) -> InterviewWorkspaceReport:
        skills = [str(skill) for skill in candidate.get("skills", [])[:5]]
        if not skills:
            skills = ["Leadership", "Communication", "Stakeholder Management"]

        competencies = []
        for index, skill in enumerate(skills):
            match_score = float(getattr(analysis, "match_score", 0) or 0)
            if match_score >= 85 and index < 3:
                evidence = "High"
                confidence = 90
                validate = False
            elif match_score >= 70:
                evidence = "Medium"
                confidence = 72
                validate = True
            else:
                evidence = "Low"
                confidence = 45
                validate = True

            competencies.append(
                InterviewCompetency(
                    name=skill,
                    evidence_level=evidence,
                    confidence=confidence,
                    validate_in_interview=validate,
                    rationale="Derived from current candidate analysis and available profile evidence.",
                )
            )

        fit_score = float(getattr(analysis, "match_score", 0) or 0)
        confidence_score = int(sum(c.confidence for c in competencies) / max(1, len(competencies)))
        risk_level = "Low" if fit_score >= 80 else "Medium" if fit_score >= 60 else "High"

        recommendation = "Interview" if fit_score >= 70 else "Review" if fit_score >= 40 else "Reject"

        readiness = InterviewReadinessService().calculate(fit_score, confidence_score, competencies)
        validation_topics = [c.name for c in competencies if c.validate_in_interview]
        plan = InterviewPlanService().build(validation_topics)
        questions = InterviewQuestionService().build(competencies)
        scorecard = InterviewEvaluationService().build_scorecard(competencies)
        decision_readiness = InterviewEvaluationService().decision_readiness(readiness.score, scorecard)

        return InterviewWorkspaceReport(
            candidate_name=getattr(analysis, "candidate_name", "Candidate"),
            role_title=role_title,
            fit_score=fit_score,
            confidence_score=confidence_score,
            risk_level=risk_level,
            recommendation=recommendation,
            readiness=readiness,
            competencies=competencies,
            plan=plan,
            questions=questions,
            scorecard=scorecard,
            decision_readiness=decision_readiness,
        )
