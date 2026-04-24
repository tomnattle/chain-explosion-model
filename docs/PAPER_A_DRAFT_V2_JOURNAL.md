# Paper A Draft v2 (Journal-Friendly)

## Title

Statistical Measure Dependence in CHSH Analysis:  
A Reproducible `Δ`-Mapping Closure Case Study

## Running Title

Statistical-Object Dependence in CHSH

---

## Abstract

Bell/CHSH discussions have primarily focused on loophole closure, while the effect of statistical-object definition on conclusion binding remains under-audited even in loophole-closed settings. We address this gap through a reproducible `Δ`-mapping closure protocol. Using event-level data, we compute `binary`, `continuous_raw`, and `NCC` tracks in parallel, lock preprocessing and seeds, and run bootstrap, exact paired-swap permutation, and mapping-sensitivity scans. We evaluate closure via four criteria (Definition/Dimensional/Process/Statistical) with explicit downgrade-on-failure policy.

Under the current primary mapping (`half_split`), `LowCos` shows lower fitting error than the Bell polyline baseline (`wRMSE(Bell)=0.058318`, `wRMSE(LowCos)=0.014459`, `wRMSE(HighCos)=0.016552`), with 95% CI for `wRMSE(LowCos)-wRMSE(Bell)` equal to `[-0.049243, -0.036555]` and `P(wRMSE(LowCos) < wRMSE(Bell))=1.000000`. The 9-bin exact permutation test yields one-sided `p=0.0117188` (two-sided `p=0.0234375`). Automated draft closure status indicates all four checks as `PASS`, while retaining explicit boundaries: `slot->±1` remains an assumption, and claims are restricted to the current mapping/protocol domain.

We position this work as a methods contribution rather than a terminal foundational verdict. The proposed workflow can serve as an audit add-on for Bell-style reporting to reduce metric-selection bias and narrative overreach.

## Keywords

CHSH; statistical object; delta mapping; reproducibility; audit workflow

---

## 1. Introduction

Bell/CHSH studies have long focused on experimental loopholes (detection efficiency, locality, freedom-of-choice) and their closure conditions. Even in idealized loophole-closed scenarios, a methodological issue remains: whether conclusion binding is invariant under changes in statistical-object definition.

This paper addresses object-level consistency rather than ontological adjudication. On the same event-level sample pool, we compare `binary`, `continuous_raw`, and `NCC` tracks under a single reproducible workflow for `E(Δ)` analysis.

Our contributions are:

1. A preregistered operational `Δ`-mapping protocol tied to uncertainty and robustness procedures.
2. Parallel cross-metric reporting with explicit closure criteria (Definition/Dimensional/Process/Statistical).
3. A repository-anchored reproducibility chain (scripts, artifacts, failure logging, downgrade policy).

---

## 2. Methods

### 2.1 Objective and Scope

The goal is to audit sensitivity of CHSH conclusions to statistical-object choices, not to assert one ontologically unique metric.

### 2.2 Data and Preregistration

Event-level NIST HDF5 data are used. Before execution, we lock:

- data path and hash,
- preprocessing order,
- `Δ` definition,
- metric formulas,
- bootstrap settings and seeds.

### 2.3 `Δ` Mapping and Aggregation

One-hot click code is decoded by `v=2^k -> slot k`. Circular Alice/Bob slot distance is folded to `0..8`, then mapped to `0..180°`.  
This mapping is engineering-reproducible but not claimed as an official unique physical definition. The `slot->±1` rule is explicit and tested via alternative mappings.

### 2.4 Model Comparison and Statistics

For `E(Δ)` we compare:

- Bell piecewise-linear baseline,
- `LowCos = a*cos(Δ)+b` (weighted least squares),
- `HighCos = sign(a)*cos(Δ)`.

Primary error metric: weighted RMSE.  
Uncertainty: binomial parametric bootstrap (95% CI).  
Significance: exact 9-bin paired-swap permutation test.

### 2.5 Closure and Failure Policy

Four closure checks:

- Definition closure,
- Dimensional closure,
- Process closure,
- Statistical closure.

Any failed item triggers downgrade to `provisional evidence` plus failure-log archival.

### 2.6 Robustness Design

