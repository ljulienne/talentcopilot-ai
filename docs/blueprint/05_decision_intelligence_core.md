# 05 — Decision Intelligence Core

## Purpose

The Decision Intelligence Core is the analytical engine of TalentCopilot.

It converts evidence into explainable hiring recommendations.

## Core engines

1. Evidence Intelligence
2. Fit Intelligence
3. Competency Intelligence
4. Risk Intelligence
5. Budget Intelligence
6. Interview Intelligence
7. Confidence Intelligence
8. Recommendation Intelligence
9. Executive Intelligence
10. Decision Trace

## Engine independence

Each engine must remain independent.

The Budget Engine does not modify Fit Score.  
The Risk Engine does not modify Evidence Score.  
The Recommendation Engine combines outputs.

## Example

```text
Fit Score: 92
Budget Fit: 42
Risk: Medium
Confidence: 91

Recommendation:
Review Compensation Feasibility
```

This is better than incorrectly rejecting a strong candidate because of budget.
