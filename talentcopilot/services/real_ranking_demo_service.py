from dataclasses import dataclass

from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput, RealRankingOutput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline


@dataclass
class RealRankingDemo:
    title: str
    output: RealRankingOutput


class RealRankingDemoService:
    def run_demo(self) -> RealRankingDemo:
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
        candidates = [
            CandidateTextInput(
                filename="alice_cv.txt",
                text='''
Alice Martin
Experience
8 years experience leading HRIS transformation projects.
Led Project Management and Stakeholder Management initiatives.
Skills
HRIS, Project Management, Stakeholder Management, Leadership, Workday
Achievements
Improved adoption by 35%.
''',
                expected_salary=90000,
            ),
            CandidateTextInput(
                filename="sophie_cv.txt",
                text='''
Sophie Chen
Experience
10 years experience leading global HRIS transformation.
Skills
HRIS, Project Management, Stakeholder Management, Leadership, SuccessFactors
Achievements
Reduced implementation timeline by 25%.
''',
                expected_salary=125000,
            ),
            CandidateTextInput(
                filename="david_cv.txt",
                text='''
David Smith
Experience
1 years experience in graphic design.
Skills
Graphic Design, Branding
''',
                expected_salary=50000,
            ),
        ]

        output = RealRankingPipeline().run(
            RealRankingInput(
                job_filename="job.txt",
                job_text=job_text,
                candidates=candidates,
            )
        )
        return RealRankingDemo("Real ranking demo", output)
