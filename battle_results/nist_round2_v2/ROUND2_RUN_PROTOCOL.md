# Round 2 Run Protocol (Preregistered)

## Goal

Execute reproducible CHSH simulations under the locked hypothesis and no-smuggling constraints.

## Fixed Inputs (to fill before run)

- `model_version`:
- `code_commit_or_tag`:
- `seed_list`:
- `runs_per_seed`:
- `trials_per_run`:
- `settings_schedule`:
- `pairing_rule`:
- `drop_rules`:
- `output_dir`:

## Parameter Freeze

- All fields above must be frozen before the first official run.
- Changes require a new protocol file (`ROUND2_RUN_PROTOCOL_vX.md`).

## Execution Steps

1. Validate environment and dependencies.
2. Save config snapshot to output directory.
3. Run simulation for all seeds and runs.
4. Compute `E_ab`, `E_abp`, `E_apb`, `E_apbp`, and `S`.
5. Run no-smuggling checklist and store signed result.
6. Export summary and raw artifacts.

## Mandatory Outputs

- `run_config_locked.json`
- `run_summary.json`
- `chsh_metrics.csv` (per run: counts, `E` terms, `S`)
- `seed_replay_manifest.json`
- `NO_SMUGGLING_AUDIT_RESULT.md`

## CHSH Computation Lock

- `E = (N_pp + N_mm - N_pm - N_mp) / N_total` per setting cell.
- `S = E_ab + E_abp + E_apb - E_apbp`.
- No formula modification allowed after run start.

## Pass / Fail Rule (Protocol-Level)

- **Pass-P:** no-smuggling checklist all pass; reproducibility passes; output complete.
- **Fail-P:** any missing artifact, failed audit item, or undeclared config drift.
