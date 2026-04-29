# NIST v4 Audit Summary (Email Pack)

## Figures
- Figure 1: `chart1_same_index_quantization_v4.png` (same-index quantization sweep)
- Figure 2: `chart2_protocol_premium_stair_v4.png` (protocol premium staircase, 2.33 -> 2.77 -> 2.83)

## 1) same_index_quantization_sweep_v4 (veil-off)
- Continuous raw metric: `S_raw = 1.117683` (95% CI `1.097130 ~ 1.138496`)
- On the same data after binarization: `S_raw(quant_2) = 2.297779`
- Continuous normalized metric: `S_norm = 2.320815`; split-fixed denominator: `S_norm_fixedden = 2.297303`
- Takeaway: with fixed same-index pairing, metric choice materially changes reported S values.

## 2) nist_unified_semantics_audit_v4 (premium decomposition)
- `same_index S_binary_chsh = 2.329417`
- `external_bucket_all S_binary_chsh = 2.775687` (vs same-index `+0.446270`)
- `event_anchor_nearest S_binary_chsh = 2.834670` (vs external bucket `+0.058983`)
- External bucket edge sensitivity: `S_range = 0.022401` (offset 0..14)
- same-index bootstrap CI: `2.295300 ~ 2.370163`
- Takeaway: high-S regime is strongly coupled to pairing semantics and can be quantitatively decomposed.

## 3) nist_revival_20pct_closure_v4 (local closure checks)
- same_index and same_index_strict are consistent: `2.329417`
- A/B anchor symmetry gap: `delta_abs = 0.001356` (small)
- second sample probe：`available=True, readable=True`
- closure checks:
  - `same_index_not_near_2p82`: `True`
  - `pure_bucket_in_2p8_zone`: `True`
  - `anchor_asymmetry_small`: `True`
  - `edge_sensitivity_bounded`: `True`

## Scope boundary
- This pack supports mechanism-level decomposition and protocol-sensitivity claims.
- This pack does not assert ontology-level final judgment.