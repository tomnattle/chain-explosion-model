# Round 2 Result Interpretation (Preregistered)

This file prevents post-hoc narrative changes.

## Outcome Class A: `S <= 2`

- Interpretation: under locked assumptions and implementation, no Bell-bound breach observed.
- Action: treat as mechanism constraint; identify which additional modeled mechanism is required.
- Not allowed: re-labeling failed runs as success by changing formula/window/filtering afterward.

## Outcome Class B: `S > 2`

- Interpretation is valid only if no-smuggling audit fully passes.
- Required checks:
  - no shared runtime state across wings,
  - no global post-selection,
  - no hidden synchronous oracle,
  - deterministic replay matches summary.
- If any check fails, result is classified **invalid-B** (implementation leakage), not physics support.

## Bell-Meaning Statement Lock

If valid `S > 2` is observed here, the claim is limited to:

- It falsifies the combination "local realism + full setting independence" under this modeling frame.
- It does **not** by itself prove nonlocal ontology.

## Reporting Template (fill after run)

- `result_class`: A / B / invalid-B
- `S_mean`:
- `S_std`:
- `max_S`:
- `runs_count`:
- `audit_status`: pass/fail
- `primary_interpretation`:
- `limitations`:
