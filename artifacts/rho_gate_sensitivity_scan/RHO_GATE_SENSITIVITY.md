# Rho gate sensitivity (v6)

- Fixed mu=1.5495, eta=0.08, bw=2.9999999860115105e-05.
- rho in [2.3, 2.4], n=500.
- joint_pass count on grid: **1**

## Transitions from rho_ref
{
  "rho_ref": 2.35,
  "index_nearest_rho_ref": 250,
  "joint_pass_at_nearest_grid": true,
  "index_pass_center": 250,
  "rho_at_pass_center": 2.35,
  "step_rho": 0.00020040080160299567,
  "increasing_rho": {
    "rho_last_pass": 2.35,
    "rho_first_fail": 2.3503006012024046,
    "index_fail": 251
  },
  "decreasing_rho": {
    "rho_last_pass": 2.35,
    "rho_first_fail": 2.349899799599198,
    "index_fail": 249
  },
  "first_fail_increasing": {
    "rho": 2.3503006012024046,
    "failed_gates": [
      "atomic_clock_modes",
      "f0_gate"
    ],
    "f0_rel_err": 4.476652662951346e-05
  },
  "just_before_fail_increasing": {
    "rho": 2.35,
    "failed_gates": [],
    "f0_rel_err": 0.0
  },
  "first_fail_decreasing": {
    "rho": 2.349899799599198,
    "failed_gates": [
      "atomic_clock_modes",
      "f0_gate"
    ],
    "f0_rel_err": 1.4923893475097342e-05
  },
  "just_before_fail_decreasing": {
    "rho": 2.35,
    "failed_gates": [],
    "f0_rel_err": 0.0
  }
}

## Plots
- rho_vs_nrmse_y_panels.png, rho_vs_f0_rel_err.png, rho_vs_joint_pass.png
- RHO_GATE_SENSITIVITY.json, rho_gate_scan.csv