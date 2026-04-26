# Ripple Quantum Tests v2 Summary

This version separates shape similarity from constant-level checks.

- shape threshold: `0.18`
- MRI constant tolerance (relative): `0.02`
- Atomic clock center tolerance (Hz): `20000.0`

| test | nrmse | shape_pass | constant_pass | final_pass | note |
|---|---:|:---:|:---:|:---:|---|
| laser_threshold | 0.018726 | yes | yes | yes | Threshold shape comparison only. |
| semiconductor_cutoff | 0.018966 | yes | yes | yes | Cutoff-shape comparison only. |
| mri_larmor | 0.004509 | yes | yes | yes | gamma relative error=0.008855 |
| atomic_clock_modes | 0.072342 | yes | yes | yes | center frequency error=11770.000 Hz |

## Reading Guide

- `shape_pass` only means curve-shape compatibility.
- `constant_pass` checks whether key constants are also close enough.
- This still does not claim first-principles derivation unless a dedicated derivation module is added.