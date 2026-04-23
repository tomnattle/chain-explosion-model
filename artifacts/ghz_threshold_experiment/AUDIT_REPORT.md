# AUDIT REPORT

Protocol-sensitivity audit for GHZ-style statistics under detector nonlinearity and event-selection rules.

- threshold: **0.3500**
- pump_gain: **0.4500**
- coincidence_rate_floor: **0.0100**

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
| threshold_binary_gated_mean | -0.003339 | 0.6011 | threshold=0.350, coincidence_rate=0.6011 |
| threshold_shared_pump_gated_mean | 0.002700 | 0.5806 | threshold=0.350, pump_gain=0.450, coincidence_rate=0.5806 |
| context_pump_gated_mean | 0.009194 | 0.5808 | threshold=0.350, pump_gain=0.450, ctx_phases=[0.00,3.14,3.14,3.14], coincidence_rate=0.5808 |

## Table 3: Local Sensitivity Around Operating Threshold

| series | value at threshold | local dF/dT |
|---|---:|---:|
| F_threshold_binary | -0.001880 | -0.041413 |
| F_threshold_shared_pump | 0.001016 | 0.008815 |
| F_threshold_binary_gated | -0.002826 | -0.082477 |
| F_threshold_shared_pump_gated | 0.002771 | 0.034430 |
| F_context_pump_gated | 0.009859 | -0.008537 |

## Table 4: Robustness Snapshot

| item | value |
|---|---:|
| bootstrap_draws | 50 |
| bootstrap_subsample | 30000 |
| F_context_mean_bootstrap_sd | 0.021665 |
| seed_sweep_count | 3 |
| seed_sweep_context_f_sd | 0.014781 |

## Table 5: Target-Attainment Failure Decomposition

| stage | candidate F | target F | abs gap | coincidence R | R-floor margin | likely bottleneck |
|---|---:|---:|---:|---:|---:|---|
| coarse | 0.027115 | 4.000000 | 3.972885 | 0.570069 | 0.560069 | correlation shape mismatch dominates |
| fine | 0.042322 | 4.000000 | 3.957678 | 0.671097 | 0.661097 | correlation shape mismatch dominates |

### Audit Note

This report audits statistical sensitivity and bookkeeping assumptions. It does not, by itself, claim or refute ontology.
