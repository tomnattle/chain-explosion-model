# Round 2 No-Smuggling Checklist (Preregistered)

This checklist is mandatory. Any failed item marks the run invalid for Bell-interpretation claims.

## Hard Constraints

- [ ] **C1 No shared runtime state:** Alice/Bob event handlers cannot read/write each other's mutable state.
- [ ] **C2 No global post-selection:** event inclusion cannot depend on joint outcomes observed after both sides finish.
- [ ] **C3 No hidden synchronous oracle:** no global step that injects instantaneous cross-wing info into both updates.
- [ ] **C4 Local timeline only:** each side uses only locally available history plus source-origin data that is causally allowed.
- [ ] **C5 Deterministic reproducibility:** fixed seed list reproduces same statistics within declared tolerance.
- [ ] **C6 Metric immutability:** CHSH formula and filtering rules are fixed before execution.

## Measurement-Dependence Specific Constraints

- [ ] **M1 Explicit declaration:** where `rho(lambda|a,b) != rho(lambda)` is implemented must be named in code.
- [ ] **M2 No hidden backdoor:** no undeclared dependence path from remote setting to local outcome.
- [ ] **M3 Side-local computability:** local outcome function can be evaluated without reading remote live setting.

## Audit Evidence To Save

- [ ] Git commit hash / dirty status snapshot.
- [ ] Full run config JSON snapshot.
- [ ] Random seed list and run count.
- [ ] Raw per-trial logs or deterministic replay artifacts.
- [ ] CHSH aggregation script output (with pair counts and `E` table).
- [ ] This checklist with pass/fail marks and reviewer initials.

## Invalidating Conditions

- Any unchecked hard constraint.
- Any undocumented rule change after first official run.
- Any mismatch between declared config and executed config.
