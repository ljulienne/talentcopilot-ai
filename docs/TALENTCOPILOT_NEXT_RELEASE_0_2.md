# TalentCopilot Next — Release 0.2

## Knowledge Concentration Engine

Release 0.2 introduces the first reusable Organization Intelligence diagnostic.

### Business question

Where is critical knowledge dangerously concentrated, and what should the organization do next?

### Inputs

CSV or Excel employee/skills exports. Required columns: `name`, `department`, `skills`.

Optional columns improve the diagnosis: `critical_skills`, `backup_for`, `retirement_risk`, `documentation_level`, `role`, `manager`, `employee_id`.

### Outputs

- Explainable Knowledge Risk Score per skill.
- High, medium and low risk classification.
- Evidence: holder count, backups, retirement exposure, documentation and departmental concentration.
- Recommended actions.
- Executive Brief.
- CSV export of the diagnosis.

### Design principle

TalentCopilot does not become an HRIS. It analyzes exports and transforms them into decision intelligence.
