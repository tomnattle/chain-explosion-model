#!/usr/bin/env python3
"""
Generate a concise markdown gate report from v9 real-data results.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="v9 gate report generator")
    ap.add_argument(
        "--in-json",
        type=str,
        default="artifacts/ripple_quantum_tests_v9_realdata/RIPPLE_QUANTUM_TESTS_V9_REALDATA_RESULTS.json",
    )
    ap.add_argument(
        "--out-md",
        type=str,
        default="artifacts/ripple_quantum_tests_v9_realdata/RIPPLE_QUANTUM_TESTS_V9_GATE_REPORT.md",
    )
    args = ap.parse_args()

    payload = json.loads(Path(args.in_json).read_text(encoding="utf-8-sig"))
    opt = payload["optimum"]
    gates = payload["gates"]
    rows = payload["experiments"]
    row_gate = {x["name"]: x for x in payload.get("experiment_gate_result", [])}

    lines = [
        "# V9 Realdata Gate Report",
        "",
        f"- final_pass: **{gates['final_pass']}**",
        f"- optimum: mu={opt['mu']:.6f}, rho={opt['rho']:.6f}, eta={opt['eta']:.6f}",
        f"- thresholds: val_r2>={gates['val_r2_min']}, blind_r2>={gates['blind_r2_min']}, blind_nrmse<=fit_nrmse*{gates['blind_nrmse_max_ratio']}",
        "",
        "| experiment | fit_nrmse | val_nrmse | blind_nrmse | fit_r2 | val_r2 | blind_r2 | gate_pass |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for r in rows:
        gp = row_gate.get(r["name"], {}).get("pass", False)
        lines.append(
            f"| {r['name']} | {r['fit_nrmse']:.6f} | {r['val_nrmse']:.6f} | {r['blind_nrmse']:.6f} | "
            f"{r['fit_r2']:.6f} | {r['val_r2']:.6f} | {r['blind_r2']:.6f} | {'Y' if gp else 'N'} |"
        )

    out_path = Path(args.out_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

