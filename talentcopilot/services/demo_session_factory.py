from typing import Dict, List

from talentcopilot.ai.enterprise_pipeline import EnterprisePipeline


def demo_job() -> Dict:
    return {
        "title": "Transformation Lead",
        "required_skills": [
            "Project Management",
            "Stakeholder Management",
            "Change Management",
            "HRIS",
        ],
        "keywords": ["transformation", "governance", "adoption", "HRIS"],
    }


def demo_candidates() -> List[Dict]:
    return [
        {
            "name": "Alice Martin",
            "title": "Senior Transformation Manager",
            "skills": [
                "Project Management",
                "Stakeholder Management",
                "Change Management",
                "HRIS",
            ],
            "years_experience": 9,
            "achievements": [
                "Led HRIS transformation project across 6 departments.",
                "Improved user adoption by 35%.",
                "Managed stakeholder governance and executive reporting.",
            ],
        },
        {
            "name": "David Smith",
            "title": "Reporting Analyst",
            "skills": ["Excel", "Reporting", "Data Analysis"],
            "years_experience": 4,
            "achievements": [
                "Prepared monthly HR dashboards.",
                "Supported operational reporting for HR teams.",
            ],
        },
        {
            "name": "Mei Chen",
            "title": "HRIS Project Lead",
            "skills": [
                "HRIS",
                "Project Management",
                "Change Management",
                "Training",
            ],
            "years_experience": 7,
            "achievements": [
                "Deployed employee self-service portal.",
                "Coordinated UAT and training for 400 users.",
                "Reduced support tickets after go-live.",
            ],
        },
    ]


def create_demo_recruitment_session():
    return EnterprisePipeline().run(demo_job(), demo_candidates())


class DemoSessionFactory:
    @staticmethod
    def demo_job():
        return demo_job()

    @staticmethod
    def demo_candidates():
        return demo_candidates()

    @staticmethod
    def create_demo_recruitment_session():
        return create_demo_recruitment_session()

    @staticmethod
    def create_session():
        return create_demo_recruitment_session()
