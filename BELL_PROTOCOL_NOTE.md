# Bell Protocol Note (Strict vs Pseudo-Violation)

## Scope

This note documents which protocol choices can make a local continuous model appear to violate CHSH, and which choices restore strict CHSH constraints.

## Strict Protocol (audit baseline)

Required conditions:

- Binary outputs are fixed to `A,B in {+1,-1}` for every trial.
- Event pairing is strict (one paired A/B outcome per trial).
- No postselection (no event discard).
- Setting choices are independent random variables.
- Local response only:
  - `A = f(lambda, setting_A)`
  - `B = g(lambda, setting_B)`

Expected outcome:

- `S` stays near `2` (finite-sample fluctuation around the bound).

Reference script:

- `explore_chsh_strict_protocol.py`

## Pseudo-Violation Switches

The following switches can push `S` above `2` without requiring nonlocal ontology:

- Threshold detector gating with missed-event discard.
- Coincidence-only postselection (keep only both-detected events).
- Setting-dependent event retention rules.
- Flexible pairing windows that implicitly re-pair events.

Reference scripts:

- `explore_chsh_operation_audit.py`
- `explore_chsh_strict_vs_postselected_compare.py`

## Practical Interpretation

- CHSH mathematics is not invalidated.
- A reported `S > 2` must be interpreted together with protocol details.
- Ontology claims (nonlocality vs local mechanism) are stronger than what a non-strict pipeline alone can justify.

## Repository Integration

- `run_battle_plan.py` includes strict protocol gate:
  - `chsh_strict_S <= 2.02`
- This threshold allows finite-sample noise while preserving strict-bound intent.

