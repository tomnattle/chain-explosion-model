# Triplet Material Mapping v1

## Run summary
- source_csv: `artifacts/ripple_triplet_material_mapping_v1/input_template_refractive_index.csv`
- rows: `3`
- n(MAE): `0.00000000e+00`

## Model assumption (v1)
- Vacuum-like reference is the anchor state.
- Material state is a deviation from anchor.
- v1 simplification keeps rho fixed at rho_ref and solves mu from n(λ).
- eta is inferred from k(λ) using exponential intensity attenuation.

## Next step (v2)
- joint-fit mu/rho/eta with smoothness constraints over wavelength,
- evaluate physical monotonicity and cross-material consistency.
