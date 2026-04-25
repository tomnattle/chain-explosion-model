# Title (English)

Denominator-Audit Robustness Analysis for Bell/CHSH Statistics: A Reconciliation Study of Strict vs Standard Protocols

## Abstract

We present a denominator-audit framework for Bell/CHSH statistics to disentangle mechanism effects from protocol-bookkeeping effects under a shared data context. The protocol compares strict and standard definitions in parallel and separates evaluation into an engineering gate (computability and basic data sufficiency) and a thesis gate (claim-level preregistered criteria). On the same NIST completeblind event stream, binary CHSH yields `S_strict=2.336276` (window `0.0`) and `S_standard=2.839387` (window `15.0`), i.e., `Delta=+0.503111` from pairing-rule change alone. Bootstrap (`n=2000`) gives `CI95_strict=[2.295151, 2.378669]` and `CI95_standard=[2.820420, 2.857413]`; because `2sqrt(2)=2.828427` lies inside the standard CI, we do not claim Tsirelson violation. A simulated fallback run also shows that `S_standard` does not necessarily exceed `S_strict`, reinforcing protocol sensitivity. These outcomes indicate that high `S` values alone are not claim-complete evidence. We therefore report a method-level, boundary-aware conclusion: Bell/CHSH claims should be interpreted through protocol definitions, uncertainty intervals, and retained negative results, rather than through peak statistics alone.

## 1. Introduction

Bell/CHSH statistics are widely used to discuss classical versus non-classical boundaries. In practical pipelines, however, pairing windows, normalization choices, and inclusion rules can significantly affect reported `S` values. If one only reads final `S` peaks, bookkeeping-driven shifts may be mistaken for mechanism-level breakthroughs.

This work restores an auditable ledger view: strict and standard protocols are computed in parallel, engineering computability is separated from thesis-level claim criteria, and both positive and negative outcomes are retained. The contribution is an accountable protocol-audit workflow, not an ontology replacement thesis.

### 1.1 Related Work (Placeholder)

References will be organized along four strands:

1. standard Bell/CHSH experimental definitions and reporting practice;
2. detector-window, efficiency, and post-selection impacts on reported correlations;
3. preregistration and reproducibility frameworks in foundational experiments;
4. methodological value of negative results in high-claim domains.

## 2. Methods

### 2.1 Metric Registry

We use the standard CHSH form `S = E(a,b)+E(a,b')+E(a',b)-E(a',b')`, while explicitly registering two protocol definitions:

1. strict: tighter coincidence/pairing window;
2. standard: wider conventional window.

Both are computed from the same source context, but with different inclusion rules. We treat this as protocol-difference auditing, not as interchangeable evidence.

### 2.2 Experimental Protocol

Two representative result bundles are currently included:

- NIST-index (real CSV source):
  - strict: `pair_count=136632`, `S=2.336276`
  - standard: `pair_count=148670`, `S=2.839387`
  - strict bootstrap CI95 (`n=2000`): `[2.295151, 2.378669]`
  - standard bootstrap CI95 (`n=2000`): `[2.820420, 2.857413]`
  - rule-driven delta: `S_standard - S_strict = +0.503111`
- simulated fallback:
  - strict: `S=2.017316`
  - standard: `S=2.008601`

We use two gate layers:

- engineering gate: pair-count and computability checks;
- thesis gate: strict upper bound and cross-protocol relation constraints.

This separation prevents direct promotion of “computable outputs” into “thesis-level claims.”

## 3. Results

### 3.1 Main Results

In the NIST-index run, engineering gates pass but thesis gates fail, primarily because `S_strict=2.336276` violates the preregistered strict upper bound (`strict_max_S=2.02`). At the same time, the strict-standard gap (`+0.503111`) is much larger than finite-sample noise in either branch, indicating a systematic analysis-rule sensitivity. Therefore:

1. current evidence supports protocol-level computability with high `S`;
2. current evidence does not satisfy preregistered thesis closure criteria.

Suggested assets:

- Figure 1: strict vs standard `S` comparison;
- Table 1: protocol configuration and gate criteria.

### 3.2 Robustness

The simulated fallback run shows `S_standard` not exceeding `S_strict`, highlighting sensitivity to protocol definitions. Bootstrap CIs on real data further constrain interpretation: standard-window `S` is high but its CI still includes `2sqrt(2)`, so this result should not be presented as Tsirelson violation. This reinforces a core audit principle: retain negative outcomes and avoid cherry-picking only high-`S` views.

Suggested assets:

- Figure 2: joint view of pair count vs `S`;
- Figure 3: strict-standard delta across configurations;
- Table 2: key metrics with gate pass/fail status.

## 4. Discussion

The evidence naturally separates into three layers:

1. numerical layer: high `S` values can appear;
2. protocol layer: such values are protocol-definition dependent;
3. claim layer: thesis gates are independent and may still fail.

From an audit perspective, failed thesis gates are not wasted outputs but essential falsification evidence that constrains over-interpretation.

## 5. Conclusion

Supported claims:

- Bell/CHSH outputs are highly sensitive to protocol bookkeeping;
- engineering computability can hold while thesis closure fails;
- strict-standard reconciliation is mandatory before strong claims.

Non-supported extrapolations:

- a single high `S` is insufficient for mechanism-level proof;
- engineering pass should not be interpreted as thesis pass.

Boundary statement (explicit):

- This work demonstrates analysis-rule sensitivity (especially pairing-window and metric-definition sensitivity) in Bell/CHSH readouts.
- This work does not, by itself, establish any replacement ontology for quantum theory.

Future work:

- complete full A/B denominator audits (`none` vs `energy_weighted`);
- expand multi-seed analyses (bootstrap CI has been added in this version);
- finalize figure/table package and related-work integration.

## Appendix

Code repository (public):

- https://github.com/tomnattle/chain-explosion-model

Currently cited result files:

- `artifacts/reports/chsh_battle_result_nist.json`
- `artifacts/reports/chsh_battle_result.json`
- `artifacts/reports/chsh_bootstrap_ci_standard15.json`
- `artifacts/reports/chsh_bootstrap_ci_strict0.json`

To be added:

- reproducibility command registry;
- figure-generation scripts;
- locked environment/version manifest.

Terminology standard:

- Shared terminology registry: `papers/TERMINOLOGY.md`.
