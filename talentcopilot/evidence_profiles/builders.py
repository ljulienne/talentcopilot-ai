from __future__ import annotations

import hashlib
import re
from typing import Iterable, List

from talentcopilot.document_intelligence.candidate_extractor import CandidateDocumentExtractor
from talentcopilot.document_intelligence.models import ExtractedCandidateProfile
from talentcopilot.evidence_profiles.models import CandidateEvidenceProfile, EvidenceItem, MissionEvidenceProfile
from talentcopilot.job_intelligence.models import RoleProfile


TECHNOLOGIES = ("SAP SuccessFactors", "Workday", "Oracle", "SAP HCM", "SAP HR", "PeopleSoft", "Cornerstone", "Talentsoft", "Saba", "Power BI", "Tableau", "QlikSense", "Business Objects")
LANGUAGES = ("English", "French", "Mandarin", "Chinese", "Spanish", "German", "Italian", "Portuguese")
SENIORITY_PATTERNS = (("executive", r"\b(?:chief|chro|vice president|vp|director)\b"), ("senior", r"\b(?:senior|lead|head|manager)\b"), ("mid", r"\b(?:consultant|specialist|analyst|coordinator)\b"), ("junior", r"\b(?:junior|assistant|trainee|intern)\b"))


def _clean(value: str) -> str:
    return " ".join(str(value or "").replace("’", "'").split())


def _hash(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _dedupe(values: Iterable[str]) -> List[str]:
    result, seen = [], set()
    for value in values:
        clean = _clean(value)
        key = clean.casefold()
        if clean and key not in seen:
            seen.add(key); result.append(clean)
    return result


def _evidence_id(prefix: str, category: str, value: str) -> str:
    digest = hashlib.sha1(f"{prefix}|{category}|{value.casefold()}".encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _excerpt(text: str, value: str, radius: int = 90) -> str:
    match = re.search(re.escape(value), text, re.I)
    if not match:
        return value
    start=max(0, match.start()-radius); end=min(len(text), match.end()+radius)
    return _clean(text[start:end])


def _find_terms(text: str, terms: Iterable[str]) -> List[str]:
    return [term for term in terms if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I)]


class CandidateEvidenceProfileBuilder:
    version = "candidate-evidence-profile-builder-v1.0"

    def build(self, *, candidate_text: str, extracted_candidate: ExtractedCandidateProfile | None = None, candidate_name: str | None = None) -> CandidateEvidenceProfile:
        text = _clean(candidate_text)
        extracted = extracted_candidate
        if extracted is None:
            data = CandidateDocumentExtractor(extraction_mode=CandidateDocumentExtractor.DETERMINISTIC_MODE).extract_candidate_dict_from_text(candidate_text)
            name = candidate_name or data.get("name") or "Unknown Candidate"
            skills = data.get("skills", [])
            certifications = data.get("certifications", [])
            languages = data.get("languages", [])
            responsibilities = data.get("responsibilities", [])
            achievements = data.get("achievements", [])
        else:
            name = candidate_name or extracted.candidate_name
            skills = list(extracted.skills)
            signal = CandidateDocumentExtractor(extraction_mode=CandidateDocumentExtractor.DETERMINISTIC_MODE).signals
            certifications = signal.extract_certifications(candidate_text)
            languages = signal.extract_languages(candidate_text)
            responsibilities = signal.extract_responsibilities(candidate_text)
            achievements = signal.extract_achievements(candidate_text)
        technologies = _find_terms(text, TECHNOLOGIES)
        languages = _dedupe([*languages, *_find_terms(text, LANGUAGES)])
        evidence: List[EvidenceItem] = []
        groups = {"skill": skills, "technology": technologies, "certification": certifications, "language": languages, "responsibility": responsibilities, "achievement": achievements}
        for category, values in groups.items():
            for value in _dedupe(values):
                evidence.append(EvidenceItem(_evidence_id("candidate", category, value), category, value, value.casefold(), _excerpt(text, value), "candidate_cv", 90 if category in {"technology", "certification", "language"} else 82))
        return CandidateEvidenceProfile(candidate_name=name, skills=_dedupe(skills), technologies=_dedupe(technologies), certifications=_dedupe(certifications), languages=languages, responsibilities=_dedupe(responsibilities), achievements=_dedupe(achievements), evidence=evidence, source_text_hash=_hash(candidate_text))


class MissionEvidenceProfileBuilder:
    version = "mission-evidence-profile-builder-v1.0"

    def build(self, *, job_text: str, role_profile: RoleProfile | None = None) -> MissionEvidenceProfile:
        text = _clean(job_text)
        role = role_profile
        title = role.role_title if role else self._infer_title(text)
        required = list(role.required_skills) if role else []
        preferred = list(role.preferred_skills) if role else []
        responsibilities = list(role.responsibilities) if role else []
        languages = list(role.languages) if role else _find_terms(text, LANGUAGES)
        certifications = list(role.certifications) if role else []
        years = int(role.minimum_years_experience or 0) if role else self._years(text)
        technologies = _find_terms(text, TECHNOLOGIES)
        seniority = self._seniority(f"{title} {text}")
        critical = self._critical(text, [*required, *technologies])
        evidence: List[EvidenceItem] = []
        groups = {"required_skill": required, "preferred_skill": preferred, "technology": technologies, "language": languages, "certification": certifications, "responsibility": responsibilities, "critical_criterion": critical}
        for category, values in groups.items():
            for value in _dedupe(values):
                evidence.append(EvidenceItem(_evidence_id("mission", category, value), category, value, value.casefold(), _excerpt(text, value), "job_description", 92 if category in {"required_skill", "critical_criterion"} else 84))
        return MissionEvidenceProfile(role_title=title, required_skills=_dedupe(required), preferred_skills=_dedupe(preferred), technologies=_dedupe(technologies), languages=_dedupe(languages), certifications=_dedupe(certifications), responsibilities=_dedupe(responsibilities), critical_criteria=_dedupe(critical), minimum_years_experience=years, seniority=seniority, evidence=evidence, source_text_hash=_hash(job_text))

    def _infer_title(self, text: str) -> str:
        match=re.search(r"\b((?:senior\s+)?(?:global\s+|international\s+)?(?:hris|human resources information systems?)\s+(?:project\s+)?(?:manager|director|lead|consultant|analyst))\b", text, re.I)
        return match.group(1).title().replace("Hris", "HRIS") if match else "Unknown Role"

    def _years(self, text: str) -> int:
        match=re.search(r"\b(\d{1,2})\s*\+?\s*(?:years?|ans)\b", text, re.I)
        return int(match.group(1)) if match else 0

    def _seniority(self, text: str) -> str:
        for label, pattern in SENIORITY_PATTERNS:
            if re.search(pattern, text, re.I): return label
        return "unspecified"

    def _critical(self, text: str, known: Iterable[str]) -> List[str]:
        critical=[]
        for value in _dedupe(known):
            around=_excerpt(text, value, 55)
            if re.search(r"\b(?:required|mandatory|must|essential|critical|indispensable|requis|obligatoire)\b", around, re.I): critical.append(value)
        return critical
