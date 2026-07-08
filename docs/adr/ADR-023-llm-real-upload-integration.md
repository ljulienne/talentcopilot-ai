# ADR-023 — LLM Real Upload Integration

## Status

Accepted

## Context

Real Upload previously relied on local extraction and heuristics.

This caused incorrect candidate names and weak real-world parsing.

## Decision

Add a dedicated LLM-compatible real upload and ranking pipeline.

## Consequences

- Real uploaded CVs are analyzed with structured extraction.
- The previous Real Upload remains available.
- The new page enables quality testing before replacing the old workflow.
