# V10 Failure Anatomy

- data_dir: `artifacts/ripple_quantum_tests_v9_realdata_input_template`
- locked triplet: μ=1.55, ρ=2.35, η=0.08

## Absorption
- full-span R² (locked): `0.593904`
- full-span NRMSE (locked): `0.189053`
- d2y RMS (curvature proxy): `2.17974e-06`

**Diagnosis:**
- Diagnostic Lorentz bump materially reduces error at LOCKED triplet → missing resonance/broadband loss term in alpha(omega).

## Group delay
- full-span R² (locked): `0.496390`
- corr(tau, |dn/dω|): `0.9973242212102806`
- corr(tau, model_tau): `0.9998139678028224`

**Diagnosis:**
- (none)

## Dispersion (reference)
- full-span R² (locked): `-5.566843`

## Reflectance
- full-span R² (locked): `0.973154`

## Next step (v10 → v11)
- If Lorentz diagnostic helps: extend alpha(omega) with a bounded oscillator term (audit-only branch).
- If tau vs dn/dω decorrelates: regenerate group_delay from a single phase model or unify omega grid and units.