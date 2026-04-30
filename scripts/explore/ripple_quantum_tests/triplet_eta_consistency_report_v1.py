"""
triplet_eta_consistency_report_v1

Evaluate whether eta_fit tracks absorption proxy k_ref.
Input: CSV from triplet_material_mapping_v7_1_joint.py
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    vx = sum((v - mx) ** 2 for v in x)
    vy = sum((v - my) ** 2 for v in y)
    if vx <= 1e-18 or vy <= 1e-18:
        return 0.0
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return cov / (vx**0.5 * vy**0.5)


def monotonic_non_decreasing(vals: list[float]) -> bool:
    return all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))


def main() -> int:
    p = argparse.ArgumentParser(description="Report eta-k consistency from joint mapping CSV")
    p.add_argument("--input-csv", required=True)
    p.add_argument("--out-dir", default="artifacts/ripple_triplet_eta_consistency_v1")
    a = p.parse_args()

    rows = []
    with Path(a.input_csv).open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(
                {
                    "material": row["material"],
                    "k_ref": float(row["k_ref"]),
                    "eta_fit": float(row["eta_fit"]),
                }
            )

    by_mat: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_mat[row["material"]].append(row)

    material_reports = []
    all_k, all_eta = [], []
    for m, rs in by_mat.items():
        rs_sorted = sorted(rs, key=lambda z: z["k_ref"])
        ks = [z["k_ref"] for z in rs_sorted]
        etas = [z["eta_fit"] for z in rs_sorted]
        all_k.extend(ks)
        all_eta.extend(etas)
        material_reports.append(
            {
                "material": m,
                "rows": len(rs),
                "k_nonzero_rows": sum(1 for v in ks if v > 0),
                "pearson_eta_vs_k": pearson(ks, etas),
                "eta_monotonic_by_k": monotonic_non_decreasing(etas),
                "eta_min": min(etas) if etas else 0.0,
                "eta_max": max(etas) if etas else 0.0,
            }
        )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_csv": a.input_csv,
        "global": {
            "rows": len(rows),
            "pearson_eta_vs_k": pearson(all_k, all_eta),
        },
        "materials": sorted(material_reports, key=lambda x: x["material"]),
    }

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "TRIPLET_ETA_CONSISTENCY_V1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        "# Triplet Eta Consistency v1",
        "",
        f"- global pearson(eta,k): `{payload['global']['pearson_eta_vs_k']:.6f}`",
        "",
        "| material | rows | k_nonzero_rows | pearson(eta,k) | eta_monotonic_by_k | eta_min | eta_max |",
        "|---|---:|---:|---:|---|---:|---:|",
    ]
    for m in payload["materials"]:
        lines.append(
            f"| {m['material']} | {m['rows']} | {m['k_nonzero_rows']} | {m['pearson_eta_vs_k']:.6f} | {m['eta_monotonic_by_k']} | {m['eta_min']:.6f} | {m['eta_max']:.6f} |"
        )
    (out / "TRIPLET_ETA_CONSISTENCY_V1.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

