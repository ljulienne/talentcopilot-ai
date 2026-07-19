"""Bridge real document upload results into the official RecruitmentSession.

Release 3.1.1A keeps the existing document reader and real ranking pipeline, but
normalises their output into the Release 3 source of truth so every downstream
module consumes the same candidate IDs, scores and ranks.
"""

from __future__ import annotations

import re
import json
from typing import Any, Iterable, List, Optional
from uuid import uuid4

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.candidate_identity import resolve_candidate_id
from talentcopilot.services.analysis_provenance import build_provenance
from talentcopilot.services.candidate_name_resolver import CandidateNameResolver
from talentcopilot.services.real_upload_ranking_service import (
    RealUploadRankingReport,
    RealUploadRankingService,
)
from talentcopilot.services.upload_text_reader_service import UploadedTextDocument


class RecruitmentUploadSessionService:
    """Create an official, interoperable session from uploaded documents."""

    def __init__(
        self,
        ranking_service: Optional[RealUploadRankingService] = None,
        name_resolver: Optional[CandidateNameResolver] = None,
    ):
        self.ranking_service = ranking_service or RealUploadRankingService()
        self.name_resolver = name_resolver or CandidateNameResolver()

    def run(
        self,
        job_document: UploadedTextDocument,
        candidate_documents: List[UploadedTextDocument],
    ) -> RecruitmentSession:
        report = self.ranking_service.run(job_document, candidate_documents)
        if report.ranking_output is None:
            raise ValueError(report.status or "The uploaded documents could not be analysed.")
        return self.from_report(report)

    def from_report(self, report: RealUploadRankingReport) -> RecruitmentSession:
        output = report.ranking_output
        if output is None:
            raise ValueError(report.status or "Missing ranking output.")

        documents = list(report.candidate_documents or [])
        candidates = []
        analyses = []

        for position, ranked in enumerate(getattr(output, "ranked_candidates", []) or [], start=1):
            extracted_name = str(
                getattr(ranked, "candidate_name", "Candidate")
                or "Candidate"
            ).strip()

            document = self._find_candidate_document(
                extracted_name,
                documents,
                position - 1,
                ranked=ranked,
            )

            candidate_name = self.name_resolver.resolve(
                text=str(getattr(document, "text", "") or ""),
                filename=str(getattr(document, "filename", "") or ""),
                extracted_name=extracted_name,
            )

            candidate = self._candidate_dict(
                candidate_name,
                document,
                ranked,
            )
            candidate_id = resolve_candidate_id(candidate)
            candidate["candidate_id"] = candidate_id
            candidates.append(candidate)

            # Role Fit remains the official matching score.
            #
            # ranking_score is deliberately not substituted here because it
            # represents a different consolidated decision metric.
            role_fit_score = self._first_number(
                getattr(ranked, "fit_score", None),
                getattr(ranked, "ranking_score", None),
                0.0,
            )

            decision_score = self._optional_number(
                getattr(ranked, "ranking_score", None)
            )
            rank = int(getattr(ranked, "rank", position) or position)
            recommendation = str(getattr(ranked, "recommendation", "Review required") or "Review required")
            rationale = str(getattr(ranked, "rationale", "") or "")

            analyses.append(
                CandidateAnalysisState(
                    candidate_name=candidate_name,
                    candidate_id=candidate_id,
                    status=CandidateAnalysisStatus.ANALYZED,
                    match_score=round(role_fit_score, 2),
                    decision_score=decision_score,
                    rank=rank,
                    score_breakdown=self._score_breakdown(
                        ranked,
                        role_fit_score,
                        decision_score,
                    ),
                    notes=[
                        "Created from real uploaded documents.",
                        f"Recommendation: {recommendation}",
                        rationale,
                    ],
                )
            )

        # Release 4.2.1:
        # the official recruitment rank derives exclusively from the
        # official match score. Decision/ranking scores remain internal
        # decision-support signals and never determine the public order.
        analyses.sort(
            key=lambda item: (
                -float(item.match_score or 0),
                str(item.candidate_name or "").casefold(),
                str(item.candidate_id or ""),
            )
        )

        for index, analysis in enumerate(analyses, start=1):
            analysis.rank = index

        role_title = str(getattr(output, "role_title", "Recruitment") or "Recruitment")
        job_document = report.job_document
        job = {
            "title": role_title,
            "source": getattr(job_document, "filename", "uploaded-job"),
            "raw_text": getattr(job_document, "text", ""),
            "required_skills": self._extract_skills(getattr(job_document, "text", "")),
        }

        provenance = build_provenance(
            job_text=str(getattr(job_document, "text", "") or ""),
            candidate_texts=[
                str(getattr(doc, "text", "") or "")
                for doc in documents
            ],
        )

        return RecruitmentSession(
            session_id=f"upload-{uuid4().hex[:10]}",
            job=job,
            candidates=candidates,
            status=SessionStatus.COMPLETED,
            analyses=analyses,
            metadata={
                "source": "real_upload",
                "job_filename": getattr(job_document, "filename", ""),
                "candidate_filenames": [
                    getattr(doc, "filename", "")
                    for doc in documents
                ],
                "workflow_version": "3.2.1A.2.2",
                **provenance.as_metadata(),
            },
        )

    def _candidate_dict(self, name: str, document: Any, ranked: Any) -> dict:
        text = str(getattr(document, "text", "") or "")
        filename = str(getattr(document, "filename", "") or "")
        profile = self._profile(ranked)
        skills = self._profile_skills(profile) or self._extract_skills(text)
        evidence = self._mission_fit_evidence(profile) or self._profile_evidence(profile)
        if not evidence:
            evidence = self._extract_evidence(text)

        return {
            "name": name,
            "title": str(getattr(profile, "role_title", "") or ""),
            "skills": skills,
            "achievements": evidence,
            "years_experience": self._extract_years(text),
            "source": filename,
            "filename": filename,
            "raw_text": text,
            "upload_recommendation": str(getattr(ranked, "recommendation", "") or ""),
            "upload_rationale": str(getattr(ranked, "rationale", "") or ""),
        }

    def _find_candidate_document(
        self,
        name: str,
        documents: List[Any],
        fallback_index: int,
        ranked: Any = None,
    ):
        # Prefer an explicit source filename when exposed by the ranking models.
        possible_filenames = [
            getattr(ranked, "candidate_filename", None),
            getattr(ranked, "filename", None),
            getattr(ranked, "source_filename", None),
        ]

        matching_output = getattr(ranked, "matching_output", None)
        possible_filenames.extend(
            [
                getattr(matching_output, "candidate_filename", None),
                getattr(matching_output, "filename", None),
                getattr(matching_output, "source_filename", None),
            ]
        )

        normalized_filenames = {
            str(value).strip().lower()
            for value in possible_filenames
            if value
        }

        for document in documents:
            document_filename = str(
                getattr(document, "filename", "") or ""
            ).strip().lower()

            if (
                document_filename
                and document_filename in normalized_filenames
            ):
                return document

        # Then match the current extracted identity against document text.
        lowered = str(name or "").lower().strip()

        for document in documents:
            document_text = str(
                getattr(document, "text", "") or ""
            ).lower()

            if lowered and lowered in document_text:
                return document

        # Finally preserve the previous deterministic positional fallback.
        if 0 <= fallback_index < len(documents):
            return documents[fallback_index]

        return None

    def _profile(self, ranked: Any):
        matching = getattr(ranked, "matching_output", None)
        decision = getattr(matching, "decision_output", None)
        return getattr(decision, "profile", None)

    def _profile_skills(self, profile: Any) -> List[str]:
        graph = getattr(profile, "evidence_graph", None)
        nodes = getattr(graph, "nodes", []) or []
        values = []
        for node in nodes:
            node_type = str(getattr(node, "node_type", "") or "").lower()
            if "skill" in node_type or "competenc" in node_type:
                label = str(getattr(node, "label", "") or "").strip()
                if label and label not in values:
                    values.append(label)
        return values[:12]


    def _mission_fit_evidence(self, profile: Any) -> List[str]:
        """Return recruiter-readable evidence generated by Mission Fit v2."""
        metadata = getattr(profile, "metadata", {}) or {}
        raw = metadata.get("mission_fit_evidence")
        if not raw:
            return []
        try:
            values = json.loads(raw) if isinstance(raw, str) else list(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        return [str(value).strip() for value in values if str(value).strip()][:10]

    def _profile_evidence(self, profile: Any) -> List[str]:
        graph = getattr(profile, "evidence_graph", None)
        sources = getattr(graph, "sources", []) or []
        values = []
        for source in sources:
            excerpt = str(getattr(source, "excerpt", "") or "").strip()
            label = str(getattr(source, "label", "") or "").strip()
            value = excerpt or label
            if value and value not in values:
                values.append(value)
        return values[:8]

    def _extract_skills(self, text: str) -> List[str]:
        lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
        values = []
        capture = False
        for line in lines:
            lower = line.lower().rstrip(":")
            if lower in {"skills", "competencies", "requirements", "required skills", "key skills"}:
                capture = True
                continue
            if capture and lower in {"experience", "education", "achievements", "summary", "responsibilities"}:
                break
            if capture:
                for item in re.split(r"[,;|•]", line):
                    clean = item.strip(" -\t")
                    if 2 < len(clean) <= 80 and clean not in values:
                        values.append(clean)
            if len(values) >= 12:
                break
        return values[:12]

    def _extract_evidence(self, text: str) -> List[str]:
        values = []
        for line in str(text or "").splitlines():
            clean = line.strip(" -•\t")
            if len(clean) >= 25 and any(char.isdigit() for char in clean):
                values.append(clean)
            if len(values) >= 6:
                break
        return values

    def _extract_years(self, text: str) -> float:
        match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", str(text or ""), re.IGNORECASE)
        return float(match.group(1)) if match else 0.0

    def _score_breakdown(
        self,
        ranked: Any,
        role_fit_score: float,
        decision_score: Optional[float],
    ) -> dict:
        profile = self._profile(ranked)
        metadata = getattr(profile, "metadata", {}) or {}

        breakdown = {
            # Backward-compatible key retained for existing consumers.
            "official_upload_fit": round(role_fit_score, 2),

            # Explicit terminology for new consumers.
            "role_fit": round(role_fit_score, 2),

            "evidence_quality": self._number(
                metadata.get("evidence_quality_score")
            ),
            "confidence": self._number(
                getattr(ranked, "confidence_score", None)
            ),
        }

        raw_dimensions = metadata.get("mission_fit_breakdown")
        if raw_dimensions:
            try:
                dimensions = json.loads(raw_dimensions) if isinstance(raw_dimensions, str) else raw_dimensions
                for key, value in dict(dimensions).items():
                    breakdown[f"mission_fit_{key}"] = round(self._number(value), 2)
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        # Missing values remain missing; they are never converted into zero.
        if decision_score is not None:
            breakdown["decision_score"] = round(
                decision_score,
                2,
            )

        return breakdown

    def _first_number(self, *values: Any) -> float:
        for value in values:
            if value is not None:
                return self._number(value)
        return 0.0

    def _optional_number(
        self,
        value: Any,
    ) -> Optional[float]:
        """Convert a numeric value while preserving missing data."""
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _number(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
