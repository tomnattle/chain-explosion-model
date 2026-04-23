# AUDIT REPORT

Protocol-sensitivity audit for GHZ-style statistics under detector nonlinearity and event-selection rules.

- threshold: **0.3500**
- pump_gain: **0.4500**
- coincidence_rate_floor: **0.0100**
- denominator_mode: **energy_weighted**

## Table 1: Metric Definition Registry

| model | statistic definition | sample inclusion | denominator / normalization |
|---|---|---|---|
| continuous_baseline_ncc | `E=<ABC>/sqrt(<A^2><B^2><C^2>)` | all events | NCC denominator |
| threshold_binary_mean | `E=<ABC>` | all events after ternary detector | none |
| threshold_shared_pump_mean | `E=<ABC>` with shared pump term | all events after ternary detector | none |
| threshold_binary_gated_mean | `E=<ABC | all-click>` | coincidence-only (all three click) | conditional mean |
| threshold_shared_pump_gated_mean | `E=<ABC | all-click>` with shared pump term | coincidence-only (all three click) | conditional mean |
| context_pump_gated_mean | `E=<ABC | all-click>` with context phase offsets | coincidence-only (all three click) | conditional mean |

## Table 2: Inclusion / Coincidence Registry

| model | F | avg coincidence rate | note |
|---|---:|---:|---|
| threshold_binary_gated_mean | -0.013406 | 0.6158 | threshold=0.350, coincidence_rate=0.6158 |
| threshold_shared_pump_gated_mean | -0.073863 | 0.5846 | threshold=0.350, pump_gain=0.450, coincidence_rate=0.5846 |
| context_pump_gated_mean | 0.060826 | 0.5760 | threshold=0.350, pump_gain=0.450, ctx_phases=[0.00,3.14,3.14,3.14], coincidence_rate=0.5760, backend=numpy |

## Table 3: Local Sensitivity Around Operating Threshold

| series | value at threshold | local dF/dT |
|---|---:|---:|
| F_threshold_binary | 0.015500 | 0.187105 |
| F_threshold_shared_pump | -0.020250 | -0.145526 |
| F_threshold_binary_gated | 0.027718 | 0.448448 |
| F_threshold_shared_pump_gated | -0.072918 | 0.054391 |
| F_context_pump_gated | 0.059998 | 0.166244 |

## Table 4: Robustness Snapshot

| item | value |
|---|---:|
| bootstrap_draws | 5 |
| bootstrap_subsample | 1000 |
| F_context_mean_bootstrap_sd | 0.149360 |
| seed_sweep_count | 3 |
| seed_sweep_context_f_sd | 0.034850 |
| seed_sweep_context_f_p05 | -0.046618 |
| seed_sweep_context_f_p95 | 0.022624 |

## Table 5: Target-Attainment Failure Decomposition

| stage | candidate F | target F | abs gap | coincidence R | R-floor margin | likely bottleneck |
|---|---:|---:|---:|---:|---:|---|
| coarse | 0.174347 | 4.000000 | 3.825653 | 0.557750 | 0.547750 | correlation shape mismatch dominates |
| fine | 0.238993 | 4.000000 | 3.761007 | 0.599000 | 0.589000 | correlation shape mismatch dominates |

## Table 6: Correlation vs Coincidence (selection trade-off)

| bucket (R) | mean F_context_pump_gated | count |
|---|---:|---:|
| [0.0,0.2) | 0.063877 | 22 |
| [0.2,0.4) | 0.026521 | 16 |
| [0.4,0.6) | 0.042019 | 14 |
| [0.6,0.8) | 0.065274 | 14 |
| [0.8,1.0] | 0.051119 | 14 |

## Table 7: Global Perturbation Robustness

| item | value |
|---|---:|
| perturb_draws | 20 |
| target_abs_f | 0.080000 |
| success_ratio | 0.000000 |
| f_sd | 0.007645 |
| max_abs_f | 0.066994 |

## Table 8: Null-Model Sanity Check

| item | value |
|---|---:|
| null_draws | 20 |
| null_f_sd | 0.108830 |
| null_max_abs_f | 0.210063 |
| null_false_positive_ratio | 0.500000 |

## Table 9: Matched-Protocol QM Comparison

| item | value |
|---|---:|
| qm_reference_f | 4.000000 |
| context_operating_f | 0.060826 |
| context_to_qm_efficiency | 0.015206 |
| context_best_abs_f | 0.365276 |
| context_best_to_qm_efficiency | 0.091319 |

### Audit Note

This report audits statistical sensitivity and bookkeeping assumptions. It does not, by itself, claim or refute ontology.
