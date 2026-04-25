# Zenodo Metadata Prep (Trilogy v1)

Last updated: 2026-04-25  
Purpose: Form-ordered backup for the third paper submission.

## Upload files (recommended)

Core files:

1. `papers/audit-trilogy-paper/audit-trilogy-paper-v1.pdf`
2. `papers/audit-trilogy-paper/ABSTRACT_FINAL.en.md`
3. `papers/audit-trilogy-paper/draft.en.md`
4. `papers/audit-trilogy-paper/SUBMISSION_CHECKLIST.md`

Supporting evidence files:

5. `artifacts/reports/chsh_bootstrap_ci_standard15.json`
6. `artifacts/reports/chsh_bootstrap_ci_strict0.json`
7. `artifacts/reports/ncc_singles_bridge_real.png`
8. `papers/ghz-threebody-paper/tables/table1_search_registry.md`
9. `papers/ghz-threebody-paper/tables/table2_coarse_fine_topk.md`
10. `papers/ghz-threebody-paper/tables/table3_robustness.md`

## Zenodo form values (in form order)

### 1) Digital Object Identifier

- Do you already have a DOI for this upload?: **No**
- Existing DOI field: leave empty

### 2) Resource type

- `Publication` -> `Preprint`

### 3) Title

- `Analysis Rule Sensitivity in Bell and GHZ Experiments: A Reproducible Audit Framework`

### 4) Publication date

- `2026-04-25`

### 5) Authors/Creators

- Use final publication author list.
- Format: `Family name, Given name`

### 6) Description

This paper synthesizes two published audit lines into a single reproducible framework for Bell and GHZ interpretation under analysis-rule sensitivity. Using public records and artifact-linked evidence, we show that Bell/CHSH on the same NIST event stream shifts from S_strict=2.336276 to S_standard=2.839387 (Delta=+0.503111) under protocol change, while GHZ search under the current audited pipeline remains far from F=4 (best fine-stage F=0.085396). We formalize a ledger-style audit protocol that treats pairing windows, denominator policy, post-selection, and uncertainty as first-class reported variables. We further introduce a singles-aware diagnostics layer (C_norm = coincidences / sqrt(singles_A * singles_B)) as a testable bridge for normalization-path analysis, while explicitly avoiding ontology-level promotion from current evidence. The contribution is a publication-ready, boundary-aware audit standard with claim-to-artifact traceability across both lines. Related records: Bell DOI https://doi.org/10.5281/zenodo.19763028 ; GHZ DOI https://doi.org/10.5281/zenodo.19763473 ; Code repository: https://github.com/tomnattle/chain-explosion-model

### 7) Licenses

- `Creative Commons Attribution 4.0 International (CC BY 4.0)`

### 8) Copyright

- `Copyright (C) 2026 The Authors.`

### 9) Keywords and subjects

- Bell test
- GHZ
- analysis rule sensitivity
- protocol audit
- denominator policy
- post-selection
- reproducibility
- claim boundary

### 10) Languages

- `English` (`eng`)

### 11) Version

- `v1.0`

## Notes

- Keep community empty for fastest publication.
- This paper is method-level synthesis, not ontology replacement claim.
