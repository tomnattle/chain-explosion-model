# Rho atomic lock audit — entry index

This folder is the **human-facing entry point** for the post-lock ρ audit chain.

## Canonical traceability

1. **Sidecar extension (machine-readable, with script SHA256):**  
   `artifacts/ripple_unified_lock/RHO_ATOMIC_LOCK_AUDIT_EXTENSION.json`  
   Regenerated when you run `summarize_lock_run.py` (unless `--skip-rho-audit-extension`).

2. **Merged narrative:**  
   `artifacts/ripple_unified_lock/FINAL_AUDIT_SUMMARY.md` — section **“Rho atomic lock chain (post-lock audit)”**.

## What to open first

| Question | Primary artifact |
|----------|------------------|
| Who kills ρ? | `artifacts/rho_sensitivity_breakdown/RHO_SENSITIVITY_BREAKDOWN.json`, `rho_executioner_nrmse_y.png` |
| Wide ρ scan + f0 curve | `artifacts/rho_gate_sensitivity_scan/` |
| Feasible (μ,ρ) slice, η fixed | `artifacts/rho_mu_feasibility_map/` |
| Is ρ = μ² required? | `artifacts/verify_rho_mu2_constraint/` |

## Scope

All statements in this chain refer to **v6 `joint_curves` + `state_after_de` gates** and the **toy bridges** in code. They do **not** identify a laboratory material unless a separate mapping is defined and tested.
