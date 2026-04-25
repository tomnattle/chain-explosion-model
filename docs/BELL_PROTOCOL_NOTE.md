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

## NCC denominator observability bridge

One common objection is: if a normalized continuous metric is used, where does its denominator come from in detector data?

Repository bridge script:

- `scripts/explore/explore_ncc_singles_coincidence_bridge.py`

It computes, from the same event stream:

- `singles_A(a)`, `singles_B(b)`
- `coincidences(a,b)` under a declared coincidence window
- `C_norm(a,b) = coincidences(a,b) / sqrt(singles_A(a) * singles_B(b))`
- optional signed variant `C_signed_norm(a,b) = sum(oA*oB) / sqrt(singles_A(a) * singles_B(b))`

This makes the denominator mapping explicit and reproducible as an engineering observable.
It does **not** by itself prove equivalence to standard CHSH `E(a,b)`.

## Repository Integration

- `run_battle_plan.py` includes strict protocol gate:
  - `chsh_strict_S <= 2.02`
- This threshold allows finite-sample noise while preserving strict-bound intent.

## Independent line (P4): protocol audit vs experimental CHSH

The closure / strict-vs-postselected scripts (`explore_chsh_strict_protocol.py`, `explore_chsh_operation_audit.py`, `explore_chsh_closure_protocol.py`, `explore_chsh_local_wave_closure_full.py`, etc.) constitute a **separate** track from reproducing NIST CHSH numbers on public HDF5.

- **Purpose:** reproducibly show how **measurement pipelines** (thresholds, coincidence gating, pairing) move `S` under an explicitly coded local model.
- **Conclusion scope:** clarifies the **link between protocol choice and reported `S`**, not the ontology of a specific lab dataset.
- **Do not merge claims** between this track and the NIST blind-test archive without a new preregistration that states both assumptions together.

See also: `battle_results/nist_round2_v2/P4_PROTOCOL_AUDIT_SCOPE.md`.

