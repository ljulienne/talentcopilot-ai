# Release 6.0A.1 — Unified PDF Report Export

Base snapshot: `8ff0915ca7f9090b811346f8055f6943bfafe2a8`

- Adds a central `ReportExportService`.
- Converts Recruitment Mission Brief, Reports V2, Executive Reporting and the
  legacy decision workspace export implementation to PDF.
- Leaves scoring, ranking, recommendation, evidence and AI engines unchanged.
- Adds regression tests for PDF signature, MIME type and file naming.
