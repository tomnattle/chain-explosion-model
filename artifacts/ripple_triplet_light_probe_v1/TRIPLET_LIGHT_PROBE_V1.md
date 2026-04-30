# Ripple Triplet Light Probe v1

## Config
- mu=1.55, rho=2.35, eta=0.08
- exponents: expo_mu=0.25, expo_rho=0.25, k_eta=0.0
- reference: (mu_ref, rho_ref, eta_ref)=(1.55, 2.35, 0.08)

## Core derived values
- effective speed ratio: v/c_ref = `1.00000000`
- effective speed: v_eff = `299792458.000` m/s
- effective refractive-like index: n_eff = `1.00000000`

## Attenuation examples
- x=12.000: amp_ratio=0.38289289, intensity_ratio=0.14660696
- x=26.000: amp_ratio=0.12493021, intensity_ratio=0.01560756

## Notes
- This is a model-internal probe for comparison and calibration.
- `distance_unit` is in model path units, not automatically SI meters.
- Next step: compare v_eff and attenuation curve against selected mainstream media datasets.
