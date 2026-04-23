import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = ROOT / "unsolved_problems_collision"


@dataclass(frozen=True)
class ProblemSpec:
    tier: str
    slug: str
    title: str
    question: str
    why_fit_model: str
    scenario: str
    steps: int = 260
    width: int = 220
    height: int = 160


PROBLEMS: List[ProblemSpec] = [
    ProblemSpec(
        tier="tier1_model_tailored",
        slug="abraham_minkowski_controversy",
        title="亚伯拉罕-闵可夫斯基之争",
        question="介质中光动量是增大还是减小，如何在同一框架中解释两种实验叙事？",
        why_fit_model="区分相速度（扩散前沿）与动量代理量（方向性流量），观察是否出现双重解释窗口。",
        scenario="medium_momentum",
    ),
    ProblemSpec(
        tier="tier1_model_tailored",
        slug="quantum_measurement_problem",
        title="量子测量问题",
        question="探测器触发后，局部吸收事件如何影响全局扩散图样？",
        why_fit_model="实现阈值吸收探测器，观察测量是否自然带来全局图样重排。",
        scenario="measurement_absorption",
    ),
    ProblemSpec(
        tier="tier1_model_tailored",
        slug="non_parallel_curve_double_slit",
        title="非蝴蝶形双缝干涉（曲线缝）",
        question="曲线双缝是否可在离散网格里自发形成非常规干涉纹理？",
        why_fit_model="直接把缝几何写入栅格障碍，检查图样是否对几何形状敏感。",
        scenario="curved_double_slit",
    ),
    ProblemSpec(
        tier="tier2_frontier_potential",
        slug="non_hermitian_topology_mirage_bath",
        title="非厄米拓扑与幻影浴",
        question="在耗散体系中，远距离发射源是否通过全局模式产生有效耦合？",
        why_fit_model="使用方向保持+侧向耗散规则，测量两源关联强度与距离关系。",
        scenario="two_emitter_dissipative",
    ),
    ProblemSpec(
        tier="tier2_frontier_potential",
        slug="confining_light_unicorn",
        title="关住独角兽：极端局域光",
        question="微小腔体中能量是否可形成近稳态驻留？",
        why_fit_model="构造高反射微腔，监测腔内能量衰减常数与驻留时间。",
        scenario="micro_cavity",
    ),
    ProblemSpec(
        tier="tier3_grand_challenge",
        slug="quantum_gravity_discrete_spacetime",
        title="量子引力（离散时空网格视角）",
        question="网格“曲率”变化是否会系统性偏折能量传播路径？",
        why_fit_model="把介质映射看作有效度规，统计传播重心偏转。",
        scenario="curved_metric",
    ),
    ProblemSpec(
        tier="tier3_grand_challenge",
        slug="light_transport_in_disordered_media",
        title="光在无序介质中的传输",
        question="随机缺陷会导致穿透受抑还是出现异常透射窗口？",
        why_fit_model="引入可控缺陷密度并扫描透射系数，找局域化阈值。",
        scenario="disordered_medium",
    ),
]


def _build_masks(spec: ProblemSpec) -> Dict[str, np.ndarray]:
    h, w = spec.height, spec.width
    yy, xx = np.mgrid[0:h, 0:w]
    masks: Dict[str, np.ndarray] = {}

    barrier = np.zeros((h, w), dtype=bool)
    medium = np.ones((h, w), dtype=float)
    detector = np.zeros((h, w), dtype=bool)

    if spec.scenario in {"medium_momentum", "measurement_absorption", "curved_double_slit"}:
        bx = w // 2
        barrier[:, bx] = True
        if spec.scenario == "curved_double_slit":
            curve1 = (h * 0.32 + 8 * np.sin(np.linspace(0, np.pi, h))).astype(int)
            curve2 = (h * 0.64 + 10 * np.sin(np.linspace(0, np.pi, h) + 0.7)).astype(int)
            barrier[:, bx] = True
            for y in range(h):
                if abs(y - curve1[y]) <= 2 or abs(y - curve2[y]) <= 2:
                    barrier[y, bx] = False
        else:
            slit_w = 7
            c1 = h // 2 - 25
            c2 = h // 2 + 25
            barrier[c1:c1 + slit_w, bx] = False
            barrier[c2:c2 + slit_w, bx] = False
        if spec.scenario == "medium_momentum":
            medium[:, bx + 1 :] = 0.78
        if spec.scenario == "measurement_absorption":
            detector[:, int(w * 0.83)] = True

    if spec.scenario == "two_emitter_dissipative":
        medium[:, :] = 0.94
        medium[:, w // 2 - 2 : w // 2 + 2] = 0.86

    if spec.scenario == "micro_cavity":
        cx, cy = int(w * 0.62), h // 2
        cavity_r = 14
        ring = np.abs(np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - cavity_r) <= 1.4
        barrier[ring] = True
        core = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) <= cavity_r - 2
        medium[~core] = 0.92
        medium[core] = 0.995

    if spec.scenario == "curved_metric":
        center = np.array([h / 2, w / 2])
        r2 = (yy - center[0]) ** 2 + (xx - center[1]) ** 2
        medium = 0.93 + 0.10 * np.exp(-r2 / (2 * (0.2 * w) ** 2))

    if spec.scenario == "disordered_medium":
        rng = np.random.default_rng(42)
        defects = rng.random((h, w)) < 0.08
        medium[defects] = 0.74

    masks["barrier"] = barrier
    masks["medium"] = medium
    masks["detector"] = detector
    return masks


