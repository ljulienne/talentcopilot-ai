# 10 — Risk Intelligence Engine

## Purpose

Risk Intelligence identifies risks that may affect the hiring decision.

It answers:

> What could make this hiring decision unsafe, premature or difficult?

## Inputs

- Evidence Intelligence Report
- Fit Intelligence Report
- Role requirements
- Evidence Graph

## Outputs

- Risk Score
- Risk Level
- Risk Factors
- Mitigation Actions
- Summary

## Design rules

1. Risk Intelligence does not modify Fit Score.
2. A risk is not automatically a rejection.
3. A high-fit candidate can still have high risk.
4. A low-fit candidate can have low operational risk but still not be recommended.
5. Every risk must be actionable where possible.

## Example

```text
Fit: 88
Risk: Medium
Reason: Critical skill not fully evidenced
Mitigation: Validate during structured interview
```
