
from dataclasses import dataclass, field


@dataclass
class DemoRequirement:
    name: str
    importance: str = "High"
    expected_level: str = "Advanced"


@dataclass
class DemoCapability:
    name: str
    detected_level: str = "Advanced"
    confidence: int = 90
    evidence: list = field(default_factory=list)


@dataclass
class DemoEvidence:
    text: str


@dataclass
class DemoMatchDetail:
    requirement: DemoRequirement
    score: int
    explanation: str
    capability: DemoCapability | None = None


@dataclass
class DemoGap:
    competency: str
    severity: str
    explanation: str
    recommendation: str


@dataclass
class DemoQuestion:
    priority: str
    linked_competency: str
    question: str
    purpose: str


@dataclass
class DemoCandidate:
    name: str
    current_role: str
    capabilities: list


@dataclass
class DemoJob:
    title: str


@dataclass
class DemoMatchResult:
    overall_score: int
    confidence_score: int
    recommendation: str
    executive_summary: str
    match_details: list
    gaps: list
    interview_questions: list
    job: DemoJob


def _candidate(name, role, score, confidence, recommendation, strengths, gaps, languages):
    capabilities = [
        DemoCapability(s, "Advanced", 90, [DemoEvidence(f"Demonstrated experience in {s}.")])
        for s in strengths + languages
    ]

    match_details = [
        DemoMatchDetail(
            requirement=DemoRequirement(s),
            score=90 if i < 2 else 82,
            explanation=f"{name} shows strong evidence of {s}.",
            capability=DemoCapability(s, "Advanced", 90)
        )
        for i, s in enumerate(strengths)
    ]

    demo_gaps = [
        DemoGap(
            competency=g,
            severity="Medium",
            explanation=f"{g} is not strongly demonstrated in the CV.",
            recommendation=f"Explore {g} during the interview."
        )
        for g in gaps
    ]

    questions = [
        DemoQuestion(
            priority="High",
            linked_competency=strengths[0],
            question=f"Can you describe a project where you used {strengths[0]} in a complex HR environment?",
            purpose="Validate real hands-on experience."
        )
    ]

    return {
        "file": f"{name.replace(' ', '_')}_CV.pdf",
        "candidate": DemoCandidate(name, role, capabilities),
        "match_result": DemoMatchResult(
            overall_score=score,
            confidence_score=confidence,
            recommendation=recommendation,
            executive_summary=f"{name} is a strong demo profile with experience in {', '.join(strengths[:3])}.",
            match_details=match_details,
            gaps=demo_gaps,
            interview_questions=questions,
            job=DemoJob("HRIS Project Manager")
        )
    }


def load_demo_batch():
    job = DemoJob("HRIS Project Manager")

    results = [
        _candidate(
            "Alice Martin",
            "Senior HRIS Consultant",
            94,
            96,
            "Strong Shortlist",
            ["HRIS", "Project Management", "API Integration", "Change Management"],
            ["Oracle HCM"],
            ["French", "English"]
        ),
        _candidate(
            "Bob Chen",
            "HR Data Lead",
            89,
            93,
            "Interview",
            ["HR Analytics", "Power BI", "SQL", "Stakeholder Management"],
            ["Payroll"],
            ["English", "Mandarin"]
        ),
        _candidate(
            "Claire Dubois",
            "HRIS Project Manager",
            86,
            91,
            "Interview",
            ["HRIS", "Talent Management", "Change Management"],
            ["API Integration"],
            ["French", "English"]
        ),
        _candidate(
            "David Smith",
            "Payroll Systems Analyst",
            78,
            88,
            "Keep in Pipeline",
            ["Payroll", "Time & Attendance", "HR Reporting"],
            ["Change Management", "API Integration"],
            ["English"]
        ),
        _candidate(
            "Emma Wang",
            "International HR Project Lead",
            83,
            90,
            "Interview",
            ["Project Management", "Stakeholder Management", "International Collaboration"],
            ["Power BI"],
            ["French", "English", "Mandarin"]
        )
    ]

    return {
        "success": True,
        "job": job,
        "results": results,
        "errors": []
    }


def load_demo_recruitment_context():
    return {
        "job_title": "HRIS Project Manager",
        "company": "TalentCopilot Demo Corp",
        "department": "HR Technology",
        "location": "Paris / Remote",
        "recruitment_type": "Permanent",
        "language": "Auto Detect",
        "max_candidates": 50,
        "created_at": "demo"
    }
