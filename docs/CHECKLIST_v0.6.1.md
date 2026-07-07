# Validation Checklist — v0.6.1

## Colab

- [ ] ZIP uploaded to `/content`.
- [ ] ZIP extracted to `/content/mega_sprint_15`.
- [ ] `install_megasprint.py` executed.
- [ ] Sprint tests are green.

## GitHub

- [ ] `git status` reviewed.
- [ ] Commit created with: `Mega Sprint 15 - Decision Intelligence`.
- [ ] Push completed.

## Streamlit Cloud

- [ ] App rebooted.
- [ ] No import error.
- [ ] Decision Workspace still opens.
- [ ] Candidate analysis still works.
- [ ] Optional: Decision Intelligence card visible if integrated.

## Expected Test Command

```bash
python -m pytest tests/test_decision_engine.py tests/test_decision_models.py tests/test_decision_ui_cards.py -q
```
