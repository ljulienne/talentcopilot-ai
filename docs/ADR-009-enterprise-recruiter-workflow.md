# ADR-009 — Enterprise Recruiter Workflow

## Status

Accepted

## Context

TalentCopilot now has a central `RecruitmentSession`, but recruiters need a clear workflow showing where the recruitment stands and what should happen next.

## Decision

Create `RecruiterWorkflowEngine`, which derives workflow stages from a recruitment session.

## Consequences

Positive:
- makes the product easier to demo;
- connects AI analysis to recruiter operations;
- prepares future persistence and reporting.

Trade-offs:
- workflow state is currently derived, not fully user-editable.
