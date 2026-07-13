# Release 3.2.1A.2 — Candidate Intelligence Premium

## Product outcome

Candidate Intelligence is now presented as a concise decision brief:

- official match score;
- official rank;
- executive recommendation;
- decision confidence;
- evidence coverage;
- top strengths;
- transferable evidence;
- missing evidence;
- hiring risks;
- interview priorities.

## Architecture

`CandidateIntelligenceViewService` organises the existing
`CandidateWorkspaceReport` and `CandidateIntelligenceSnapshot`.

It does not call the matching engine, Decision Core, LLM, demo pipeline,
or interview generator. Official score and rank remain unchanged.

## Out of scope

- score calibration;
- matching changes;
- new Decision Core calculations;
- automatic question generation;
- multi-project persistence.
