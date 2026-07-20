# Release 6.2C — Decision Ranking Activation

## Purpose
Activate a distinct, evidence-grounded interview-priority ranking while preserving Mission Fit as the official objective matching score.

## Changes
- Adds `DecisionRankingPolicy` v1.1.
- Gives material weight to recent-role alignment, domain persistence, career drift, seniority alignment and transferability.
- Applies transparent alignment adjustments only when Career Intelligence identifies evidence-backed blockers.
- Publishes the decision-policy breakdown and blockers in candidate metadata.
- Uses the exact decision score when creating the official recruitment session.
- Orders official recruitment consumers by `interview_priority` while retaining `mission_fit_rank` separately.

## Guardrails
- No candidate-name rules.
- Mission Fit is never overwritten.
- Decision ranking is deterministic and evidence-grounded.
