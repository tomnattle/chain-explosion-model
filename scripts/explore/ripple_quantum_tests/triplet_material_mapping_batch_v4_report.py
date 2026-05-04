"""
triplet_material_mapping_batch_v4_report

Build diagnostic report from v3 batch outputs:
- n_mean and mu_mean monotonicity
- linear fit slope mu_mean ~ a * n_mean + b
- scatter plot mu_mean vs n_mean
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_v3_csv(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(
                {
                    "material": row["material"],
                    "mu_mean": float(row["mu_mean"]),
                    "rho_mean": float(row["rho_mean"]),
                    "eta_mean": float(row["eta_mean"]),
                    "source_csv": row["source_csv"],
                }
            )
    return rows


def mean_n_from_source_csv(source_csv: Path) -> float:
    vals = []
    with source_csv.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            vals.append(float(row["n_ref"]))
    return float(np.mean(vals)) if vals else float("nan")


def monotonic_non_decreasing(arr: list[float]) -> bool:
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))


def write_md(path: Path, payload: dict) -> None:
    lines = [
        "# Triplet Material Mapping Batch v4 Report",
        "",
        "## Diagnostics",
        f"- monotonic_by_n_mu: `{payload['diagnostics']['monotonic_by_n_mu']}`",
        f"- linear_fit: `mu_mean = {payload['diagnostics']['fit_a']:.6f} * n_mean + {payload['diagnostics']['fit_b']:.6f}`",
        f"- R2: `{payload['diagnostics']['fit_r2']:.6f}`",
        "",
        "## Per material",
        "",
        "| material | n_mean | mu_mean | rho_mean | eta_mean |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in payload["rows"]:
        lines.append(
            f"| {r['material']} | {r['n_mean']:.6f} | {r['mu_mean']:.6f} | {r['rho_mean']:.6f} | {r['eta_mean']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Note",
            "- This is trend diagnostics, not causal proof.",
            "- eta trend requires non-zero k(λ) material tables.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Generate v4 diagnostics report from v3 batch summary")
    p.add_argument(
        "--v3-csv",
        type=str,
        default="artifacts/ripple_triplet_material_mapping_v3_batch/TRIPLET_MATERIAL_MAPPING_BATCH_V3.csv",
    )
    p.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ripple_triplet_material_mapping_v4_report",
    )
    a = p.parse_args()

    base = Path(a.v3_csv).resolve().parent.parent.parent
    rows = load_v3_csv(Path(a.v3_csv))
    for r in rows:
        src = Path(r["source_csv"])
        if not src.is_absolute():
            src = base / src
        r["n_mean"] = mean_n_from_source_csv(src)

    rows_sorted = sorted(rows, key=lambda x: x["n_mean"])
    xs = np.array([r["n_mean"] for r in rows_sorted], dtype=float)
    ys = np.array([r["mu_mean"] for r in rows_sorted], dtype=float)
    a_fit, b_fit = np.polyfit(xs, ys, 1)
    y_hat = a_fit * xs + b_fit
    ss_res = float(np.sum((ys - y_hat) ** 2))
    ss_tot = float(np.sum((ys - np.mean(ys)) ** 2))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-18)
    mono = monotonic_non_decreasing(list(ys))

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # figure
    fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=130)
    ax.scatter(xs, ys, s=40)
    for r in rows_sorted:
        ax.annotate(r["material"], (r["n_mean"], r["mu_mean"]), xytext=(5, 4), textcoords="offset points", fontsize=8)
    xg = np.linspace(float(xs.min()), float(xs.max()), 100)
    ax.plot(xg, a_fit * xg + b_fit, lw=1.4)
    ax.set_xlabel("n_mean")
    ax.set_ylabel("mu_mean")
    ax.set_title("Triplet mapping trend: mu_mean vs n_mean")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "MU_MEAN_VS_N_MEAN_V4.png")
    plt.close(fig)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_v3_csv": a.v3_csv,
        "rows": rows_sorted,
        "diagnostics": {
            "monotonic_by_n_mu": mono,
            "fit_a": float(a_fit),
            "fit_b": float(b_fit),
            "fit_r2": float(r2),
        },
    }
    (out / "TRIPLET_MATERIAL_MAPPING_BATCH_V4_REPORT.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_md(out / "TRIPLET_MATERIAL_MAPPING_BATCH_V4_REPORT.md", payload)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

