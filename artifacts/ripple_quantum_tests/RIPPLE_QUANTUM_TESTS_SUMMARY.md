# Ripple Quantum Tests Summary

This suite compares a QM-like reference curve with a ripple-model curve in four tasks.

- pass threshold (NRMSE): `0.1800`

| test | nrmse | pass |
|---|---:|:---:|
| laser_threshold | 0.009503 | yes |
| semiconductor_cutoff | 0.018966 | yes |
| mri_larmor | 0.004509 | yes |
| atomic_clock_modes | 0.072342 | yes |

## Interpretation

- Pass means curve-shape similarity under current parameterization.
- It does not automatically prove first-principles equivalence.
- MRI/atomic-clock exact constants still require deeper derivation tasks.