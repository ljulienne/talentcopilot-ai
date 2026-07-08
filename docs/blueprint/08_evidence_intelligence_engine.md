# 08 — Evidence Intelligence Engine

## Purpose

Evidence Intelligence evaluates the quality, coverage and reliability of candidate evidence.

It does not decide whether a candidate is good or bad.

It answers:

> Is the available evidence strong enough to support a hiring decision?

## Outputs

- Evidence Quality Score
- Evidence Coverage Score
- Evidence Reliability Score
- Evidence Density
- Evidence Strengths
- Evidence Gaps
- Evidence Readiness

## Design rules

1. Evidence Intelligence does not produce final hiring recommendations.
2. Evidence Intelligence does not modify Fit Score directly.
3. Low evidence quality should reduce confidence, not automatically reject the candidate.
4. Every gap should be explicit and actionable.

## Example

A candidate with a strong fit but weak evidence should become:

```text
Fit: High
Evidence Quality: Low
Confidence: Low
Recommendation: Interview — More evidence required
```

Not:

```text
Reject
```
