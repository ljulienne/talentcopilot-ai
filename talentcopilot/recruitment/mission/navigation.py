"""Stable section map for the Recruitment Mission workspace."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MissionSection:
    key: str
    label: str
    question: str


MISSION_SECTIONS: Tuple[MissionSection, ...] = (
    MissionSection("overview", "Mission overview", "Where does this recruitment stand?"),
    MissionSection("ranking", "Candidate ranking", "Who should I review first?"),
    MissionSection("reasoning", "Recruiter reasoning", "Why does the ranking look this way?"),
    MissionSection("comparison", "Candidate comparison", "What differentiates the shortlist?"),
    MissionSection("interview", "Interview preparation", "What should I validate next?"),
    MissionSection("decision", "Hiring decision", "Is the mission ready for a human decision?"),
    MissionSection("report", "Executive report", "How do I share the recommendation?"),
)
