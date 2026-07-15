# TalentCopilot-AI — Release 3.3

## Official Match UX Simplification

- **Official Match** = `CandidateAnalysisState.match_score` / modern `fit_score`
- **AI Confidence** = canonical `score_breakdown["confidence"]`
- **Official Rank** = persisted session rank

Internal `ranking_score` and `decision_score` remain backend diagnostics and are no longer exposed as competing recruiter-facing scores. The calibration reference confirmed expected Official Match values of 86, 66, 30 and 25. No scoring formula is changed.
