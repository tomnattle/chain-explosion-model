# Ripple Quantum Tests v6 (joint)

- Optimum: mu=1.549039, rho=2.348105, eta=0.078053, bw_GHz=6.014889e-05
- Joint loss: `0.18260291` | `joint_pass`: **False**
- gamma_rel_err: `1.669e-16` | f0_rel_err: `2.824e-04`

| test | nrmse_x | nrmse_y | R² | shape_ok |
|---|---:|---:|---:|:---:|
| laser_threshold | 0.000055 | 0.000050 | 1.000000 | Y |
| semiconductor_cutoff | 0.000049 | 0.000198 | 1.000000 | Y |
| mri_larmor | 0.000000 | 0.000000 | 1.000000 | Y |
| atomic_clock_modes | 113.823882 | 0.182292 | -0.071047 | N |
