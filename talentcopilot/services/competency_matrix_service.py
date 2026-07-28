from __future__ import annotations

import json
import re
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

from talentcopilot.models.competency_matrix import (
    CandidateCompetencyMatrix,
    CompetencyAssessment,
    CompetencyAuditEntry,
)
from talentcopilot.technical_requirements import TechnicalRequirementService


class CompetencyMatrixService:
    """Build and persist the candidate competency radar for one role.

    Product rules:
    - radar axes come from the job requirements, not from the whole CV;
    - the AI estimate remains immutable and traceable;
    - human interview ratings are stored separately;
    - role requirements cannot be deleted during an interview;
    - competencies discovered during the interview can be added, renamed,
      archived and restored;
    - no operation changes the official fit score, official rank or canonical
      recommendation stored in the recruitment session.
    """

    SCALE_MAX = 5.0
    DEFAULT_REQUIRED_LEVEL = 4.0
    VALIDATION_STATUSES = (
        "To validate",
        "Partially confirmed",
        "Confirmed",
        "Not demonstrated",
        "Not assessed",
    )

    def __init__(self, storage_dir: str | Path | None = None):
        self.storage_dir = Path(storage_dir or ".talentcopilot_data/competency_matrices")
        self.technical_requirements = TechnicalRequirementService()

    def build(self, report, session=None) -> CandidateCompetencyMatrix:
        job = dict(getattr(session, "job", {}) or {}) if session is not None else {}
        role_title = str(job.get("title") or getattr(session, "role_title", "Recruitment") or "Recruitment")
        job_id = str(job.get("job_id") or getattr(session, "session_id", "session") or "session")
        candidate_id = str(
            getattr(report, "candidate_id", "")
            or self._slug(getattr(report, "candidate_name", "candidate"))
        )

        skills = list(getattr(report, "skills", []) or [])
        skill_lookup = {
            self._slug(getattr(skill, "name", "")): skill
            for skill in skills
            if str(getattr(skill, "name", "") or "").strip()
        }
        candidate = self._candidate(session, report)
        requirements = self._role_requirements(job, skills)
        evidence_lookup = {
            self._slug(requirement["name"]): self.technical_requirements.evaluate_candidate(
                requirement, candidate
            )
            for requirement in requirements
            if str(requirement.get("requirement_kind") or "general_capability")
            != "general_capability"
        }

        existing = self.load(candidate_id, job_id)
        if existing is not None:
            changed = self._synchronise_role_requirements(
                existing, requirements, skill_lookup, evidence_lookup
            )
            self._merge_current_evidence(existing, skill_lookup, evidence_lookup)
            if changed:
                existing.updated_at = self._utc_now()
                self.save(existing, snapshot=False)
            return existing

        competencies = [
            self._assessment_from_requirement(requirement, skill_lookup, evidence_lookup)
            for requirement in requirements
        ]

        return CandidateCompetencyMatrix(
            candidate_id=candidate_id,
            candidate_name=str(getattr(report, "candidate_name", "Candidate")),
            job_id=job_id,
            role_title=role_title,
            competencies=competencies,
        )

    def update(
        self,
        matrix: CandidateCompetencyMatrix,
        updates: dict[str, dict],
        *,
        evaluator: str,
        rationale: str = "Interview assessment",
        status: str | None = None,
    ) -> CandidateCompetencyMatrix:
        allowed = {
            "interviewer_level",
            "validation_status",
            "comment",
            "interview_evidence",
            "category",
            "importance",
        }
        by_id = {item.competency_id: item for item in matrix.competencies}
        changed = False

        for competency_id, values in (updates or {}).items():
            item = by_id.get(competency_id)
            if item is None or not item.is_active:
                continue

            for field_name, new_value in (values or {}).items():
                if field_name not in allowed:
                    continue
                if field_name == "interviewer_level" and new_value is not None:
                    new_value = self._level(new_value)
                if field_name == "validation_status":
                    new_value = (
                        str(new_value)
                        if str(new_value) in self.VALIDATION_STATUSES
                        else "To validate"
                    )
                if field_name in {"comment", "interview_evidence", "category", "importance"}:
                    new_value = str(new_value or "").strip()

                previous = getattr(item, field_name)
                if previous == new_value:
                    continue
                self._audit(
                    matrix,
                    item.competency_id,
                    field_name,
                    previous,
                    new_value,
                    evaluator,
                    rationale,
                )
                setattr(item, field_name, new_value)
                changed = True

            if item.interviewer_level is not None:
                item.consolidated_level = self._consolidate(
                    item.ai_estimated_level,
                    item.interviewer_level,
                    item.confidence,
                )

        target_status = status or ("interview_in_progress" if changed else matrix.status)
        if target_status != matrix.status:
            self._audit(
                matrix,
                "matrix",
                "status",
                matrix.status,
                target_status,
                evaluator,
                rationale,
            )
            matrix.status = target_status
            changed = True

        if changed:
            matrix.matrix_version += 1
            matrix.updated_at = self._utc_now()
            self.save(matrix)
        return matrix

    def add_competency(
        self,
        matrix: CandidateCompetencyMatrix,
        competency_name: str,
        *,
        evaluator: str,
        interviewer_level: float = 3.0,
        category: str = "Additional interview evidence",
        importance: str = "Additional",
        comment: str = "",
        rationale: str = "Competency discovered during interview",
    ) -> CompetencyAssessment:
        name = " ".join(str(competency_name or "").split())
        if not name:
            raise ValueError("A competency name is required.")

        existing = next(
            (
                item
                for item in matrix.competencies
                if self._slug(item.competency_name) == self._slug(name)
            ),
            None,
        )
        if existing is not None:
            if not existing.is_active and not existing.is_job_requirement:
                self.restore_competency(matrix, existing.competency_id, evaluator=evaluator)
            return existing

        competency_id = self._unique_competency_id(matrix, name)
        now = self._utc_now()
        level = self._level(interviewer_level)
        item = CompetencyAssessment(
            competency_id=competency_id,
            competency_name=name,
            category=str(category or "Additional interview evidence").strip(),
            importance=str(importance or "Additional").strip(),
            required_level=0.0,
            ai_estimated_level=0.0,
            confidence="Human assessed",
            evidence_status="Interview evidence",
            evidence="Added by the evaluator during the interview.",
            interviewer_level=level,
            consolidated_level=level,
            validation_status="To validate",
            comment=str(comment or "").strip(),
            interview_evidence=str(comment or "").strip(),
            origin="interview_added",
            is_active=True,
            added_by=str(evaluator or "Human evaluator"),
            added_at=now,
        )
        matrix.competencies.append(item)
        self._audit(matrix, competency_id, "competency", None, item.competency_name, evaluator, rationale)
        matrix.status = "interview_in_progress"
        matrix.matrix_version += 1
        matrix.updated_at = now
        self.save(matrix)
        return item

    def rename_competency(
        self,
        matrix: CandidateCompetencyMatrix,
        competency_id: str,
        new_name: str,
        *,
        evaluator: str,
        rationale: str = "Interview-added competency renamed",
    ) -> bool:
        item = self._find(matrix, competency_id)
        if item is None or item.is_job_requirement:
            return False
        name = " ".join(str(new_name or "").split())
        if not name or name == item.competency_name:
            return False
        if any(
            other.competency_id != item.competency_id
            and other.is_active
            and self._slug(other.competency_name) == self._slug(name)
            for other in matrix.competencies
        ):
            raise ValueError("This competency already exists in the radar.")
        previous = item.competency_name
        item.competency_name = name
        self._audit(matrix, item.competency_id, "competency_name", previous, name, evaluator, rationale)
        matrix.matrix_version += 1
        matrix.updated_at = self._utc_now()
        self.save(matrix)
        return True

    def remove_competency(
        self,
        matrix: CandidateCompetencyMatrix,
        competency_id: str,
        *,
        evaluator: str,
        reason: str = "Removed from the post-interview radar",
    ) -> bool:
        item = self._find(matrix, competency_id)
        if item is None or item.is_job_requirement or not item.is_active:
            return False
        item.is_active = False
        item.removed_reason = str(reason or "Archived by evaluator").strip()
        self._audit(matrix, item.competency_id, "is_active", True, False, evaluator, item.removed_reason)
        matrix.matrix_version += 1
        matrix.updated_at = self._utc_now()
        self.save(matrix)
        return True

    def restore_competency(
        self,
        matrix: CandidateCompetencyMatrix,
        competency_id: str,
        *,
        evaluator: str,
        rationale: str = "Interview-added competency restored",
    ) -> bool:
        item = self._find(matrix, competency_id)
        if item is None or item.is_job_requirement or item.is_active:
            return False
        item.is_active = True
        item.removed_reason = ""
        self._audit(matrix, item.competency_id, "is_active", False, True, evaluator, rationale)
        matrix.matrix_version += 1
        matrix.updated_at = self._utc_now()
        self.save(matrix)
        return True

    def finalize(
        self,
        matrix: CandidateCompetencyMatrix,
        *,
        evaluator: str,
        rationale: str = "Post-interview competency radar saved",
    ) -> CandidateCompetencyMatrix:
        previous_status = matrix.status
        matrix.status = "post_interview"
        matrix.finalized_at = self._utc_now()
        matrix.finalized_by = str(evaluator or "Human evaluator")
        self._audit(
            matrix,
            "matrix",
            "status",
            previous_status,
            matrix.status,
            evaluator,
            rationale,
        )
        matrix.matrix_version += 1
        matrix.updated_at = matrix.finalized_at
        self.save(matrix)
        return matrix

    def save(self, matrix: CandidateCompetencyMatrix, *, snapshot: bool = True) -> Path:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(matrix.candidate_id, matrix.job_id)
        payload = json.dumps(matrix.to_dict(), indent=2, ensure_ascii=False)
        path.write_text(payload, encoding="utf-8")

        if snapshot:
            history_dir = self.storage_dir / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            history_path = history_dir / (
                f"{self._slug(matrix.job_id)}__{self._slug(matrix.candidate_id)}"
                f"__v{matrix.matrix_version:04d}.json"
            )
            history_path.write_text(payload, encoding="utf-8")
        return path

    def load(self, candidate_id: str, job_id: str) -> CandidateCompetencyMatrix | None:
        path = self._path(candidate_id, job_id)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["competencies"] = [
            CompetencyAssessment(**self._known_fields(CompetencyAssessment, item))
            for item in payload.get("competencies", [])
        ]
        payload["audit_history"] = [
            CompetencyAuditEntry(**self._known_fields(CompetencyAuditEntry, item))
            for item in payload.get("audit_history", [])
        ]
        return CandidateCompetencyMatrix(
            **self._known_fields(CandidateCompetencyMatrix, payload)
        )

    def comparison_rows(self, matrices: Iterable[CandidateCompetencyMatrix]) -> list[dict]:
        matrices = list(matrices)
        competency_names: list[str] = []
        for matrix in matrices:
            for item in matrix.active_competencies():
                if item.competency_name not in competency_names:
                    competency_names.append(item.competency_name)
        rows = []
        for name in competency_names:
            row = {"Competency": name}
            for matrix in matrices:
                item = next(
                    (
                        value
                        for value in matrix.active_competencies()
                        if value.competency_name == name
                    ),
                    None,
                )
                row[matrix.candidate_name] = item.effective_level() if item else None
            rows.append(row)
        return rows

    def _role_requirements(self, job: Mapping, skills: list) -> list[dict]:
        catalog = self.technical_requirements.catalog(job)
        if catalog.requirements:
            return [item.to_dict() for item in catalog.requirements]

        raw = (
            job.get("required_skills")
            or job.get("competencies")
            or job.get("skills")
            or []
        )
        requirements: list[dict] = []
        seen: set[str] = set()

        if isinstance(raw, (str, Mapping)):
            raw = [raw]

        for value in raw:
            requirement = self._normalise_requirement(value)
            if not requirement:
                continue
            key = self._slug(requirement["name"])
            if key in seen:
                continue
            seen.add(key)
            requirements.append(requirement)

        if not requirements:
            role_skills = [
                skill
                for skill in skills
                if str(getattr(skill, "requirement_type", "")) == "Role requirement"
            ]
            fallback = role_skills or skills
            for skill in fallback:
                name = str(getattr(skill, "name", "") or "").strip()
                key = self._slug(name)
                if not name or key in seen:
                    continue
                seen.add(key)
                requirements.append(
                    {
                        "name": name,
                        "required_level": self.DEFAULT_REQUIRED_LEVEL,
                        "importance": "Critical",
                        "category": self._category(name),
                    }
                )

        return requirements[: self.technical_requirements.MAX_RADAR_AXES]

    def _normalise_requirement(self, value) -> dict | None:
        if isinstance(value, Mapping):
            name = str(
                value.get("name")
                or value.get("competency")
                or value.get("skill")
                or value.get("label")
                or ""
            ).strip()
            if not name:
                return None
            required_level = self._level(
                value.get("required_level")
                or value.get("expected_level")
                or value.get("level")
                or self.DEFAULT_REQUIRED_LEVEL
            )
            importance = str(
                value.get("importance")
                or value.get("criticality")
                or ("Critical" if required_level >= 4 else "Supporting")
            ).strip()
            category = str(value.get("category") or self._category(name)).strip()
            return {
                "name": name,
                "required_level": required_level,
                "importance": importance,
                "category": category,
                "family": str(value.get("family") or "Role requirement"),
                "requirement_kind": str(value.get("requirement_kind") or "general_capability"),
                "source_excerpt": str(value.get("source_excerpt") or ""),
                "aliases": tuple(value.get("aliases") or (name,)),
                "related_terms": tuple(value.get("related_terms") or ()),
                "interview_priority": str(value.get("interview_priority") or "Validate"),
            }

        name = str(value or "").strip()
        if not name:
            return None
        return {
            "name": name,
            "required_level": self.DEFAULT_REQUIRED_LEVEL,
            "importance": "Critical",
            "category": self._category(name),
            "family": "Role requirement",
            "requirement_kind": "general_capability",
            "source_excerpt": "",
            "aliases": (name,),
            "related_terms": (),
            "interview_priority": "Validate",
        }

    def _assessment_from_requirement(
        self, requirement: dict, skill_lookup: dict, evidence_lookup: dict
    ) -> CompetencyAssessment:
        name = requirement["name"]
        skill = skill_lookup.get(self._slug(name))
        technical_evidence = evidence_lookup.get(self._slug(name))
        ai_level = (
            float(technical_evidence.estimated_level)
            if technical_evidence is not None
            else self._ai_level(skill)
        )
        confidence = (
            technical_evidence.confidence
            if technical_evidence is not None
            else str(getattr(skill, "confidence", "Low") if skill is not None else "Low")
        )
        evidence_status = (
            technical_evidence.evidence_status
            if technical_evidence is not None
            else str(getattr(skill, "status", "Not demonstrated") if skill is not None else "Not demonstrated")
        )
        evidence = (
            technical_evidence.evidence
            if technical_evidence is not None
            else str(getattr(skill, "evidence", "") if skill is not None else f"No direct evidence of {name} was identified in the current CV data.")
        )
        return CompetencyAssessment(
            competency_id=self._slug(name),
            competency_name=name,
            category=requirement["category"],
            importance=requirement["importance"],
            required_level=requirement["required_level"],
            ai_estimated_level=ai_level,
            confidence=confidence,
            evidence_status=evidence_status,
            evidence=evidence,
            consolidated_level=ai_level,
            origin="job_requirement",
            requirement_family=str(requirement.get("family") or "Role requirement"),
            requirement_kind=str(requirement.get("requirement_kind") or "general_capability"),
            source_excerpt=str(requirement.get("source_excerpt") or ""),
            related_evidence=list(technical_evidence.related_evidence if technical_evidence else ()),
            interview_priority=(technical_evidence.interview_priority if technical_evidence else str(requirement.get("interview_priority") or "Validate")),
        )

    def _synchronise_role_requirements(
        self, matrix, requirements, skill_lookup, evidence_lookup
    ) -> bool:
        changed = False
        by_id = {item.competency_id: item for item in matrix.competencies}
        required_ids: set[str] = set()

        for requirement in requirements:
            competency_id = self._slug(requirement["name"])
            required_ids.add(competency_id)
            current = by_id.get(competency_id)
            if current is None:
                matrix.competencies.append(
                    self._assessment_from_requirement(requirement, skill_lookup, evidence_lookup)
                )
                changed = True
                continue
            if current.origin != "job_requirement":
                continue
            for field_name in (
                "competency_name", "required_level", "importance", "category",
                "requirement_family", "requirement_kind", "source_excerpt", "interview_priority",
            ):
                source_key = {
                    "competency_name": "name",
                    "requirement_family": "family",
                }.get(field_name, field_name)
                new_value = requirement.get(source_key, getattr(current, field_name))
                if getattr(current, field_name) != new_value:
                    setattr(current, field_name, new_value)
                    changed = True
            if not current.is_active:
                current.is_active = True
                current.removed_reason = ""
                changed = True

        # Requirements removed from the job are retained for auditability but
        # no longer shown as active axes. Interview-added competencies are not
        # affected by this synchronization.
        if requirements:
            for item in matrix.competencies:
                if item.origin == "job_requirement" and item.competency_id not in required_ids:
                    if item.is_active:
                        item.is_active = False
                        item.removed_reason = "No longer present in the current job requirements."
                        changed = True
        return changed

    def _merge_current_evidence(self, matrix, skill_lookup, evidence_lookup):
        for item in matrix.competencies:
            if item.origin != "job_requirement":
                continue
            technical_evidence = evidence_lookup.get(item.competency_id)
            skill = skill_lookup.get(item.competency_id)
            if technical_evidence is not None:
                item.evidence = technical_evidence.evidence
                item.confidence = technical_evidence.confidence
                item.evidence_status = technical_evidence.evidence_status
                item.related_evidence = list(technical_evidence.related_evidence)
                item.interview_priority = technical_evidence.interview_priority
                if item.interviewer_level is None and matrix.status == "pre_interview":
                    item.ai_estimated_level = float(technical_evidence.estimated_level)
                    item.consolidated_level = item.ai_estimated_level
                continue
            if skill is None:
                continue
            item.evidence = str(getattr(skill, "evidence", item.evidence) or item.evidence)
            item.confidence = str(getattr(skill, "confidence", item.confidence) or item.confidence)
            item.evidence_status = str(getattr(skill, "status", item.evidence_status) or item.evidence_status)
            if item.interviewer_level is None and matrix.status == "pre_interview":
                item.ai_estimated_level = self._ai_level(skill)
                item.consolidated_level = item.ai_estimated_level
        return matrix

    def _candidate(self, session, report) -> dict:
        if session is None:
            return {}
        candidate_id = str(getattr(report, "candidate_id", "") or "")
        candidate_name = str(getattr(report, "candidate_name", "") or "")
        for candidate in getattr(session, "candidates", []) or []:
            if candidate_id and str(candidate.get("candidate_id") or "") == candidate_id:
                return dict(candidate)
            if candidate_name and str(candidate.get("name") or "") == candidate_name:
                return dict(candidate)
        return {}

    def _ai_level(self, skill) -> float:
        if skill is None:
            return 0.0
        raw = float(getattr(skill, "level", 0) or 0)
        value = raw / 20.0 if raw > self.SCALE_MAX else raw
        return round(max(0.0, min(self.SCALE_MAX, value)), 2)

    def _consolidate(self, ai_level: float, interviewer_level: float, confidence: str) -> float:
        ai_weight = {
            "High": 0.45,
            "Moderate": 0.35,
            "Limited": 0.25,
            "Low": 0.15,
        }.get(str(confidence), 0.30)
        return round(
            (float(ai_level) * ai_weight)
            + (float(interviewer_level) * (1.0 - ai_weight)),
            1,
        )

    def _audit(self, matrix, competency_id, field_name, previous, new, evaluator, rationale):
        matrix.audit_history.append(
            CompetencyAuditEntry(
                competency_id=str(competency_id),
                field_name=str(field_name),
                previous_value=previous,
                new_value=new,
                evaluator=str(evaluator or "Human evaluator"),
                rationale=str(rationale or "Interview assessment"),
            )
        )

    def _find(self, matrix, competency_id) -> CompetencyAssessment | None:
        return next(
            (item for item in matrix.competencies if item.competency_id == competency_id),
            None,
        )

    def _unique_competency_id(self, matrix, name: str) -> str:
        base = self._slug(name)
        existing = {item.competency_id for item in matrix.competencies}
        if base not in existing:
            return base
        index = 2
        while f"{base}-{index}" in existing:
            index += 1
        return f"{base}-{index}"

    def _path(self, candidate_id: str, job_id: str) -> Path:
        return self.storage_dir / f"{self._slug(job_id)}__{self._slug(candidate_id)}.json"

    def _level(self, value: object) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = 0.0
        return round(max(0.0, min(self.SCALE_MAX, number)), 1)

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

    @staticmethod
    def _known_fields(dataclass_type, payload: Mapping) -> dict:
        names = {field.name for field in fields(dataclass_type)}
        return {key: value for key, value in dict(payload or {}).items() if key in names}

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()
