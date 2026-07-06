from talentcopilot.core.models import (
    Candidate,
    CandidateCapability,
    Evidence,
    Gap,
    InterviewQuestion,
    Job,
    JobRequirement,
    MatchDetail,
    MatchResult,
)


def _capability(name, level="Advanced", confidence=90):
    return CandidateCapability(
        name=name,
        category="Demo",
        detected_level=level,
        confidence=confidence,
        evidence=[
            Evidence(
                text=f"Demonstrated experience in {name}.",
                source="Demo CV",
                linked_competency=name,
                confidence=confidence,
            )
        ],
    )


def _requirement(name, importance="High", expected_level="Advanced", weight=10.0):
    return JobRequirement(
        name=name,
        category="Demo",
        importance=importance,
        expected_level=expected_level,
        weight=weight,
    )


def _candidate(name, role, score, confidence, recommendation, strengths, gaps, languages):
    capabilities = [
        _capability(skill, "Advanced", 90)
        for skill in strengths + languages
    ]

    candidate = Candidate(
        name=name,
        current_role=role,
        experiences=[f"Enterprise experience related to {role}."],
        certifications=[],
        languages=languages,
        capabilities=capabilities,
    )

    job = Job(
        title="HRIS Project Manager",
        description="Demo HRIS project manager role.",
        requirements=[_requirement(skill) for skill in strengths],
    )

    match_details = []

    for index, skill in enumerate(strengths):
        requirement = _requirement(skill)
        capability = _capability(skill, "Advanced", 90)

        match_details.append(
            MatchDetail(
                requirement=requirement,
                capability=capability,
                score=90 if index < 2 else 82,
                confidence=90,
                explanation=f"{name} shows strong evidence of {skill}.",
            )
        )

    demo_gaps = [
        Gap(
            competency=gap,
            severity="Medium",
            explanation=f"{gap} is not strongly demonstrated in the CV.",
            recommendation=f"Explore {gap} during the interview.",
        )
        for gap in gaps
    ]

    questions = [
        InterviewQuestion(
            priority="High",
            linked_competency=strengths[0],
            question=f"Can you describe a project where you used {strengths[0]} in a complex HR environment?",
            purpose="Validate real hands-on experience.",
        )
    ]

    match_result = MatchResult(
        candidate=candidate,
        job=job,
        overall_score=score,
        confidence_score=confidence,
        recommendation=recommendation,
        executive_summary=f"{name} is a strong demo profile with experience in {', '.join(strengths[:3])}.",
        match_details=match_details,
        gaps=demo_gaps,
        interview_questions=questions,
    )

    return {
        "file": f"{name.replace(' ', '_')}_CV.pdf",
        "candidate": candidate,
        "match_result": match_result,
    }


def load_demo_batch():
    job = Job(
        title="HRIS Project Manager",
        description="Demo HRIS Project Manager recruitment.",
        requirements=[
            _requirement("HRIS"),
            _requirement("Project Management"),
            _requirement("API Integration"),
            _requirement("Change Management"),
        ],
    )

    results = [
        _candidate(
            "Alice Martin",
            "Senior HRIS Consultant",
            94,
            96,
            "Strong Shortlist",
            ["HRIS", "Project Management", "API Integration", "Change Management"],
            ["Oracle HCM"],
            ["French", "English"],
        ),
        _candidate(
            "Bob Chen",
            "HR Data Lead",
            89,
            93,
            "Interview",
            ["People Analytics", "Power BI", "SQL", "Stakeholder Management"],
            ["Payroll"],
            ["English", "Mandarin"],
        ),
        _candidate(
            "Claire Dubois",
            "HRIS Project Manager",
            86,
            91,
            "Interview",
            ["HRIS", "Talent Management", "Change Management"],
            ["API Integration"],
            ["French", "English"],
        ),
        _candidate(
            "David Smith",
            "Payroll Systems Analyst",
            78,
            88,
            "Keep in Pipeline",
            ["Payroll Integration", "Time & Attendance", "Reporting"],
            ["Change Management", "API Integration"],
            ["English"],
        ),
        _candidate(
            "Emma Wang",
            "International HR Project Lead",
            83,
            90,
            "Interview",
            ["Project Management", "Stakeholder Management", "International Collaboration"],
            ["Power BI"],
            ["French", "English", "Mandarin"],
        ),
    ]

    return {
        "success": True,
        "job": job,
        "results": results,
        "errors": [],
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
        "created_at": "demo",
    }
