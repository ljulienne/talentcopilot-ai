# Release 6.1B.2 — Career Intelligence & Decision Ranking

## Added
- Evidence-grounded `CareerIntelligenceEngine`.
- Functional alignment, recent-role alignment, domain persistence, career drift, seniority alignment and transferability.
- `CareerFitReport` with strengths, concerns, summary and interview focus.
- Dual ranking contract: preserved Mission Fit rank plus recommended decision rank.
- Decision score dominated by Mission Fit and refined by Career Intelligence, Recruiter Intelligence and confidence.

## Guardrails
- The calibrated Mission Fit score is never overwritten by Career Intelligence.
- Career conclusions use generic text/evidence signals and never candidate names.
- Both `mission_fit_rank` and `decision_rank` are exposed for transparency.
