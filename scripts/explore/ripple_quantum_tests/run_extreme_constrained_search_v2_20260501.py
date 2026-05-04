from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Constrained search for extreme material pack.")
    p.add_argument("--max-trials", type=int, default=72, help="Limit number of trial combinations to run.")
    a = p.parse_args()

    root = Path(__file__).resolve().parents[3]
    map_script = root / "scripts/explore/ripple_quantum_tests/triplet_material_mapping_v7_1_joint.py"
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

    baseline_path = (
        root
        / "artifacts/ripple_triplet_material_mapping_v7_1_joint/extreme_pack_final_20260501/TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.json"
    )
    base = json.loads(baseline_path.read_text(encoding="utf-8"))
    base_mae = {m["material"]: float(m["n_mae"]) for m in base["materials"]}

    out_root = root / "artifacts/ripple_triplet_material_mapping_v7_1_joint/search_extreme_constrained_v2_20260501"
    eta_root = root / "artifacts/ripple_triplet_eta_consistency_v1/search_extreme_constrained_v2_20260501"
    out_root.mkdir(parents=True, exist_ok=True)
    eta_root.mkdir(parents=True, exist_ok=True)

    grid = []
    for fit_iters in [12, 16, 20]:
        for w_eta_target in [0.2, 0.25, 0.3]:
            for w_smooth_eta in [0.8, 1.0]:
                for w_eta_floor in [0.25, 0.35, 0.5]:
                    for gaas_cap in [2.0, 2.5]:
                        for highn_cap in [2.0, 3.0, 4.0]:
                            grid.append(
                                {
                                    "fit_iters": fit_iters,
                                    "w_eta_target": w_eta_target,
                                    "w_smooth_eta": w_smooth_eta,
                                    "w_eta_floor": w_eta_floor,
                                    "gaas_cap": gaas_cap,
                                    "highn_cap": highn_cap,
                                }
                            )
    # 按需截断，控制总时长
    max_trials = max(int(a.max_trials), 1)
    grid = grid[:max_trials]

    rows = []
    for idx, c in enumerate(grid, 1):
        name = f"trial_{idx:03d}"
        out_dir = out_root / name
        eta_dir = eta_root / name
        cmd = [
            sys.executable,
            str(map_script),
            "--device",
            "cpu",
            "--out-dir",
            str(out_dir.relative_to(root)).replace("\\", "/"),
            "--fit-iters",
            str(c["fit_iters"]),
            "--eta-steps",
            "61",
            "--w-eta-target",
            str(c["w_eta_target"]),
            "--w-smooth-eta",
            str(c["w_smooth_eta"]),
            "--w-eta-floor",
            str(c["w_eta_floor"]),
            "--w-eta-lowk-shape",
            "1.0",
            "--eta-max-override",
            f"gaas={c['gaas_cap']}",
            "--eta-max-override",
            f"highnlowk={c['highn_cap']}",
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
        mae = {m["material"]: float(m["n_mae"]) for m in m_json["materials"]}
        max_mae = max(mae.values())
        nonmono = [
            m["material"]
            for m in e_json["materials"]
            if int(m["k_nonzero_rows"]) > 0 and not bool(m["eta_monotonic_by_k"])
        ]

        # 硬门槛: 非单调=0，且 core4 不退化过多（允许轻微波动）
        core4_ok = (
            mae["si"] <= base_mae["si"] + 0.010
            and mae["sio2"] <= base_mae["sio2"] + 0.010
            and mae["kdemo"] <= base_mae["kdemo"] + 0.010
            and mae["gaas"] <= base_mae["gaas"] + 0.015
        )
        feasible = (len(nonmono) == 0) and core4_ok

        score = (
            1.20 * mae["highnlowk"]
            + 0.60 * max_mae
            + 0.35 * mae["gaas"]
            + 0.20 * mae["midkcurve"]
            + (0.20 if not feasible else 0.0)
        )

        rows.append(
            {
                "trial": name,
                "feasible": feasible,
                "nonmono": nonmono,
                "score": score,
                "max_mae": max_mae,
                "highnlowk_mae": mae["highnlowk"],
                "gaas_mae": mae["gaas"],
                "midkcurve_mae": mae["midkcurve"],
                "si_mae": mae["si"],
                "sio2_mae": mae["sio2"],
                "kdemo_mae": mae["kdemo"],
                **c,
            }
        )

    feas = [r for r in rows if r["feasible"]]
    if feas:
        feas.sort(key=lambda r: (r["score"], r["highnlowk_mae"], r["max_mae"]))
        best = feas[0]
    else:
        rows.sort(key=lambda r: (r["score"], len(r["nonmono"]), r["max_mae"]))
        best = rows[0]
    rows.sort(key=lambda r: (not r["feasible"], r["score"]))

    summary = {
        "baseline": base_mae,
        "total_trials": len(rows),
        "feasible_trials": len(feas),
        "best": best,
        "top10": rows[:10],
    }
    out = out_root / "SEARCH_SUMMARY.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(best, ensure_ascii=False, indent=2))
    print(f"summary={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
