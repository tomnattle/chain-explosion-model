# Title (Working)

From Protocol-Sensitive Statistics to Boundary-Aware Interpretation:  
A Unified Audit Framework for Bell and GHZ Analyses

## Abstract

This paper synthesizes two published audit studies into a single reproducible framework for evaluating high-correlation claims under protocol sensitivity. Building on Bell/CHSH and GHZ three-body audits, we formalize a ledger-style method that separates mechanism evidence from bookkeeping artifacts through explicit metric registration, denominator-policy tracking, gate-separated evaluation, and negative-result retention. Across both lines, we identify a shared risk: strong headline statistics can be materially affected by inclusion rules, post-selection settings, and denominator handling if uncertainty and protocol definitions are not jointly reported. We therefore provide a cross-study audit protocol with evidence traceability to public artifacts and DOI-linked records, and we state claim boundaries explicitly at the method level. Under the current evidence base, our contribution is a reproducible interpretation framework, not an ontology replacement claim.

## 1. Introduction

High-correlation results are often discussed at claim level before auditing how protocol choices shape the reported statistics. In practice, windowing, denominator definitions, sample inclusion, and gating choices can alter metric values substantially, even when source data context is shared.

This paper serves as the synthesis layer of an audit trilogy. Instead of introducing a new standalone metric, we integrate existing Bell and GHZ audit outcomes into a unified reporting and evaluation framework that is reproducible, boundary-aware, and resistant to cherry-picking.

### 1.1 Prior Published Audits

- Bell audit preprint DOI: `10.5281/zenodo.19763028`
- GHZ audit preprint DOI: `10.5281/zenodo.19763473`

### 1.2 Scope and Boundary

- In scope: methodological synthesis, protocol-risk mapping, evidence traceability, and reporting standards.
- Out of scope: declaring ontology-level replacement of standard quantum theory from current audit evidence alone.

## 2. Unified Audit Framework

### 2.1 Ledger-Style Core Principles

1. **Metric registry first**: define statistic forms, denominators, and inclusion rules before interpretation.
2. **Protocol parallelism**: compute strict/standard or A/B denominator variants under shared data context.
3. **Gate separation**: separate engineering computability from thesis-level claim criteria.
4. **Uncertainty binding**: require CI/robustness context for all headline metrics.
5. **Negative-result retention**: keep failed or non-supporting branches visible in the evidence chain.

### 2.2 Minimal Required Audit Record

- Data source and preprocessing trace
- Metric definition table
- Protocol parameter table
- A/B comparison outputs
- Robustness outputs (bootstrap/seed sweep)
- Claim-boundary statement

## 3. Cross-Study Synthesis (Bell vs GHZ)

### 3.1 Bell Line: Protocol-Window Sensitivity

Use published Bell evidence to summarize:

- strict vs standard `S` divergence under shared event stream
- CI interpretation boundary (including Tsirelson-related non-claim boundary)
- gate pass/fail split between engineering and thesis criteria

Evidence pointers:

- `artifacts/reports/chsh_bootstrap_ci_standard15.json`
- `artifacts/reports/chsh_bootstrap_ci_strict0.json`
- Zenodo Bell record: `https://zenodo.org/records/19763028`

### 3.2 GHZ Line: Post-Selection and Denominator Sensitivity

Use published GHZ evidence to summarize:

- denominator mode and gating effects under fixed pipeline
- two-stage search outcomes versus target gap
- robustness and failure-decomposition outcomes

Evidence pointers:

- `papers/ghz-threebody-paper/tables/table1_search_registry.md`
- `papers/ghz-threebody-paper/tables/table2_coarse_fine_topk.md`
- `papers/ghz-threebody-paper/tables/table3_robustness.md`
- Zenodo GHZ record: `https://zenodo.org/records/19763473`

### 3.3 Shared Failure Modes

Draft synthesis checklist (to be completed with final values):

1. bookkeeping-sensitive inflation risk
2. denominator-policy ambiguity risk
3. post-selection sensitivity risk
4. headline-statistic over-interpretation risk
5. missing-negative-results risk

## 4. Singles-Aware Normalization Diagnostics

This section defines a diagnostics layer for singles/correlation bookkeeping consistency checks.  
Use this section to connect existing bridge artifacts and explain how denominator-side fluctuations can affect interpretation confidence.

Primary artifact candidate:

- `artifacts/reports/ncc_singles_bridge_real.png`

Companion files (as applicable):

- `artifacts/reports/ncc_singles_bridge_real.json`
- `artifacts/reports/cnorm_e_delta_bridge_real.md`

## 5. Reproducibility and Evidence Traceability

### 5.1 Public Records

- Bell DOI: `https://doi.org/10.5281/zenodo.19763028`
- GHZ DOI: `https://doi.org/10.5281/zenodo.19763473`

### 5.2 Code Repository

- `https://github.com/tomnattle/chain-explosion-model`

### 5.3 Traceability Table (Template)

| Claim ID | Claim summary | Artifact path/DOI | Status |
|---|---|---|---|
| C1 | [fill] | [fill] | supported / not supported |
| C2 | [fill] | [fill] | supported / not supported |
| C3 | [fill] | [fill] | supported / not supported |

## 6. Discussion

Discuss what the synthesized audits support, what they do not support, and why boundary-aware interpretation is necessary for high-claim domains.  
Explicitly separate:

- numerical behavior
- protocol dependence
- claim-level interpretation

## 7. Conclusion

### 7.1 Supported Conclusions (method-level)

- [fill with evidence-linked method conclusions]

### 7.2 Non-Supported Extrapolations

- [fill with explicit non-claims]

### 7.3 Next Work Package

- matched-seed full A/B summary across Bell and GHZ lines
- expanded robustness (`>=20` seeds where applicable)
- unified appendix for command-level reproducibility

## Appendix A: Submission-Ready Checklist

- [ ] All strong claims mapped to artifacts/DOIs
- [ ] CI/robustness attached to headline statistics
- [ ] Negative-result branches preserved
- [ ] Boundary statement included
- [ ] Terminology consistent with `papers/TERMINOLOGY.md`
- [ ] Repository URL and record DOIs included
