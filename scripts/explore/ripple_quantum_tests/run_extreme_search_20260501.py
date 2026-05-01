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

    out_root = root / "artifacts/ripple_triplet_material_mapping_v7_1_joint/search_extreme_20260501"
    out_root.mkdir(parents=True, exist_ok=True)
    eta_out_root = root / "artifacts/ripple_triplet_eta_consistency_v1/search_extreme_20260501"
    eta_out_root.mkdir(parents=True, exist_ok=True)

    trials = []
    for fit_iters in [8, 10, 12]:
        for eta_steps in [61, 81]:
            for w_eta_target in [0.15, 0.2, 0.3]:
                for w_smooth_eta in [0.8, 1.0, 1.2]:
                    for w_eta_floor in [0.5, 0.6, 0.8]:
                        for w_eta_lowk_shape in [0.6, 0.8, 1.0]:
                            if len(trials) >= 36:
                                break
                            trials.append(
                                {
                                    "fit_iters": fit_iters,
                                    "eta_steps": eta_steps,
                                    "w_eta_target": w_eta_target,
                                    "w_smooth_eta": w_smooth_eta,
                                    "w_eta_floor": w_eta_floor,
                                    "w_eta_lowk_shape": w_eta_lowk_shape,
                                }
                            )
                        if len(trials) >= 36:
                            break
                    if len(trials) >= 36:
                        break
                if len(trials) >= 36:
                    break
            if len(trials) >= 36:
                break
        if len(trials) >= 36:
            break

    results = []
    for idx, t in enumerate(trials, 1):
        name = f"trial_{idx:03d}"
        out_dir = out_root / name
        eta_dir = eta_out_root / name
        cmd = [
            sys.executable,
            str(script),
            "--device",
            "cpu",
            "--out-dir",
            str(out_dir.relative_to(root)).replace("\\", "/"),
            "--fit-iters",
            str(t["fit_iters"]),
            "--eta-steps",
            str(t["eta_steps"]),
            "--w-eta-target",
            str(t["w_eta_target"]),
            "--w-smooth-eta",
            str(t["w_smooth_eta"]),
            "--w-eta-floor",
            str(t["w_eta_floor"]),
            "--w-eta-lowk-shape",
            str(t["w_eta_lowk_shape"]),
            "--input",
            *inputs,
        ]
        subprocess.run(cmd, cwd=root, check=True, stdout=subprocess.DEVNULL)

        csv_path = out_dir / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.csv"
        eta_cmd = [
            sys.executable,
            str(eta_script),
            "--input-csv",
            str(csv_path.relative_to(root)).replace("\\", "/"),
            "--out-dir",
            str(eta_dir.relative_to(root)).replace("\\", "/"),
        ]
        subprocess.run(eta_cmd, cwd=root, check=True, stdout=subprocess.DEVNULL)

        m_json = json.loads((out_dir / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.json").read_text(encoding="utf-8"))
        e_json = json.loads((eta_dir / "TRIPLET_ETA_CONSISTENCY_V1.json").read_text(encoding="utf-8"))

        maes = [m["n_mae"] for m in m_json["materials"]]
        mean_mae = sum(maes) / len(maes)
        max_mae = max(maes)
        gaas_mae = next(m["n_mae"] for m in m_json["materials"] if m["material"] == "gaas")

        nonmono = 0
        for m in e_json["materials"]:
            if m["k_nonzero_rows"] > 0 and not m["eta_monotonic_by_k"]:
                nonmono += 1

        global_pearson = e_json["global"]["pearson_eta_vs_k"]
        score = (
            0.55 * mean_mae
            + 0.25 * max_mae
            + 0.20 * gaas_mae
            + 0.015 * nonmono
            - 0.03 * max(global_pearson, 0.0)
        )

        results.append(
            {
                "trial": name,
                "score": score,
                "mean_mae": mean_mae,
                "max_mae": max_mae,
                "gaas_mae": gaas_mae,
                "nonmono_count": nonmono,
                "global_pearson": global_pearson,
                **t,
            }
        )

    results.sort(key=lambda x: x["score"])
    summary = {
        "total_trials": len(results),
        "best": results[0],
        "top10": results[:10],
    }
    summary_path = out_root / "SEARCH_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"trials={len(results)}")
    print(json.dumps(results[0], indent=2, ensure_ascii=False))
    print(f"summary={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
