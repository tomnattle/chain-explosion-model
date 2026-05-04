# Triplet Material Mapping Batch v4 Report

## Diagnostics
- monotonic_by_n_mu: `True`
- linear_fit: `mu_mean = 11.583682 * n_mean + -10.144030`
- R2: `0.983744`

## Per material

| material | n_mean | mu_mean | rho_mean | eta_mean |
|---|---:|---:|---:|---:|
| input_air_visible_demo | 1.000273 | 1.551695 | 2.350000 | 0.000000 |
| input_water_visible_demo | 1.335000 | 4.923537 | 2.350000 | 0.000000 |
| input_sio2_malitson_visible | 1.461643 | 7.074946 | 2.350000 | 0.000000 |

## Note
- This is trend diagnostics, not causal proof.
- eta trend requires non-zero k(λ) material tables.
