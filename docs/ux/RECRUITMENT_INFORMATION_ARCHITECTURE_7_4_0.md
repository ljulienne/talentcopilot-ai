# Recruitment Information Architecture Contract

## Product principle

**One workflow, one context, one next action.**

## Workflow

1. Create recruitment
2. Add job description
3. Add candidates
4. Review analysis
5. Deep-dive candidates
6. Prepare interviews
7. Record interview findings
8. Compare finalists
9. Make decision

## Page contracts

| Space | Owns | Primary action |
|---|---|---|
| Recruitment Workspace | Progress, shortlist, alerts, next action | Review shortlisted candidates |
| Candidate Intelligence | Summary, competencies, evidence, risks | Prepare interview |
| Interview Intelligence | Playbook, notes, validation, assessment | Save assessment and compare |
| Comparison & Decision | Comparison, rationale, final record | Finalize recommendation |

## Progressive disclosure

- Level 1: decision status and next action.
- Level 2: strengths, risks, gaps and readiness indicators.
- Level 3: full reasoning, evidence trace and audit details.

## Navigation contract

Every recruitment page should receive and preserve:

- recruitment/session identifier;
- selected candidate identifier when relevant;
- current workflow stage;
- return destination;
- reason for transition.

## Visual contract

The top viewport should contain:

- compact role/session context;
- workflow progress;
- four or fewer material indicators;
- one primary action;
- at most one secondary back action.

Long-form analysis belongs below the fold or behind progressive disclosure.
