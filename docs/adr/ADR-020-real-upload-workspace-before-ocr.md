# ADR-020 — Real Upload Workspace before OCR

## Status

Accepted

## Context

TalentCopilot needs to support real files.

OCR is useful but not required for text PDFs, DOCX and TXT files.

## Decision

Introduce upload workflow before OCR.

## Consequences

- Real documents can be tested immediately.
- OCR can be added later without changing the ranking pipeline.
- The workflow becomes more realistic for demonstrations.
