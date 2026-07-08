from dataclasses import dataclass, field
from typing import List

from talentcopilot.llm_extraction.real_ranking import LLMCandidateTextInput, LLMRealRankingInput, LLMRealRankingOutput, LLMRealRankingPipeline
from talentcopilot.services.upload_text_reader_service import UploadedTextDocument


@dataclass
class LLMRealUploadReport:
    status: str
    job_document: UploadedTextDocument | None = None
    candidate_documents: List[UploadedTextDocument] = field(default_factory=list)
    ranking_output: LLMRealRankingOutput | None = None


class LLMRealUploadService:
    def run(self, job_document: UploadedTextDocument, candidate_documents: List[UploadedTextDocument]) -> LLMRealUploadReport:
        valid_candidates = [doc for doc in candidate_documents if doc.text.strip() and doc.status == "OK"]

        if not job_document or not job_document.text.strip():
            return LLMRealUploadReport(
                status="Missing job document text",
                job_document=job_document,
                candidate_documents=candidate_documents,
            )

        if not valid_candidates:
            return LLMRealUploadReport(
                status="Missing candidate document text",
                job_document=job_document,
                candidate_documents=candidate_documents,
            )

        output = LLMRealRankingPipeline().run(
            LLMRealRankingInput(
                job_filename=job_document.filename,
                job_text=job_document.text,
                candidates=[
                    LLMCandidateTextInput(filename=doc.filename, text=doc.text)
                    for doc in valid_candidates
                ],
            )
        )

        return LLMRealUploadReport(
            status="Ready",
            job_document=job_document,
            candidate_documents=valid_candidates,
            ranking_output=output,
        )

    def run_demo(self) -> LLMRealUploadReport:
        job = UploadedTextDocument(
            filename="job.txt",
            file_type="txt",
            text="HRIS Director\nMinimum 8 years experience. Required skills: HRIS, Project Management, Leadership.",
        )
        candidates = [
            UploadedTextDocument(
                filename="loretta.txt",
                file_type="txt",
                text="LORETTA DANIELSON, MBA, SPHR, SHRM-SCP\nHuman Resources Director\nHRIS, Change Management, Talent Acquisition",
            ),
            UploadedTextDocument(
                filename="vincent.txt",
                file_type="txt",
                text="Vincent BLAKOE\nFreelance International HRIS Project Manager\n13 years experience with Workday, SuccessFactors, Saba and Talentsoft.",
            ),
        ]
        return self.run(job, candidates)
