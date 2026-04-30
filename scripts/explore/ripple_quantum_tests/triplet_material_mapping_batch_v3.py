"""
triplet_material_mapping_batch_v3

Batch-run v2 material mapping on multiple CSV files and generate a compact summary.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_one(v2_script: Path, input_csv: Path, out_dir: Path, extra_args: list[str]) -> Path:
    target = out_dir / input_csv.stem
    target.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python",
        str(v2_script),
        "--input-csv",
        str(input_csv),
        "--out-dir",
        str(target),
        *extra_args,
    ]
    subprocess.run(cmd, check=True)
    return target / "TRIPLET_MATERIAL_MAPPING_V2.json"


def summarize_one(payload: dict) -> dict:
    rows = payload.get("rows", [])
    if not rows:
        return {
            "rows": 0,
            "n_mae": None,
            "mu_mean": None,
            "rho_mean": None,
            "eta_mean": None,
        }
    n = len(rows)
    n_mae = sum(abs(float(r.get("n_err", 0.0))) for r in rows) / n
    mu_mean = sum(float(r.get("mu_fit", 0.0)) for r in rows) / n
    rho_mean = sum(float(r.get("rho_fit", 0.0)) for r in rows) / n
    eta_mean = sum(float(r.get("eta_fit", 0.0)) for r in rows) / n
    k_nonzero_rows = sum(1 for r in rows if float(r.get("k_ref", 0.0)) > 0)
    return {
        "rows": n,
        "n_mae": n_mae,
        "mu_mean": mu_mean,
        "rho_mean": rho_mean,
        "eta_mean": eta_mean,
        "k_nonzero_rows": k_nonzero_rows,
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
        "# Triplet Material Mapping Batch v3",
        "",
        "| material | rows | k_nonzero_rows | n_mae | mu_mean | rho_mean | eta_mean | source_csv |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['material']} | {r['rows']} | {r['k_nonzero_rows']} | {r['n_mae']:.8e} | {r['mu_mean']:.6f} | {r['rho_mean']:.6f} | {r['eta_mean']:.6f} | {r['source_csv']} |"
        )
    lines.extend(
        [
            "",
            "## Note",
            "- Compare monotonic trends across materials (e.g., n level vs mu/rho means).",
            "- For eta identifiability, include non-zero k(λ) tables where available.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch run material mapping v2 and build summary")
    p.add_argument(
        "--inputs",
        type=str,
        nargs="+",
        required=True,
        help="Multiple input CSV files",
    )
    p.add_argument(
        "--v2-script",
        type=str,
        default="scripts/explore/ripple_quantum_tests/triplet_material_mapping_v2.py",
    )
    p.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ripple_triplet_material_mapping_v3_batch",
    )
    # pass-through args for v2
    p.add_argument("--rho-min", type=float, default=1.0)
    p.add_argument("--rho-max", type=float, default=4.0)
    p.add_argument("--rho-steps", type=int, default=81)
    p.add_argument("--eta-min", type=float, default=0.0)
    p.add_argument("--eta-max", type=float, default=0.3)
    p.add_argument("--eta-steps", type=int, default=81)
    p.add_argument("--w-n", type=float, default=1.0)
    p.add_argument("--w-eta-target", type=float, default=0.2)
    p.add_argument("--w-smooth-rho", type=float, default=2.0)
    p.add_argument("--w-smooth-eta", type=float, default=2.0)
    return p.parse_args()


def main() -> int:
    a = parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v2_script = Path(a.v2_script)
    extra = [
        "--rho-min",
        str(a.rho_min),
        "--rho-max",
        str(a.rho_max),
        "--rho-steps",
        str(a.rho_steps),
        "--eta-min",
        str(a.eta_min),
        "--eta-max",
        str(a.eta_max),
        "--eta-steps",
        str(a.eta_steps),
        "--w-n",
        str(a.w_n),
        "--w-eta-target",
        str(a.w_eta_target),
        "--w-smooth-rho",
        str(a.w_smooth_rho),
        "--w-smooth-eta",
        str(a.w_smooth_eta),
    ]

    summary_rows: list[dict] = []
    run_index: list[dict] = []
    for s in a.inputs:
        src = Path(s)
        out_json = run_one(v2_script, src, out, extra)
        payload = json.loads(out_json.read_text(encoding="utf-8"))
        summ = summarize_one(payload)
        material = src.stem
        summary_rows.append(
            {
                "material": material,
                "rows": summ["rows"],
                "n_mae": summ["n_mae"] if summ["n_mae"] is not None else 0.0,
                "mu_mean": summ["mu_mean"] if summ["mu_mean"] is not None else 0.0,
                "rho_mean": summ["rho_mean"] if summ["rho_mean"] is not None else 0.0,
                "eta_mean": summ["eta_mean"] if summ["eta_mean"] is not None else 0.0,
                "k_nonzero_rows": summ["k_nonzero_rows"] if summ["k_nonzero_rows"] is not None else 0,
                "source_csv": str(src),
            }
        )
        run_index.append(
            {
                "material": material,
                "source_csv": str(src),
                "result_json": str(out_json),
            }
        )

    summary_json = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runs": run_index,
        "summary": summary_rows,
    }
    (out / "TRIPLET_MATERIAL_MAPPING_BATCH_V3.json").write_text(
        json.dumps(summary_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(out / "TRIPLET_MATERIAL_MAPPING_BATCH_V3.csv", summary_rows)
    write_md(out / "TRIPLET_MATERIAL_MAPPING_BATCH_V3.md", summary_rows)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

