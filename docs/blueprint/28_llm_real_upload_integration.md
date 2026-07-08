# 28 — LLM Real Upload Integration

## Purpose

This sprint connects structured LLM extraction to real uploaded documents.

## Flow

```text
Uploaded CV
    ↓
Text extraction
    ↓
LLM CandidateExtractionResult
    ↓
Candidate dict adapter
    ↓
DecisionCoreInput

Uploaded Job Description
    ↓
Text extraction
    ↓
LLM RoleExtractionResult
    ↓
DecisionCoreInput
```

## Design rules

1. LLM extraction replaces heuristics when enabled.
2. Fallback remains available.
3. Decision Core remains the only scoring layer.
4. UI must show extraction mode and structured extraction outputs.
