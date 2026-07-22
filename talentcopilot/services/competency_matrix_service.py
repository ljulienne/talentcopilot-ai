from __future__ import annotations

import json
import re
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from talentcopilot.models.competency_matrix import (
    CandidateCompetencyMatrix,
    CompetencyAssessment,
    CompetencyAuditEntry,
)


class CompetencyMatrixService:
    """Build, persist and compare editable competency matrices.

    The matrix is a decision-support view. It never changes the official match
    score, rank or recommendation stored in the recruitment session.
    """

    SCALE_MAX = 5.0

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir or ".talentcopilot_data/competency_matrices")

    def build(self, report, session=None) -> CandidateCompetencyMatrix:
        job = dict(getattr(session, "job", {}) or {}) if session is not None else {}
        role_title = str(job.get("title") or getattr(session, "role_title", "Recruitment") or "Recruitment")
        job_id = str(
            job.get("job_id")
            or getattr(session, "session_id", "session")
            or "session"
        )
        candidate_id = str(getattr(report, "candidate_id", "") or self._slug(getattr(report, "candidate_name", "candidate")))

        existing = self.load(candidate_id, job_id)
        if existing is not None:
            return self._merge_current_evidence(existing, report)

        competencies = []
        for skill in list(getattr(report, "skills", []) or [])[:10]:
            ai_level = round(max(0.0, min(5.0, float(getattr(skill, "level", 0) or 0) / 20.0)), 1)
            required_level = 4.0 if getattr(skill, "requirement_type", "") == "Role requirement" else 3.0
            competencies.append(
                CompetencyAssessment(
                    competency_id=self._slug(getattr(skill, "name", "competency")),
                    competency_name=str(getattr(skill, "name", "Competency")),
                    category=self._category(getattr(skill, "name", "")),
                    importance="Critical" if required_level >= 4.0 else "Supporting",
                    required_level=required_level,
                    ai_estimated_level=ai_level,
                    confidence=str(getattr(skill, "confidence", "Moderate")),
                    evidence_status=str(getattr(skill, "status", "Limited evidence")),
                    evidence=str(getattr(skill, "evidence", "") or "No direct evidence identified."),
                    consolidated_level=ai_level,
                )
            )

        matrix = CandidateCompetencyMatrix(
            candidate_id=candidate_id,
            candidate_name=str(getattr(report, "candidate_name", "Candidate")),
            job_id=job_id,
            role_title=role_title,
            competencies=competencies,
        )
        return matrix

    def update(
        self,
        matrix: CandidateCompetencyMatrix,
        updates: dict[str, dict],
        *,
        evaluator: str,
        rationale: str = "Interview assessment",
        status: str | None = None,
    ) -> CandidateCompetencyMatrix:
        allowed = {field.name for field in fields(CompetencyAssessment)} - {
            "competency_id", "competency_name", "ai_estimated_level", "evidence"
        }
        by_id = {item.competency_id: item for item in matrix.competencies}

        for competency_id, values in (updates or {}).items():
            item = by_id.get(competency_id)
            if item is None:
                continue
            for field_name, new_value in values.items():
                if field_name not in allowed:
                    continue
                if field_name in {"required_level", "interviewer_level", "consolidated_level"} and new_value is not None:
                    new_value = round(max(0.0, min(self.SCALE_MAX, float(new_value))), 1)
                previous = getattr(item, field_name)
                if previous == new_value:
                    continue
                matrix.audit_history.append(
                    CompetencyAuditEntry(
                        competency_id=competency_id,
                        field_name=field_name,
                        previous_value=previous,
                        new_value=new_value,
                        evaluator=evaluator or "Human evaluator",
                        rationale=rationale,
                    )
                )
                setattr(item, field_name, new_value)

            if item.interviewer_level is not None:
                item.consolidated_level = self._consolidate(
                    item.ai_estimated_level,
                    item.interviewer_level,
                    item.confidence,
                )

        matrix.matrix_version += 1
        matrix.status = status or ("interview_in_progress" if updates else matrix.status)
        matrix.updated_at = datetime.now(timezone.utc).isoformat()
        self.save(matrix)
        return matrix

    def save(self, matrix: CandidateCompetencyMatrix) -> Path:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(matrix.candidate_id, matrix.job_id)
        path.write_text(json.dumps(matrix.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self, candidate_id: str, job_id: str) -> CandidateCompetencyMatrix | None:
        path = self._path(candidate_id, job_id)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["competencies"] = [CompetencyAssessment(**item) for item in payload.get("competencies", [])]
        payload["audit_history"] = [CompetencyAuditEntry(**item) for item in payload.get("audit_history", [])]
        return CandidateCompetencyMatrix(**payload)

    def comparison_rows(self, matrices: Iterable[CandidateCompetencyMatrix]) -> list[dict]:
        matrices = list(matrices)
        competency_names = []
        for matrix in matrices:
            for item in matrix.competencies:
                if item.competency_name not in competency_names:
                    competency_names.append(item.competency_name)
        rows = []
        for name in competency_names:
            row = {"Competency": name}
            for matrix in matrices:
                item = next((value for value in matrix.competencies if value.competency_name == name), None)
                row[matrix.candidate_name] = item.effective_level() if item else None
            rows.append(row)
        return rows

    def _merge_current_evidence(self, matrix, report):
        current = {self._slug(getattr(skill, "name", "")): skill for skill in getattr(report, "skills", []) or []}
        for item in matrix.competencies:
            skill = current.get(item.competency_id)
            if skill is not None:
                item.evidence = str(getattr(skill, "evidence", item.evidence) or item.evidence)
                item.confidence = str(getattr(skill, "confidence", item.confidence) or item.confidence)
                item.evidence_status = str(getattr(skill, "status", item.evidence_status) or item.evidence_status)
        return matrix

    def _consolidate(self, ai_level: float, interviewer_level: float, confidence: str) -> float:
        ai_weight = {"High": 0.45, "Moderate": 0.35, "Limited": 0.25, "Low": 0.15}.get(confidence, 0.30)
        return round((float(ai_level) * ai_weight) + (float(interviewer_level) * (1.0 - ai_weight)), 1)

    def _path(self, candidate_id: str, job_id: str) -> Path:
        return self.storage_dir / f"{self._slug(job_id)}__{self._slug(candidate_id)}.json"

    def _slug(self, value: object) -> str:
        return re.sub(r"[^a-z0-9]+", "-", str(value or "item").lower()).strip("-") or "item"

    def _category(self, name: object) -> str:
        value = str(name or "").lower()
        if any(token in value for token in ("lead", "manage", "stakeholder", "budget", "governance")):
            return "Leadership & Delivery"
        if any(token in value for token in ("sap", "hris", "system", "data", "technical", "automation")):
            return "Technology & HRIS"
        if any(token in value for token in ("recruit", "talent", "people", "coaching")):
            return "People & Talent"
        return "Role Capability"
