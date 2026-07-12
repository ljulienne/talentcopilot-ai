from types import SimpleNamespace

from talentcopilot.services.candidate_name_resolver import (
    CandidateNameResolver,
)
from talentcopilot.services.recruitment_upload_session_service import (
    RecruitmentUploadSessionService,
)
from talentcopilot.services.upload_text_reader_service import (
    UploadedTextDocument,
)


VINCENT_CV_TEXT = """
ABOUT ME

During my 13 years in HRIS/HR consulting, I implemented international
projects for AstraZeneca, Siemens, BNP Paribas, Credit Suisse,
Standard Chartered Bank and Renault.

Vincent BLAKOE
35 years old
French Nationality
Driving Licence
7 rue du Monastère
38450 VIF
vincent.blakoe@hris-freelance.com
+33.(0).7.81.00.56.75

Freelance International HRIS Project Manager / Program Manager / Consultant
LinkedIn: linkedin.com/in/vincentblakoe
"""


def test_resolver_uses_personal_email_before_client_company():
    resolver = CandidateNameResolver()

    name = resolver.resolve(
        text=VINCENT_CV_TEXT,
        filename="Blakoe Vincent(1).pdf",
        extracted_name="Credit Suisse",
    )

    assert name == "Vincent Blakoe"


def test_resolver_reads_uppercase_header_name():
    resolver = CandidateNameResolver()

    name = resolver.resolve(
        text="VINCENT BLAKOE\nHRIS Project Manager\n13 years experience",
        filename="resume.pdf",
        extracted_name="Candidate",
    )

    assert name == "Vincent Blakoe"


def test_resolver_rejects_company_as_existing_name():
    resolver = CandidateNameResolver()

    name = resolver.resolve(
        text="Credit Suisse\nvincent.blakoe@example.com",
        filename="resume.pdf",
        extracted_name="Credit Suisse",
    )

    assert name == "Vincent Blakoe"


def test_resolver_can_use_uploaded_filename():
    resolver = CandidateNameResolver()

    name = resolver.resolve(
        text="Professional profile without a visible header",
        filename="Blakoe Vincent(1).pdf",
        extracted_name="Unknown Candidate",
    )

    assert name == "Blakoe Vincent"


def test_upload_session_replaces_wrong_pipeline_identity():
    document = UploadedTextDocument(
        filename="Blakoe Vincent(1).pdf",
        file_type="pdf",
        text=VINCENT_CV_TEXT,
    )

    ranked = SimpleNamespace(
        candidate_name="Credit Suisse",
        fit_score=72.0,
        rank=1,
        recommendation="Recommended",
        rationale="Strong HRIS experience.",
        matching_output=None,
    )

    output = SimpleNamespace(
        role_title="International HRIS Program Manager",
        ranked_candidates=[ranked],
    )

    report = SimpleNamespace(
        ranking_output=output,
        candidate_documents=[document],
        job_document=UploadedTextDocument(
            filename="job.pdf",
            file_type="pdf",
            text="International HRIS Program Manager",
        ),
        status="Ready",
    )

    session = RecruitmentUploadSessionService().from_report(report)

    assert session.candidates[0]["name"] == "Vincent Blakoe"
    assert session.ranked_analyses[0].candidate_name == "Vincent Blakoe"
    assert session.ranked_analyses[0].match_score == 72.0
    assert session.ranked_analyses[0].rank == 1
