from talentcopilot.decision_core.budget_intelligence_models import BudgetContext, CandidateCompensation
from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput, DecisionCoreOutput


class DecisionCoreOrchestrator:
    pipeline_version = "dic-v2.0-alpha-i"

    def analyze_candidate(self, data: DecisionCoreInput) -> DecisionCoreOutput:
        role = RoleRequirements(
            role_title=data.role_title,
            required_skills=data.required_skills,
            preferred_skills=data.preferred_skills,
            minimum_years_experience=data.minimum_years_experience,
        )

        budget_context = None
        compensation = None
        if data.target_salary is not None and data.maximum_salary is not None and data.expected_salary is not None:
            budget_context = BudgetContext(
                target_salary=float(data.target_salary),
                maximum_salary=float(data.maximum_salary),
            )
            compensation = CandidateCompensation(
                expected_salary=float(data.expected_salary),
                relocation_required=data.relocation_required,
                visa_sponsorship_required=data.visa_sponsorship_required,
            )

        profile = CandidateDecisionProfileService().build_from_candidate_dict(
            data.candidate,
            data.role_title,
            role,
            budget_context,
            compensation,
        )

        return DecisionCoreOutput(
            profile=profile,
            pipeline_version=self.pipeline_version,
            engine_status=self._engine_status(profile),
        )

    def analyze_many(self, inputs: list[DecisionCoreInput]) -> list[DecisionCoreOutput]:
        return [self.analyze_candidate(item) for item in inputs]

    def _engine_status(self, profile):
        actions = {step.action for step in profile.decision_trace.steps}
        return {
            "evidence_graph": "OK" if "CREATE_EVIDENCE_GRAPH" in actions else "Missing",
            "evidence_intelligence": "OK" if "EVALUATE_EVIDENCE_QUALITY" in actions else "Missing",
            "fit_intelligence": "OK" if "EVALUATE_CANDIDATE_FIT" in actions else "Missing",
            "risk_intelligence": "OK" if "EVALUATE_HIRING_RISK" in actions else "Missing",
            "budget_intelligence": "OK" if "EVALUATE_BUDGET_FEASIBILITY" in actions else "Not provided",
            "confidence_intelligence": "OK" if "EVALUATE_ANALYSIS_CONFIDENCE" in actions else "Missing",
            "recommendation_intelligence": "OK" if "GENERATE_FINAL_RECOMMENDATION" in actions else "Missing",
            "executive_intelligence": "OK" if "GENERATE_EXECUTIVE_SUMMARY" in actions else "Missing",
        }
