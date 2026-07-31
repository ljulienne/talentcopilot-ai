# Release 8.7.0 — Recruitment Action Center

## Purpose

Turn cross-project portfolio signals into accountable operational follow-up without changing the candidate decision source of truth.

## Added

- One deterministic action per non-archived recruitment project.
- Persistent execution statuses: Open, In progress and Done.
- Stable action identifiers based on the project, action category and recommended action.
- Search and filters by status, severity and owner.
- Direct opening of the recruitment project concerned by an action.
- Status actor and update timestamp for operational traceability.
- Direct transition from the Analytics attention queue to the Action Center.

## Guardrails

- Completing an action does not suppress the underlying portfolio alert.
- Action status is stored only in project-management metadata.
- Candidate identities, evidence, interviews, compensation, scores and ranks are not recalculated or altered.
- Unsaved active projects must be saved before their action status can be persisted.
- No deadlines or recruiter-capacity assumptions are invented.
