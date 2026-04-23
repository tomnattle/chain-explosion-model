# GHZ Conditional NCC Audit

- samples: **400000**, seed: **0**
- phase scan steps: **36**
- bootstrap: draws=**200**, subsample=**100000**

| metric family | E(XXX) | E(XYY) | E(YXY) | E(YYX) | F |
|---|---:|---:|---:|---:|---:|
| quantum_reference | 1.000000 | -1.000000 | -1.000000 | -1.000000 | 4.000000 |
| unconditional_ncc | -0.000393 | 0.000617 | 0.000617 | 0.000617 | -0.002246 |
| conditional_ncc | -0.000571 | -0.000571 | 0.000597 | 0.000597 | -0.001193 |

## Bootstrap 95% CI (conditional NCC)

- E(XXX): [-0.003522, 0.001992]
- E(XYY): [-0.003522, 0.001992]
- E(YXY): [-0.003029, 0.004262]
- E(YYX): [-0.003029, 0.004262]
- F: [-0.008525, 0.006058]

## Two-body to three-body analogy checklist

| step | two-body Bell success path | GHZ conditional test counterpart |
|---|---|---|
| 1 | keep continuous response | keep continuous response (X/Y bases) |
| 2 | NCC normalization on pair | conditional NCC on (B,C | sign(A)) |
| 3 | recover curved correlator | test whether conditional split restores non-zero GHZ F |