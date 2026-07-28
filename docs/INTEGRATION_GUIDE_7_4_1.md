# Integration Guide — Release 7.4.1

## Base commit

Install only on Git commit:

`54e1e9185981282fd9f9733a5f1eacce3d86d531`

## Files changed

- `talentcopilot/models/competency_matrix.py`
- `talentcopilot/services/competency_matrix_service.py`
- `talentcopilot/ui/competency_star.py`
- `talentcopilot/ui/candidate_workspace.py`
- `talentcopilot/ui/interview_intelligence.py`
- `tests/test_release_7_4_1_role_aligned_competency_radar.py`

## Validation

Run:

```bash
python -m compileall -q talentcopilot
pytest -q tests/test_release_7_4_1_role_aligned_competency_radar.py \
  tests/test_competency_star_restoration.py \
  tests/test_release_7_3_0_dynamic_competency_matrix.py \
  tests/stable/test_stable_interview_evaluation.py \
  tests/test_release_4_7_interview_intelligence_pro.py \
  tests/test_release_7_4_0_lot_4_interview_decision_flow.py
pytest -q
```

## Expected UX

1. Candidate Intelligence shows a read-only radar: role expectation versus pre-interview AI estimate.
2. Interview Intelligence allows human assessment and evidence capture.
3. Added interview competencies are clearly identified as additional and do not alter job requirements.
4. Finalization saves a post-interview radar and its version history.
