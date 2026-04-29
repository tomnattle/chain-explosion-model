"""
nist_semantics_contribution_summary_v1.py
-----------------------------------------
Build a compact contribution summary from:
1) nist_unified_semantics_audit_v1.json
2) same_index_quantization_sweep_v1.json

Outputs:
- JSON with delta decomposition
- Markdown note for fast review
"""

import argparse
import json
import os


def main() -> None:
    ap = argparse.ArgumentParser(description="Summarize semantics contributions on NIST audit outputs.")
    ap.add_argument(
        "--unified-json",
        default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v1.json",
    )
    ap.add_argument(
        "--quant-json",
        default="battle_results/nist_clock_reference_audit_v1/results/same_index_quantization_sweep_v1.json",
    )
    ap.add_argument(
        "--out-json",
        default="battle_results/nist_clock_reference_audit_v1/results/nist_semantics_contribution_summary_v1.json",
    )
    ap.add_argument(
        "--out-md",
        default="battle_results/nist_clock_reference_audit_v1/results/nist_semantics_contribution_summary_v1.md",
    )
    args = ap.parse_args()

    with open(args.unified_json, "r", encoding="utf-8") as f:
        uj = json.load(f)
    with open(args.quant_json, "r", encoding="utf-8") as f:
        qj = json.load(f)

    real = uj["real_matrix"]
    same = real["same_index"]
    ext = real["external_clock_bin"]
    evt = real["event_anchor_nearest"]

    # Pairing contributions under same metric
    d_pair_binary_ext = float(ext["S_binary"] - same["S_binary"])
    d_pair_binary_evt = float(evt["S_binary"] - same["S_binary"])
    d_pair_norm_ext = float(ext["S_cont_norm"] - same["S_cont_norm"])
    d_pair_norm_evt = float(evt["S_cont_norm"] - same["S_cont_norm"])

    # Normalization contributions under same pairing
    d_norm_same = float(same["S_cont_norm"] - same["S_cont_raw"])
    d_norm_ext = float(ext["S_cont_norm"] - ext["S_cont_raw"])
    d_norm_evt = float(evt["S_cont_norm"] - evt["S_cont_raw"])

    # Quantization contributions from same-index sweep
    rows = qj["rows"]
    row_cont = next(r for r in rows if r["label"] == "continuous")
    row_q2 = next(r for r in rows if r["label"] == "quant_2")
    d_quant_raw_q2_vs_cont = float(row_q2["S_raw"] - row_cont["S_raw"])
    d_quant_norm_q2_vs_cont = float(row_q2["S_norm"] - row_cont["S_norm"])

    summary = {
        "version": "nist-semantics-contribution-summary-v1",
        "inputs": {
            "unified_json": os.path.abspath(args.unified_json),
            "quant_json": os.path.abspath(args.quant_json),
        },
        "baseline": {
            "same_index_S_binary": float(same["S_binary"]),
            "same_index_S_cont_raw": float(same["S_cont_raw"]),
            "same_index_S_cont_norm": float(same["S_cont_norm"]),
        },
        "delta_pairing": {
            "binary_external_minus_same": d_pair_binary_ext,
            "binary_event_minus_same": d_pair_binary_evt,
            "cont_norm_external_minus_same": d_pair_norm_ext,
            "cont_norm_event_minus_same": d_pair_norm_evt,
        },
        "delta_normalization": {
            "same_index_cont_norm_minus_cont_raw": d_norm_same,
            "external_cont_norm_minus_cont_raw": d_norm_ext,
            "event_cont_norm_minus_cont_raw": d_norm_evt,
        },
        "delta_quantization_same_index": {
            "raw_quant2_minus_continuous": d_quant_raw_q2_vs_cont,
            "norm_quant2_minus_continuous": d_quant_norm_q2_vs_cont,
        },
        "quick_read": {
            "pairing_is_major_driver_binary": abs(d_pair_binary_evt) > abs(d_quant_raw_q2_vs_cont),
            "pairing_is_major_driver_norm": abs(d_pair_norm_evt) > abs(d_quant_norm_q2_vs_cont),
            "same_index_near_2p82": abs(float(same["S_binary"]) - 2.82) <= 0.02 or abs(float(same["S_cont_norm"]) - 2.82) <= 0.02,
        },
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    md = []
    md.append("# NIST Semantics Contribution Summary v1")
    md.append("")
    md.append("## Baseline (same_index)")
    md.append(f"- S_binary: {same['S_binary']:.6f}")
    md.append(f"- S_cont_raw: {same['S_cont_raw']:.6f}")
    md.append(f"- S_cont_norm: {same['S_cont_norm']:.6f}")
    md.append("")
    md.append("## Delta Pairing")
    md.append(f"- binary: external - same = {d_pair_binary_ext:+.6f}")
    md.append(f"- binary: event - same = {d_pair_binary_evt:+.6f}")
    md.append(f"- cont_norm: external - same = {d_pair_norm_ext:+.6f}")
    md.append(f"- cont_norm: event - same = {d_pair_norm_evt:+.6f}")
    md.append("")
    md.append("## Delta Normalization (cont_norm - cont_raw)")
    md.append(f"- same_index: {d_norm_same:+.6f}")
    md.append(f"- external_clock_bin: {d_norm_ext:+.6f}")
    md.append(f"- event_anchor_nearest: {d_norm_evt:+.6f}")
    md.append("")
    md.append("## Delta Quantization (same_index, quant2 - continuous)")
    md.append(f"- raw: {d_quant_raw_q2_vs_cont:+.6f}")
    md.append(f"- norm: {d_quant_norm_q2_vs_cont:+.6f}")
    md.append("")
    md.append("## Quick Read")
    md.append(f"- Pairing major driver (binary): {summary['quick_read']['pairing_is_major_driver_binary']}")
    md.append(f"- Pairing major driver (norm): {summary['quick_read']['pairing_is_major_driver_norm']}")
    md.append(f"- Same-index near 2.82: {summary['quick_read']['same_index_near_2p82']}")
    md.append("")

    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("saved:", args.out_json)
    print("saved:", args.out_md)


if __name__ == "__main__":
    main()
