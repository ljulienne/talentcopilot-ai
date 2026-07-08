# 21 — Job Intelligence Foundation

## Purpose

Job Intelligence converts job descriptions into structured role requirements.

It is the role-side equivalent of Document Intelligence.

## Pipeline

```text
Job Description
    ↓
Document Loader
    ↓
Text Cleaner
    ↓
Language Detection
    ↓
Job Section Segmentation
    ↓
AI Structured Extraction
    ↓
RoleProfile
    ↓
Decision Core RoleRequirements
```

## Outputs

- RoleProfile
- required skills
- preferred skills
- minimum years of experience
- responsibilities
- languages
- certifications
- budget assumptions if present

## Design rules

1. Job Intelligence extracts requirements.
2. It does not score candidates.
3. It must produce data consumable by Decision Core.
4. It should preserve raw excerpts for explainability.
