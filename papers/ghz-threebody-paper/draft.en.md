# Title (English)

Denominator Recovery and Post-Selection Audit in a GHZ Three-Body Model: A Two-Stage Search-Based Mechanism Check

## Abstract

This work audits high-correlation claims in a GHZ three-body model by explicitly separating mechanism effects from bookkeeping effects. We compare denominator settings (`none` vs `energy_weighted`) under a unified pipeline, run a two-stage search (90 deg coarse + 2 deg fine), and evaluate the `F`-`coincidence_rate` trade-off. Under the current setup (`samples=80000`, `numba_cpu`, gated protocol), the best fine-stage candidate reaches only `F=0.085396`, still far from the target `F=4` with `|err|=3.914604`. Failure decomposition consistently points to correlation-shape mismatch rather than coincidence sparsity as the dominant bottleneck. We therefore report a method-level audit conclusion and do not promote ontology-level claims.

## 1. Introduction

GHZ-type constructions are often used to discuss the boundary between classical and non-classical correlations. However, when detector thresholds, shared perturbations, and coincidence post-selection are involved, metric definitions can materially affect reported correlation strength. Comparing only final `F` values without auditing denominator logic and sample inclusion rules may conflate bookkeeping artifacts with mechanism improvements.

To address this, we use a penetration-style audit protocol: (i) register metric definitions explicitly, (ii) scan parameter space with fixed rules instead of cherry-picking, and (iii) jointly inspect `F` and `coincidence_rate` to identify potential selection-driven inflation. The contribution of this paper is a reproducible GHZ audit workflow with a transparent negative-result evidence chain.

### 1.1 Related Work (Placeholder)

References will be added along four tracks:

1. standard GHZ multi-party witness definitions and implementations;
2. detector-threshold, post-selection, and coincidence-collapse effects;
3. parameter-search and robustness-evaluation practices in foundational modeling;
4. reporting norms for negative results and boundary-aware claims.

## 2. Methods

### 2.1 Metrics and Denominator Mechanism

We register two denominator modes in the same simulation protocol:

1. `none`: conditional mean on gated samples without extra energy weighting;
2. `energy_weighted`: weighted conditional mean where weights are the product of absolute local response amplitudes.

Both modes share the same event generation and coincidence gating, differing only in denominator/weight bookkeeping. Importantly, our ternary-output gated statistic is not identical to the standard binary GHZ witness; results should be interpreted within this audited protocol.

### 2.2 Two-Stage Search Protocol

The search spans `pump_gain` and four context phase offsets (`XXX/XYY/YXY/YYX`).

- Coarse stage: `90 deg` phase grid over the full configured range;
- Fine stage: `2 deg` local neighborhood refinement around coarse Top-k candidates;
- Constraint: a minimum `coincidence_rate` floor is enforced to avoid extreme sparse-event configurations;
- Robustness: bootstrap and seed-sweep statistics are logged together with target-attainment decomposition.

## 3. Results

### 3.1 Main Results

With `samples=80000`, `threshold=0.35`, `pump_gain=0.45`, `denominator_mode=energy_weighted`, and backend `numba_cpu`:

- default context setting yields `F=-0.001124` with `coincidence_rate=0.5844`;
- coarse search best candidate: `F=0.074761` (`R=0.5691`);
- fine search best candidate: `F=0.085396` (`R=0.6704`);
- distance to target remains large: `|err|=3.914604` from `F=4`.

No nonlinear jump toward `F=4` is observed under the current protocol. Suggested figure mapping:

- Figure 1: `fig1_f_vs_threshold.png`
- Figure 2: `fig2_mechanism_heatmap.png`

### 3.2 Trade-off and Robustness

Robustness summary:

- bootstrap: `draws=10`, `F_context_mean_bootstrap_sd=0.056036`;
- seed sweep: `count=3`, `seed_sweep_context_f_sd=0.010787`;
- failure decomposition: both coarse and fine stages are labeled as `correlation shape mismatch dominates`.

For trade-off analysis, `F_context_pump_gated` does not trend toward 4 in any `R` bucket. Bin means range from `-0.019317` in `[0.0,0.2)` to `-0.001344` in `[0.8,1.0]`, staying close to zero overall. Suggested mapping:

- Figure 3: `fig3_f_vs_coincidence_tradeoff.png`
- Table 1: search configuration registry
- Table 2: coarse/fine Top-k summary
- Table 3: robustness statistics

## 4. Discussion

The current evidence indicates that, within the tested model family, raising `F` is mainly limited by correlation-shape structure rather than by simple sample-thinning effects. Fine-stage search improves over coarse-stage peaks, but only marginally and still far below the target level.

From an audit perspective, denominator recovery is useful because it explicitly decouples numerator correlation from denominator/sample bookkeeping. Under this decoupling, no near-4 behavior emerges, which weakens a bookkeeping-only explanation for extreme values.

Limitations remain: seed count is still small, and a full system-level A/B summary for `none` vs `energy_weighted` is still pending. Larger sample sizes and broader seed coverage are required for stronger statistical confidence.

## 5. Conclusion

Supported claims:

1. Under the current audited GHZ protocol, we do not observe evidence of `F` approaching 4;
2. target-failure decomposition favors correlation-shape mismatch over coincidence sparsity;
3. denominator recovery improves interpretability and bookkeeping transparency.

Non-supported claims:

- this does not universally falsify all GHZ-like model variants;
- this audited metric should not be treated as a strict replacement of the standard GHZ witness.

Next steps:

- complete strict A/B runs (`none` vs `energy_weighted`) with matched seeds and grids;
- extend robustness to `>=20` seeds;
- expand high-sample and finer-neighborhood scans.

## Appendix

Data outputs:

- `artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_SUMMARY.md`
- `artifacts/ghz_threshold_experiment/AUDIT_REPORT.md`
- `artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_RESULTS.json`
- figures: `ghz_threshold_F_vs_T.png`, `ghz_threshold_mechanism_heatmap.png`

Reproducibility command used for the current reported run:

```bash
python scripts/explore/ghz_threshold/explore_ghz_threshold_pipeline.py --compute-backend numba_cpu --samples 80000 --search --search-samples 25000 --search-gain-steps 4 --search-phase-step-deg 90 --search-top-k 20 --fine-search --fine-seed-k 5 --fine-phase-half-span-deg 4 --fine-phase-step-deg 2 --fine-gain-steps 4 --audit-bootstrap-draws 10 --audit-bootstrap-subsample 12000 --audit-seeds 0,1,2 --out-dir artifacts/ghz_threshold_experiment
```

Terminology standard:

- Shared terminology registry: `papers/TERMINOLOGY.md`.
