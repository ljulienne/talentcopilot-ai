# 04 — CandidateDecisionProfile

## Purpose

`CandidateDecisionProfile` is the future central object of TalentCopilot.

It represents the complete decision intelligence profile of a candidate for a specific recruitment.

## Why it matters

Today, different workspaces may derive candidate information independently.

In the target architecture, intelligence is calculated once and reused everywhere.

## High-level structure

```text
CandidateDecisionProfile
│
├── Candidate Identity
├── Recruitment Context
├── Evidence Intelligence
├── Fit Intelligence
├── Competency Intelligence
├── Risk Intelligence
├── Budget Intelligence
├── Interview Intelligence
├── Confidence Intelligence
├── Recommendation Intelligence
├── Executive Intelligence
└── Decision Trace
```

## Design rule

A workspace reads from `CandidateDecisionProfile`.

A workspace does not recalculate Fit, Risk, Budget, Confidence or Recommendation.

## Future consumers

- Candidate Workspace
- Comparison Workspace
- Interview Workspace
- Hiring Budget Workspace
- Decision Board
- Executive Reporting
- Analytics Dashboard
- Talent Locator
- Market Intelligence
