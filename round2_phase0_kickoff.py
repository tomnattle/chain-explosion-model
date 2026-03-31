"""
round2_phase0_kickoff.py
------------------------
第二场统一战线 — Phase 0：官方合规日志 + HDF5 layout 自检 + 下一步提示。
不修改第一场归档；输出写入 battle_results/nist_round2_v2/

用法（在仓库根目录）:
  python round2_phase0_kickoff.py
  python round2_phase0_kickoff.py --skip-compliance   # 仅 layout
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "battle_results", "nist_round2_v2")
DEFAULT_COMPLETEBLIND = os.path.join(ROOT, "data", "17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
DEFAULT_TRAINING = os.path.join(
    ROOT, "data", "03_31_CH_pockel_100kHz.run4.afterTimingfix2_training.dat.compressed.build.hdf5"
)


def run(cmd, cwd=ROOT):
    print("+", " ".join(cmd))
    return subprocess.call(cmd, cwd=cwd)


def main():
    ap = argparse.ArgumentParser(description="Round2 Phase0: compliance + layout gate")
    ap.add_argument("--skip-compliance", action="store_true")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    lines = []
    lines.append("round2_phase0 %s" % datetime.utcnow().isoformat() + "Z")
    lines.append("")

    if not args.skip_compliance:
        log_json = os.path.join(OUT_DIR, "NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json")
        rc = run(
            [sys.executable, "nist_official_compliance_report.py", "--hdf5", DEFAULT_COMPLETEBLIND, "--out-json", log_json]
        )
        lines.append("nist_official_compliance_report.py exit=%d" % rc)
        if rc != 0:
            print("compliance failed")
            return rc

    h5_list = []
    if os.path.isfile(DEFAULT_TRAINING):
        h5_list.append(DEFAULT_TRAINING)
    if os.path.isfile(DEFAULT_COMPLETEBLIND):
        h5_list.append(DEFAULT_COMPLETEBLIND)
    if h5_list:
        snap = os.path.join(OUT_DIR, "PHASE0_layouts_snapshot.json")
        cmd = [sys.executable, "nist_hdf5_layout_check.py", "--json", snap]
        for p in h5_list:
            cmd.extend(["--hdf5", p])
        rc = run(cmd)
        lines.append("nist_hdf5_layout_check.py exit=%d" % rc)
        try:
            with open(snap, "r", encoding="utf-8") as f:
                layouts = json.load(f)
            for L in layouts:
                lab = L.get("path", "").split(os.sep)[-1][:48]
                ok = L.get("grid_side_streams_compatible")
                lines.append("  %s grid_compatible=%s" % (lab, ok))
        except Exception as exc:
            lines.append("  (could not read snapshot: %s)" % exc)

    stamp = os.path.join(OUT_DIR, "PHASE0_LAST_RUN.txt")
    with open(stamp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\n--- Phase 0 done ---")
    print("log:", stamp)
    print("\nNext (human / team):")
    print("  1) Read: battle_results/nist_round2_v2/ROUND2_KICKOFF.md")
    print("  2) Obtain yaml or SI outcome+coincidence definition -> fill chsh_preregistered_config_nist_v2_TEMPLATE.json")
    print("  3) P4 parallel: run_battle_plan / closure scripts (independent line: P4_PROTOCOL_AUDIT_SCOPE.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
