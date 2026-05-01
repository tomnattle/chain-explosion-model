from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    script = root / "scripts/explore/ripple_quantum_tests/triplet_material_mapping_v7_1_joint.py"
    eta_script = root / "scripts/explore/ripple_quantum_tests/triplet_eta_consistency_report_v1.py"

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

    out_root = root / "artifacts/ripple_triplet_material_mapping_v7_1_joint/sweep_w_eta_extreme_20260501"
    out_root.mkdir(parents=True, exist_ok=True)
    eta_root = root / "artifacts/ripple_triplet_eta_consistency_v1/sweep_w_eta_extreme_20260501"
    eta_root.mkdir(parents=True, exist_ok=True)

    results = []
    for w_eta in [0.15, 0.2, 0.25, 0.3, 0.35, 0.4]:
        for fit_iters in [10, 12]:
            name = f"w{w_eta:g}_it{fit_iters}"
            out_dir = out_root / name
            eta_dir = eta_root / name
            cmd = [
                sys.executable,
                str(script),
                "--device",
                "cpu",
                "--out-dir",
                str(out_dir.relative_to(root)).replace("\\", "/"),
                "--fit-iters",
                str(fit_iters),
                "--eta-steps",
                "61",
                "--w-eta-target",
                str(w_eta),
                "--w-smooth-eta",
                "1.0",
                "--w-eta-floor",
                "0.5",
                "--w-eta-lowk-shape",
                "1.0",
                "--input",
                *inputs,
            ]
            subprocess.run(cmd, cwd=root, check=True, stdout=subprocess.DEVNULL)

            csv_path = out_dir / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(eta_script),
                    "--input-csv",
                    str(csv_path.relative_to(root)).replace("\\", "/"),
                    "--out-dir",
                    str(eta_dir.relative_to(root)).replace("\\", "/"),
                ],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
            )

            m_json = json.loads((out_dir / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.json").read_text(encoding="utf-8"))
            e_json = json.loads((eta_dir / "TRIPLET_ETA_CONSISTENCY_V1.json").read_text(encoding="utf-8"))

            maes = [m["n_mae"] for m in m_json["materials"]]
            mean_mae = sum(maes) / len(maes)
            max_mae = max(maes)

            bad = []
            nonmono = 0
            for m in e_json["materials"]:
                if m["k_nonzero_rows"] <= 0:
                    continue
                if not m["eta_monotonic_by_k"]:
                    nonmono += 1
                    bad.append(m["material"])
                if m["pearson_eta_vs_k"] < 0.0:
                    bad.append(f"{m['material']}:neg_r")

            score = mean_mae + 0.35 * max_mae + 0.04 * nonmono
            results.append(
                {
                    "name": name,
                    "w_eta_target": w_eta,
                    "fit_iters": fit_iters,
                    "mean_mae": mean_mae,
                    "max_mae": max_mae,
                    "nonmono_count": nonmono,
                    "nonmono_materials": [m["material"] for m in e_json["materials"] if m["k_nonzero_rows"] > 0 and not m["eta_monotonic_by_k"]],
                    "score": score,
                }
            )

    results.sort(key=lambda x: (x["nonmono_count"], x["score"]))
    summary_path = out_root / "SWEEP_SUMMARY.json"
    summary_path.write_text(json.dumps({"results": results, "best": results[0]}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(results[0], indent=2, ensure_ascii=False))
    print(f"summary={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
