# ADR-005 — Recruiter Copilot v2

## Status

Accepted

## Context

The Decision Intelligence layer produces a structured hiring recommendation. Recruiters still need practical guidance to act on it:

- what to do next;
- what to ask during interviews;
- what concerns to validate;
- how to summarize the candidate for stakeholders.

## Decision

Create a deterministic `RecruiterCopilotEngine` that consumes `DecisionReport` and produces a `RecruiterCopilotReport`.

The engine is independent from LLM calls and can be rendered in Streamlit.

## Consequences

Positive:

- makes TalentCopilot more action-oriented;
- reduces recruiter cognitive load;
- prepares future conversational copilot features;
- supports interview planning and hiring committee summaries.

Trade-offs:

- introduces another output layer;
- final UI integration remains optional until the Decision Workspace is updated.
