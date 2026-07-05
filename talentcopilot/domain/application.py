from dataclasses import dataclass
from typing import Optional

from talentcopilot.domain.candidate import CandidateProfile


@dataclass
class Application:
    application_id: str
    candidate: CandidateProfile
    job_title: str
    source_file: str = ""
    status: str = "analyzed"
    recruitment_id: Optional[str] = None
