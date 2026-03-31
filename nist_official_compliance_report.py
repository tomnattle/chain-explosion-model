"""
nist_official_compliance_report.py
---------------------------------
依据 NIST《Description of Data》(bell-test-data-file-folder-descriptions) 对
completeblind HDF5 做结构核对，并写出 JSON 运行日志（不依赖非官方 ±1 映射）。

用法:
  python nist_official_compliance_report.py [--hdf5 path] [--out-json path]
"""

import argparse
import json
import os
import sys

import numpy as np

try:
    import h5py
except Exception:
    print("need h5py")
    sys.exit(1)

DEFAULT_H5 = r"data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5"
DEFAULT_OUT = r"battle_results/nist_round2_v2/NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json"


def decode_cw45_byte1_nibbles(byte):
    """2015 page: low 4 bits carry Alice (bits 0-1) and Bob (bits 2-3) one-hot-style RNG flags."""
    b = int(byte) & 0xFF
    return {
        "alice0": (b >> 0) & 1,
        "alice1": (b >> 1) & 1,
        "bob0": (b >> 2) & 1,
        "bob1": (b >> 3) & 1,
        "raw_byte_masked": b,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hdf5", default=DEFAULT_H5)
    ap.add_argument("--out-json", default=DEFAULT_OUT)
    ap.add_argument("--validate-sample", type=int, default=25000000, help="grid rows to scan clicks")
    args = ap.parse_args()

    log = {
        "reference": {
            "document_title": "Description of Data (Bell Test)",
            "url": "https://www.nist.gov/document/bell-test-data-file-folder-descriptions",
            "document_version_note": "LAST UPDATED ON December 23, 2015 (per page)",
        },
        "hdf5_path": os.path.abspath(args.hdf5),
        "official_definitions": {
            "cw45_clicks": "Bytes 2-3 (Alice) and 4-5 (Bob): uint16 one-hot over 16 Pockels-window "
            "time bins; EXACTLY ONE bit set means one slot fired; slot 1 = bit 0 ... slot 16 = bit 15.",
            "slot_to_bit_index": "For valid single-click word v, bit_index k = log2(v), k in 0..15; slot number = k + 1.",
            "cw45_settings_byte1_bits": (
                "Byte 1 (cw45 five-byte event): decode nibble b as alice0=(b>>0)&1, alice1=(b>>1)&1, "
                "bob0=(b>>2)&1, bob1=(b>>3)&1 (public page one-hot-style RNG; exactly one of each party's pair should be 1). "
                "HDF5 stores separate `alice/settings` and `bob/settings`; see settings_encoding_validation for split-column checks."
            ),
            "what_is_NOT_in_public_doc": [
                "Mapping from single-slot index k to a CHSH binary outcome in {-1,+1} for one party.",
                "Numeric conversion from config radius (alice=4 bob=5 in cw45 naming) to HDF5 row-delta coincidence window — "
                "doc states delay-from-sync comes from yaml used by build_file_txt.py / bell_analysis_code.",
            ],
        },
        "hdf5_inventory": {},
        "empirical_grid": {},
        "click_encoding_validation": {},
        "settings_encoding_validation": {},
        "window_policy_recommendation": {},
        "compliance_checklist_2015": {},
    }

    with h5py.File(args.hdf5, "r") as f:
        inv = {}
        for side in ("alice", "bob"):
            for name in f[side].keys():
                d = f[side][name]
                if hasattr(d, "shape"):
                    inv["%s/%s" % (side, name)] = {"shape": list(d.shape), "dtype": str(d.dtype)}
        log["hdf5_inventory"] = inv
        cfg = {}
        for side in ("alice", "bob"):
            cg = "config/%s" % side
            cfg[side] = {
                "radius": int(f["%s/radius" % cg][()]),
                "bitoffset": int(f["%s/bitoffset" % cg][()]),
                "pk": int(f["%s/pk" % cg][()]),
            }
        log["hdf5_inventory"]["config"] = cfg
        log["hdf5_inventory"]["offsets"] = {
            k: int(f[k][()])
            for k in (
                "offsets/firstsync/alice",
                "offsets/firstsync/bob",
                "offsets/lastidx/alice",
                "offsets/lastidx/bob",
            )
            if k in f
        }

        lg = int(f["alice/clicks"].shape[0])
        la = int(f["alice/laserPulseNumber"].shape[0])
        lb = int(f["bob/laserPulseNumber"].shape[0])
        log["empirical_grid"] = {
            "grid_length_alice_clicks": lg,
            "laserPulseNumber_length_alice": la,
            "laserPulseNumber_length_bob": lb,
            "ratio_grid_over_alice_laserPulseNumber": float(lg) / float(la),
            "note": "Public doc does not state a single integer 'bins per pulse' for this HDF5 row layout; "
            "pulse-level trial ID requires yaml/analysis code or separate derivation.",
        }

        n = min(int(args.validate_sample), lg)
        ca = f["alice/clicks"][:n]
        cb = f["bob/clicks"][:n]
        pw_a = (ca > 0) & ((ca & (ca - 1)) == 0)
        pw_b = (cb > 0) & ((cb & (cb - 1)) == 0)
        bad_a = int(np.sum((ca > 0) & ~pw_a))
        bad_b = int(np.sum((cb > 0) & ~pw_b))
        log["click_encoding_validation"] = {
            "rows_scanned": n,
            "alice_nonzero": int(np.count_nonzero(ca)),
            "bob_nonzero": int(np.count_nonzero(cb)),
            "alice_non_power_of_two_nonzero": int(bad_a),
            "bob_non_power_of_two_nonzero": int(bad_b),
            "conforms_to_one_hot_slot_rule": bool(bad_a == 0 and bad_b == 0),
            "conforms_to_2015_slot_rule": bool(bad_a == 0 and bad_b == 0),
            "rule": "v==0 no click; v==2**k valid one-hot (slot k+1); v>0 and not power of two => invalid",
        }

        # settings: same sample window as clicks for bitwise stats; gap histogram uses 5M
        sa_n = f["alice/settings"][:n].astype(np.uint16)
        sb_n = f["bob/settings"][:n].astype(np.uint16)
        a_lo = sa_n & 3
        b_lo = sb_n & 3
        strict_party2 = (a_lo == 1) | (a_lo == 2)
        strict_party2_b = (b_lo == 1) | (b_lo == 2)
        upper_clear_a = (sa_n >> 2) == 0
        upper_clear_b = (sb_n >> 2) == 0
        uniq_a, cnt_a = np.unique(sa_n, return_counts=True)
        uniq_b, cnt_b = np.unique(sb_n, return_counts=True)
        top_a = np.argsort(-cnt_a)[: min(16, len(cnt_a))]
        top_b = np.argsort(-cnt_b)[: min(16, len(cnt_b))]
        log["settings_encoding_validation"] = {
            "reference_note": "cw45 packs Alice+Bob RNG bits into one byte 1; this HDF5 uses separate `alice/settings` and `bob/settings`. "
            "We therefore (i) test each column's low 2 bits as a 2-bit one-hot (values 1 or 2), "
            "(ii) reconstruct b = (alice&3) | ((bob&3)<<2) and decode as cw45 byte1 nibbles.",
            "rows_scanned": n,
            "alice_settings_unique_top": [
                {"value": int(uniq_a[i]), "count": int(cnt_a[i]), "decode_low2_bits": decode_cw45_byte1_nibbles(uniq_a[i] & 3)}
                for i in top_a
            ],
            "bob_settings_unique_top": [
                {"value": int(uniq_b[i]), "count": int(cnt_b[i]), "decode_low2_bits": decode_cw45_byte1_nibbles(uniq_b[i] & 3)}
                for i in top_b
            ],
            "alice_low2_is_one_hot_1_or_2": {
                "violations": int(np.sum(~strict_party2)),
                "fraction_ok": float(np.mean(strict_party2)) if n else 0.0,
            },
            "bob_low2_is_one_hot_1_or_2": {
                "violations": int(np.sum(~strict_party2_b)),
                "fraction_ok": float(np.mean(strict_party2_b)) if n else 0.0,
            },
            "alice_only_low2_bits_used": {
                "violations_upper_bits": int(np.sum(~upper_clear_a)),
                "fraction_ok": float(np.mean(upper_clear_a)) if n else 0.0,
            },
            "bob_only_low2_bits_used": {
                "violations_upper_bits": int(np.sum(~upper_clear_b)),
                "fraction_ok": float(np.mean(upper_clear_b)) if n else 0.0,
            },
            "reconstructed_byte1_exclusive_nibbles_ok": bool(
                np.all(strict_party2 & strict_party2_b & upper_clear_a & upper_clear_b)
            ),
            "non_official_assumptions_remain": [
                "CHSH binary ±1 from slot index (e.g. 0-7 vs 8-15) is NOT in public Description-of-Data.",
                "HDF5 row-delta 'standard' windows (e.g. 10, 15) are NOT radius-from-yaml coincidence unless separately derived.",
            ],
        }

        # settings change spacing (first 5M rows)
        m = min(5_000_000, lg)
        sa = f["alice/settings"][:m].astype(np.int16)
        da = np.diff(sa, prepend=sa[0])
        ich = np.nonzero(da)[0]
        if len(ich) > 1:
            gaps = np.diff(ich)
            ug, cnt = np.unique(gaps, return_counts=True)
            top = np.argsort(-cnt)[:5]
            log["empirical_grid"]["settings_change_gap_histogram_top5"] = [
                {"gap_rows": int(ug[i]), "count": int(cnt[i])} for i in top
            ]

    log["window_policy_recommendation"] = {
        "same_hdf5_row": {
            "definition": "Use grid index i as the time label for both sides; coincidence with pair window 0 enforces "
            "Alice row i paired to Bob row i (same position in merged parallel arrays).",
            "alignment_with_public_doc": "Public doc guarantees merged HDF5 has parallel alice/bob streams of equal length; "
            "same index is the only alignment rule that does not require yaml-derived pulse reconstruction.",
            "limitation": "Does not by itself prove 'same laser pulse phase'—that is analysis-chain dependent.",
        },
        "radius_based_window": {
            "definition_needed": "cw45 folder name: radius 4 at Alice, 5 at Bob around sync-defined click window.",
            "blocker": "This repository build has NO per-event delay datasets; only config radius integers and offsets. "
            "Converting radius to HDF5 row-delta coincidence width is NOT specified in the public page — requires yaml / bell_analysis_code.",
        },
        "legacy_v1_standard_window_15": {
            "status": "HEURISTIC_ONLY",
            "reason": "Integer 15 was used in exploratory index-space pairing; it is NOT derived from published radius→row conversion here.",
        },
    }

    log["chsh_binary_outcome_note"] = {
        "nist_excel_ordering_reference": "Peter data calculations: 16 joint outcome columns ++ab, +0ab, 0+ab, 00ab, ... across "
            "four setting cells — this is a JOINT (A,B) basis including 0 (no click), not a per-party slot-half ±1 rule.",
        "v1_placeholder_split_0_7_vs_8_15": "NOT derived from the public Description-of-Data page; do not label 'official'.",
    }

    ce = log["click_encoding_validation"]
    se = log["settings_encoding_validation"]
    log["compliance_checklist_2015"] = {
        "slot_one_hot_valid": bool(ce.get("conforms_to_one_hot_slot_rule")),
        "settings_structurally_consistent_with_split_cw45_nibbles": bool(
            se.get("reconstructed_byte1_exclusive_nibbles_ok")
        ),
        "same_grid_row_coincidence_is_only_public_doc_safe_without_yaml": True,
        "radius_row_window_must_not_be_called_official_without_yaml": True,
        "slot_to_plus_minus_is_undefined_in_public_page": True,
        "non_official_heuristics_documented": bool(True),
    }

    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as fp:
        json.dump(log, fp, indent=2, ensure_ascii=False)
    print("wrote", os.path.abspath(args.out_json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
