# FINAL AUDIT VERDICT (v1)

Date: 2026-04-29  
Scope: NIST completeblind semantics audit (`v1 -> v2 -> v3`)

## Final Position

This audit supports a **mechanism-level conclusion**, not an ontology-level verdict.

- `same_index` baseline is stable around `S ~ 2.33`.
- `S ~ 2.8+` appears when pairing semantics become wider/more selective.
- Therefore, high-S behavior is strongly protocol-sensitive.

## Core Quantitative Findings

### Baseline (same-index)
- `S_binary_chsh = 2.329417`
- `S_cont_norm_corr = 2.320815`

### External-clock modes (window=15)
- `external_clock_bucket_all S_binary_chsh = 2.775687` (primary external-clock semantics)
- `external_clock_nearest_1to1 S_binary_chsh = 2.808666` (loophole probe)

### Event-anchored mode (window=15)
- `event_anchor_nearest S_binary_chsh = 2.834670` (loophole probe)

Interpretation: nearest-matching and event-anchored rules produce upward shifts relative to the strict same-index baseline.

## Resolved Challenge Items

- **U1 Confirmed**: Pure bucket mode and nearest mode are now explicitly separated.
- **U2 Confirmed**: Event-anchored mode is explicitly labeled `loophole_probe`.
- **U3 Confirmed**: `binary_chsh` and continuous-correlation families are explicitly separated.
- **U4 Checked**: Fixed-denominator normalization added; on same-index baseline, no material difference observed.
- **U5 Checked**: `multi_event_t_rate = 0.0` on the audited main sample.
- **U7 Checked**: one-hot filtering quantified (`drop_ratio_A ~ 6.45%`, `drop_ratio_B ~ 6.16%`).

## Decision

- External communication is now technically supportable **at mechanism level**:
  - protocol sensitivity established,
  - baseline and probe modes separated,
  - key implementation risks disclosed and tested.
- Do not elevate to ontology claims in this version.

## Evidence Index

- `results/nist_unified_semantics_audit_v1.json`
- `results/nist_unified_semantics_audit_v2.json`
- `results/nist_unified_semantics_audit_v3.json`
- `results/nist_unified_semantics_heatmap_v1.png`
- `results/nist_unified_semantics_heatmap_v2.png`
- `results/nist_unified_semantics_counterfactual_v1.png`
- `results/same_index_quantization_sweep_v1.json`
- `results/same_index_quantization_sweep_v1.png`
- `results/nist_revival_20pct_closure_v1.json`
- `results/nist_revival_20pct_closure_v1.md`
- `results/nist_semantics_contribution_summary_v1.json`
- `results/nist_semantics_contribution_summary_v1.md`
- `scripts/explore/质疑/nist_unified_semantics_audit_v1_py/response_v1.md`

