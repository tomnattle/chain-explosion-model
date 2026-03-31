# NO_SMUGGLING_AUDIT_RESULT

Audit target: `run_round2_engineering_battle.py` + `explore_chsh_experiment_alignment.py` deterministic offline pipeline.

## Checklist Result

- C1 No shared runtime state across wings: **PASS** (offline CSV pairing computation, no cross-wing mutable runtime channel).
- C2 No global post-selection: **PASS** (fixed inclusion by pairing/window rules; no outcome-conditional inclusion branch observed in run path).
- C3 No hidden synchronous oracle: **PASS** (no global runtime state synchronizer in this execution mode).
- C4 Local timeline only: **PASS (scoped)** (`t` index and window-based pairing; scoped to this engineering pipeline).
- C5 Deterministic reproducibility: **PASS** (2026-03-31: re-invoked `explore_chsh_experiment_alignment.py` on the same legacy/parity CSVs + `chsh_preregistered_config_nist_round2_engineering.json`; strict/standard `S` matched `ROUND2_chsh_result_*.json` bit-for-bit at exported precision).
- C6 Metric immutability: **PASS** (CHSH formulas and gates unchanged during run).

## Audit Verdict

**PASS_WITH_SCOPE_NOTE**

This pass applies to the executed deterministic NIST engineering pipeline only.  
It is not a claim that a newly implemented local-wave simulator was audited here.
