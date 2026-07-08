# 13 — Recommendation Intelligence Engine

## Purpose

Recommendation Intelligence converts multiple intelligence signals into a clear next action.

It answers:

> What should the hiring team do next, and why?

## Inputs

- Fit Intelligence
- Evidence Intelligence
- Risk Intelligence
- Budget Intelligence
- Confidence Intelligence

## Outputs

- Recommendation
- Recommendation Category
- Rationale
- Decision Blocking Factors
- Next Actions

## Recommendation levels

- Strong Hire
- Hire
- Interview
- Review Compensation Feasibility
- More Evidence Required
- Review
- Reject

## Design rules

1. A candidate with very low fit must be rejected.
2. Budget cannot rescue a no-fit candidate.
3. High fit with low budget fit triggers compensation review.
4. High fit with low confidence triggers more evidence required.
5. High risk prevents strong hire unless mitigated.
6. Recommendation must be explainable.
