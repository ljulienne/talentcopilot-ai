# ADR-022 — LLM Extraction Engine

## Status

Accepted

## Context

Heuristic extraction fails on real CV layouts and headers.

Examples include candidate names being confused with section titles.

## Decision

Introduce a structured LLM extraction engine with Pydantic models.

## Consequences

- CV parsing quality improves.
- Job parsing quality improves.
- Decision Core receives richer structured inputs.
- Fallback extraction remains available for demo and offline testing.
