# TalentCopilot-AI — Release 3.0.1

## Candidate Score & Ranking Consistency

Release 3.0.1 establishes a single official score and ranking flow for the Release 3 recruitment session.

### Fixed

- Added stable `candidate_id` support to session candidates and analyses.
- Candidate Workspace now joins candidates and analyses by ID before using name fallback.
- Candidate Intelligence continues to preserve the official session score without recalculation.
- Corrected legacy score fallback logic so a valid `0` is never replaced by another score.
- Legacy session results are now ranked deterministically by score.
- Added deterministic tie-breaking for the official Release 3 ranking.

### Improved

- The lightweight Enterprise Pipeline now distinguishes:
  - exact required-skill evidence;
  - transferable capability evidence;
  - mission-context relevance;
  - experience readiness.
- Partial but relevant evidence can produce a low, explainable score instead of an unjustified zero.
- Each analysis exposes a `score_breakdown` for future explainability features.

### Product guardrail

A zero score remains possible when no relevant or transferable evidence exists. Release 3.0.1 does not apply an artificial minimum score.
