# Release 8.0.1 — Decision Ranking Consistency Hotfix

## Base

- Release: `8.0.0-premium-unified-experience`
- Commit: `c19055e7f9fe752658d86752ae9aef5f6668896b`

## Fixed

Decision Board previously displayed `decision_rank` as the candidate's official recruitment rank. This could show Louis Julienne as rank #2 while Dashboard Perspective, Candidate Intelligence, Interview and Compare & Decide correctly displayed rank #1.

The hotfix now:

- reads the canonical candidate record from Recruitment Source of Truth;
- displays `mission_rank` as the official recruitment rank;
- keeps `decision_rank` and `interview_priority` available as separate internal decision signals;
- resolves candidates by immutable candidate ID rather than display name;
- uses the same rank in the selector and the candidate summary card.

## Preserved

No official score is recalculated. Evidence, interview assessments, compensation data, workflow state, recommendations and PDF reports remain unchanged.
