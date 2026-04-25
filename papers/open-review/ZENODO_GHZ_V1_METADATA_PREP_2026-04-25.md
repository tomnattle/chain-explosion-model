# Zenodo Metadata Prep (GHZ v1)

Last updated: 2026-04-25  
Purpose: Form-ordered backup for the GHZ preprint submission, based on the Bell v1 submission experience.

## Upload files (prepare first)

Required core files:

1. `papers/ghz-threebody-paper/ghz-threebody-paper-v1.1.pdf`  
   - Includes GitHub repository URL in Appendix.
2. `papers/ghz-threebody-paper/ABSTRACT_FINAL.en.md`
3. `papers/ghz-threebody-paper/tables/table1_search_registry.md`
4. `papers/ghz-threebody-paper/tables/table2_coarse_fine_topk.md`
5. `papers/ghz-threebody-paper/tables/table3_robustness.md`

Optional supporting files:

6. `papers/ghz-threebody-paper/ABSTRACT_FINAL.zh.md`
7. `papers/ghz-threebody-paper/figures/fig3_f_vs_coincidence_tradeoff.png`
8. `papers/ghz-threebody-paper/draft.en.md`
9. `papers/ghz-threebody-paper/draft.zh.md`

## Zenodo form values (in form order)

### 1) Digital Object Identifier

- Do you already have a DOI for this upload?: **No**
- Existing DOI field: leave empty

### 2) Resource type

- `Publication` -> `Preprint`

### 3) Title

- `Denominator Recovery and Post-Selection Audit in a GHZ Three-Body Model: A Two-Stage Search-Based Mechanism Check`

### 4) Publication date

- `2026-04-25`

### 5) Authors/Creators

- Use real publication author list (same policy as Bell record)
- Format: `Family name, Given name`

### 6) Description

This paper introduces a denominator-recovery audit framework for high-correlation claims in a GHZ three-body model, aimed at separating mechanism gain from post-selection bookkeeping gain. Within a unified pipeline, we compare `none` and `energy_weighted` denominator modes and run a two-stage search (90 deg coarse + 2 deg fine), while jointly auditing `F` and `coincidence_rate` trade-offs. Under the current configuration (`samples=80000`, `numba_cpu`, fixed gating), the best fine-stage candidate reaches only `F=0.085396`, remaining far from the target `F=4` with `|err|=3.914604`. Target-attainment decomposition consistently indicates correlation-shape mismatch as the dominant bottleneck rather than coincidence sparsity. Robustness indicators (bootstrap and seed sweep) do not show convergence toward 4 either. We therefore report a method-level conclusion: within the tested model family and protocol, no evidence supports an `F->4` transition. Strong GHZ-style claims should be evaluated through joint auditing of denominator logic, sample-inclusion rules, and retained failure cases. The contribution is a reproducible, ledger-style audit workflow for GHZ correlation studies. Code repository: https://github.com/tomnattle/chain-explosion-model

### 7) Licenses

- `Creative Commons Attribution 4.0 International (CC BY 4.0)`

### 8) Copyright

- `Copyright (C) 2026 The Authors.`

### 9) Keywords and subjects

- GHZ
- three-body model
- post-selection audit
- denominator recovery
- correlation-shape mismatch
- reproducibility
- robustness analysis
- negative results

### 10) Languages

- `English` (`eng`)

### 11) Version

- `v1.0` (first GHZ release)

## Notes

- Community selection can be left empty for fastest publication.
- For new-version drafts on Zenodo, do not fill an existing Zenodo DOI in the "already have DOI" field; keep it as "No" unless importing an external DOI.
- Bell published reference record: https://zenodo.org/records/19763028
