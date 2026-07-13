from talentcopilot.interview.models import InterviewCompetency
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.services.candidate_name_resolver import CandidateNameResolver
from talentcopilot.services.skill_normalization import canonical_skill


def test_loretta_identity_ignores_credentials_and_section_heading():
    text = """
    LORETTA DANIELSON, MBA, SPHR, SHRM-SCP
    312-555-5555 | lorettadanielson@gmail.com
    LinkedIn.com/in/lorettadanielson
    HUMAN RESOURCES DIRECTOR
    Signature HR Qualifications
    """
    assert CandidateNameResolver().resolve(
        text=text,
        filename="Loretta_CV.pdf",
        extracted_name="Signature HR Qualifications",
    ) == "Loretta Danielson"


def test_real_identity_cases_remain_stable():
    resolver = CandidateNameResolver()

    assert resolver.resolve(
        text="Vincent BLAKOE\nvincent.blakoe@hris-freelance.com",
        filename="Blakoe Vincent.pdf",
        extracted_name="Credit Suisse",
    ) == "Vincent Blakoe"

    assert resolver.resolve(
        text="LOUIS JULIENNE\nlouisjulienne1987@gmail.com",
        filename="LouisJulienneResume_2026.pdf",
        extracted_name="Candidate",
    ) == "Louis Julienne"

    assert resolver.resolve(
        text="Zelma O'Reilly\nWork Experience",
        filename="Zelma O.pdf",
        extracted_name="Candidate",
    ) == "Zelma O'Reilly"


def test_bilingual_hris_aliases_are_canonical():
    assert canonical_skill("SIRH") == "hris"
    assert canonical_skill("gestion de projets") == "project management"
    assert canonical_skill("conduite du changement") == "change management"
    assert canonical_skill("Microsoft Power BI") == "power bi"
    assert canonical_skill("system integrations") == "interfaces"


def test_interview_questions_are_specific_and_varied():
    competencies = [
        InterviewCompetency("SAP SuccessFactors", "Medium", 70, True, "Some evidence."),
        InterviewCompetency("Power BI reporting", "Medium", 70, True, "Some evidence."),
        InterviewCompetency("Change Management", "Low", 40, True, "Limited evidence."),
        InterviewCompetency("Stakeholder Management", "Medium", 65, True, "Some evidence."),
    ]

    questions = InterviewQuestionService().build(
        competencies,
        role_title="HRIS Project Manager",
        candidate={"achievements": [], "years_experience": 10},
        mission_requirements=[c.name for c in competencies],
    )

    assert len(questions) == 4
    assert len({question.question for question in questions}) == 4
    assert "systems, modules, interfaces" in questions[0].question.lower()
    assert "source data" in questions[1].question.lower()
    assert "user groups resisted" in questions[2].question.lower()
    assert "conflicting priorities" in questions[3].question.lower()
    assert not all(
        "the most difficult trade-off" in question.question
        for question in questions
    )
