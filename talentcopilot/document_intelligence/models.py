from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LoadedDocument:
    filename: str
    file_type: str
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class DocumentSection:
    title: str
    content: str
    confidence: int = 80


@dataclass
class DocumentAnalysis:
    filename: str
    language: str
    cleaned_text: str
    sections: List[DocumentSection] = field(default_factory=list)


@dataclass
class ExtractedCandidateProfile:
    candidate_name: str
    skills: List[str] = field(default_factory=list)
    raw_excerpt: str = ""
    language: str = "unknown"
    extraction_status: str = "OK"
