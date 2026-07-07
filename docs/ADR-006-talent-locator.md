# ADR-006 — Talent Locator

## Status

Accepted

## Context

TalentCopilot needs to evolve from candidate-by-candidate analysis to proactive talent discovery.

The first safe and maintainable step is internal talent pool search. External sources require later connector-specific work, legal review and consent-aware design.

## Decision

Create a deterministic `TalentLocatorEngine` that ranks candidates from a provided talent pool using:

- skills overlap,
- keyword match,
- evidence hints,
- seniority hints,
- explainable locator reasons.

## Consequences

Positive:

- supports proactive sourcing;
- remains compliant by avoiding unauthorized scraping;
- creates a connector-ready abstraction for future integrations.

Trade-offs:

- semantic embeddings are not yet included;
- external search is intentionally out of scope for this sprint.
