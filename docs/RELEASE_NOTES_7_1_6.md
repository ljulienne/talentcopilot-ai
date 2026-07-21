# Release 7.1.6 — Narrative Compression & Semantic Variation

## Purpose

Reduce lexical repetition and mechanically assembled prose in Recruitment Workspace narratives without changing official scores, ranks, risks or recommendations.

## Changes

- merges redundant project-management and resource-management atoms into one concise professional phrase;
- preserves specific achievements instead of reducing them to generic taxonomy labels;
- varies wording between Executive Summary and Recruiter Reasoning;
- removes repeated uncertainty lists from consecutive reasoning paragraphs;
- distinguishes evidence questions from established capability gaps;
- adds deterministic lexical-quality checks for forbidden connectors, repeated n-grams and excessive sentence overlap;
- preserves compatibility with Releases 7.1.2 through 7.1.5.

## Example improvement

Before:

> The profile is distinguished by project management, supported by evidence of project-management responsibilities and budget / resource management, supported by evidence of budget and resource responsibilities.

After:

> The profile is distinguished by project management with budget and resource ownership, rather than tenure alone.

Recruiter Reasoning uses a complementary formulation:

> The strongest support comes from project management accountability with budget and resource control.

## Business invariants

This release does not recalculate or modify:

- official match scores;
- official candidate ranks;
- confidence scores;
- recommendations;
- recorded risks.
