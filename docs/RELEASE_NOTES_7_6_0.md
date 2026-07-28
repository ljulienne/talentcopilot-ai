# TalentCopilot-AI Release 7.6.0

## Technical Requirement Intelligence & Unified Competency Model

This release introduces one deterministic role-requirement catalog shared by the competency radar, interview preparation, Recruitment Overview heatmap, pool alignment chart, and post-interview assessment.

### Main changes

- Preserves exact role requirements such as SAP SuccessFactors, Power BI, applied AI, Core HR, interfaces, acceptance testing, data quality, change adoption, provider management, and team/international leadership.
- Distinguishes direct evidence, related/transferable evidence, and no direct evidence in candidate CVs.
- Generates dedicated interview probes for SAP SuccessFactors, Power BI technical depth, and AI-for-HR governance and delivery.
- Replaces the previous binary 100%-only pool coverage calculation with the average of the exact heatmap alignment values.
- Uses the same ordered requirement catalog for the radar, heatmap, pool overview, interview scorecard, and saved post-interview matrix.
- Migrates prior saved matrices safely: obsolete generic job axes are retained in history but deactivated; interview-added competencies and human assessments remain auditable.
- Does not recalculate or mutate the official role-fit score or official rank.

### Validation on the supplied HRIS test documents

For Louis Julienne, the engine identifies:

- Power BI & HR Reporting: direct evidence; technical ownership and depth to confirm.
- SAP SuccessFactors & Core HR: related HRIS experience, but no direct product evidence; mandatory interview probe.
- AI Solutions for HR: related analytics/data-science background, but no direct deployed AI evidence; transferability and governance probe.
- Interfaces, testing, data quality, change management, project leadership, and international delivery: direct or related evidence depending on the CV excerpt.

### Compatibility

The official score and rank source of truth remains unchanged. The new catalog is an explainable presentation and evaluation layer.
