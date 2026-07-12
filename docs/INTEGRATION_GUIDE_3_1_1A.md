# Integration Guide — Release 3.1.1A

## Official flow

`Uploaded JD + CVs` → `UploadTextReaderService` → `RealUploadRankingService` → `RecruitmentUploadSessionService` → `RecruitmentSession` → all Recruitment modules.

## Source of truth

- Candidate identity: `candidate_id`
- Official score: `CandidateAnalysisState.match_score`
- Official rank: `CandidateAnalysisState.rank`
- Official ordering: `RecruitmentSession.ranked_analyses`

## Important rule

Downstream modules must consume the session. They must not re-run document ranking or reconstruct candidate scores.

## Demo mode

`Load sample data` remains available for presentations, but real uploads are the primary action.
