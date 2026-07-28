# TalentCopilot-AI — Release 7.5.0

## Visual Recruitment Command Center & Guided Navigation

Validated base release: `7.4.2-radar-visibility-bilingual-star`

### Product changes

- A new **Recruitment Overview** page becomes the visual entry point after candidate analysis.
- Five decision-oriented visuals replace long text-first summaries:
  - candidate ranking;
  - talent-pool fit distribution;
  - candidate-by-competency heatmap;
  - role-requirement coverage across the pool;
  - interview assessment progress.
- The dashboard supports three clearly separated perspectives:
  - official role fit;
  - pre-interview competency alignment;
  - post-interview competency alignment.
- Post-interview visuals use the versioned competency matrices saved by Interview Intelligence.
- The workflow shell now groups nine technical states into four recruiter-facing stages:
  - Analyze;
  - Review candidates;
  - Interview;
  - Compare & decide.
- The primary action from Recruitment Workspace opens the visual overview once analysis is complete.
- Candidate selection from the overview is preserved across Candidate Intelligence and Interview Intelligence.
- Contextual guidance recommends the next action from the actual workflow state.
- Detailed explanations remain available on demand instead of being displayed by default.

### Governance guardrails

Release 7.5.0 never recalculates or overwrites:

- official Mission Fit;
- official candidate rank;
- canonical AI confidence;
- the pre-interview competency estimate;
- the saved post-interview competency matrix.

The new competency-alignment indicators are explicitly labelled as advisory visual indicators. They compare candidate levels with job-required levels and remain separate from the official matching score.

### Visual limits

- Candidate ranking is limited to the ten leading candidates on the chart.
- The comparison heatmap displays up to six candidates and nine competencies for readability.
- All candidates and competencies remain available in the detailed workspaces and underlying data.
