# ADR-001 — Blueprint-first architecture

## Status

Accepted

## Context

TalentCopilot has reached a point where adding more UI without a reference architecture would increase inconsistency.

## Decision

Before implementing Decision Intelligence Core v2, TalentCopilot will define an Enterprise Blueprint.

## Consequences

- Future development will follow documented architecture.
- Workspaces will become consumers of central intelligence objects.
- Decision logic will be moved out of UI pages and into engines.
