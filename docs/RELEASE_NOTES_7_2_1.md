# Release 7.2.1 — Interview Evidence Grounding

## Summary

This release prevents internal taxonomy labels from being presented as quotations from a candidate CV in the Targeted Interview Playbook.

## Changes

- Distinguishes authentic CV evidence, structured inference, and evidence gaps.
- Uses `Your CV states` only for sufficiently detailed, action-oriented source text.
- Uses `Your experience suggests` when a competency is inferred from structured candidate data.
- Uses `The CV provides limited detail` when the evidence is absent or insufficient.
- Removes the unrelated first-achievement fallback that could repeat the same statement across competencies.
- Rejects internal labels such as `Management scope`, `Project ownership`, and `Tool exposure` as quoted evidence.
- Reads evidence from achievements, responsibilities, and structured experience entries.
- Updates the interview question engine version so previously cached playbooks are invalidated.
- Restores the `Generate Interview Strategy` label required by the stable UI contract.

## Stability

The release does not modify official scores, rankings, candidate identities, or Candidate Intelligence recommendations.
