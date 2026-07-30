# TalentCopilot-AI 8.4.0 — Persistent Recruitment Projects

## Purpose

Release 8.4.0 turns the existing Projects page into a real continuity layer for
recruitment decisions. A recruiter can explicitly save an active recruitment,
leave the current browser session, reopen the saved project and continue from
the same official candidate identities, scores, ranks and decision evidence.

## Delivered capabilities

- Explicit **Save project** control in the Projects workspace.
- Versioned JSON project schema for canonical `RecruitmentSession` data.
- Restoration of:
  - job and candidate evidence;
  - candidate IDs, official Talent Fit scores and official ranks;
  - score breakdown and source-of-truth fingerprint;
  - interview evaluations and finalist selection;
  - compensation, availability and budget inputs;
  - final-decision rationale, decisive evidence, accepted risks and history.
- Automatic updates after the recruiter has explicitly saved a project once.
- Atomic JSON writes to prevent partially written project files.
- Backward-compatible opening of historical recruitment-store files.
- Configurable local data root through `TALENTCOPILOT_DATA_DIR`.

## Privacy and deployment boundary

A new upload is not silently written to disk. Persistence starts only when the
recruiter selects **Save project**. The current implementation uses the local
runtime filesystem. It is a continuity foundation, not a production multi-user
database, and files may not survive infrastructure replacement on hosting
platforms with ephemeral storage.

## Governance

- Official scores and ranks are restored, never recomputed.
- The persisted source-of-truth snapshot is validated during reopening.
- A project whose persisted scores no longer match its official fingerprint is
  rejected instead of being silently repaired.
- Interview, compensation and final decisions remain separate evidence layers.

## Validation

- Release 8.4.0 targeted and persistence tests: passed.
- Releases 8.0.0–8.3.0 and stable recruitment regressions: passed.
- Full suite: 254 tests passed using an offline Streamlit import stub because
  Streamlit is unavailable in the build container.
- The package installer reruns the suite in the real Colab environment.
