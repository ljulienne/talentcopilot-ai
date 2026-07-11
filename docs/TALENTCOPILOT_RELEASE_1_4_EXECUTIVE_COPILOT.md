# TalentCopilot Release 1.4 — Executive Copilot

Release 1.4 consolidates the Executive Copilot Core, Executive Design System, response view, interactive workspace and contextual actions.

## Validation

- Guided and free-text question routing
- Evidence-based ExecutiveAnswer rendering
- Executive Health, confidence, engine coverage and data readiness
- Follow-up questions and contextual navigation
- Session action plan
- Release manifest and Doctor readiness check
- Release audit command

## Commands

```bash
python tools/talentcopilot_doctor.py
python tools/release_audit.py --release 1.4
pytest -q
```
