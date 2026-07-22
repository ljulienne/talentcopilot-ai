# Release 7.4.0 Lot 1 — Recruitment UX Audit

## Executive diagnosis

The recruitment engines are materially stronger than the current experience used to access them. The principal UX debt is structural rather than analytical: the application exposes many dense views, repeats decision content across workspaces, and relies on sidebar navigation rather than a guided recruitment flow.

## Observed current-state issues

### 1. Navigation does not mirror the recruitment journey

The primary shell groups pages into Start, Diagnose, Decide and Explore. Candidate Intelligence and Interview Intelligence are placed under Explore, while Comparison and Decision Board remain legacy routes. This makes the most important recruitment sequence difficult to discover.

### 2. Recruitment Workspace is both cockpit and container

The routed Recruitment Workspace delegates to a mission workspace that can render overview, candidate, comparison, interview, decision, advisor and reporting content. This concentrates too many responsibilities in one destination and reproduces content that also exists on dedicated pages.

### 3. Excessive tabs and vertical depth

Candidate Intelligence exposes six tabs after several decision summaries. Interview views expose four to seven tabs. The mission workspace adds another layer of views and nested tabs. Users must scan long pages before reaching the action that advances the process.

### 4. Repeated information

Recommendation, match score, evidence, risks, interview priorities and next actions appear in multiple workspaces. Repetition makes it unclear which screen is authoritative and increases the risk of future inconsistency.

### 5. Weak contextual transitions

The code supports queued navigation requests, but recruitment pages rarely expose a single contextual primary action. Candidate and recruitment context can be preserved in session state, yet transitions do not consistently transport the selected candidate and workflow stage.

### 6. Visual hierarchy is analysis-first rather than decision-first

Long narrative sections and data tables dominate. Status, progress, readiness, material risks and the next action should be visible before detailed reasoning.

## Current page responsibility findings

| Current destination | Current responsibility | UX issue |
|---|---|---|
| Recruitment Workspace | Overview plus embedded candidate, comparison, interview, decision and reporting views | Overloaded container |
| Candidate Intelligence | Recommendation, score explanation, advisor, decision center, skills, matrix, evidence, risks, interview focus | Too much content before and inside six tabs |
| Interview Intelligence | Readiness, playbook, live evaluation and scorecard | Valuable scope, but candidate summary is repeated |
| Comparison | Ranking, gaps, matrix and differentiators | Hidden as a legacy route |
| Decision Board | Decision evidence and actions | Hidden as a legacy route and separated from comparison |

## Target information architecture

### Recruitment Workspace

Owns workflow progress, shortlist state, operational alerts and the next recommended action. It shows compact previews of candidate and interview status, never full candidate reasoning.

### Candidate Intelligence

Owns the candidate recommendation, competency matrix, detailed evidence and material risks. Target views: Summary, Competencies, Evidence & Risks, Interview Plan.

### Interview Intelligence

Owns preparation, questions, note capture, competency validation and interview assessment. Candidate information is limited to a compact context header.

### Comparison & Decision

Owns finalist comparison and the final decision record. Comparison and decision may remain separate technical routes initially, but should behave as one consecutive stage.

## Duplication rule

One information type has one authoritative home. Other pages may show a one-line preview and a contextual link, but must not reproduce the full content.

## Recommended migration sequence

1. Introduce a workflow shell and persistent recruitment context.
2. Add page-level primary and secondary actions.
3. Redesign Recruitment Workspace as a compact cockpit.
4. Consolidate Candidate Intelligence into four views.
5. Connect Interview Intelligence to saved candidate context and competency validation.
6. Expose Comparison and Decision as visible consecutive stages.
7. Apply the premium visual system after responsibilities and transitions are stable.

## Guardrails

- Do not alter matching scores, ranks, identities or recommendation logic.
- Do not create a second source of truth for workflow state.
- Do not add visualizations without a decision purpose.
- Do not hide critical uncertainty behind decorative indicators.
- Preserve legacy routes during migration, using aliases where necessary.
