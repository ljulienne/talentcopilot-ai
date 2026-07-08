from dataclasses import dataclass

from talentcopilot.real_matching.models import RealMatchingInput, RealMatchingOutput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline


@dataclass
class RealMatchingDemo:
    title: str
    output: RealMatchingOutput


class RealMatchingDemoService:
    def run_demo(self) -> RealMatchingDemo:
        candidate_text = '''
Alice Martin
Experience
8 years experience leading HRIS transformation projects.
Led Project Management and Stakeholder Management initiatives.
Skills
HRIS, Project Management, Stakeholder Management, Leadership, Workday
Achievements
Improved adoption by 35%.
'''
        job_text = '''
Transformation Lead
Responsibilities
Lead HRIS transformation projects and stakeholder management.
Requirements
Minimum 6 years experience.
Required skills: Project Management, Stakeholder Management, HRIS.
Languages
English and French.
Compensation
85000 100000
'''
        output = RealMatchingPipeline().run(
            RealMatchingInput(
                candidate_filename="alice_cv.txt",
                candidate_text=candidate_text,
                job_filename="transformation_lead_job.txt",
                job_text=job_text,
                expected_salary=90000,
            )
        )
        return RealMatchingDemo("Strong candidate real matching demo", output)
