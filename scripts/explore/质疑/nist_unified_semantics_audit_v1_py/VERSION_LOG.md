# Version Log (Challenge Handling)

## v1
- Base script: `scripts/explore/nist_unified_semantics_audit_v1.py`
- Initial findings generated.
- Known issues entered from `a.txt/b.txt/c.txt`.

## v2
- New script: `scripts/explore/nist_unified_semantics_audit_v2.py`
- Fixes:
  - Added `external_clock_bucket_all` as primary external-clock mode.
  - Kept nearest modes but marked as `loophole_probe`.
  - Split output semantics: `binary_chsh` vs `continuous_corr`.
- Key result:
  - `external_clock_bucket_all S_binary_chsh = 2.775687`
  - `external_clock_nearest_1to1 S_binary_chsh = 2.808666`

## v3
- New script: `scripts/explore/nist_unified_semantics_audit_v3.py`
- Fixes:
  - Added `cont_norm_fixedden`.
  - Added same-index multi-event diagnostics.
  - Added one-hot filtering diagnostics.
- Key diagnostics:
  - `multi_event_t_rate = 0.0`
  - `drop_ratio_A ~ 6.45%`, `drop_ratio_B ~ 6.16%`

## v4
- New script: `scripts/explore/nist_unified_semantics_audit_v4.py`
- Fixes:
  - Bucket edge offset sensitivity scan (`offset=0..14`).
  - Strict same-index mode (`drop_multi_event_t`).
  - Built-in bootstrap CI for key CHSH outputs.
  - Fixed-den split train/test to reduce leakage concern.
  - Anchor symmetry check (A-anchor vs B-anchor).
- Key diagnostics:
  - `external offset S_binary range = 0.022401`
  - `A/B anchor delta_abs = 0.001356`
  - same-index CI and event-anchor CI produced in JSON.

## v4 (other core scripts)
- New script: `scripts/explore/nist_revival_20pct_closure_v4.py`
  - Closure aligned to v4 semantics (pure bucket primary, explicit split)
  - Robust second-sample probe with readable/error reason
  - Outputs:
    - `results/nist_revival_20pct_closure_v4.json`
    - `results/nist_revival_20pct_closure_v4.md`

- New script: `scripts/explore/nist_same_index_quantization_sweep_v4.py`
  - Added bootstrap CI for each quantization level
  - Added `norm_fixedden` with train/test split denominator
  - Added strict same-index diagnostic fields
  - Output:
    - `results/same_index_quantization_sweep_v4.json`

