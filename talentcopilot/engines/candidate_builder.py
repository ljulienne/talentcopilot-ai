
from talentcopilot.core.models import Candidate, CandidateCapability, Evidence
from talentcopilot.engines.competency_extractor import extract_competencies


def build_candidate_from_cv_text(cv_text, fallback_name="Unknown Candidate"):
    extraction = extract_competencies(cv_text)

    capabilities = []

    for item in extraction.get("competencies", []):
        competency_name = item.get("competency", "")
        evidence_items = item.get("evidence", [])

        evidence_objects = [
            Evidence(
                text=e,
                source="CV",
                linked_competency=competency_name,
                confidence=item.get("confidence", 70)
            )
            for e in evidence_items
        ]

        capability = CandidateCapability(
            name=competency_name,
            category=item.get("category", "General"),
            detected_level=item.get("detected_level", "Unknown"),
            confidence=item.get("confidence", 70),
            evidence=evidence_objects
        )

        capabilities.append(capability)

    candidate = Candidate(
        name=fallback_name,
        current_role="",
        capabilities=capabilities
    )

    return candidate
