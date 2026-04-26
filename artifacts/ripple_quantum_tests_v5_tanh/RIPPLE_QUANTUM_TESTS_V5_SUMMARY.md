# Ripple Quantum Tests v5 (rigorous)

## Metrics

- `nrmse_x`, `nrmse_y`, `r2` per test (see JSON).
- Shape pass: both NRMSEs ≤ (0.18, 0.18) and R² ≥ 0.999.

## Identifiability

- MRI: single κ from algebra; no 4-parameter search.
- Atomic: v = c = 299792458.0 m/s; L from f₀ and n; bw only optimized.

## Results

| test | nrmse_x | nrmse_y | R² | shape | const | final |
|---|---:|---:|---:|:---:|:---:|:---:|
| laser_threshold | 0.000000 | 0.000000 | 1.000000 | Y | Y | Y |
| semiconductor_cutoff | 0.000000 | 0.000000 | 1.000000 | Y | Y | Y |
| mri_larmor | 0.000000 | 0.000000 | 1.000000 | Y | Y | Y |
| atomic_clock_modes | 0.000000 | 0.000000 | 1.000000 | Y | Y | Y |

Figures: `artifacts\ripple_quantum_tests_v5_tanh\RIPPLE_V5_RIGOROUS_2x2.png`