def _run_simulation(spec: ProblemSpec) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    h, w = spec.height, spec.width
    masks = _build_masks(spec)
    barrier = masks["barrier"]
    medium = masks["medium"]
    detector = masks["detector"]

    grid = np.zeros((h, w), dtype=float)
    source_positions = [(h // 2, 5)]
    if spec.scenario == "two_emitter_dissipative":
        source_positions = [(h // 2 - 22, 5), (h // 2 + 22, 5)]

    source_power = 80.0
    for y, x in source_positions:
        grid[y, x] = source_power

    A, S, B = 0.95, 0.035, 0.015
    if spec.scenario == "curved_metric":
        A, S, B = 0.90, 0.06, 0.015
    if spec.scenario == "disordered_medium":
        A, S, B = 0.92, 0.05, 0.02

    loss = 0.986 if spec.scenario != "micro_cavity" else 0.993
    threshold = 1e-6
    detector_hits = 0
    source_trace = []

    for _ in range(spec.steps):
        new_grid = grid * 0.03
        active = np.argwhere(grid > threshold)
        for y, x in active:
            if barrier[y, x]:
                continue

            e = grid[y, x] * medium[y, x] * loss
            if e < threshold:
                continue

            if detector[y, x]:
                detector_hits += 1
                continue

            if x + 1 < w and not barrier[y, x + 1]:
                new_grid[y, x + 1] += e * A
            if y + 1 < h and not barrier[y + 1, x]:
                new_grid[y + 1, x] += e * S
            if y - 1 >= 0 and not barrier[y - 1, x]:
                new_grid[y - 1, x] += e * S
            if x - 1 >= 0 and not barrier[y, x - 1]:
                new_grid[y, x - 1] += e * B

        # 持续注入源，避免单脉冲快速熄灭导致无可分析信号。
        for y, x in source_positions:
            new_grid[y, x] += source_power

        grid = new_grid
        source_trace.append(float(grid[:, 5].sum()))

    screen = grid[:, -1].copy()
    intensity = np.log1p(grid)

    metrics = {
        "max_screen": float(screen.max()),
        "mean_screen": float(screen.mean()),
        "total_energy": float(grid.sum()),
        "detector_hits": float(detector_hits),
        "source_column_energy_final": float(grid[:, 5].sum()),
        "source_column_energy_trend": float(np.mean(source_trace[-20:])) if len(source_trace) >= 20 else float(np.mean(source_trace)),
    }
    return intensity, screen, metrics


def _write_problem_files(spec: ProblemSpec, intensity: np.ndarray, screen: np.ndarray, metrics: Dict[str, float]) -> None:
    problem_dir = BASE_DIR / spec.tier / spec.slug
    data_dir = problem_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    readme = problem_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                f"# {spec.title}",
                "",
                "## 未解决核心问题",
                spec.question,
                "",
                "## 为什么适合光-介质扰动模型",
                spec.why_fit_model,
                "",
                "## 本目录内容",
                "- `data/metrics.json`: 本次实验指标",
                "- `data/screen_profile.csv`: 末端屏幕能量分布",
                "- `data/final_grid.npy`: 最终能量网格（对数前）",
                "- `data/heatmap.png`: 最终对数能量热力图",
            ]
        ),
        encoding="utf-8",
    )

    with (data_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "problem": spec.slug,
                "scenario": spec.scenario,
                "steps": spec.steps,
                "grid_shape": [spec.height, spec.width],
                "metrics": metrics,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    with (data_dir / "screen_profile.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["y", "screen_energy"])
        for y, v in enumerate(screen.tolist()):
            writer.writerow([y, float(v)])

    np.save(data_dir / "final_grid.npy", np.expm1(intensity))

    plt.figure(figsize=(8, 4.5))
    plt.imshow(intensity, cmap="magma", aspect="auto", origin="upper")
    plt.colorbar(label="log(1+energy)")
    plt.title(spec.title)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.tight_layout()
    plt.savefig(data_dir / "heatmap.png", dpi=120)
    plt.close()


def main() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    index_path = BASE_DIR / "README.md"
    lines = [
        "# Unsolved Problems Collision Pack",
        "",
        "本目录按梯队记录未解决问题，并放置模型实验产出数据。",
        "",
        "## 目录结构",
        "- `tier1_model_tailored/`：为模型量身定制的问题",
        "- `tier2_frontier_potential/`：前沿潜力问题",
        "- `tier3_grand_challenge/`：宏大背景问题",
        "",
        "## 自动产物",
        "每个问题目录均包含 `README.md` 与 `data/` 实验文件。",
    ]
    index_path.write_text("\n".join(lines), encoding="utf-8")

    for spec in PROBLEMS:
        intensity, screen, metrics = _run_simulation(spec)
        _write_problem_files(spec, intensity, screen, metrics)
        print(f"[done] {spec.tier}/{spec.slug}")

    print(f"Generated pack at: {BASE_DIR}")


if __name__ == "__main__":
    main()
