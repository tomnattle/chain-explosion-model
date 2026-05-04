from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_profile(root: Path, profile: str, out_tag: str, inputs: list[str]) -> tuple[Path, Path]:
    map_script = root / "scripts/explore/ripple_quantum_tests/triplet_material_mapping_v7_1_joint.py"
    eta_script = root / "scripts/explore/ripple_quantum_tests/triplet_eta_consistency_report_v1.py"

    map_out = root / f"artifacts/ripple_triplet_material_mapping_v7_1_joint/{out_tag}"
    eta_out = root / f"artifacts/ripple_triplet_eta_consistency_v1/{out_tag}"

    cmd_map = [
        sys.executable,
        str(map_script),
        "--device",
        "cpu",
        "--profile",
        profile,
        "--out-dir",
        str(map_out.relative_to(root)).replace("\\", "/"),
        "--input",
        *inputs,
    ]
    subprocess.run(cmd_map, cwd=root, check=True)

    cmd_eta = [
        sys.executable,
        str(eta_script),
        "--input-csv",
        str((map_out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.csv").relative_to(root)).replace("\\", "/"),
        "--out-dir",
        str(eta_out.relative_to(root)).replace("\\", "/"),
    ]
    subprocess.run(cmd_eta, cwd=root, check=True)
    return map_out, eta_out


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    date_tag = datetime.now(timezone.utc).strftime("%Y%m%d")
    inputs = [
        "si=artifacts/ripple_triplet_material_mapping_v1/input_si_green1995_demo.csv",
        "sio2=artifacts/ripple_triplet_material_mapping_v1/input_sio2_malitson_visible.csv",
        "kdemo=artifacts/ripple_triplet_material_mapping_v1/input_template_with_k_demo.csv",
        "gaas=artifacts/ripple_triplet_material_mapping_v1/input_gaas_aspnes_demo.csv",
        "air=artifacts/ripple_triplet_material_mapping_v1/input_air_visible_demo.csv",
        "water=artifacts/ripple_triplet_material_mapping_v1/input_water_visible_demo.csv",
        "metalx=artifacts/ripple_triplet_material_mapping_v1/input_extreme_metal_like_demo.csv",
        "ultralowk=artifacts/ripple_triplet_material_mapping_v1/input_extreme_ultralowk_demo.csv",
        "highnlowk=artifacts/ripple_triplet_material_mapping_v1/input_extreme_highn_lowk_demo.csv",
        "midkcurve=artifacts/ripple_triplet_material_mapping_v1/input_extreme_midk_curved_demo.csv",
    ]

    robust_tag = f"profile_robust_{date_tag}"
    si_tag = f"profile_si_priority_{date_tag}"
    robust_map_out, robust_eta_out = run_profile(root, "robust", robust_tag, inputs)
    si_map_out, si_eta_out = run_profile(root, "si_priority", si_tag, inputs)

    robust_map = json.loads((robust_map_out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.json").read_text(encoding="utf-8"))
    robust_eta = json.loads((robust_eta_out / "TRIPLET_ETA_CONSISTENCY_V1.json").read_text(encoding="utf-8"))
    si_map = json.loads((si_map_out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.json").read_text(encoding="utf-8"))
    si_eta = json.loads((si_eta_out / "TRIPLET_ETA_CONSISTENCY_V1.json").read_text(encoding="utf-8"))

    def extract(map_json: dict, eta_json: dict) -> dict:
        mae = {m["material"]: float(m["n_mae"]) for m in map_json["materials"]}
        nonmono = [
            m["material"]
            for m in eta_json["materials"]
            if int(m["k_nonzero_rows"]) > 0 and not bool(m["eta_monotonic_by_k"])
        ]
        return {
            "n_mae": mae,
            "max_n_mae": max(mae.values()),
            "global_eta_k_pearson": float(eta_json["global"]["pearson_eta_vs_k"]),
            "nonmono_materials": nonmono,
            "all_monotonic_k_positive": len(nonmono) == 0,
        }

    robust = extract(robust_map, robust_eta)
    si_pri = extract(si_map, si_eta)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profiles": {
            "robust": {
                "map_out": str(robust_map_out.relative_to(root)).replace("\\", "/"),
                "eta_out": str(robust_eta_out.relative_to(root)).replace("\\", "/"),
                **robust,
            },
            "si_priority": {
                "map_out": str(si_map_out.relative_to(root)).replace("\\", "/"),
                "eta_out": str(si_eta_out.relative_to(root)).replace("\\", "/"),
                **si_pri,
            },
        },
    }

    out_dir = root / f"artifacts/ripple_triplet_material_mapping_v7_1_joint/profile_compare_{date_tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "PROFILE_COMPARE_SUMMARY.json"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Triplet Mapping Profile Compare",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        "",
        "| profile | max_n_mae | si_n_mae | highnlowk_n_mae | gaas_n_mae | all_monotonic_k>0 | global_pearson(eta,k) |",
        "|---|---:|---:|---:|---:|---|---:|",
    ]
    for pname in ["robust", "si_priority"]:
        p = summary["profiles"][pname]
        lines.append(
            f"| {pname} | {p['max_n_mae']:.6f} | {p['n_mae']['si']:.6f} | {p['n_mae']['highnlowk']:.6f} | {p['n_mae']['gaas']:.6f} | {p['all_monotonic_k_positive']} | {p['global_eta_k_pearson']:.6f} |"
        )
        if p["nonmono_materials"]:
            lines.append(f"- {pname} non-monotonic: {', '.join(p['nonmono_materials'])}")
    out_md = out_dir / "PROFILE_COMPARE_SUMMARY.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"[ok] wrote {out_json}")
    print(f"[ok] wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

