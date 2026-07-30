# TalentCopilot-AI 8.3.0 — Candidate Decision Workspace

## Purpose

Release 8.3.0 consolidates the candidate decision journey without creating a
second score or ranking. Candidate Intelligence now connects the immutable
pre-interview result with interview evidence, compensation and availability,
and the final human decision.

## Delivered capabilities

- Consolidated Candidate Decision Workspace in Candidate Intelligence.
- Explicit three-stage decision journey:
  - pre-interview assessment;
  - interview evidence;
  - final human decision.
- Role-requirement table preserving pre- and post-interview levels separately.
- Candidate-specific strengths, risks and interview validation priorities.
- Compensation status, budget signal, expected salary, availability, notice
  period and flexibility displayed separately from Talent Fit.
- Compare & Decide matrix with independent columns for Talent Fit, evidence
  confidence, critical risk, interview assessment, compensation fit,
  availability and final recommendation.
- Final-decision audit trail with owner, timestamp, rationale, decisive evidence
  and consciously accepted or conditionally managed risks.
- Candidate and comparison PDF exports sourced from the same consolidated view.
- Candidate Intelligence presentation rank aligned with the canonical
  source-of-truth order; no score or ranking engine was modified.

## Governance

- Official Talent Fit is never recalculated.
- Official candidate order is read from RecruitmentSourceOfTruthService.
- Interview evidence remains a separate layer.
- Compensation and availability never alter Talent Fit.
- Final recommendations remain human-owned and auditable.

## Validation

- Release 8.3.0 targeted tests: passed.
- Releases 8.0.0–8.2.0 and related candidate/workflow/PDF regressions: passed.
- Full suite: 254 tests passed using an offline Streamlit import stub because
  Streamlit is unavailable in the build container.
- The package installer reruns the full suite in the real Colab environment.
