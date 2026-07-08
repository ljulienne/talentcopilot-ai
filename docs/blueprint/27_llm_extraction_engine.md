# 27 — LLM Extraction Engine

## Purpose

The LLM Extraction Engine replaces brittle heuristics with structured extraction.

## Inputs

- CV text
- Job description text

## Outputs

- CandidateExtractionResult
- RoleExtractionResult

## Architecture

```text
Document Loader
        ↓
LLM Extraction Engine
        ↓
Pydantic validation
        ↓
Normalized business objects
        ↓
Decision Core
```

## Design rules

1. The LLM extracts data; it does not make hiring decisions.
2. Outputs must be structured and validated.
3. Missing information must remain missing.
4. Fallback must be available when API calls fail.
5. Decision Core remains responsible for scores and recommendations.
