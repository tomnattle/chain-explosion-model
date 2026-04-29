# Rho executioner breakdown

- Largest |d(nrmse_y)/dρ| at ref: **nrmse_atomic_clock_modes**
- Slopes: `{"nrmse_laser_threshold": 0.02660414380520109, "nrmse_semiconductor_edge": 0.0233030631614268, "nrmse_mri_larmor": 0.0, "nrmse_atomic_clock_modes": 185.61536163314258}`

## First joint fail (newly violated vs previous)
{
  "increasing_rho": {
    "direction": "increasing_rho",
    "rho_last_pass": 2.35,
    "rho_first_fail": 2.350150753768844,
    "newly_failed": [
      "shape:atomic_clock_modes",
      "f0_gate"
    ],
    "failed_gates_full": [
      "atomic_clock_modes",
      "f0_gate"
    ]
  },
  "decreasing_rho": {
    "direction": "decreasing_rho",
    "rho_last_pass": 2.35,
    "rho_first_fail": 2.3499497487437186,
    "newly_failed": [
      "shape:atomic_clock_modes",
      "f0_gate"
    ],
    "failed_gates_full": [
      "atomic_clock_modes",
      "f0_gate"
    ]
  }
}

- Files: `RHO_SENSITIVITY_BREAKDOWN.json`, `rho_executioner_nrmse_y.png`, `rho_executioner_series.csv`