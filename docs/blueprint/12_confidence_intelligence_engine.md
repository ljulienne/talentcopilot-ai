# 12 — Confidence Intelligence Engine

## Purpose

Confidence Intelligence measures how reliable the AI analysis is.

It answers:

> How certain can we be about this candidate analysis?

## Important distinction

Confidence is not Fit.

A candidate can have:

- high fit and high confidence;
- high fit and low confidence;
- low fit and high confidence;
- low fit and low confidence.

## Inputs

- Evidence Intelligence Report
- Fit Intelligence Report
- Risk Intelligence Report
- Optional Budget Intelligence Report
- Decision Trace

## Outputs

- Confidence Score
- Confidence Level
- Confidence Drivers
- Confidence Gaps
- Decision Quality Signal

## Design rules

1. Confidence does not modify Fit Score.
2. Confidence affects recommendation wording.
3. Low confidence should trigger validation, not automatic rejection.
4. Confidence must be explainable.
