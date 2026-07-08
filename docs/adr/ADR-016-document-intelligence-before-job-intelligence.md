# ADR-016 — Document Intelligence before Job Intelligence

## Status

Accepted

## Context

TalentCopilot must start consuming real documents.

CV analysis is the most visible and valuable first real-data use case.

## Decision

Implement Document Intelligence foundation before Job Intelligence.

## Consequences

- Candidate extraction can be tested immediately.
- The AI Platform Core starts being used by a real feature.
- Future CV-to-DecisionCore integration becomes easier.
