"""
nist_revival_20pct_closure_v4.py
--------------------------------
Closure v4:
- Uses v4 audit semantics (pure bucket primary, loophole probes separated)
- Keeps raw/norm split explicit
- Adds robust second-sample loading (graceful failure details)
"""

import argparse
import json
import os
from typing import Any, Dict

import h5py


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def probe_hdf5_basic(hdf5_path: str) -> Dict[str, Any]:
    if not os.path.isfile(hdf5_path):
        return {"available": False, "readable": False, "reason": "file_not_found"}
    try:
        with h5py.File(hdf5_path, "r") as h5:
            keys = list(h5.keys())
            return {"available": True, "readable": True, "top_level_keys": keys}
    except Exception as e:
        return {"available": True, "readable": False, "reason": str(e)}


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST closure v4 summary")
    ap.add_argument(
        "--audit-v4-json",
        default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v4.json",
    )
    ap.add_argument(
        "--second-hdf5",
        default="data/03_31_CH_pockel_100kHz.run4.afterTimingfix2_training.dat.compressed.build.hdf5",
    )
    ap.add_argument(
        "--out-json",
        default="battle_results/nist_clock_reference_audit_v1/results/nist_revival_20pct_closure_v4.json",
    )
    ap.add_argument(
        "--out-md",
        default="battle_results/nist_clock_reference_audit_v1/results/nist_revival_20pct_closure_v4.md",
    )
    args = ap.parse_args()

    v4 = load_json(args.audit_v4_json)

    same = v4["same_index"]
    strict = v4["same_index_strict"]
    ext_scan = v4["external_bucket_offset_scan"]
    evt_sym = v4["event_anchor_symmetry"]
    ci = v4["bootstrap_ci"]
    second_probe = probe_hdf5_basic(args.second_hdf5)

    out = {
        "version": "nist-revival-20pct-closure-v4",
        "source_audit": os.path.abspath(args.audit_v4_json),
        "same_index": same,
        "same_index_strict": strict,
        "external_bucket_edge_sensitivity": {
            "S_binary_min": ext_scan["S_binary_min"],
            "S_binary_max": ext_scan["S_binary_max"],
            "S_binary_range": ext_scan["S_binary_range"],
            "offset0_snapshot": ext_scan["offset0_snapshot"],
        },
        "event_anchor_symmetry": evt_sym,
        "bootstrap_ci_binary": {
            "same_index": ci["same_index_binary_chsh"],
            "same_index_strict": ci["same_index_strict_binary_chsh"],
            "event_anchor_A": ci["event_anchor_A_binary_chsh"],
            "event_anchor_B": ci["event_anchor_B_binary_chsh"],
        },
        "raw_norm_split_explicit": True,
        "second_sample_probe": second_probe,
        "closure_checks": {
            "same_index_not_near_2p82": abs(float(same["S_binary_chsh"]) - 2.82) > 0.02,
            "pure_bucket_in_2p8_zone": abs(float(ext_scan["offset0_snapshot"]["S_binary_chsh"]) - 2.82) <= 0.05,
            "anchor_asymmetry_small": float(evt_sym["delta_abs"]) < 0.01,
            "edge_sensitivity_bounded": float(ext_scan["S_binary_range"]) < 0.05,
        },
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    lines = [
        "# NIST Revival 20% Closure v4",
        "",
        "## Snapshot",
        f"- same_index S_binary_chsh = {same['S_binary_chsh']:.6f}",
        f"- same_index_strict S_binary_chsh = {strict['S_binary_chsh']:.6f}",
        f"- pure_bucket(offset=0) S_binary_chsh = {ext_scan['offset0_snapshot']['S_binary_chsh']:.6f}",
        "",
        "## Robustness",
        f"- bucket edge S range = {ext_scan['S_binary_range']:.6f}",
        f"- event anchor A/B delta = {evt_sym['delta_abs']:.6f}",
        f"- same_index CI95 = [{ci['same_index_binary_chsh']['lo']:.6f}, {ci['same_index_binary_chsh']['hi']:.6f}]",
        "",
        "## Second sample probe",
        f"- available={second_probe['available']} readable={second_probe['readable']}",
        f"- reason={second_probe.get('reason', 'ok')}",
        "",
        "## Closure checks",
        f"- same_index_not_near_2p82: {out['closure_checks']['same_index_not_near_2p82']}",
        f"- pure_bucket_in_2p8_zone: {out['closure_checks']['pure_bucket_in_2p8_zone']}",
        f"- anchor_asymmetry_small: {out['closure_checks']['anchor_asymmetry_small']}",
        f"- edge_sensitivity_bounded: {out['closure_checks']['edge_sensitivity_bounded']}",
    ]
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("saved:", args.out_json)
    print("saved:", args.out_md)


if __name__ == "__main__":
    main()
