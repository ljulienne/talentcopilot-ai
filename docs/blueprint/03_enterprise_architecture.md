# 03 — Enterprise Architecture

## Target architecture

TalentCopilot should evolve toward three layers:

```text
Product Blueprint
        ↓
Decision Intelligence Core
        ↓
User Workspaces
```

## Layer 1 — Product Blueprint

The Blueprint defines:

- product vision;
- domain model;
- principles;
- business rules;
- recommendation framework;
- score definitions;
- audit rules;
- roadmap.

## Layer 2 — Decision Intelligence Core

The Decision Intelligence Core calculates:

- Fit Intelligence;
- Evidence Intelligence;
- Competency Intelligence;
- Risk Intelligence;
- Budget Intelligence;
- Confidence Intelligence;
- Recommendation Intelligence;
- Executive Intelligence.

## Layer 3 — User Workspaces

Workspaces display outputs from the Decision Intelligence Core.

They should not contain core business scoring logic.

## Target data flow

```text
Job Description
        ↓
Candidate Data
        ↓
Evidence Extraction
        ↓
CandidateDecisionProfile
        ↓
Decision Intelligence Core
        ↓
Workspaces
        ↓
Decision Trace
```

## Key architecture rule

The UI must not be the source of truth.

The future source of truth is:

```text
CandidateDecisionProfile
```
