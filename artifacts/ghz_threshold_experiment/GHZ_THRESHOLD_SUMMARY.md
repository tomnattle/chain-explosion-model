# GHZ Threshold Audit (new experiment branch)

- samples: **250000**, seed: **0**
- threshold(default row): **0.350**
- shared pump gain(default row): **0.450**
- gated scan coincidence floor: **0.010**
- context phase offsets [XXX,XYY,YXY,YYX]: **[0.00, 3.14, 3.14, 3.14]**

| model | E(XXX) | E(XYY) | E(YXY) | E(YYX) | F | note |
|---|---:|---:|---:|---:|---:|---|
| QM_reference | 1.000000 | -1.000000 | -1.000000 | -1.000000 | 4.000000 | Ideal GHZ Pauli benchmark |
| continuous_baseline_ncc | -0.002629 | -0.001067 | -0.001067 | -0.001067 | 0.000573 | No detector threshold |
| threshold_binary_mean | -0.001148 | 0.000336 | 0.000336 | 0.000336 | -0.002156 | threshold=0.350 |
| threshold_shared_pump_mean | -0.001396 | -0.000792 | -0.000792 | -0.000792 | 0.000980 | threshold=0.350, pump_gain=0.450 |
| threshold_binary_gated_mean | -0.001486 | 0.000618 | 0.000618 | 0.000618 | -0.003339 | threshold=0.350, coincidence_rate=0.6011 |
| threshold_shared_pump_gated_mean | -0.001848 | -0.001516 | -0.001516 | -0.001516 | 0.002700 | threshold=0.350, pump_gain=0.450, coincidence_rate=0.5806 |
| context_pump_gated_mean | -0.001848 | -0.003681 | -0.003681 | -0.003681 | 0.009194 | threshold=0.350, pump_gain=0.450, ctx_phases=[0.00,3.14,3.14,3.14], coincidence_rate=0.5808 |

## Interpretation guardrails

- Threshold tracks use ternary detector output {-1,0,+1}; F here is not directly Mermin's binary ±1 witness.
- Gated tracks apply coincidence post-selection (all three clicked), then conditional mean on survived events.
- For very high threshold, coincidence rate can collapse; scan values are clamped to 0 when rate < floor.
- This branch is for mechanism audit (detector nonlinearity + shared source perturbation), not claim replacement.

## Coarse search

- checked: **1536** combos, search_samples: **80000**
- best F: **0.027115** at gain=1.200, phases=[4.71,1.57,1.57,1.57], R=0.5701
- best |F|: **0.030356** (F=-0.030356) at gain=0.760, phases=[1.57,4.71,4.71,4.71], R=0.5220
- closest to target F=4.000: F=0.027115, |err|=3.972885, gain=1.200, phases=[4.71,1.57,1.57,1.57], R=0.5701
- fine checked: **2025** local combos
- fine closest target: F=0.042322, |err|=3.957678, gain=1.400, phases=[4.71,2.36,2.36,2.36], R=0.6711