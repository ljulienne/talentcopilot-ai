# Release 3.2.1A.1 — Recruitment Workspace Premium

## Product outcome

The active Recruitment Workspace now opens with a decision-oriented cockpit:

- mission and session context;
- number of imported and analysed candidates;
- official top-ranked candidate and score;
- five-step workflow progression;
- current stage;
- next recommended action.

## Architecture

`RecruitmentCockpitService` builds a presentation model exclusively from the
official `RecruitmentSession` and the existing workspace report.

No matching, ranking, evidence or recommendation is recalculated.

## Out of scope

- matching calibration;
- multi-project persistence;
- Candidate Intelligence redesign;
- Interview Intelligence redesign;
- report redesign.
