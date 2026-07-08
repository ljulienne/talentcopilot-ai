from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput
from talentcopilot.hybrid_matching.report_engine import HybridRecruiterReportEngine


def test_hybrid_recruiter_report_is_created():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Vincent Blakoe",
            role_title="HRIS Manager",
            candidate_skills=["SIRH", "Workday", "OCTIME", "Business Objects"],
            required_skills=["HRIS", "Time Management", "Reporting"],
            years_experience=13,
            titles=["HRIS Consultant", "HRIS Project Manager"],
            achievements=["Improved adoption by 35%."],
        )
    )

    assert report.recruiter_report is not None
    assert report.recruiter_report.executive_summary
    assert report.recruiter_report.action_recommendation
    assert report.recruiter_report.interview_focus


def test_report_engine_action_levels():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Candidate",
            role_title="HRIS Manager",
            candidate_skills=["Graphic Design"],
            required_skills=["HRIS", "Payroll"],
            years_experience=1,
        )
    )

    recruiter_report = HybridRecruiterReportEngine().build(report)

    assert recruiter_report.readiness_level in {"Low fit", "Partial fit", "Qualified with validation points", "Strong fit"}
    assert recruiter_report.action_recommendation in {
        "Prioritize for interview",
        "Interview with targeted validation",
        "Review before shortlisting",
        "Do not prioritize",
    }
