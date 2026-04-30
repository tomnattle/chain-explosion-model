"""
material_optical_csv_validate_v1

Validate optical table CSV format for triplet mapping:
- required columns: wavelength_nm, n_ref
- optional column: k_ref
- checks: numeric, positive wavelength, non-negative n_ref/k_ref, monotonic wavelength
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Validate optical CSV for triplet material mapping")
    p.add_argument("--input-csv", type=str, required=True)
    p.add_argument(
        "--out-json",
        type=str,
        default="artifacts/ripple_triplet_material_mapping_v1/OPTICAL_CSV_VALIDATE_V1.json",
    )
    a = p.parse_args()

    src = Path(a.input_csv)
    rows = []
    issues: list[str] = []
    warnings: list[str] = []
    with src.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        cols = [c.strip() for c in (r.fieldnames or [])]
        required = {"wavelength_nm", "n_ref"}
        if not required.issubset(set(cols)):
            issues.append(f"missing required columns: {sorted(required - set(cols))}")
            payload = {
                "ok": False,
                "source_csv": str(src),
                "issues": issues,
                "warnings": warnings,
                "rows": 0,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            Path(a.out_json).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"[fail] {issues[0]}")
            return 1

        has_k = "k_ref" in cols
        for i, row in enumerate(r, start=2):
            try:
                wl = float(row["wavelength_nm"])
                n = float(row["n_ref"])
                k = float(row.get("k_ref", "0") or 0.0)
            except Exception:
                issues.append(f"line {i}: non-numeric value")
                continue
            if wl <= 0:
                issues.append(f"line {i}: wavelength_nm must be > 0")
            if n <= 0:
                issues.append(f"line {i}: n_ref must be > 0")
            if k < 0:
                issues.append(f"line {i}: k_ref must be >= 0")
            rows.append((wl, n, k))

    if rows:
        for i in range(1, len(rows)):
            if rows[i][0] <= rows[i - 1][0]:
                warnings.append("wavelength_nm is not strictly increasing")
                break
        k_nonzero = sum(1 for _, _, k in rows if k > 0)
        if not has_k:
            warnings.append("k_ref column missing; eta identifiability will be weak")
        elif k_nonzero == 0:
            warnings.append("k_ref all zeros; eta fit may collapse near zero")

    ok = len(issues) == 0
    payload = {
        "ok": ok,
        "source_csv": str(src),
        "rows": len(rows),
        "k_nonzero_rows": sum(1 for _, _, k in rows if k > 0),
        "issues": issues,
        "warnings": warnings,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    out = Path(a.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] wrote {out}" if ok else f"[fail] wrote {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

