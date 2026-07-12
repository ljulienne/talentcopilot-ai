# Release 3.1.1B — Interview Performance & Quality Hotfix

## Changes

- Interview Intelligence now consumes the active official `RecruitmentSession`.
- Removed the hidden `RealRankingDemoService` execution from the active page.
- Candidate fit remains the official `match_score` from `session.ranked_analyses`.
- Interview questions are shown only after an explicit user action and cached in the Streamlit session.
- Questions now use mission requirements, candidate evidence, evidence gaps, ownership, trade-offs and measurable outcomes.
- The page displays an immediate interview overview before question generation.

## Non-goals

- No matching score changes.
- No ranking changes.
- No new LLM dependency.
- No global cache infrastructure.
