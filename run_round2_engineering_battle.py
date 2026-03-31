"""
run_round2_engineering_battle.py
--------------------------------
第二场「工程战」（不声称官方）：两套路槽->+-1 + 同一套配对窗，输出敏感性对照。

1) legacy_half CSV  (同 v1 占位)
2) parity CSV       (偶槽 +1 奇槽 -1)
3) 对两路各跑 explore_chsh_experiment_alignment（fork_only 论点门）
4) 再对两路各跑第一场同一判据：chsh_preregistered_config_nist_index.json（strict_max_S=2.02 等）

用法:
  python run_round2_engineering_battle.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
H5 = os.path.join(ROOT, "data", "17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
OUT_DIR = os.path.join(ROOT, "battle_results", "nist_round2_v2")
CSV_LEGACY = os.path.join(ROOT, "data", "nist_round2_engineering_legacy.csv")
CSV_PARITY = os.path.join(ROOT, "data", "nist_round2_engineering_parity.csv")
CFG_ALIGN = os.path.join(ROOT, "chsh_preregistered_config_nist_round2_engineering.json")
CFG_ROUND1_GATE = os.path.join(ROOT, "chsh_preregistered_config_nist_index.json")


def run(cmd):
    print("+", " ".join(cmd))
    rc = subprocess.call(cmd, cwd=ROOT)
    if rc != 0:
        raise SystemExit("failed: %s" % rc)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.isfile(H5):
        print("missing HDF5:", H5)
        return 1

    run(
        [
            sys.executable,
            "convert_nist_hdf5_to_events_csv.py",
            "--hdf5",
            H5,
            "--config",
            "nist_convert_config_round2_legacy.json",
            "--output",
            CSV_LEGACY,
        ]
    )
    run(
        [
            sys.executable,
            "convert_nist_hdf5_to_events_csv.py",
            "--hdf5",
            H5,
            "--config",
            "nist_convert_config_round2_parity.json",
            "--output",
            CSV_PARITY,
        ]
    )

    j1 = os.path.join(OUT_DIR, "ROUND2_chsh_result_legacy.json")
    j2 = os.path.join(OUT_DIR, "ROUND2_chsh_result_parity.json")
    run(
        [
            sys.executable,
            "explore_chsh_experiment_alignment.py",
            "--events-csv",
            CSV_LEGACY,
            "--config",
            CFG_ALIGN,
            "--out-json",
            j1,
            "--out-png",
            os.path.join(OUT_DIR, "ROUND2_figure_legacy.png"),
        ]
    )
    run(
        [
            sys.executable,
            "explore_chsh_experiment_alignment.py",
            "--events-csv",
            CSV_PARITY,
            "--config",
            CFG_ALIGN,
            "--out-json",
            j2,
            "--out-png",
            os.path.join(OUT_DIR, "ROUND2_figure_parity.png"),
        ]
    )

    j1_g = os.path.join(OUT_DIR, "ROUND2_chsh_legacy_under_round1_gate.json")
    j2_g = os.path.join(OUT_DIR, "ROUND2_chsh_parity_under_round1_gate.json")
    if not os.path.isfile(CFG_ROUND1_GATE):
        print("missing Round1 gate config:", CFG_ROUND1_GATE)
        return 1
    run(
        [
            sys.executable,
            "explore_chsh_experiment_alignment.py",
            "--events-csv",
            CSV_LEGACY,
            "--config",
            CFG_ROUND1_GATE,
            "--out-json",
            j1_g,
            "--out-png",
            os.path.join(OUT_DIR, "ROUND2_figure_legacy_under_round1_gate.png"),
        ]
    )
    run(
        [
            sys.executable,
            "explore_chsh_experiment_alignment.py",
            "--events-csv",
            CSV_PARITY,
            "--config",
            CFG_ROUND1_GATE,
            "--out-json",
            j2_g,
            "--out-png",
            os.path.join(OUT_DIR, "ROUND2_figure_parity_under_round1_gate.png"),
        ]
    )

    R = {
        "battle": "nist_round2_engineering_dual_mapping",
        "started_utc": datetime.utcnow().isoformat() + "Z",
        "disclaimer": "Engineering hypotheses only; not NIST-official CHSH reproduction.",
        "alignment_config": os.path.basename(CFG_ALIGN),
        "legacy": load_json(j1),
        "parity": load_json(j2),
    }
    if R["legacy"].get("strict") and R["parity"].get("strict"):
        R["delta_S_strict"] = float(R["parity"]["strict"]["S"]) - float(R["legacy"]["strict"]["S"])
        R["delta_S_standard"] = float(R["parity"]["standard"]["S"]) - float(R["legacy"]["standard"]["S"])

    R["under_round1_gate"] = {
        "config_file": os.path.basename(CFG_ROUND1_GATE),
        "note": "Same thesis gates as Round1 archive: strict_max_S, standard_min_S, require_standard_S_gt_strict_S; standard window=15 index.",
        "legacy": load_json(j1_g),
        "parity": load_json(j2_g),
    }

    gate_only = {
        "battle_addon": "round2_data_under_round1_thesis_gate",
        "utc": datetime.utcnow().isoformat() + "Z",
        "round1_gate_config": os.path.basename(CFG_ROUND1_GATE),
        "legacy": R["under_round1_gate"]["legacy"],
        "parity": R["under_round1_gate"]["parity"],
        "summary": {
            "legacy_thesis_pass": R["under_round1_gate"]["legacy"].get("thesis_pass"),
            "parity_thesis_pass": R["under_round1_gate"]["parity"].get("thesis_pass"),
        },
    }
    gate_path = os.path.join(OUT_DIR, "ROUND2_UNDER_ROUND1_GATE.json")
    with open(gate_path, "w", encoding="utf-8") as f:
        json.dump(gate_only, f, indent=2, ensure_ascii=False)
    print("wrote", gate_path)

    rep = os.path.join(OUT_DIR, "ROUND2_ENGINEERING_BATTLE_REPORT.json")
    with open(rep, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2, ensure_ascii=False)
    print("wrote", rep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
