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
            )
        )
        return HybridIntelligenceDemo(report=report)
