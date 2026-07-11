# TalentCopilot Next Release 0.6.1

## Stability hotfix

Fixes the Streamlit Diagnose page crash:

`NameError: name 'insights' is not defined`

The knowledge diagnostic renderer now returns its generated insights explicitly. The page aggregates knowledge, organization graph, and collaboration insights using defensive empty-list fallbacks before generating the AI Decision Queue.
