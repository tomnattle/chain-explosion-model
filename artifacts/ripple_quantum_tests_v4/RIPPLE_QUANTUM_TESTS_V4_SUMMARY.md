# Ripple Quantum Tests v4

Baseline uses v3-style ripple parameters; optimized uses `scipy.optimize.differential_evolution` on bounded domains.

- shape threshold: `0.18`
- MRI γ relative tolerance: `0.02`
- clock center tolerance (Hz): `20000.0`

## Baseline

| test | nrmse | shape | const | final | note |
|---|---:|:---:|:---:|:---:|---|
| laser_threshold | 0.028013 | Y | Y | Y | ripple th=0.5000, a_hi=2.0500, a_lo=0.0300 |
| semiconductor_cutoff | 0.027911 | Y | Y | Y | ripple sigmoid c=2.0300, k=16.5000 |
| mri_larmor | 0.098210 | Y | N | N | gamma_qm=42.577000, gamma_derived=35.299448, rel_err=0.170927 |
| atomic_clock_modes | 0.182292 | N | N | N | f0_qm=9.192631770 GHz, f0_ripple=9.194251101 GHz, err_hz=1619330.917 |

## Optimized

| test | nrmse | shape | const | final | note |
|---|---:|:---:|:---:|:---:|---|
| laser_threshold | 0.000000 | Y | Y | Y | ripple th=0.5000, a_hi=2.2000, a_lo=0.0200 |
| semiconductor_cutoff | 0.000000 | Y | Y | Y | ripple sigmoid c=2.0000, k=20.0000 |
| mri_larmor | 0.000160 | Y | Y | Y | gamma_qm=42.577000, gamma_derived=42.577000, rel_err=0.000000 |
| atomic_clock_modes | 0.000000 | Y | Y | Y | f0_qm=9.192631770 GHz, f0_ripple=9.192631770 GHz, err_hz=0.000 |

## Interpretation

- **Laser / semiconductor (shape-only constants):** the optimizer can drive NRMSE to ~0 when ripple parameters are free, because the reference curves live in the same function family. That is a *curve-matching* success, not a physics identification.
- **MRI / atomic (derived constants):** passing `final_pass` means the search found medium/cavity parameters inside the stated bounds such that derived γ (or cavity f₀) and the ripple curve both meet tolerances.

## Figures

- `RIPPLE_V4_BASELINE_2x2.png`
- `RIPPLE_V4_OPTIMIZED_2x2.png` (if optimization ran)
- `RIPPLE_V4_NRMSE_BEFORE_AFTER.png`
- Per-test `*_baseline.png` / `*_optimized.png`