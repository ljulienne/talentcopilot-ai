from talentcopilot.enterprise_demo.repository import EnterpriseDemoRepository
from talentcopilot.enterprise_demo.recruitment_factory import EnterpriseRecruitmentFactory
from talentcopilot.enterprise_demo.simulation_engine import EnterpriseSimulationEngine


class EnterpriseDemoEngine:
    """
    High-level entry point for Enterprise Demo.

    Returns a Streamlit-compatible analysis_batch.
    """

    def __init__(self):
        self.repository = EnterpriseDemoRepository()
        self.recruitment_factory = EnterpriseRecruitmentFactory(self.repository)
        self.simulation_engine = EnterpriseSimulationEngine(self.repository)

    def launch(
        self,
        organization_id: str = "ORG001",
        job_id: str = "JOB001",
        scenario: str = "balanced",
        candidate_count: int = 12,
    ):
        recruitment = self.recruitment_factory.build_recruitment(
            organization_id=organization_id,
            job_id=job_id,
            scenario=scenario,
            candidate_count=candidate_count,
        )

        return self.simulation_engine.run(recruitment)


def launch_enterprise_demo(
    organization_id: str = "ORG001",
    job_id: str = "JOB001",
    scenario: str = "balanced",
    candidate_count: int = 12,
):
    engine = EnterpriseDemoEngine()

    return engine.launch(
        organization_id=organization_id,
        job_id=job_id,
        scenario=scenario,
        candidate_count=candidate_count,
    )
