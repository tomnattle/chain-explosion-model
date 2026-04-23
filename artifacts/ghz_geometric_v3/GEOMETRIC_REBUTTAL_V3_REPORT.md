# Geometric Rebuttal V3

This package addresses 4 audit questions from cross-examination.

## Q1 Low-R statistical stability
- Added bootstrap CI bars for selected high-F points on Pareto scatter.
- Added F bootstrap summaries by R bins.

## Q2 Cliff realism vs coarse grid artifact
- Added local dense refinement around R_min focus and compared coarse vs fine curves.

## Q3 Third-variable confounding check
- Added R-vs-parameter scatter maps colored by F.
- Added simple correlation diagnostics in JSON.

## Q4 External experiment condition alignment
- Added optional external F/R JSON hook (`--external-f-r-json`).
- Current run status: see JSON field `q4_external_alignment.status`.

## Files
- `Q1_PARETO_WITH_CI.png`
- `Q2_RMIN_CLIFF_COARSE_VS_FINE.png`
- `Q3_THIRD_VARIABLE_SCATTERS.png`
- `GEOMETRIC_REBUTTAL_V3_RESULTS.json`