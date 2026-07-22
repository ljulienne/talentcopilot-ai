from talentcopilot.interview.models import InterviewCompetency
from talentcopilot.interview.question_service import InterviewQuestionService


def _competency(name="People Management"):
    return InterviewCompetency(
        name=name,
        evidence_level="Low",
        confidence=38,
        validate_in_interview=True,
        rationale="Interview validation is required.",
    )


def test_internal_taxonomy_label_is_never_quoted_as_cv_evidence():
    question = InterviewQuestionService().build(
        [_competency()],
        role_title="HRIS Manager",
        candidate={
            "skills": ["People Management"],
            "achievements": ["Management scope"],
        },
        mission_requirements=["People Management"],
    )[0]

    assert "Your CV states" not in question.question
    assert "‘Management scope’" not in question.question
    assert "Your experience suggests exposure to People Management" in question.question


def test_authentic_cv_line_can_be_used_as_grounded_evidence():
    source = "Led a team of eight HRIS specialists across regional implementation projects."
    question = InterviewQuestionService().build(
        [_competency("Team Leadership")],
        role_title="HRIS Manager",
        candidate={
            "skills": ["Team Leadership"],
            "achievements": [source],
        },
        mission_requirements=["Team Leadership"],
    )[0]

    assert "Your CV states" in question.question
    assert source in question.question


def test_evidence_gap_uses_limited_detail_language_not_a_false_quote():
    question = InterviewQuestionService().build(
        [_competency("Budget Management")],
        role_title="HRIS Manager",
        candidate={
            "skills": ["HRIS"],
            "achievements": ["Led an HRIS deployment across APAC."],
        },
        mission_requirements=["Budget Management"],
    )[0]

    assert question.question.startswith("The CV provides limited detail about Budget Management.")
    assert "Your CV states" not in question.question
    assert "Led an HRIS deployment" not in question.question


def test_question_engine_version_invalidates_old_cached_playbooks():
    assert InterviewQuestionService.ENGINE_VERSION == "7.2.1-evidence-grounding"
