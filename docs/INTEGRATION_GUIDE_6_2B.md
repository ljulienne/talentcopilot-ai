# Integration Guide — Release 6.2B

Install on top of committed Release 6.2A.

The release extends, without replacing, `RecruitmentSourceOfTruth`.

Canonical fields:
- `mission_fit_score`: objective CV-to-role compatibility.
- `mission_rank`: ordering by Mission Fit.
- `career_fit_score`: trajectory alignment signal.
- `decision_score`: consolidated recommendation signal.
- `interview_priority`: recommended recruiter review order.
- `confidence`: evidence confidence.

Existing sessions without explicit dual-rank metadata remain compatible. New upload sessions preserve both ranks in `CandidateAnalysisState.score_breakdown`.
