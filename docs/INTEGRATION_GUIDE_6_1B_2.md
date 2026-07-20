# Integration Guide — Release 6.1B.2

The real ranking pipeline now builds candidate and mission evidence profiles, runs Career Intelligence, and computes a recommended interview-priority score.

Metadata keys:
- `career_intelligence`
- `career_fit_score`
- `career_fit_confidence`
- `career_summary`
- `career_strengths`
- `career_concerns`
- `career_interview_focus`
- `decision_ranking_contract`
- `decision_score`
- `mission_fit_rank`
- `decision_rank`

`fit_score` remains the calibrated Mission Fit score. `rank` is the recommended decision priority. The original analytical order remains available through `mission_fit_rank`.
