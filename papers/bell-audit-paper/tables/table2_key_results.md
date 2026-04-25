# Table 2: Key CHSH Results, Uncertainty, and Gate Status

| config | S_strict | S_standard | Delta(standard-strict) | CI95_strict | CI95_standard | engineering_pass | thesis_pass | thesis_reason |
|---|---:|---:|---:|---|---|---|---|---|
| NIST (same event stream) | 2.336276 | 2.839387 | 0.503111 | [2.295151, 2.378669] | [2.820420, 2.857413] | True | False | strict S=2.336276 > strict_max_S=2.020000 |
| SimFallback | 2.017316 | 2.008601 | -0.008715 | NA | NA | True | False | standard S=2.008601 not greater than strict S=2.017316 (require_standard_S_gt_strict_S) |

Notes:
- NIST CI uses bootstrap (`n=2000`) on binary CHSH at fixed windows (`strict=0.0`, `standard=15.0`).
- `2sqrt(2)=2.828427` lies inside `CI95_standard`; no Tsirelson-violation claim is made.