# 24 — Real Upload Workspace

## Purpose

Real Upload Workspace is the first UI that accepts real files instead of pasted text.

It bridges real user documents to the Real Ranking Pipeline.

## Flow

```text
Job file upload
        ↓
DocumentLoader
        ↓
Job Intelligence
        ↓
RoleProfile

Candidate file uploads
        ↓
DocumentLoader
        ↓
Document Intelligence
        ↓
Real Ranking Pipeline
        ↓
CandidateDecisionProfiles
```

## Design rules

1. Uploaded files are converted to text before analysis.
2. The UI does not score candidates.
3. Real Ranking consumes the extracted text.
4. OCR is out of scope for this package and will be added later.
