"""
run_nist_round2_compare.py
--------------------------
第二场对照： layout 检测 +（若存在 CSV）诊断 + 对齐子进程。
P3：比较 training 与 completeblind 是否可走同一网格管；若不能，报告中明文阻塞原因。

用法：
  python run_nist_round2_compare.py \\
    --training-hdf5 data/03_31_CH_pockel_100kHz.run4.afterTimingfix2_training.dat.compressed.build.hdf5 \\
    --completeblind-hdf5 data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5 \\
    --completeblind-csv data/nist_completeblind_side_streams.csv \\
    --alignment-config chsh_preregistered_config_nist_index.json \\
    --out-dir battle_results/nist_round2_v2
"""

import argparse
import json
import os
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description="NIST round2 layout compare + optional CHSH run")
    ap.add_argument("--training-hdf5", default="")
    ap.add_argument("--completeblind-hdf5", default="")
    ap.add_argument("--completeblind-csv", default="data/nist_completeblind_side_streams.csv")
    ap.add_argument("--alignment-config", default="chsh_preregistered_config_nist_index.json")
    ap.add_argument("--out-dir", default="battle_results/nist_round2_v2")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    from nist_hdf5_layout_check import describe_layout

    report = {
        "round": "nist_v2_p3_layout_and_optional_chsh",
        "layouts": [],
        "p3_blockers": [],
        "actions": [],
    }

    paths = []
    if args.training_hdf5:
        paths.append(("training", args.training_hdf5))
    if args.completeblind_hdf5:
        paths.append(("completeblind", args.completeblind_hdf5))

    for label, p in paths:
        d = describe_layout(p)
        d["label"] = label
        report["layouts"].append(d)
        if d.get("exists") and not d.get("grid_side_streams_compatible"):
            report["p3_blockers"].append(
                "%s: not grid_side_streams_compatible; cannot use same v1 nist_hdf5_grid "
                "converter as completeblind; need v2 decoder or different HDF5 product." % label
            )

    diag_json = os.path.join(args.out_dir, "diagnostics_completeblind.json")
    battle_json = os.path.join(args.out_dir, "chsh_alignment_completeblind_rerun.json")

    if args.completeblind_csv and os.path.isfile(args.completeblind_csv):
        subprocess.check_call(
            [
                sys.executable,
                "nist_chsh_diagnostics.py",
                "--events-csv",
                args.completeblind_csv,
                "--window-strict",
                "0",
                "--window-standard",
                "15",
                "--out-json",
                diag_json,
            ],
            cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
        )
        report["actions"].append("wrote diagnostics: %s" % diag_json)

        if os.path.isfile(args.alignment_config):
            subprocess.check_call(
                [
                    sys.executable,
                    "explore_chsh_experiment_alignment.py",
                    "--events-csv",
                    args.completeblind_csv,
                    "--config",
                    args.alignment_config,
                    "--out-json",
                    battle_json,
                    "--out-png",
                    os.path.join(args.out_dir, "figure_chsh_alignment_rerun.png"),
                ],
                cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
            )
            report["actions"].append("wrote alignment: %s" % battle_json)
        else:
            report["actions"].append("missing alignment config: %s" % args.alignment_config)
    else:
        report["actions"].append("skip csv steps: missing %s" % args.completeblind_csv)

    out_path = os.path.join(args.out_dir, "p3_compare_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    # Py2 compat: avoid unicode issues on Windows
    sys.exit(main())
