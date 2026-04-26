# Ripple Quantum Tests v3 Summary

v3 separates derived-constant mode and calibrated-reference mode.

- constant mode: `calibrated`
- shape threshold: `0.18`
- MRI constant tolerance (relative): `0.02`
- Atomic clock center tolerance (Hz): `20000.0`

| test | nrmse | shape_pass | constant_mode | constant_pass | final_pass |
|---|---:|:---:|---|:---:|:---:|
| laser_threshold | 0.028013 | yes | shape_only | yes | yes |
| semiconductor_cutoff | 0.027911 | yes | shape_only | yes | yes |
| mri_larmor | 0.004509 | yes | calibrated_reference | yes | yes |
| atomic_clock_modes | 0.072342 | yes | calibrated_reference | yes | yes |

## Notes

- In `derived` mode, MRI/atomic constants come from model parameters (no direct target assignment).
- In `calibrated` mode, constants are near target by design and serve as a comparison baseline.
- If only calibrated passes but derived fails, it indicates parameter-fit ability, not derivation maturity.