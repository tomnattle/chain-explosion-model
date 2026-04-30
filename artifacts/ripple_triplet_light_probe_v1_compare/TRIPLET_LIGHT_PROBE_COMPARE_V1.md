# Triplet Light Probe Comparison v1

## Model snapshot
- n_eff(model) = `1.00000000`
- eta(model) = `0.08000000`
- attenuation(model) = `0.694871` dB / distance_unit
- mapping assumption: `1 distance_unit = 1.0 km`
- inferred attenuation(model) = `0.694871` dB/km

## Reference comparison (illustrative ranges)

| medium | n_model | n_ref | n_delta | n_ratio | att_model(dB/km) | att_ref(dB/km) | att_ratio | note |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| vacuum | 1 | 1 | 0 | 1 | 0.694871 | 0 | 6.94871e+11 | ideal reference |
| air_STP_visible | 1 | 1.00027 | -0.00027 | 0.99973 | 0.694871 | n/a | n/a | weakly dispersive; near 1 |
| water_visible | 1 | 1.333 | -0.333 | 0.750188 | 0.694871 | n/a | n/a | strong wavelength dependence |
| silica_fiber_1550nm | 1 | 1.444 | -0.444 | 0.692521 | 0.694871 | 0.2 | 3.47436 | telecom low-loss window |
| silicon_1550nm | 1 | 3.48 | -2.48 | 0.287356 | 0.694871 | n/a | n/a | high index semiconductor |

## Caution
- This comparison is a blind probe sanity check, not a claim of one-to-one SI identification.
- The attenuation mapping depends on distance-unit calibration (`unit_to_km`).
