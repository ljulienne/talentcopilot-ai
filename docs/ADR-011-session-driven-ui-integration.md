# ADR-011 — Session-Driven UI Integration

## Status
Accepted

## Context

TalentCopilot has multiple AI engines and many Streamlit pages, but pages were not consistently reading from the same `RecruitmentSession`.

## Decision

Introduce a demo session factory and strengthen `SessionStore` so UI pages can share the same `RecruitmentSession` through Streamlit session state.

## Consequences

Positive:
- pages become coherent;
- demo workflow becomes easier;
- a user can launch one session and see it reflected across pages.

Trade-off:
- this is still a demo-level integration; later sprints should integrate real CV upload parsing into the same pipeline.
