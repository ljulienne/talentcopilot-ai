from dataclasses import dataclass

from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput, HybridMatchingReport


@dataclass
class HybridIntelligenceDemo:
    report: HybridMatchingReport


class HybridIntelligenceDemoService:
    def run_demo(self) -> HybridIntelligenceDemo:
        report = HybridMatchingEngine().analyze(
            HybridMatchingInput(
                candidate_name="Vincent Blakoe",
                role_title="HRIS Project Manager",
                candidate_skills=["SIRH", "Workday", "OCTIME", "Business Objects", "conduite du changement"],
                required_skills=["HRIS", "Project Management", "Time Management", "Reporting", "Change Management"],
                years_experience=13,
                titles=["HRIS Consultant", "International HRIS Project Manager", "HRIS Lead"],
                achievements=[
                    "Led international HRIS transformation across several countries.",
                    "Implemented Workday and SuccessFactors modules.",
                    "Improved adoption by 35%.",
                ],
                responsibilities=[
                    "Managed stakeholders and coordinated HR transformation projects.",
                    "Led change management and system migration activities.",
                ],
            )
        )
        return HybridIntelligenceDemo(report=report)
