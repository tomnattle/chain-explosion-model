# Extreme refractive-index demos (mapping stress tests)

These CSVs are **synthetic** grids meant to widen coverage in `(n, k, wavelength)` so joint mapping does not only see "comfortable" visible-range dielectrics.

| File | Intent |
|---|---|
| `input_extreme_metal_like_demo.csv` | Strong absorption ramp: `k` increases with wavelength; `n` increases with wavelength (coherent with `eta_target` trends). |
| `input_extreme_ultralowk_demo.csv` | Tiny positive `k` (~1e-10..1e-11) to stress the low-k shape prior. |
| `input_extreme_highn_lowk_demo.csv` | High `n` with small but nonzero `k` (high-index dielectric / weak loss). |
| `input_extreme_midk_curved_demo.csv` | Mid `k` with a non-monotonic `n(λ)` curve (shape stress, not a single-parameter monotone trend). |

Notes:

- `metalx` needs a higher `eta` ceiling than the global cap; `triplet_material_mapping_v7_1_joint.py` defaults include `metalx=2.8` via `eta_max_overrides`.
- If you intentionally want **inconsistent** `(n,k)` toy data (e.g. `n` falls while `k` rises), expect `eta_monotonic_by_k` checks to fail — that is a feature of the diagnostic, not necessarily a bug in the fitter.
