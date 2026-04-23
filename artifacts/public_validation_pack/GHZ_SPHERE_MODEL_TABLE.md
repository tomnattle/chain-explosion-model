# GHZ correlators: three hidden-variable schemes vs QM

- samples: **1000000**, seed: **0**
- correlator: **NCC triple** `mean(A*B*C)/sqrt(mean(A^2)mean(B^2)mean(C^2))`
- angles: X at **0**, Y at **π/2** in each party’s cosine argument (scheme 1 & 3).

| model | E(XXX) | E(XYY) | E(YXY) | E(YYX) | F |
|---|---:|---:|---:|---:|---:|
| QM_reference_GHZ | 1.000000 | -1.000000 | -1.000000 | -1.000000 | 4.000000 |
| scheme1_four_lambdas | -0.000379 | -0.001070 | 0.000913 | 0.001071 | -0.001294 |
| scheme2_sphere_user_xy_xz | -0.000735 | -0.000735 | -0.000735 | -0.000735 | 0.001471 |
| scheme2b_sphere_bloch_nx_ny | -0.000735 | -0.001841 | -0.001841 | -0.001841 | 0.004786 |
| scheme3_best_phi | 0.001178 | -0.000363 | -0.000363 | 0.000624 | 0.001281 |

## Notes

- **QM row** is the standard ±1 GHZ prediction; continuous NCC may still yield different magnitudes.
- **Scheme 2 (user)** at angle 0: `measure_X` and `measure_Y` both return **n_x**; all four triples coincide → identical E and F≈0.
- **Scheme 2b** uses **X→n_x, Y→n_y** on the same S^2 sample (non-degenerate at zero angle).
- **Scheme 3**: one scalar **φ** on Charlie only, chosen on a grid to minimize |E(XXX)−1|; other correlators are **not** separately fitted (honest single-knob test).
