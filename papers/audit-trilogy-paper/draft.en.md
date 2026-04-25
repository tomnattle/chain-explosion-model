# Title (English)

Analysis Rule Sensitivity in Bell and GHZ Experiments:  
A Reproducible Audit Framework

## Abstract

Bell `S` and GHZ-style `F` readouts can be highly sensitive to analysis rules such as pairing windows, denominator policy, and post-selection constraints, even under a shared data context. Using two published audits over public artifacts, we show that Bell/CHSH on the same NIST event stream shifts from `S_strict=2.336276` to `S_standard=2.839387` (`Delta=+0.503111`) under protocol change, while GHZ three-body search under the current audited pipeline remains far from `F=4` (best fine-stage `F=0.085396`). We therefore provide a reproducible, ledger-style audit framework that treats analysis rules as first-class reported variables and keeps claim boundaries explicitly at the method level.

## 1. Introduction

High-correlation statistics are often discussed at claim level before analysis rules are fully audited. In practical Bell/GHZ pipelines, pairing windows, denominator definitions, sample inclusion, and gating can materially affect headline metrics. If such rules are not reported as explicit variables, bookkeeping effects can be mistaken for mechanism effects.

This paper is the synthesis layer of an audit trilogy. Rather than introducing a new ontology claim, we unify two published audit lines into a single reporting and interpretation framework designed for reproducibility, boundary awareness, and resistance to cherry-picking.

We call this the auditor effect: selecting pairing windows and denominator rules can effectively pre-condition the reported `S` value before any physical interpretation is made. Treating this effect as an explicit reporting target is one of the core contributions of the present framework.

### 1.1 Published Audit Records

- Bell audit DOI: `https://doi.org/10.5281/zenodo.19763028`
- GHZ audit DOI: `https://doi.org/10.5281/zenodo.19763473`

### 1.2 Scope and Boundary

- In scope: method-level synthesis, rule-sensitivity mapping, and claim-to-artifact traceability.
- Out of scope: declaring ontology-level replacement of standard quantum theory from current evidence.

## 2. Unified Audit Framework

### 2.1 Five Core Principles

1. **Metric registry first**: define statistic forms, denominators, and inclusion rules before interpretation.
2. **Protocol parallelism**: compute strict/standard and denominator A/B variants under shared context.
3. **Gate separation**: separate engineering computability from thesis-level claim criteria.
4. **Uncertainty binding**: attach CI/robustness context to every headline metric.
5. **Negative-result retention**: preserve failed branches as evidence, not noise.

### 2.2 Minimum Audit Record

- data source and preprocessing trace
- metric definition table
- protocol parameter table
- A/B comparison outputs
- robustness outputs (bootstrap/seed sweep)
- explicit boundary statement

## 3. Cross-Study Evidence Synthesis

### 3.1 Bell Line: Window and Protocol Sensitivity

On the same NIST completeblind stream, binary CHSH changes from:

- `S_strict=2.336276` (window `0.0`)
- `S_standard=2.839387` (window `15.0`)
- `Delta=+0.503111` from analysis-rule change

Bootstrap (`n=2000`) reports:

- `CI95_strict=[2.295151, 2.378669]`
- `CI95_standard=[2.820420, 2.857413]`

Because `2sqrt(2)=2.828427` lies inside the standard CI, this line does not support a Tsirelson-violation claim.

### 3.2 GHZ Line: Post-Selection and Denominator Sensitivity

Under the published audited configuration (`samples=80000`, `numba_cpu`, gated protocol), GHZ search reports:

- coarse best: `F=0.074761`
- fine best: `F=0.085396`
- target gap from `F=4`: `|err|=3.914604`

Current evidence does not show near-`4` behavior under this audited pipeline. Failure decomposition points to correlation-shape mismatch rather than coincidence sparsity as the dominant bottleneck.

### 3.3 Shared Risk Pattern

Both lines reveal the same structural risk: strong headline statistics can be produced or suppressed by analysis rules unless denominator policy, post-selection logic, and uncertainty are jointly reported.

## 4. Singles-Aware Diagnostics and the 2.828 Pathway

We define a singles-aware diagnostics layer to track denominator-side observability and interpretation confidence:

- `C_norm = coincidences / sqrt(singles_A * singles_B)`

The NCC normalization pathway can be written as:

`<cos(lambda-a) * cos(lambda-b)> / <cos^2(lambda)>`
`= [cos(Delta)/2] / [1/2]`
`= cos(Delta)`

