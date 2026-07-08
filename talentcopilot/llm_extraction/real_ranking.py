from dataclasses import dataclass, field
from typing import List

from talentcopilot.llm_extraction.real_matching import LLMRealMatchingInput, LLMRealMatchingOutput, LLMRealMatchingPipeline


@dataclass
class LLMCandidateTextInput:
    filename: str
    text: str
    expected_salary: float | None = None


@dataclass
class LLMRealRankingInput:
    job_filename: str
    job_text: str
    candidates: List[LLMCandidateTextInput] = field(default_factory=list)


@dataclass
class LLMRankedCandidate:
    rank: int
    candidate_name: str
    recommendation: str
    fit_score: int
    confidence_score: int
    risk_level: str
    ranking_score: int
    matching_output: LLMRealMatchingOutput


@dataclass
class LLMRealRankingOutput:
    role_title: str
    total_candidates: int
    ranked_candidates: List[LLMRankedCandidate] = field(default_factory=list)


class LLMRealRankingPipeline:
    RECOMMENDATION_WEIGHT = {
        "Strong Hire": 100,
        "Hire": 90,
        "Interview": 72,
        "Review Compensation Feasibility": 68,
        "More Evidence Required": 55,
        "Review": 45,
        "Reject": 0,
    }

    RISK_PENALTY = {
        "Low": 0,
        "Medium": 8,
        "High": 18,
        "Critical": 35,
    }

    def run(self, data: LLMRealRankingInput) -> LLMRealRankingOutput:
        matches = []
        for candidate in data.candidates:
            matches.append(
                LLMRealMatchingPipeline().run(
                    LLMRealMatchingInput(
                        candidate_filename=candidate.filename,
                        candidate_text=candidate.text,
                        job_filename=data.job_filename,
                        job_text=data.job_text,
                        expected_salary=candidate.expected_salary,
                    )
                )
            )

        ranked = []
        for match in matches:
            profile = match.decision_output.profile
            score = self._ranking_score(profile)
            ranked.append(
                LLMRankedCandidate(
                    rank=0,
                    candidate_name=profile.candidate_name,
                    recommendation=profile.recommendation or "No recommendation",
                    fit_score=int(profile.fit_score or 0),
                    confidence_score=int(profile.confidence_score or 0),
                    risk_level=profile.risk_level or "Unknown",
                    ranking_score=score,
                    matching_output=match,
                )
            )

        ranked.sort(key=lambda item: item.ranking_score, reverse=True)
        for index, item in enumerate(ranked, start=1):
            item.rank = index

        role_title = matches[0].role_extraction.facts.title if matches else "Unknown Role"
        return LLMRealRankingOutput(
            role_title=role_title,
            total_candidates=len(data.candidates),
            ranked_candidates=ranked,
        )

    def _ranking_score(self, profile) -> int:
        rec_score = self.RECOMMENDATION_WEIGHT.get(profile.recommendation or "Review", 40)
        fit = int(profile.fit_score or 0)
        confidence = int(profile.confidence_score or 0)
        risk_penalty = self.RISK_PENALTY.get(profile.risk_level or "Medium", 10)

        score = int(rec_score * 0.4 + fit * 0.4 + confidence * 0.2 - risk_penalty)
        return max(0, min(100, score))
