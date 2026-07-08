# 09 — Fit Intelligence Engine

## Purpose

Fit Intelligence evaluates how well a candidate matches a role.

It answers:

> Does this candidate fit the job requirements?

## Inputs

- Evidence Graph
- Evidence Intelligence Report
- Role requirements
- Required skills
- Preferred skills
- Minimum experience

## Outputs

- Fit Score
- Skill Match Score
- Experience Match Score
- Achievement Signal Score
- Fit Drivers
- Fit Gaps
- Explanation

## Design rules

1. Fit Intelligence measures fit only.
2. Budget must not change Fit Score.
3. Risk must not change Fit Score.
4. Low evidence quality may lower confidence, but not hide the raw fit signal.
5. Every Fit Driver and Fit Gap must reference evidence where possible.

## Example

```text
Required skills:
- Project Management
- Stakeholder Management
- HRIS

Candidate evidence:
- Project Management
- Stakeholder Management

Fit Gap:
- HRIS not evidenced
```
