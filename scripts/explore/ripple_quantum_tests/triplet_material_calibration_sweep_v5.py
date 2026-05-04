"""
triplet_material_calibration_sweep_v5

Sweep calibration hyperparameters for triplet material mapping v2:
- distance_unit_to_m
- eta_max
- w_eta_target

Focus:
- detect eta saturation (hitting eta_max)
- compare fit quality and stability
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def read_v2_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(payload: dict, eta_max: float) -> dict:
    rows = payload.get("rows", [])
    if not rows:
        return {
            "rows": 0,
            "n_mae": None,
            "eta_mean": None,
            "eta_sat_ratio": None,
            "mu_mean": None,
            "rho_mean": None,
        }
    n = len(rows)
    n_mae = sum(abs(float(r.get("n_err", 0.0))) for r in rows) / n
    eta_vals = [float(r.get("eta_fit", 0.0)) for r in rows]
    sat = sum(1 for e in eta_vals if abs(e - eta_max) <= 1e-9)
    return {
        "rows": n,
        "n_mae": n_mae,
        "eta_mean": sum(eta_vals) / n,
        "eta_sat_ratio": sat / n,
        "mu_mean": sum(float(r.get("mu_fit", 0.0)) for r in rows) / n,
        "rho_mean": sum(float(r.get("rho_fit", 0.0)) for r in rows) / n,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_md(path: Path, rows: list[dict]) -> None:
    lines = [
        "# Triplet Material Calibration Sweep v5",
        "",
        "| case | distance_unit_to_m | eta_max | w_eta_target | n_mae | eta_mean | eta_sat_ratio | mu_mean |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['case']} | {r['distance_unit_to_m']:.3e} | {r['eta_max']:.3f} | {r['w_eta_target']:.3f} | {r['n_mae']:.8e} | {r['eta_mean']:.6f} | {r['eta_sat_ratio']:.4f} | {r['mu_mean']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Heuristic selection rule",
            "- Prefer low n_mae, low eta_sat_ratio, and non-extreme mu_mean simultaneously.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Calibration sweep for material mapping v2")
    p.add_argument(
        "--input-csv",
        type=str,
        default="artifacts/ripple_triplet_material_mapping_v1/input_si_green1995_demo.csv",
    )
    p.add_argument(
        "--v2-script",
        type=str,
        default="scripts/explore/ripple_quantum_tests/triplet_material_mapping_v2.py",
    )
    p.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ripple_triplet_material_calibration_sweep_v5",
    )
    p.add_argument(
        "--distance-unit-to-m-list",
        type=float,
        nargs="+",
        default=[1.0, 1e-2, 1e-4, 1e-6],
    )
    p.add_argument("--eta-max-list", type=float, nargs="+", default=[0.3, 1.0, 2.0])
    p.add_argument("--w-eta-target-list", type=float, nargs="+", default=[0.05, 0.2, 1.0])
    return p.parse_args()


def main() -> int:
    a = parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v2 = Path(a.v2_script)
    input_csv = Path(a.input_csv)
    summary_rows: list[dict] = []
    runs: list[dict] = []

    i = 0
    for d2m, eta_max, w_eta in itertools.product(
        a.distance_unit_to_m_list, a.eta_max_list, a.w_eta_target_list
    ):
        i += 1
        case = f"case_{i:03d}"
        case_dir = out / case
        case_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "python",
            str(v2),
            "--input-csv",
            str(input_csv),
            "--out-dir",
            str(case_dir),
            "--distance-unit-to-m",
            str(d2m),
            "--eta-max",
            str(eta_max),
            "--w-eta-target",
            str(w_eta),
        ]
        subprocess.run(cmd, check=True)
        js = read_v2_json(case_dir / "TRIPLET_MATERIAL_MAPPING_V2.json")
        s = summarize(js, eta_max=float(eta_max))
        row = {
            "case": case,
            "distance_unit_to_m": float(d2m),
            "eta_max": float(eta_max),
            "w_eta_target": float(w_eta),
            "n_mae": float(s["n_mae"]),
            "eta_mean": float(s["eta_mean"]),
            "eta_sat_ratio": float(s["eta_sat_ratio"]),
            "mu_mean": float(s["mu_mean"]),
            "rho_mean": float(s["rho_mean"]),
        }
        summary_rows.append(row)
        runs.append({"case": case, "out_dir": str(case_dir), "cmd": cmd})

    # sort by saturation then n_mae then |mu|
    summary_rows.sort(key=lambda r: (r["eta_sat_ratio"], r["n_mae"], abs(r["mu_mean"])))
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_csv": str(input_csv),
        "runs": runs,
        "summary": summary_rows,
        "best_case": summary_rows[0] if summary_rows else None,
    }
    (out / "TRIPLET_MATERIAL_CALIBRATION_SWEEP_V5.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(out / "TRIPLET_MATERIAL_CALIBRATION_SWEEP_V5.csv", summary_rows)
    write_md(out / "TRIPLET_MATERIAL_CALIBRATION_SWEEP_V5.md", summary_rows)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

