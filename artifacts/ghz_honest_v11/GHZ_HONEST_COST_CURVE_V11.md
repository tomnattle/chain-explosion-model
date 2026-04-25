# GHZ Honest Cost-Benefit Curve — v11

**No anchors. No illustrative curves. Data only.**

- seed: `0`
- samples: `200000`
- score function: `abs(A_XXX) * abs(B_XXX) * abs(C_XXX)` (preregistered)
- scheme3 best phi: `5.759587` rad (honest grid search over 360 points)
- scheme3 |F| at 100% retention: `0.005806`

## Full-retention F values (retention = 1.00, no selection)

| scheme | F |
|---|---:|
| scheme1_four_lambdas | -0.001187 |
| scheme2b_sphere_bloch | -0.002081 |
| scheme3_best_phi=5.7596 | -0.005806 |

## F at each retention level

| retention | scheme1 F | scheme2b F | scheme3 F |
|---:|---:|---:|---:|
| 0.05 | 0.017987 | -0.009667 | 0.005523 |
| 0.10 | 0.006118 | 0.000582 | 0.002569 |
| 0.15 | 0.002735 | 0.001739 | -0.001762 |
| 0.20 | 0.001925 | 0.011140 | -0.000917 |
| 0.25 | 0.001392 | -0.001296 | -0.000284 |
| 0.30 | -0.001882 | -0.008679 | 0.003531 |
| 0.35 | -0.003799 | -0.000854 | -0.000474 |
| 0.40 | -0.009486 | 0.003490 | -0.003439 |
| 0.45 | -0.008663 | -0.001321 | -0.008329 |
| 0.50 | -0.012188 | -0.001290 | -0.006178 |
| 0.55 | -0.016235 | -0.000656 | -0.013041 |
| 0.60 | -0.011684 | -0.000231 | -0.018177 |
| 0.65 | -0.010304 | -0.003183 | -0.011453 |
| 0.70 | -0.007394 | -0.001239 | -0.007353 |
| 0.75 | -0.006585 | -0.001397 | -0.009699 |
| 0.80 | -0.005988 | -0.002631 | -0.008550 |
| 0.85 | -0.005668 | -0.002117 | -0.005446 |
| 0.90 | -0.003319 | -0.002075 | -0.004895 |
| 0.95 | -0.001412 | -0.002170 | -0.004629 |
| 1.00 | -0.001187 | -0.002081 | -0.005806 |

## Interpretation guardrails

- F values above are NCC-continuous, not binary Mermin.  LHV binary bound is F ≤ 2; NCC scale is different.
- Score-based selection is a proxy for 'events with strongest local wave-front product'.  It is not the same as random subsampling.
- If F increases with stricter selection, that demonstrates selection can amplify apparent correlation (known phenomenon).  It does NOT prove the physical model is correct.
- If F is flat across retention levels, the score function does not strongly filter by correlation strength.
- QM reference F = 4 (binary ±1 Mermin).  NCC continuous outcomes will not reach 4 by construction.

## Anti-cheat checklist

- [x] Seed logged before data generation
- [x] Retention grid fixed before running
- [x] Score function defined and logged before running
- [x] No F target or retention endpoint pre-set
- [x] All three schemes run and saved unconditionally
- [x] Negative / low F results are NOT suppressed