# DECISION NOTE (Frozen)

Date: 2026-04-29  
Scope: NIST completeblind clock-reference and pairing-semantics audit

## Objective

Distinguish protocol effects from physical baseline by separating:

- pairing semantics (`same_index`, `external_clock_bin`, `event_anchor_nearest`)
- metric semantics (`binary`, `cont_raw`, `cont_norm`)
- quantization effect (continuous vs multi-level vs binary)

## Frozen Findings

1. **Same-index baseline is stable around 2.33**
   - `same_index S_binary = 2.3294`
   - `same_index S_cont_norm = 2.3208`
   - Angle/sign convention scans do not yield `2.82` under same-index constraints.

2. **2.8+ appears under wider pairing semantics**
   - `external_clock_bin (w=15): S_binary = 2.8087, S_cont_norm = 2.8255`
   - `event_anchor_nearest (w=15): S_binary = 2.8347, S_cont_norm = 2.8448`
   - Therefore, pairing semantics is a major driver for reaching the 2.8+ regime.

3. **Counterfactual sanity check passes**
   - `shuffled-B` control returns near-zero S across all pairing modes.
   - This rejects the claim that the pipeline can arbitrarily fabricate high S without structure.

4. **Quantization contribution is real but metric-dependent**
   - Under `same_index`, from continuous raw to binary:
     - `S_raw: 1.1177 -> 2.2978` (large increase)
   - Under normalized continuous metric:
     - binary is close to continuous norm (`~2.30` vs `~2.32`)
   - Conclusion: quantization effect exists, but interpretation depends on metric definition.

## Decision

- **Do not send external claim emails yet.**
- Treat current status as **protocol-sensitivity established**, not ontology-level conclusion.
- Use same-index baseline (`~2.33`) as hard reference for further model testing.

## Evidence Artifacts

- `results/nist_unified_semantics_audit_v1.json`
- `results/nist_unified_semantics_heatmap_v1.png`
- `results/nist_unified_semantics_counterfactual_v1.png`
- `results/same_index_angle_sign_scan_v1.json`
- `results/same_index_quantization_sweep_v1.json`
- `results/same_index_quantization_sweep_v1.png`
- `results/nist_semantics_contribution_summary_v1.json`
- `results/nist_semantics_contribution_summary_v1.md`

## Next Gate (Required Before External Communication)

1. Split conclusions by metric family (`raw` vs `norm`) with no mixed deltas.
2. Add uncertainty bands / bootstrap for key S deltas.
3. Reconfirm same-index baseline stability across at least one additional NIST run/file slice.
4. Only after (1)-(3), draft technical communication.
