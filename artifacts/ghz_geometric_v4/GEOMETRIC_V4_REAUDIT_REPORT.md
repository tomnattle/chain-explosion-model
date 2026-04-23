# Geometric V4 Re-audit

## Scope
- High-resolution internal re-audit for Q1/Q2/Q3
- Q4 closure step via transparent QM surrogate under same gated metric

## Headline Findings
- Q1: high-F points keep narrow CI and stay far above `F=2` (example: `F=3.9983`, CI `[3.9973, 4.0000]` at `R=0.2286`).
- Q2: cliff remains after local dense refinement; around `R_min=0.35`, best feasible `F` rises from `3.8930` (coarse) to `3.9275` (fine), so cliff is real but coarse grid is conservative.
- Q3: `R` mainly tracks `r_src` (`corr=0.674`), while `F` has weak linear dependence on both `r_src` and `lambda_w`, supporting structural tradeoff rather than a single extreme-parameter artifact.
- Q4 surrogate: under the same gated metric, the transparent QM surrogate keeps `F=4` with high retention (`R≈0.93~1.00`), unlike geometric high-F points (`R≈0.14~0.35`).

## Audit Interpretation
- Current geometric mechanism can reproduce high `F`, but does so in a low-retention regime.
- Under matched gating, the surrogate control indicates low `R` is not a generic algebraic necessity of high `F`; it is a cost of this mechanism/parameterization.

## Output
- `V4_Q1_HIGHRES_PARETO_CI.png`
- `V4_Q2_CLIFF_COARSE_VS_FINE.png`
- `V4_Q4_QM_SURROGATE_FR.png`
- `GEOMETRIC_V4_REAUDIT_RESULTS.json`