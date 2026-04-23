import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
try:
    import torch  # type: ignore
except Exception:
    torch = None

try:
    import torch_directml  # type: ignore
except Exception:
    torch_directml = None


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = (
    ROOT
    / "unsolved_problems_collision"
    / "tier3_grand_challenge"
    / "light_transport_in_disordered_media"
    / "data"
)


def run_once(
    disorder_density: float,
    seed: int,
    periodic: bool,
    width: int = 220,
    height: int = 160,
    steps: int = 300,
) -> Dict[str, float]:
    if torch is None:
        return _run_once_numpy(disorder_density, seed, periodic, width, height, steps)

    device = _resolve_device()
    grid = torch.zeros((height, width), dtype=torch.float32, device=device)
    medium = torch.ones((height, width), dtype=torch.float32, device=device)
    barrier = torch.zeros((height, width), dtype=torch.bool, device=device)

    source_power = 80.0
    grid[height // 2, 5] = float(source_power)

    if periodic:
        period = max(3, int(round(1.0 / max(disorder_density, 1e-6))))
        medium[:, ::period] = 0.74
    else:
        rng = np.random.default_rng(seed)
        defects = rng.random((height, width)) < disorder_density
        defects_t = torch.from_numpy(defects).to(device=device)
        medium[defects_t] = 0.74

    A, S, B = 0.92, 0.05, 0.02
    loss = 0.986

    for _ in range(steps):
        e = grid * medium * loss
        e = torch.where(e > 1e-6, e, torch.zeros_like(e))
        e = torch.where(barrier, torch.zeros_like(e), e)

        new_grid = grid * 0.03
        # 右移
        new_grid[:, 1:] += e[:, :-1] * A
        # 下移
        new_grid[1:, :] += e[:-1, :] * S
        # 上移
        new_grid[:-1, :] += e[1:, :] * S
        # 左移
        new_grid[:, :-1] += e[:, 1:] * B

        # 再次应用 barrier 抑制
        new_grid = torch.where(barrier, torch.zeros_like(new_grid), new_grid)
        new_grid[height // 2, 5] += float(source_power)
        grid = new_grid

    screen = grid[:, -1]
    transmission = float((screen.sum() / (grid.sum() + 1e-12)).item())
    envelope_x = torch.clamp(grid.mean(dim=0), min=1e-12).detach().cpu().numpy()
    x = np.arange(width)
    slope, _ = np.polyfit(x, np.log(envelope_x), 1)
    localization_len = float(-1.0 / slope) if slope < 0 else float("inf")
    screen_np = screen.detach().cpu().numpy()
    rare_channel_freq = float(np.mean(screen_np > (screen_np.mean() + 2.0 * screen_np.std())))

    return {
        "disorder_density": float(disorder_density),
        "seed": float(seed),
        "periodic": float(1 if periodic else 0),
        "transmission": transmission,
        "localization_length_proxy": localization_len,
        "rare_channel_freq": rare_channel_freq,
        "screen_mean": float(screen_np.mean()),
        "screen_max": float(screen_np.max()),
    }


def _run_once_numpy(
    disorder_density: float,
    seed: int,
    periodic: bool,
    width: int,
    height: int,
    steps: int,
) -> Dict[str, float]:
    grid = np.zeros((height, width), dtype=float)
    medium = np.ones((height, width), dtype=float)
    barrier = np.zeros((height, width), dtype=bool)

    source_power = 80.0
    grid[height // 2, 5] = source_power

    if periodic:
        period = max(3, int(round(1.0 / max(disorder_density, 1e-6))))
        medium[:, ::period] = 0.74
    else:
        rng = np.random.default_rng(seed)
        defects = rng.random((height, width)) < disorder_density
        medium[defects] = 0.74

    A, S, B = 0.92, 0.05, 0.02
    loss = 0.986

    for _ in range(steps):
        e = grid * medium * loss
        e[e <= 1e-6] = 0.0
        e[barrier] = 0.0

        new_grid = grid * 0.03
        new_grid[:, 1:] += e[:, :-1] * A
        new_grid[1:, :] += e[:-1, :] * S
        new_grid[:-1, :] += e[1:, :] * S
        new_grid[:, :-1] += e[:, 1:] * B
        new_grid[barrier] = 0.0
        new_grid[height // 2, 5] += source_power
        grid = new_grid

    screen = grid[:, -1]
    transmission = float(screen.sum() / (grid.sum() + 1e-12))
    envelope_x = np.maximum(grid.mean(axis=0), 1e-12)
    x = np.arange(width)
    slope, _ = np.polyfit(x, np.log(envelope_x), 1)
    localization_len = float(-1.0 / slope) if slope < 0 else float("inf")
    rare_channel_freq = float(np.mean(screen > (screen.mean() + 2.0 * screen.std())))

    return {
        "disorder_density": float(disorder_density),
        "seed": float(seed),
        "periodic": float(1 if periodic else 0),
        "transmission": transmission,
        "localization_length_proxy": localization_len,
        "rare_channel_freq": rare_channel_freq,
        "screen_mean": float(screen.mean()),
        "screen_max": float(screen.max()),
    }


def _resolve_device():
    if torch is not None and torch_directml is not None:
        try:
            return torch_directml.device()
        except Exception:
            pass
    if torch is not None:
        return torch.device("cpu")
    return "cpu(numpy)"


def verdict(random_rows: List[Dict[str, float]], periodic_rows: List[Dict[str, float]]) -> Tuple[str, Dict[str, float]]:
    dense_random = [r["transmission"] for r in random_rows if r["disorder_density"] >= 0.14]
    light_random = [r["transmission"] for r in random_rows if r["disorder_density"] <= 0.04]
    periodic_same = [r["transmission"] for r in periodic_rows if abs(r["disorder_density"] - 0.16) < 1e-9]

    mean_dense = float(np.mean(dense_random)) if dense_random else 0.0
    mean_light = float(np.mean(light_random)) if light_random else 0.0
    mean_periodic = float(np.mean(periodic_same)) if periodic_same else 0.0

    trend = mean_light - mean_dense
    periodic_adv = mean_periodic - mean_dense
    if trend > 0.002 and periodic_adv > 0:
        label = "支持：存在结构性趋势（随机无序压低透射，周期缺陷相对提升）"
    elif abs(trend) <= 0.002:
        label = "不支持：透射率随无序度未形成稳定趋势"
    else:
        label = "不确定：出现趋势但统计强度不足"
    return label, {
        "mean_transmission_light_random": mean_light,
        "mean_transmission_dense_random": mean_dense,
        "mean_transmission_periodic_at_0p16": mean_periodic,
        "trend_light_minus_dense": trend,
        "periodic_advantage_vs_dense_random": periodic_adv,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = _resolve_device()
    print("Backend device:", device)
    random_densities = [0.00, 0.02, 0.04, 0.08, 0.12, 0.16, 0.20]
    seeds = [11, 23, 37, 41, 53]

    rows: List[Dict[str, float]] = []
    for d in random_densities:
        for s in seeds:
            rows.append(run_once(disorder_density=d, seed=s, periodic=False))

    for d in [0.04, 0.08, 0.12, 0.16, 0.20]:
        rows.append(run_once(disorder_density=d, seed=0, periodic=True))

    csv_path = OUT_DIR / "scan_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    random_rows = [r for r in rows if r["periodic"] == 0]
    periodic_rows = [r for r in rows if r["periodic"] == 1]

    grouped = {}
    for d in random_densities:
        vals = [r["transmission"] for r in random_rows if abs(r["disorder_density"] - d) < 1e-9]
        grouped[d] = (float(np.mean(vals)), float(np.std(vals)))

    plt.figure(figsize=(7.2, 4.6))
    xs = np.array(sorted(grouped.keys()))
    ys = np.array([grouped[k][0] for k in xs])
    es = np.array([grouped[k][1] for k in xs])
    plt.errorbar(xs, ys, yerr=es, marker="o", capsize=3, label="random defects")

    px = np.array([r["disorder_density"] for r in periodic_rows])
    py = np.array([r["transmission"] for r in periodic_rows])
    plt.plot(px, py, marker="s", linestyle="--", label="periodic defects")
    plt.xlabel("disorder density")
    plt.ylabel("transmission")
    plt.title("Transmission vs disorder density")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "scan_transmission_plot.png", dpi=130)
    plt.close()

    label, details = verdict(random_rows, periodic_rows)
    verdict_md = OUT_DIR / "verdict.md"
    verdict_md.write_text(
        "\n".join(
            [
                "# Verdict",
                "",
                f"- 结论：{label}",
                "",
                "## 关键统计",
                f"- 低无序随机透射均值: {details['mean_transmission_light_random']:.6f}",
                f"- 高无序随机透射均值: {details['mean_transmission_dense_random']:.6f}",
                f"- 周期缺陷(0.16)透射: {details['mean_transmission_periodic_at_0p16']:.6f}",
                f"- 低减高差值: {details['trend_light_minus_dense']:.6f}",
                f"- 周期相对随机优势: {details['periodic_advantage_vs_dense_random']:.6f}",
                "",
                "## 判据映射",
                "- I1: transmission_vs_disorder -> `scan_summary.csv`",
                "- I2: localization_length_proxy -> `scan_summary.csv`",
                "- I3: rare_channel_freq -> `scan_summary.csv`",
                "- C1: periodic_defects 已完成",
                "- C2: seed_ensemble 已完成",
            ]
        ),
        encoding="utf-8",
    )

    metrics = {
        "rows": len(rows),
        "random_rows": len(random_rows),
        "periodic_rows": len(periodic_rows),
        "verdict": label,
        "details": details,
    }
    with (OUT_DIR / "scan_metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("Generated:", csv_path)
    print("Generated:", OUT_DIR / "scan_transmission_plot.png")
    print("Generated:", verdict_md)
    print("Generated:", OUT_DIR / "scan_metrics.json")


if __name__ == "__main__":
    main()
