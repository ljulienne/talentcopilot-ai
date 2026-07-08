from dataclasses import dataclass, field
from typing import List

from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput, RealRankingOutput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline
from talentcopilot.services.upload_text_reader_service import UploadedTextDocument


@dataclass
class RealUploadRankingReport:
    status: str
    job_document: UploadedTextDocument | None = None
    candidate_documents: List[UploadedTextDocument] = field(default_factory=list)
    ranking_output: RealRankingOutput | None = None


class RealUploadRankingService:
    def run(
        self,
        job_document: UploadedTextDocument,
        candidate_documents: List[UploadedTextDocument],
    ) -> RealUploadRankingReport:
        valid_candidates = [doc for doc in candidate_documents if doc.text.strip() and doc.status == "OK"]

        if not job_document or not job_document.text.strip():
            return RealUploadRankingReport(
                status="Missing job document text",
                job_document=job_document,
                candidate_documents=candidate_documents,
            )

        if not valid_candidates:
            return RealUploadRankingReport(
                status="Missing candidate document text",
                job_document=job_document,
                candidate_documents=candidate_documents,
            )

        ranking = RealRankingPipeline().run(
            RealRankingInput(
                job_filename=job_document.filename,
                job_text=job_document.text,
                candidates=[
                    CandidateTextInput(filename=doc.filename, text=doc.text)
                    for doc in valid_candidates
                ],
            )
        )

        return RealUploadRankingReport(
            status="Ready",
            job_document=job_document,
            candidate_documents=valid_candidates,
            ranking_output=ranking,
        )

    def run_demo(self) -> RealUploadRankingReport:
        from talentcopilot.services.upload_text_reader_service import UploadedTextDocument

        job = UploadedTextDocument(
            filename="job.txt",
            file_type="txt",
            text=(
                "Transformation Lead\nRequirements\nMinimum 6 years experience. "
                "Project Management Stakeholder Management HRIS\nCompensation\n85000 100000"
            ),
        )
        candidates = [
            UploadedTextDocument(
                filename="alice.txt",
                file_type="txt",
                text="Alice Martin\n8 years experience\nSkills\nHRIS Project Management Stakeholder Management",
            ),
            UploadedTextDocument(
                filename="david.txt",
                file_type="txt",
                text="David Smith\n1 years experience\nSkills\nGraphic Design",
            ),
        ]
        return self.run(job, candidates)
