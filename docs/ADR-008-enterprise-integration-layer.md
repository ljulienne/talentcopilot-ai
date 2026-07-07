# ADR-008 — Enterprise Integration Layer

## Status

Accepted

## Context

TalentCopilot has multiple AI engines and UI pages. The architecture is powerful but risks fragmentation if each page calls engines independently.

## Decision

Create a central enterprise integration layer based on `RecruitmentSession`.

The session becomes the source of truth for:

- job context,
- candidates,
- candidate analysis states,
- ranking,
- decisions,
- risks,
- recruiter guidance,
- pipeline health.

## Consequences

Positive:

- reduces duplication;
- supports full recruiter workflow;
- improves Streamlit integration;
- prepares reporting and persistence.

Trade-offs:

- adds orchestration complexity;
- existing pages must progressively migrate to the session model.
