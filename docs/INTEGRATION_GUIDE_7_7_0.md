# Integration Guide — Release 7.7.0

## Required base

- Release: `7.6.0-technical-requirement-intelligence`
- Commit: `3b63a3314700b5d4ccece7d8a415bcbbd64ef4f5`
- Branch: `main`

## Runtime flow

1. `RecruitmentUploadSessionService` sends the raw offer and detected role title to `TechnicalRequirementService` after official scoring is complete.
2. `DomainAgnosticRequirementExtractor` builds grounded deterministic requirements from exact names, explicit requirement cues and cross-domain capability patterns.
3. In `auto` mode, an OpenAI structured extraction can enrich the result when an API key is available. Ungrounded entries are discarded.
4. The final catalogue and extraction method are stored in the recruitment job session.
5. `CompetencyMatrixService`, `RecruitmentOverviewService`, `InterviewWorkspaceService` and `InterviewQuestionService` consume the same ordered catalogue.
6. Candidate evidence is evaluated as direct, ambiguous, related or absent using exact terms, surrounding action evidence and dynamically inferred requirement families.
7. Official scores and ranks remain immutable.

## Runtime modes

Set `TALENTCOPILOT_REQUIREMENT_MODE` to one of:

- `auto` — deterministic baseline plus grounded LLM enrichment when `OPENAI_API_KEY` is available;
- `deterministic` — offline deterministic extraction only;
- `llm` — attempts enrichment, with deterministic fallback if the model call fails.

`auto` is the default.

## Migration

A job session whose embedded requirement engine version starts with `7.7` reuses its stored catalogue. Older catalogues are regenerated from the raw offer to remove previous domain-specific assumptions.

Existing candidate competency matrices retain interview-added competencies and audit history. Job requirements no longer present are deactivated rather than deleted.

## Verification

Run:

```bash
PYTHONPATH=. TALENTCOPILOT_REQUIREMENT_MODE=deterministic pytest -q
```

The full suite should pass. The 7.7 benchmark specifically verifies software, finance, sales, supply chain, marketing and HRIS offers.

After deployment, test at least one previously unseen role and confirm:

- exact technologies from the offer appear in the radar and heatmap;
- unrelated HRIS axes do not appear;
- languages and experience conditions remain eligibility checks;
- missing or transferable technical experience generates targeted interview questions;
- dashboard coverage continues to equal the average of heatmap values;
- official scores and ranks are unchanged.
