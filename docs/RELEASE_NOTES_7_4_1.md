# TalentCopilot-AI — Release 7.4.1

## Role-Aligned Competency Radar & Post-Interview Assessment

Base snapshot: `54e1e9185981282fd9f9733a5f1eacce3d86d531`

### Product changes

- The main competency radar now uses only competencies required by the active job description.
- The radar compares the fixed role expectation with the candidate's pre-interview AI estimate derived from CV evidence.
- Candidate Intelligence presents the matrix as a read-only pre-interview decision-support view.
- Interview Intelligence is the only place where an evaluator can adjust candidate levels and validation statuses.
- Evaluators can add competencies discovered during the interview, rename them, remove them from the active radar and restore them.
- Job requirements cannot be deleted during the interview.
- Candidate answers, evaluator notes, validation status and human levels are persisted.
- Finalization creates a versioned post-interview competency radar and keeps a complete audit trail.

### Governance guardrails

The competency radar never recalculates or overwrites:

- official Mission Fit;
- official candidate rank;
- canonical AI confidence;
- the original CV-based competency estimate.

### Persistence

Current matrices are stored in:

`.talentcopilot_data/competency_matrices/`

Version history is stored in:

`.talentcopilot_data/competency_matrices/history/`
