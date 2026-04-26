# Ripple Quantum Tests v7 (three) summary

- generated_at: 2026-04-26T14:51:27.495677+00:00
- joint_pass_v7: **True**
- shared_params: mu=1.549500, rho=2.350000, eta=0.080000

## Baseline
- double_slit: nrmse_y=0.000000, R2=1.000000, pass=Y
- tunneling: nrmse_y=0.000000, R2=1.000000, pass=Y
- spin_cos2: nrmse_y=0.001183, R2=0.999998, pass=Y

## Parameter rigidity
- local pass: 27/27 (rate=1.000)
- random pass: 18/20 (rate=0.900)

## Counterfactual
- cf_wrong_sign_mapping: nrmse_y=0.714767, R2=0.999998, pass=N
- cf_wrong_angle_speed: nrmse_y=0.507240, R2=0.000053, pass=N
- cf_phase_scramble: nrmse_y=0.583325, R2=0.002680, pass=N
- expected_all_fail: True

## Seed stability (spin)
- n_seeds: 7
- nrmse mean/std/max: 0.001183 / 0.000000 / 0.001183
- R2 mean/min: 0.999998 / 0.999998
- all_pass: True
