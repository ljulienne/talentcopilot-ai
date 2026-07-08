# ADR-015 — AI Platform Core before Document Intelligence

## Status

Accepted

## Context

Document Intelligence, Job Intelligence and Talent Locator will all need LLM calls.

If each feature calls models independently, the system becomes hard to monitor and maintain.

## Decision

Introduce AI Platform Core before implementing real document extraction.

## Consequences

- LLM usage becomes centralized.
- Prompt versions are traceable.
- Cost and latency can be monitored.
- Future model switching becomes easier.
