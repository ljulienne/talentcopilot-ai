# Release 8.6.0 — Recruitment Portfolio Intelligence

## Purpose

Release 8.6.0 turns the existing Analytics route into transparent cross-project recruitment intelligence. It uses saved lifecycle, priority, owner and last-activity metadata to surface operational attention without recalculating candidate scores or inventing predictive time-to-hire metrics.

## Added

- Cross-project lifecycle distribution.
- Last-activity freshness bands based on recorded timestamps.
- One primary operational alert per project.
- Transparent attention rules for ownership, inactivity, decision, interview and pipeline conditions.
- Owner workload visibility with project, priority, decision-ready and attention counts.
- Portfolio recommendations derived from the visible alert queue.
- Active-mission analytics retained as a separate tab.

## Guardrails

- Archived projects are excluded from open-portfolio intelligence.
- No candidate score, rank or evidence field is read or changed by the portfolio intelligence service.
- Workload is descriptive; the product does not infer recruiter capacity.
- Last activity is not represented as time spent in a lifecycle stage.
- No time-to-hire forecast is generated from incomplete historical data.

## Compatibility

- Release 8.5.0 project files remain unchanged and loadable.
- Project lifecycle, archive/reopen and source-of-truth integrity controls remain active.
- The existing active-recruitment analytics service remains available in the Active mission tab.
