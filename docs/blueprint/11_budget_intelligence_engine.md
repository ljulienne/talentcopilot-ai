# 11 — Budget Intelligence Engine

## Purpose

Budget Intelligence evaluates the financial feasibility of hiring a candidate.

It answers:

> Can we realistically afford this candidate?

## Inputs

- Candidate expected salary
- Target salary
- Maximum salary
- Relocation budget
- Signing bonus
- Visa sponsorship cost
- Fit Score, for contextual recommendation only

## Outputs

- Budget Fit
- Salary Gap
- Cost Impact
- Financial Feasibility
- Budget Recommendation
- Mitigation Actions

## Design rules

1. Budget Fit does not modify Fit Score.
2. Budget Intelligence does not reject strong candidates automatically.
3. Strong fit + weak budget should become `Review Compensation Feasibility`.
4. Weak fit remains weak even if affordable.
5. Budget outputs must be explainable.

## Example

```text
Fit Score: 92
Budget Fit: 42
Recommendation: Review Compensation Feasibility
```
