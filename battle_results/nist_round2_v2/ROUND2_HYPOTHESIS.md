# Round 2 Hypothesis (Preregistered)

## Locked One-Line Position

In a strictly local, classical-wave, no-entanglement, no-superposition model, we test whether stable `S > 2` can appear under explicit measurement dependence (`rho(lambda|a,b) != rho(lambda)`), with full no-smuggling audit and no post-hoc reinterpretation.

## Scope

- This file defines only hypothesis-level assumptions.
- It does not claim quantum theory is false.
- It does not use nonlocal updates, entanglement state vectors, or superposition machinery.

## Core Assumptions

- **A1 Local causality in runtime:** Alice and Bob outcome generation uses local state only.
- **A2 Classical wave mechanism:** source emits same-origin wavefront triggers with local propagation.
- **A3 Measurement disturbance:** measurement can destroy local wavefront structure.
- **A4 Explicit measurement dependence:** settings are modeled as endogenous to system dynamics; we allow `rho(lambda|a,b) != rho(lambda)`.
- **A5 Fixed evaluation metric:** CHSH `E` and `S` are computed in the standard algebraic form.

## Non-Claims

- No claim that `S > 2` alone proves nonlocality.
- No claim that public NIST description uniquely defines slot-to-`+/-1`.
- No claim that radius-level physical coincidence is derivable without yaml/analysis chain.

## Primary Test Question

- Under A1-A5 and passing no-smuggling audit, can repeated runs produce stable `S > 2`?

## Success / Failure Definitions

- **Pass-H (hypothesis support):** `S > 2` appears robustly across preregistered seeds/runs and audit has no violations.
- **Fail-H:** `S <= 2` under preregistered conditions, or audit violation invalidates any `S > 2` run.

## Freeze Rule

- This file is frozen once first official run starts.
- Any assumption change requires a new versioned file (`ROUND2_HYPOTHESIS_vX.md`).
