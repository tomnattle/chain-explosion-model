# Triplet Material Mapping v2

## Run summary
- source_csv: `artifacts\ripple_triplet_material_mapping_v1\input_si_green1995_demo.csv`
- rows: `5`
- n(MAE): `8.88178420e-17`
- mean(mu_fit): `434.716792`
- mean(rho_fit): `2.350000`
- mean(eta_fit): `0.237000`

## Objective
- fit n(λ) with joint mu/rho/eta
- keep eta near attenuation target from k(λ)
- enforce smooth rho/eta trajectory over wavelength

## Config snapshot
- rho range: [1.0, 4.0] with 81 steps
- eta range: [0.0, 0.3] with 81 steps
- weights: w_n=1.0, w_eta_target=0.2, w_smooth_rho=2.0, w_smooth_eta=2.0
