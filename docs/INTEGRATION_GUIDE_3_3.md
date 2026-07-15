# Release 3.3 Integration Guide

The recruiter sees only Official Match, AI Confidence and Official Rank.

- Modern `fit_score` is persisted as `CandidateAnalysisState.match_score`.
- Modern confidence is persisted in `score_breakdown["confidence"]`.
- `CandidateAnalysisState.official_confidence_score` exposes that confidence.
- Candidate Intelligence and Comparison consume the same session values.

No scoring formula changes are included. Candidate identity extraction is handled separately in Release 3.3.1.
