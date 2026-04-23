# Geometric Rebuttal V3

This package addresses 4 audit questions from cross-examination.

## Q1 Low-R statistical stability
- Added bootstrap CI bars for selected high-F points on Pareto scatter.
- Added F bootstrap summaries by R bins.
- High-F examples remain clearly above `F=2` with narrow CI (e.g. `F≈3.99`, CI about `[3.989, 3.994]`).
- Low-R bin (`R<0.2`) is much wider and includes sub-2 region, so low-R claims must be conditioned on parameter region.

## Q2 Cliff realism vs coarse grid artifact
- Added local dense refinement around R_min focus and compared coarse vs fine curves.
- At `R_min=0.35`, coarse best is `F≈3.893 @ R≈0.3527`; fine local search improves to `F≈3.930 @ R≈0.3525`.
- Result: cliff exists, but coarse grid slightly underestimates feasible `F` near the boundary.

## Q3 Third-variable confounding check
- Added R-vs-parameter scatter maps colored by F.
- Added simple correlation diagnostics in JSON.
- Correlation snapshot: `corr(R, r_src)=0.678` (strong), `corr(R, lambda_w)=0.066` (weak).
- `F` has weak linear dependence on both (`corr(F, lambda_w)=-0.150`, `corr(F, r_src)=-0.118`), indicating the tradeoff is not just one-parameter artifact.

## Q4 External experiment condition alignment
- Added optional external F/R JSON hook (`--external-f-r-json`).
- Current run status: see JSON field `q4_external_alignment.status`.
- This run: `NO_EXTERNAL_DATA_PROVIDED` (no compatible external per-shot F/R table supplied).

## Files
- `Q1_PARETO_WITH_CI.png`
- `Q2_RMIN_CLIFF_COARSE_VS_FINE.png`
- `Q3_THIRD_VARIABLE_SCATTERS.png`
- `GEOMETRIC_REBUTTAL_V3_RESULTS.json`