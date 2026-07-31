# Integration Guide — Release 8.6.0

## Base

- Expected release: `8.5.0-recruitment-portfolio-lifecycle`
- Expected commit: `fd19965c17730233d0521faac0fda93436c95aab`
- Target release: `8.6.0-recruitment-portfolio-intelligence`

## Main components

- `talentcopilot/models/recruitment_portfolio_intelligence.py`
  - immutable portfolio alert, lifecycle, freshness and owner-load models.
- `talentcopilot/services/recruitment_portfolio_intelligence.py`
  - domain-agnostic operational signals derived from project metadata only.
- `talentcopilot/ui/analytics_dashboard.py`
  - portfolio health, attention queue, owner workload and active-mission tabs.

## Operational logic

The service uses only:

- project lifecycle;
- priority;
- owner;
- candidate count;
- last recorded activity;
- persisted workflow state exposed by the Release 8.5.0 portfolio summaries.

One primary alert is selected per project to avoid competing recommendations. Alert ordering is deterministic: severity, project priority, activity age and project name.

## Source-of-truth protection

The portfolio intelligence service does not load or modify official candidate scores, ranks, evidence, interview assessments, compensation inputs or decision history.

## Post-deployment visual checks

- Open **Analytics** from the sidebar.
- Confirm saved projects appear without requiring an active mission.
- Verify the lifecycle and last-activity tables.
- Confirm each project appears at most once in the Attention queue.
- Verify archived projects are excluded from open-project metrics.
- Confirm the Active mission tab still displays the current recruitment analytics.
- Open Projects from the attention queue and verify all official scores and ranks remain unchanged.
