# C_norm -> E(Δ) Bridge Report

- Input: `D:\workspace\chain-explosion-model\artifacts\reports\ncc_singles_bridge_real.json`
- Output figure: `artifacts/reports/cnorm_e_delta_bridge_real.png`
- Unique Δ count (standard branch): `2`
- Unique Δ values (deg): `[22.5, 67.5]`

## Scaling definition

- `E_tilde(Δ) = C_signed_norm(Δ) / max_abs(C_signed_norm)` (within each branch)
- `C_signed_norm = sum(oA*oB) / sqrt(singles_A*singles_B)`

## Fit quality (shape-level only)

- Strict cosine RMSE: `0.153822`
- Strict linear RMSE: `0.153822`
- Standard cosine RMSE: `0.153630`
- Standard linear RMSE: `0.153630`

## Boundary note

- CHSH 2x2 settings provide limited unique Δ values; this is not a dense continuous scan.
- This bridge is an observability/shape check, not a CHSH-equivalence proof.
