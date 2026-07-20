# TalentCopilot-AI Release 7.0 — Recruitment Reasoning Engine

## Scope

Release 7.0 replaces the canonical upload Mission Fit calculation with a generic, evidence-led reasoning layer. The engine decomposes a job description into weighted atomic criteria, assesses direct and transferable CV evidence, applies explicit mandatory-gap controls, and stores a complete criterion-level trace.

## Main changes

- Adds `talentcopilot.recruitment_reasoning` with generic criteria, assessments and trace models.
- Uses direct, transferable and missing-evidence states rather than keyword presence alone.
- Adds generic criteria for implementation, interfaces, testing, data quality, vendor management, budgets, governance, leadership, change, analytics and platform deployment.
- Gives explicitly mandatory requirements more influence without hard-coding any candidate or benchmark.
- Resolves candidate identity before ranking output, preventing company/client names from replacing the candidate name.
- Preserves the historical `mission_fit_engine` and `mission_fit_breakdown` metadata contract for backwards compatibility while adding `recruitment_reasoning_engine`, `recruitment_reasoning_trace` and `recruitment_reasoning_breakdown`.

## Benchmark observation

On the supplied HRIS test set, candidate names are correct and the decision order is Vincent Blakoe, Louis Julienne, Zelma O'Reilly, Loretta Danielson. The benchmark is used only as a regression scenario; no candidate-specific rule or score is present in the engine.
