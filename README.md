# TalentCopilot AI

**Human Intelligence. AI Amplified.**

TalentCopilot is an evidence-led Talent Intelligence platform that helps HR teams analyse candidates, structure interviews, model compensation, compare finalists and support human-owned decisions.

## Current experience

Release `8.4.0-persistent-recruitment-projects` adds controlled decision continuity without changing official scores:

- explicit project saving from the Projects workspace;
- versioned restoration of canonical candidate IDs, Talent Fit scores and ranks;
- persisted interview evidence, compensation context, finalist selection and decision history;
- automatic project updates only after an explicit first save;
- atomic local JSON storage with source-of-truth integrity validation;
- preserved Candidate Decision Workspace, universal risk grounding and PDF alignment.

The local persistence adapter is a product foundation, not a production multi-user database.

## Core recruitment spaces

- Recruitment Overview
- Dashboard Perspective
- Compensation & Budget
- Interview & Assessment
- Compare & Decide

Built with Python and Streamlit.
