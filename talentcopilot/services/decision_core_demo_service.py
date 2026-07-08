from dataclasses import dataclass
from typing import List

from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput, DecisionCoreOutput


@dataclass
class DecisionCoreDemoScenario:
    name: str
    description: str
    input_data: DecisionCoreInput


class DecisionCoreDemoService:
    def scenarios(self) -> List[DecisionCoreDemoScenario]:
        return [
            DecisionCoreDemoScenario(
                name="Strong candidate, feasible budget",
                description="High fit, acceptable risk and feasible budget.",
                input_data=DecisionCoreInput(
                    candidate={
                        "name": "Alice Martin",
                        "skills": ["Project Management", "Stakeholder Management", "HRIS"],
                        "years_experience": 8,
                        "achievements": ["Improved adoption by 35%"],
                    },
                    role_title="Transformation Lead",
                    required_skills=["Project Management", "Stakeholder Management"],
                    preferred_skills=["HRIS"],
                    minimum_years_experience=6,
                    target_salary=85000,
                    maximum_salary=100000,
                    expected_salary=90000,
                ),
            ),
            DecisionCoreDemoScenario(
                name="Strong candidate, over budget",
                description="High fit but weak budget feasibility.",
                input_data=DecisionCoreInput(
                    candidate={
                        "name": "Sophie Chen",
                        "skills": ["Project Management", "Stakeholder Management", "HRIS"],
                        "years_experience": 10,
                        "achievements": ["Led global HR transformation"],
                    },
                    role_title="Transformation Lead",
                    required_skills=["Project Management", "Stakeholder Management"],
                    preferred_skills=["HRIS"],
                    minimum_years_experience=6,
                    target_salary=85000,
                    maximum_salary=100000,
                    expected_salary=125000,
                ),
            ),
            DecisionCoreDemoScenario(
                name="No fit candidate",
                description="Low fit candidate must be rejected, even if affordable.",
                input_data=DecisionCoreInput(
                    candidate={
                        "name": "David Smith",
                        "skills": ["Graphic Design"],
                        "years_experience": 1,
                    },
                    role_title="Transformation Lead",
                    required_skills=["Project Management", "Stakeholder Management"],
                    preferred_skills=["HRIS"],
                    minimum_years_experience=6,
                    target_salary=85000,
                    maximum_salary=100000,
                    expected_salary=50000,
                ),
            ),
        ]

    def run(self, scenario_name: str | None = None) -> DecisionCoreOutput:
        scenarios = self.scenarios()
        scenario = scenarios[0]
        if scenario_name:
            scenario = next((item for item in scenarios if item.name == scenario_name), scenarios[0])
        return DecisionCoreOrchestrator().analyze_candidate(scenario.input_data)
