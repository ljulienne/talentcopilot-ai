# Integration Guide — Release 7.6.0

## Required base

- Release: `7.5.0-visual-recruitment-command-center`
- Commit: `7176e239960da6f397283729077fc4d6e3520967`
- Branch: `main`

## Runtime flow

1. `RecruitmentUploadSessionService` stores a structured `technical_requirements` catalog in the job session after the official ranking has already been computed.
2. `TechnicalRequirementService` preserves exact technologies and classifies candidate evidence as direct, related, or absent.
3. `CompetencyMatrixService` uses the catalog as the role-aligned radar source of truth.
4. `InterviewWorkspaceService` and `InterviewQuestionService` consume the same requirements and candidate evidence statuses.
5. `RecruitmentOverviewService` reads the same candidate matrices for the heatmap and pool-alignment visual.
6. Interview ratings remain versioned separately from the immutable pre-interview estimate and official role-fit score.

## Persistence and migration

When an existing matrix is loaded:

- new exact job requirements are added;
- old job requirements no longer present are deactivated, not deleted;
- interview-added competencies are preserved;
- existing human ratings remain in the audit history;
- official scores and ranks are never changed.

## Verification

After deployment, upload `offre_hris.pdf` and the four test CVs. Confirm that the radar and heatmap include exact axes such as:

- SAP SuccessFactors & Core HR
- Power BI & HR Reporting
- AI Solutions for HR
- Interfaces & Technical Delivery
- Data Quality & Core HR Reliability

For Louis Julienne, confirm that the generated interview playbook asks targeted questions about SuccessFactors and AI, while recognizing Power BI as existing evidence that requires depth validation.
