# Ripple Quantum Tests v6 (joint)

- Optimum: mu=1.549503, rho=2.349395, eta=0.080400, bw_GHz=1.800000e-05
- Joint loss: `0.18232178` | `joint_pass`: **False**
- gamma_rel_err: `1.669e-16` | f0_rel_err: `9.010e-05`

| test | nrmse_x | nrmse_y | R² | shape_ok |
|---|---:|---:|---:|:---:|
| laser_threshold | 0.000013 | 0.000012 | 1.000000 | Y |
| semiconductor_cutoff | 0.000003 | 0.000012 | 1.000000 | Y |
| mri_larmor | 0.000000 | 0.000000 | 1.000000 | Y |
| atomic_clock_modes | 113.823954 | 0.182292 | -0.071048 | N |