Beyond `half_split`, we test `parity` and `quadrant_split`. Validation logic includes LOBO and L2O with raw/clipped comparisons.

### 2.7 Reproducibility Entry Points

- Runner: `scripts/explore/run_delta_validation_pack.ps1`
- Summarizer: `scripts/explore/summarize_delta_closure.py`
- Core artifacts: `artifacts/public_validation_pack/`

---

## 3. Results

Under preregistered `Δ` mapping (`half_split`), `LowCos` fits empirical `E(Δ)` better than Bell baseline:

- `wRMSE(Bell)=0.058318`
- `wRMSE(LowCos)=0.014459`
- `wRMSE(HighCos)=0.016552`
- `95% CI[wRMSE(LowCos)-wRMSE(Bell)] = [-0.049243, -0.036555]`
- `P(wRMSE(LowCos) < wRMSE(Bell)) = 1.000000`
- permutation `p(one-sided)=0.0117188`, `p(two-sided)=0.0234375`

Draft closure summary reports:

- Definition = PASS
- Dimensional = PASS
- Process = PASS
- Statistical = PASS

### 3.1 Main Table

| Item | Value |
|---|---:|
| Mapping mode | `half_split` |
| wRMSE(Bell) | 0.058318 |
| wRMSE(LowCos) | 0.014459 |
| wRMSE(HighCos) | 0.016552 |
| P(wRMSE(LowCos) < wRMSE(Bell)) | 1.000000 |
| permutation p(one-sided) | 0.0117188 |
| permutation p(two-sided) | 0.0234375 |

---

## 4. Discussion

The core empirical signal is that statistical-object choice materially affects conclusion binding under the same sample pool. The present findings are conditional on preregistered mapping and preprocessing choices, and are not framed as a foundational-theory adjudication.

The failure-first protocol (explicit downgrade and logging rules) is a deliberate control against metric-selection bias and narrative overreach. This is intended as a methodological contribution for reporting discipline.

---

## 5. Limitations

1. `slot->±1` remains an explicit assumption and may influence effect size.  
2. Current closure evidence is strongest on the present mapping domain; broader mapping classes are pending.  
3. Cross-dataset replication is not complete yet.  
4. GHZ three-party analysis is intentionally excluded from this paper and should be treated as a separate line.

---

## 6. Conclusion

We provide a reproducible audit workflow for CHSH statistical-object sensitivity and show stable object-dependent behavior under the current `Δ` protocol. The value lies in auditable process and bounded claims, enabling structured third-party verification.

---

## Data Availability

Event-level data source and derivative artifacts are documented in:

- `docs/DELTA_MAPPING_VALIDATION_PROTOCOL.md`
- `docs/DELTA_MAPPING_RUNBOOK.md`
- `artifacts/public_validation_pack/`

If journal policy requires, add persistent archive links here: `[TO_BE_FILLED]`.

## Code Availability

Reproducibility scripts are available in this repository, notably:

- `scripts/explore/run_delta_validation_pack.ps1`
- `scripts/explore/summarize_delta_closure.py`
- `scripts/explore/explore_nist_e_delta_rigor_pack.py`
- `scripts/explore/explore_nist_e_delta_validation_sanity.py`

If journal policy requires, add release tag/DOI here: `[TO_BE_FILLED]`.

## Author Contributions

- Conceptualization: `[TO_BE_FILLED]`
- Methodology: `[TO_BE_FILLED]`
- Software: `[TO_BE_FILLED]`
- Validation: `[TO_BE_FILLED]`
- Writing - original draft: `[TO_BE_FILLED]`
- Writing - review and editing: `[TO_BE_FILLED]`

## Funding

`[TO_BE_FILLED]`

## Conflict of Interest

The authors declare no competing interests. `[EDIT_IF_NEEDED]`

## Acknowledgments

`[TO_BE_FILLED]`

## Ethics Statement

No human/animal intervention experiment was conducted in this work. `[EDIT_IF_JOURNAL_REQUIRES]`

---

## Appendix A: Artifact Checklist (Submission Bundle)

- `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_CHECKLIST.md`
- `docs/DELTA_FAILURE_LOG_TEMPLATE.md`
