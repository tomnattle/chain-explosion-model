# FINAL AUDIT SUMMARY

- **Status**: `RECOVERED`
- **Core Triplet (Locked)**: `1.5500 / 2.35 / 0.08`
- **Joint Consistency**: `Pass (V6 refined)`
- **Stability**: `100/100 Monte Carlo passed`
- **Known Limits**: `V9 Material Generalization pending`

## Anti-Cheat Identity

- git_head: `50faa31d801fbb3e20dcbe0bf0c1ece6013e4aa3`
- python: `Python 3.11.14`
- script_sha256.v6_joint: `27ac23eb7028e0cf003f68528b7b0d720ac346ad825e39236be8b81af4d7871d`
- script_sha256.v8_unify: `8b9c6c65abeb6d35652c63170ebe7bc27c5491e262d9fba27e33697e948b4313`
- script_sha256.v9_material_extension: `5a6fe52071149357c72dfe84c0187701a86a362f6bfc343b71b1ce520f873336`
- script_sha256.summarize_lock_run: `1cae4bb3404b8aeb2c9ac1bdf5f9cf7a183d6a3eebb5b95fda7fba37370c59ca`

## Traceability

- v6_primary joint_pass: `False`
- v6_primary loss: `0.182321775922`
- v6_recovered loss: `0.0`
- logical_delta (primary - recovered): `0.18232177592154905`

## Device Fingerprint

- os: `Microsoft Windows NT 10.0.26200.0`
- cpu_name: `Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz`
- cpu_cores_logical: `16`
- cpu_cores_physical: `8`
- blas_info_json: `{"numpy_version": "2.4.1", "blas_opt_info": {}, "openblas_info": {}, "mkl_info": {}}`

## Sensitivity Jitter (±0.0001 around locked triplet)

- alpha_for_audit: `0.1`
- center_loss: `1.00323507416e-16`
- hardness_score(mean slope): `505.728328408`
- slope_mu: `0.0317382878014`
- slope_rho: `1517.07627597`
- slope_eta: `0.0769709696383`

## Counterfactual Negative Control (mu fixed = 1.0)

- best_loss_under_mu1: `0.203457502856`
- best_rho_under_mu1: `2.3375`
- best_eta_under_mu1: `0.09`
- best_bw_under_mu1: `1.8e-05`

> Interpretation rule: if `best_loss_under_mu1` remains materially above recovered-loss baseline,
> then textbook-mu=1.0 does not close the same objective under this audit setup.

## Rho atomic lock chain (post-lock audit)

Independent scans on v6 gates; traceability extension:
- `artifacts/ripple_unified_lock/RHO_ATOMIC_LOCK_AUDIT_EXTENSION.json` (indexed UTC: `2026-04-29T04:48:53.056490+00:00`)

### Scripts (SHA256 in extension JSON)
- `scripts/explore/ripple_quantum_tests/rho_sensitivity_breakdown.py`
- `scripts/explore/ripple_quantum_tests/rho_gate_sensitivity_scan.py`
- `scripts/explore/ripple_quantum_tests/rho_mu_feasibility_map.py`
- `scripts/explore/ripple_quantum_tests/verify_rho_mu2_constraint.py`

### Artifact directories
- `artifacts/rho_sensitivity_breakdown/` (JSON, CSV, PNG as produced by each script)
- `artifacts/rho_gate_sensitivity_scan/` (JSON, CSV, PNG as produced by each script)
- `artifacts/rho_mu_feasibility_map/` (JSON, CSV, PNG as produced by each script)
- `artifacts/verify_rho_mu2_constraint/` (JSON, CSV, PNG as produced by each script)

### Audit-grade conclusions (toy scope only)

- **Executor**: `atomic_clock_modes` shape + **`f0_gate`** dominate rho sensitivity; steepest |d(nrmse_y)/dρ| on the atomic panel in dense scans.
- **rho = 2.35**: matches **`RHO_REF`** in `ripple_quantum_tests_v6_joint.py` via `L ∝ (rho/RHO_REF)^alpha`; joint pass is not proof of continuum material density.
- **rho ≈ mu²**: falsified as required joint attractor under the same gates (see `verify_rho_mu2_constraint`).

### Human index

- `artifacts/rho_atomic_lock_audit/RHO_ATOMIC_LOCK_CHAIN.md`