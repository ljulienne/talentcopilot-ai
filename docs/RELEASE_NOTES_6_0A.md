# TalentCopilot Release 6.0A — Recruitment Mission Architecture

## Purpose

Release 6.0A replaces the tab-heavy recruitment surface with a mission-centric, single-page workspace while preserving every official score, rank and recommendation produced by the existing engines.

## Delivered

- Pure presentation state built from `RecruitmentSession`.
- Seven decision-led, progressively disclosed mission sections.
- Mission hero, progress, executive metrics and AI guidance.
- Compatibility entry point through the existing `Recruitment Workspace` route.
- No matching, comparative-ranking or calibrated-scoring algorithm changes.

## Non-regression contract

The workspace reads `official_match_score`, `official_rank`, `official_decision_score` and `official_confidence_score` directly from the active session. It does not calculate replacements.
