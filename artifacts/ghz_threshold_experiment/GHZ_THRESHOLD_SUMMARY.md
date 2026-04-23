# GHZ Threshold Audit (new experiment branch)

- samples: **4000**, seed: **0**
- compute backend: requested **numpy**, active **numpy**
- threshold(default row): **0.350**
- shared pump gain(default row): **0.450**
- gated scan coincidence floor: **0.010**
- context phase offsets [XXX,XYY,YXY,YYX]: **[0.00, 3.14, 3.14, 3.14]**

| model | E(XXX) | E(XYY) | E(YXY) | E(YYX) | F | note |
|---|---:|---:|---:|---:|---:|---|
| QM_reference | 1.000000 | -1.000000 | -1.000000 | -1.000000 | 4.000000 | Ideal GHZ Pauli benchmark |
| continuous_baseline_ncc | -0.008075 | -0.000807 | -0.000807 | -0.000807 | -0.005655 | No detector threshold |
| threshold_binary_mean | -0.000500 | -0.004750 | -0.004750 | -0.004750 | 0.013750 | threshold=0.350 |
| threshold_shared_pump_mean | 0.004000 | 0.008000 | 0.008000 | 0.008000 | -0.020000 | threshold=0.350, pump_gain=0.450 |
| threshold_binary_gated_mean | -0.006763 | 0.002215 | 0.002215 | 0.002215 | -0.013406 | threshold=0.350, coincidence_rate=0.6158 |
| threshold_shared_pump_gated_mean | -0.001998 | 0.023955 | 0.023955 | 0.023955 | -0.073863 | threshold=0.350, pump_gain=0.450, coincidence_rate=0.5846 |
| context_pump_gated_mean | -0.001998 | -0.020941 | -0.020941 | -0.020941 | 0.060826 | threshold=0.350, pump_gain=0.450, ctx_phases=[0.00,3.14,3.14,3.14], coincidence_rate=0.5760, backend=numpy |

## Interpretation guardrails

- Threshold tracks use ternary detector output {-1,0,+1}; F here is not directly Mermin's binary ±1 witness.
- Gated tracks apply coincidence post-selection (all three clicked), then conditional mean on survived events.
- For very high threshold, coincidence rate can collapse; scan values are clamped to 0 when rate < floor.
- This branch is for mechanism audit (detector nonlinearity + shared source perturbation), not claim replacement.

## v11 audit blocks

- perturbation success ratio (|F|>=0.080): **0.0000** over 20 draws
- null-model false-positive ratio (|F|>=0.080): **0.5000** over 20 draws
- matched-protocol efficiency vs QM: **0.015206** (operating point)
- best searched efficiency vs QM: **0.091319**

## Coarse search

- checked: **1536** combos, search_samples: **1000**
- coarse phase step: **90.0 deg**
- best F: **0.174347** at gain=1.200, phases=[1.57,3.14,3.14,3.14], R=0.5577
- best |F|: **0.365276** (F=-0.365276) at gain=0.980, phases=[4.71,1.57,1.57,1.57], R=0.5358
- closest to target F=4.000: F=0.174347, |err|=3.825653, gain=1.200, phases=[1.57,3.14,3.14,3.14], R=0.5577
- fine checked: **164025** local combos
- fine closest target: F=0.238993, |err|=3.761007, gain=1.300, phases=[1.71,3.28,3.28,3.28], R=0.5990