This provides a deterministic geometric pathway to `S=2\sqrt{2}` without invoking non-locality at the level of the normalization identity itself.

This work treats the pathway to `2\sqrt{2}` in continuous, non-binarized normalization as a **testable normalization hypothesis** rather than a completed ontology proof. This pathway provides a mathematically deterministic bridge candidate between classical wave-style interference and quantum-like correlations, and may be partly explained by under-reported degrees of freedom in singles-aware normalization logic. The audit requirement is therefore strict: any such pathway must be reported with matched protocol definitions, data context, and uncertainty controls before interpretation-level promotion.

Primary evidence assets:

- `artifacts/reports/ncc_singles_bridge_real.png`
- `artifacts/reports/ncc_singles_bridge_real.json`
- `artifacts/reports/cnorm_e_delta_bridge_real.md`

## 5. Claim-to-Artifact Mapping

| Claim | Evidence | Confidence | Artifact / DOI |
|---|---|---|---|
| Pairing-window policy changes Bell `S` on the same event stream | `S_strict=2.336276`, `S_standard=2.839387`, `Delta=+0.503111` | High | `https://doi.org/10.5281/zenodo.19763028` |
| Bell interpretation must be CI-bound, not peak-only | `CI95_standard=[2.820420, 2.857413]` includes `2sqrt(2)` | High | `artifacts/reports/chsh_bootstrap_ci_standard15.json` |
| GHZ audited search does not approach `F=4` in current pipeline | best fine-stage `F=0.085396`, large target gap | High | `https://doi.org/10.5281/zenodo.19763473` |
| Singles-aware `C_norm` is a useful diagnostics bridge | real-data bridge assets available and reproducible | Medium | `artifacts/reports/ncc_singles_bridge_real.png` |
| Current evidence establishes ontology replacement | no direct evidence chain | Not supported | N/A |

## 6. Discussion

### 6.1 Numerical Layer

The observed statistic range is broad under rule changes (`S` shift in Bell; low `F` ceiling in current GHZ pipeline). Numerical values alone are therefore insufficient as claim-complete evidence.

### 6.2 Protocol Layer

Pairing windows, denominator definitions, and post-selection constraints are high-impact parameters. They should be logged and versioned as first-class experimental variables. While quantum mechanics emphasizes the observer effect on the state, our results suggest an equally critical auditor effect: selecting pairing windows and denominator rules can effectively pre-condition the reported `S` value before any physical interpretation is made.

### 6.3 Claim Layer

Current evidence supports method-level conclusions about analysis-rule sensitivity and audit necessity. It does not support direct ontology-level replacement claims.

## 7. Conclusion

### 7.1 Supported Conclusions

- Analysis rules are high-impact variables in Bell/GHZ reporting and must be explicit.
- Protocol-aware A/B reporting and CI binding are necessary for strong claims.
- A ledger-style audit workflow is reproducible and publication-ready with current artifacts.

### 7.2 Non-Supported Extrapolations

- This paper does not establish a complete ontology replacement for standard quantum theory.
- This paper does not claim that any single statistic (high `S` or low/high `F`) is interpretation-complete by itself.
- Our findings do not claim that entanglement is impossible; they indicate that current reporting standards for high-correlation events do not yet provide a noise-floor audit robust enough to exclude classical bookkeeping artifacts in all cases.

### 7.3 Next Work Package

- matched-seed full A/B summary (`none` vs `energy_weighted`) across Bell and GHZ lines
- expanded robustness (`>=20` seeds where applicable)
- unified command-level reproducibility appendix with environment hash lock

## Appendix A: Evidence and Reproducibility Pointers

### A.1 Public Records

- Bell DOI: `https://doi.org/10.5281/zenodo.19763028`
- GHZ DOI: `https://doi.org/10.5281/zenodo.19763473`

### A.2 Repository

- `https://github.com/tomnattle/chain-explosion-model`

### A.3 Key Local Artifacts

- `artifacts/reports/chsh_bootstrap_ci_standard15.json`
- `artifacts/reports/chsh_bootstrap_ci_strict0.json`
- `papers/ghz-threebody-paper/tables/table1_search_registry.md`
- `papers/ghz-threebody-paper/tables/table2_coarse_fine_topk.md`
- `papers/ghz-threebody-paper/tables/table3_robustness.md`
- `artifacts/reports/ncc_singles_bridge_real.png`
