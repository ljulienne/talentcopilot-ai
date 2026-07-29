# Integration Guide — Release 7.8.1

## Base

- Release: `7.8.0-premium-recruitment-experience`
- Commit: `9ed9a076ec2222b716f062591896e7fdc9f977a0`

## Target

- Release: `7.8.1-recruitment-journey-reporting`

## Validation checklist

1. Confirm **Home** is visible at the top of the sidebar.
2. Confirm clicking the TalentCopilot logo opens Executive Brief without deleting the active recruitment mission.
3. Confirm the Recruitment section contains Overview, Dashboard Perspective, Compensation & Budget, Interview & Assessment and Compare & decide.
4. Confirm sidebar navigation text is clearly readable in normal, hover and active states.
5. Complete candidate analysis and confirm the first automatic destination is Dashboard Perspective.
6. Confirm Dashboard Perspective shows the whole candidate pool and opens each contextual Candidate Intelligence page.
7. Return from Candidate Intelligence and confirm Dashboard Perspective remains the parent destination.
8. Define the approved position budget before interview.
9. Record candidate salary, benefits, notice period, availability and negotiation flexibility before or after interview.
10. Confirm offer scenarios display Compensation Fit independently from Talent Fit.
11. Confirm PDF downloads are visible on Overview, Dashboard Perspective, Candidate Intelligence, Interview & Assessment, Compensation & Budget and Compare & Decide.
12. Confirm the blue/cyan recruitment journey strip is rendered above each recruitment page and remains visible while scrolling on desktop.
13. Confirm normal primary actions are blue/cyan and not red.
14. Compare official candidate scores and ranks before and after compensation updates; they must remain unchanged.
15. Run the targeted 7.8.1 tests and the complete repository test suite.

## Targeted test command

```bash
python -m pytest -q \
  tests/test_release_7_8_1_recruitment_journey_reporting.py \
  tests/test_release_7_8_0_premium_recruitment_experience.py \
  tests/test_release_7_1_1_hiring_budget_consistency.py \
  tests/test_release_7_4_0_lot_2_hidden_workflow_routes.py \
  tests/test_release_7_4_0_lot_2_recruitment_workflow_shell.py
```

## Complete validation

```bash
python -m compileall -q talentcopilot app.py
python -m pytest -q --disable-warnings --maxfail=1
```
