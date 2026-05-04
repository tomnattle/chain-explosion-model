# Triplet Material Mapping v2

## Run summary
- source_csv: `artifacts/ripple_triplet_material_mapping_v1/input_si_green1995_demo.csv`
- rows: `5`
- n(MAE): `8.88178420e-17`
- mean(mu_fit): `346.278484`
- mean(rho_fit): `2.487500`
- mean(eta_fit): `0.382500`

## Objective
- fit n(λ) with joint mu/rho/eta
- keep eta near attenuation target from k(λ)
- enforce smooth rho/eta trajectory over wavelength
- add soft priors to prevent mu-only blow-up

## Config snapshot
- rho range: [1.0, 120.0] with 81 steps
- eta range: [0.0, 1.0] with 81 steps
- weights: w_n=1.0, w_eta_target=0.05, w_smooth_mu=0.05, w_smooth_rho=1.0, w_smooth_eta=1.0
- priors: w_mu_prior=0.2, w_rho_prior=0.005, mu_prior_scale=10.0, rho_prior_scale=40.0
