"""
Triplet light probe comparison v1

Compare model-internal triplet probe outputs against mainstream reference media
using refractive-index-like and attenuation-like indicators.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class RefMedium:
    name: str
    n_eff_typical: float
    note: str
    # attenuation typical in dB/km; use None when not stable/universal
    att_db_per_km_typical: float | None


REF_MEDIA: list[RefMedium] = [
    RefMedium("vacuum", 1.0, "ideal reference", 0.0),
    RefMedium("air_STP_visible", 1.00027, "weakly dispersive; near 1", None),
    RefMedium("water_visible", 1.333, "strong wavelength dependence", None),
    RefMedium("silica_fiber_1550nm", 1.444, "telecom low-loss window", 0.2),
    RefMedium("silicon_1550nm", 3.48, "high index semiconductor", None),
]


def load_probe(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def att_db_per_unit_from_eta(eta: float) -> float:
    # intensity ratio = exp(-2*eta*x), so dB(x)=10*log10(I0/I)=10*log10(e^(2eta x))
    return (20.0 * eta) / math.log(10.0)


def mk_rows(n_eff_model: float, att_db_per_unit: float, unit_to_km: float) -> list[dict]:
    rows: list[dict] = []
    att_db_per_km_model = att_db_per_unit / max(unit_to_km, 1e-12)
    for m in REF_MEDIA:
        n_delta = n_eff_model - m.n_eff_typical
        n_ratio = n_eff_model / m.n_eff_typical
        att_ref = m.att_db_per_km_typical
        if att_ref is None:
            att_delta = None
            att_ratio = None
        else:
            att_delta = att_db_per_km_model - att_ref
            att_ratio = att_db_per_km_model / max(att_ref, 1e-12)
        rows.append(
            {
                "medium": m.name,
                "n_eff_model": n_eff_model,
                "n_eff_ref": m.n_eff_typical,
                "n_delta_model_minus_ref": n_delta,
                "n_ratio_model_over_ref": n_ratio,
                "att_model_db_per_km": att_db_per_km_model,
                "att_ref_db_per_km": att_ref,
                "att_delta_model_minus_ref": att_delta,
                "att_ratio_model_over_ref": att_ratio,
                "note": m.note,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def fmt(v) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


def write_md(path: Path, payload: dict, rows: list[dict]) -> None:
    unit_to_km = payload["unit_to_km"]
    model = payload["model"]
    lines = [
        "# Triplet Light Probe Comparison v1",
        "",
        "## Model snapshot",
        f"- n_eff(model) = `{model['n_eff']:.8f}`",
        f"- eta(model) = `{model['eta']:.8f}`",
        f"- attenuation(model) = `{model['att_db_per_unit']:.6f}` dB / distance_unit",
        f"- mapping assumption: `1 distance_unit = {unit_to_km} km`",
        f"- inferred attenuation(model) = `{model['att_db_per_km']:.6f}` dB/km",
        "",
        "## Reference comparison (illustrative ranges)",
        "",
        "| medium | n_model | n_ref | n_delta | n_ratio | att_model(dB/km) | att_ref(dB/km) | att_ratio | note |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            "| {medium} | {n_eff_model} | {n_eff_ref} | {n_delta} | {n_ratio} | {att_model} | {att_ref} | {att_ratio} | {note} |".format(
                medium=r["medium"],
                n_eff_model=fmt(r["n_eff_model"]),
                n_eff_ref=fmt(r["n_eff_ref"]),
                n_delta=fmt(r["n_delta_model_minus_ref"]),
                n_ratio=fmt(r["n_ratio_model_over_ref"]),
                att_model=fmt(r["att_model_db_per_km"]),
                att_ref=fmt(r["att_ref_db_per_km"]),
                att_ratio=fmt(r["att_ratio_model_over_ref"]),
                note=r["note"],
            )
        )
    lines.extend(
        [
            "",
            "## Caution",
            "- This comparison is a blind probe sanity check, not a claim of one-to-one SI identification.",
            "- The attenuation mapping depends on distance-unit calibration (`unit_to_km`).",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare triplet probe with mainstream media references")
    p.add_argument(
        "--probe-json",
        type=str,
        default="artifacts/ripple_triplet_light_probe_v1/TRIPLET_LIGHT_PROBE_V1.json",
    )
    p.add_argument(
        "--unit-to-km",
        type=float,
        default=1.0,
        help="Assume 1 distance_unit equals this many km",
    )
    p.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ripple_triplet_light_probe_v1_compare",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    probe = load_probe(Path(args.probe_json))
    cfg = probe["config"]
    v_ratio = float(probe["derived"]["v_ratio_to_c_ref"])
    n_eff = 1.0 / max(v_ratio, 1e-12)
    eta = float(cfg["eta"])
    att_db_per_unit = att_db_per_unit_from_eta(eta)
    unit_to_km = float(args.unit_to_km)
    att_db_per_km = att_db_per_unit / max(unit_to_km, 1e-12)

    rows = mk_rows(n_eff, att_db_per_unit, unit_to_km)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "probe_json": str(Path(args.probe_json)),
        "unit_to_km": unit_to_km,
        "model": {
            "n_eff": n_eff,
            "eta": eta,
            "att_db_per_unit": att_db_per_unit,
            "att_db_per_km": att_db_per_km,
        },
        "rows": rows,
    }
    (out / "TRIPLET_LIGHT_PROBE_COMPARE_V1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(out / "TRIPLET_LIGHT_PROBE_COMPARE_V1.csv", rows)
    write_md(out / "TRIPLET_LIGHT_PROBE_COMPARE_V1.md", payload, rows)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

