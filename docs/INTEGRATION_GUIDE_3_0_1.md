# Release 3.0.1 — Integration Guide

## Baseline

This package was prepared from audited snapshot:

- branch: `main`
- commit: `6773ea1e109f35753c299285a114ce0ae99a5cc2`
- label: `Release 3.0 Lot 3 - Candidate Intelligence`

The Colab installer refuses to apply the patch to a different commit unless explicitly overridden.

## Official data flow

```text
EnterprisePipeline
  -> CandidateAnalysisState(candidate_id, match_score, rank, score_breakdown)
  -> RecruitmentSession.ranked_analyses
  -> CandidateWorkspaceService
  -> CandidateIntelligenceService
  -> UI pages
```

## Architectural rules

1. `CandidateAnalysisState.match_score` is the official matching score.
2. `CandidateAnalysisState.rank` is the official rank.
3. Candidate Intelligence may derive confidence, evidence coverage and potential signals, but must not replace `match_score`.
4. Pages must consume `session.ranked_analyses` or reports built directly from it.
5. Candidate joins must use `candidate_id`; name matching is compatibility-only.
6. Never use `a or b` to select numeric scores because zero is valid.

## Files modified

- `talentcopilot/ai/enterprise_pipeline.py`
- `talentcopilot/models/recruitment_session.py`
- `talentcopilot/models/candidate_workspace.py`
- `talentcopilot/services/candidate_identity.py`
- `talentcopilot/services/demo_session_factory.py`
- `talentcopilot/services/candidate_workspace_service.py`
- `talentcopilot/services/session_adapter.py`

## Tests added

- `tests/test_release_3_0_1_consistency.py`
- `tests/test_release_3_0_1_session_adapter.py`

## Validation

Run the complete suite after installation:

```bash
python -m pytest -q
```

Then restart Streamlit and create a fresh demo session. Existing serialized or in-memory sessions should not be used for visual validation.
