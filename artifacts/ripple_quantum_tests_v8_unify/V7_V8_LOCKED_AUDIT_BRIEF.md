# v7+v8 Locked-Parameter Joint Audit Brief

- generated_at_utc: 2026-04-26T15:38:08.177844+00:00
- shared_parameters: `mu=1.5495`, `rho=2.35`, `eta=0.08`
- scope: v7 (3 tests) + v8 (3 tests), same locked triplet

## v7 (rigidity layer)

- baseline: `joint_pass_v7 = True`
- key branch (`spin_cos2`): `nrmse_y=0.0011831971`, `R2=0.9999980207`
- local rigidity: `27/27` pass (`100%`)
- random-global rigidity: `18/20` pass (`90%`)
- counterfactual suite: all expected fail (`True`)
- seed stability: `7/7` pass, near-invariant metrics

Data source:
- `artifacts/ripple_quantum_tests_v7_three/RIPPLE_V7_THREE_RESULTS.json`

## v8 (deep-quantum layer)

- baseline: `joint_pass = True`
- baseline loss: `joint_loss=0.0526105788`
- per-test:
  - `radial_levels`: pass, `nrmse_y=0.000000`, `R2=1.000000`
  - `decoherence`: pass, `nrmse_y=0.052611`, `R2=0.997795`
  - `compton_shift`: pass, `nrmse_y=0.000000`, `R2=1.000000`
- counterfactual (`eta=0.001`): `compton_pass=False` (expected fail)
- negative controls: all expected fail (`True`)
- multi-round hardening: `100/100` rounds pass (`all_rounds_pass=True`)

Data source:
- `artifacts/ripple_quantum_tests_v8_unify/v8_quantum_grand_unification.json`

## Joint conclusion (for audit wording)

- Under the declared model class and fixed acceptance gates, the evidence now supports:
  - pass across heterogeneous tests,
  - rigidity under stress,
  - expected failure on counterfactual/negative controls,
  - and repeatable consistency across many hardening rounds.
- Recommended statement:
  - "auditable model-class consistency" is supported;
  - absolute ontology closure is not claimed.
