# TalentCopilot-AI — Release 3.1.1A

## Recruitment Workflow Restoration

### Added

- Real Job Description upload in the active Recruitment Decision Workspace.
- Multiple CV upload using the existing TXT, text-PDF and DOCX reader.
- Conversion of the existing Real Ranking output into the official `RecruitmentSession`.
- Stable candidate IDs for uploaded candidates.
- Shared official scores and ranks across Recruitment, Candidate Intelligence, Comparison, Interview, Decision and Reports.

### Changed

- Sample data is now a secondary action rather than the primary workflow.
- The active Recruitment Workspace can create or replace the shared recruitment session without visiting a legacy page.

### Architecture

The existing document reader and real ranking pipeline are preserved. The new bridge only normalises their result into the Release 3 session contract. No second matching engine or ranking is introduced.
