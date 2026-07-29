# Release 7.8.2 — Candidate Insight Grounding

## Purpose

Correct the Dashboard Perspective regression where the first role requirement could be displayed as both **Strongest area** and **Primary risk** for every candidate.

## Changes

- Candidate strengths are now selected from candidate-specific, evidence-ranked capabilities instead of the first competency in the role matrix.
- Primary risks are now selected from candidate-specific, severity-ranked Candidate Intelligence risks.
- Strength and risk are selected independently from candidate evidence; the dashboard no longer duplicates a raw first-requirement fallback.
- If evidence does not differentiate a strength, the product states `No differentiated strength established` rather than inventing one.
- If no material risk is established, the product states `No critical risk identified`.
- Dashboard PDF exports use the same grounded strength and risk fields as the visual cards.
- Official match scores, official ranks, evidence confidence and interview assessments remain unchanged.

## Root cause

Release 7.8.1 displayed `competency_scores_[pre|post][0]` and `critical_gaps[0]`. Both collections preserve role-definition order, so the first requirement — SAP SuccessFactors in the reported mission — could be reused across every candidate regardless of individual evidence.
