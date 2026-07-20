from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.interview.evaluation_service import InterviewEvaluationService
from talentcopilot.interview.models import InterviewCompetency, InterviewWorkspaceReport
from talentcopilot.interview.plan_service import InterviewPlanService
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.readiness_service import InterviewReadinessService


class InterviewWorkspaceService:
    def build_all(self, session=None) -> list[InterviewWorkspaceReport]:
        if session is None or not getattr(session, "ranked_analyses", None):
            return []

        candidates_by_id = {
            candidate.get("candidate_id"): candidate
            for candidate in (getattr(session, "candidates", []) or [])
            if candidate.get("candidate_id")
        }
        candidates_by_name = {
            candidate.get("name"): candidate
            for candidate in (getattr(session, "candidates", []) or [])
            if candidate.get("name")
        }
        job = getattr(session, "job", {}) or {}
        role_title = job.get("title") or getattr(session, "role_title", "Recruitment")
        required_skills = [str(item) for item in job.get("required_skills", []) if str(item).strip()]

        source_of_truth = RecruitmentSourceOfTruthService()
        snapshot = source_of_truth.get(session)
        analyses_by_id = {
            str(getattr(item, "candidate_id", "")): item
            for item in (getattr(session, "analyses", []) or [])
        }
        records = sorted(
            snapshot.candidates,
            key=lambda item: (
                int(item.mission_rank or 9999),
                -float(item.mission_fit_score or 0),
                item.candidate_name.casefold(),
                item.candidate_id,
            ),
        )

        reports = []
        for record in records:
            analysis = analyses_by_id.get(str(record.candidate_id))
            if analysis is None:
                continue
            candidate = candidates_by_id.get(str(record.candidate_id))
            if candidate is None:
                candidate = candidates_by_name.get(record.candidate_name, {})
            reports.append(
                self.build_one(
                    analysis,
                    candidate,
                    role_title,
                    required_skills=required_skills,
                    candidate_id=str(record.candidate_id),
                    canonical_name=str(record.candidate_name),
                    official_rank=int(record.mission_rank or len(reports) + 1),
                )
            )
        return reports

    def build_one(
        self,
        analysis,
        candidate: dict,
        role_title: str,
        required_skills: list[str] | None = None,
        candidate_id: str = "",
        canonical_name: str = "",
        official_rank: int = 0,
    ) -> InterviewWorkspaceReport:
        required_skills = [str(skill) for skill in (required_skills or []) if str(skill).strip()]
        candidate_skills = [str(skill) for skill in candidate.get("skills", []) if str(skill).strip()]
        achievements = [str(item) for item in candidate.get("achievements", []) if str(item).strip()]
        match_score = float(getattr(analysis, "match_score", 0) or 0)

        competency_names = []
        for skill in required_skills + candidate_skills:
            if skill not in competency_names:
                competency_names.append(skill)
        if not competency_names:
            competency_names = ["Leadership", "Communication", "Stakeholder Management"]

        competencies = []
        candidate_skill_tokens = {skill.lower() for skill in candidate_skills}
        for index, skill in enumerate(competency_names[:7]):
            explicitly_present = skill.lower() in candidate_skill_tokens
            evidence_excerpt = self._matching_evidence(skill, achievements)

            if explicitly_present and evidence_excerpt:
                evidence = "High"
                confidence = 88
                validate = index >= 3
                rationale = f"The profile names {skill} and includes supporting achievement evidence."
            elif explicitly_present:
                evidence = "Medium"
                confidence = 68
                validate = True
                rationale = f"The profile names {skill}, but scope, ownership and outcome remain insufficiently evidenced."
            else:
                evidence = "Low"
                confidence = 38
                validate = True
                rationale = f"{skill} is relevant to the mission but is not explicitly demonstrated in the available CV evidence."

            competencies.append(
                InterviewCompetency(
                    name=skill,
                    evidence_level=evidence,
                    confidence=confidence,
                    validate_in_interview=validate,
                    rationale=rationale,
                )
            )

        confidence_score = int(sum(c.confidence for c in competencies) / max(1, len(competencies)))
        risk_level = "Low" if match_score >= 80 else "Medium" if match_score >= 60 else "High"
        recommendation = "Interview" if match_score >= 70 else "Review" if match_score >= 40 else "Reject"

        readiness = InterviewReadinessService().calculate(match_score, confidence_score, competencies)
        validation_topics = [c.name for c in competencies if c.validate_in_interview]
        plan = InterviewPlanService().build(validation_topics)
        questions = InterviewQuestionService().build(
            competencies,
            role_title=role_title,
            candidate=candidate,
            mission_requirements=required_skills,
        )
        scorecard = InterviewEvaluationService().build_scorecard(competencies)
        decision_readiness = InterviewEvaluationService().decision_readiness(readiness.score, scorecard)

        return InterviewWorkspaceReport(
            candidate_id=candidate_id or str(getattr(analysis, "candidate_id", "") or ""),
            candidate_name=canonical_name or str(getattr(analysis, "candidate_name", "Candidate") or "Candidate"),
            official_rank=official_rank or int(getattr(analysis, "official_rank", 0) or 0),
            role_title=role_title,
            fit_score=match_score,
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

    def _matching_evidence(self, competency: str, achievements: list[str]) -> str:
        tokens = {token for token in competency.lower().replace("/", " ").split() if len(token) > 3}
        for achievement in achievements:
            lower = achievement.lower()
            if tokens and any(token in lower for token in tokens):
                return achievement
        return ""
