# ROLE_IDENTIFICATION (v6 toy, local)

## Dominant parameters (by abs Jacobian)
- nrmse_y_laser_threshold: dominant=mu, dmetric/dparam=-3.175e-02
- nrmse_y_semiconductor_cutoff: dominant=eta, dmetric/dparam=2.914e-07
- nrmse_y_mri_larmor: dominant=mu, dmetric/dparam=5.016e-13
- nrmse_y_atomic_clock_modes: dominant=bw, dmetric/dparam=-4.385e-01
- f0_rel_err: dominant=rho, dmetric/dparam=-4.278e-06
- gamma_rel_err: dominant=mu, dmetric/dparam=8.344e-13

## Gate margins at lock
- worst_shape_margin (across panels): 0.000999998
- f0_ok_margin: 2.17566e-06 (positive means f0 passes)
- gamma_ok_margin: 1e-09 (positive means gamma passes)

## Identifiability
- rank_shape_f0: 4
- condition_shape_f0: 1.5e+06

## Files
- artifacts\param_role_identification_v1\ROLE_IDENTIFICATION.json
- artifacts\param_role_identification_v1\heatmap_jacobian.png (if plot enabled)