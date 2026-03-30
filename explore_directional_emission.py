"""
explore_directional_emission.py
-------------------------------
对比“近各向同性扩散”与“方向性扩散”。

核心思想：
- 频率/颜色（这里不显式建模）与振幅/能量分布解耦；
- 通过传播权重 A/S/B 控制方向性：
  A: 前向(+x), S: 侧向(±y, 对角), B: 后向(-x)。

输出：
- directional_emission_comparison.png
  左：近各向同性结果
  中：强前向结果
  右：前/侧/后能量占比柱状图
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")

from ce_engine_v2 import propagate_double_slit_n_steps


def run_case(height, width, source_x, source_y, steps, A, S, B, lam):
    barrier = np.zeros((height, width), dtype=np.bool_)
    grid = np.zeros((height, width), dtype=np.float64)
    grid[source_y, source_x] = 1.0
    out = propagate_double_slit_n_steps(grid, barrier, A, S, B, lam, steps)
    return out


def directional_partitions(energy, source_x, source_y):
    h, w = energy.shape
    Y, X = np.indices((h, w))
    dx = X - source_x
    dy = Y - source_y

    # 前向锥：dx > 0 且 |dy| <= 0.6*dx
    forward = (dx > 0) & (np.abs(dy) <= 0.6 * dx)
    # 后向区：dx < 0
    backward = dx < 0
    # 其余算侧向
    side = ~(forward | backward)

    ef = float(np.sum(energy[forward]))
    es = float(np.sum(energy[side]))
    eb = float(np.sum(energy[backward]))
    et = ef + es + eb + 1e-18
    return ef / et, es / et, eb / et


def plot_result(iso_grid, dir_grid, iso_ratio, dir_ratio, out_png):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    eps = 1e-14
    im0 = axes[0].imshow(np.log10(iso_grid + eps), cmap="inferno", aspect="auto", origin="upper")
    axes[0].set_title("Near-isotropic spread (log10 E)", color="white")
    axes[0].set_xlabel("x", color="#8b949e")
    axes[0].set_ylabel("y", color="#8b949e")
    fig.colorbar(im0, ax=axes[0]).ax.tick_params(colors="#8b949e")

    im1 = axes[1].imshow(np.log10(dir_grid + eps), cmap="inferno", aspect="auto", origin="upper")
    axes[1].set_title("Directional spread (log10 E)", color="white")
    axes[1].set_xlabel("x", color="#8b949e")
    axes[1].set_ylabel("y", color="#8b949e")
    fig.colorbar(im1, ax=axes[1]).ax.tick_params(colors="#8b949e")

    labels = ["forward", "side", "backward"]
    x = np.arange(3)
    w = 0.36
    axes[2].bar(x - w / 2, list(iso_ratio), width=w, color="#58a6ff", label="near-isotropic")
    axes[2].bar(x + w / 2, list(dir_ratio), width=w, color="#ffa657", label="directional")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels)
    axes[2].set_ylim(0.0, 1.0)
    axes[2].set_title("Energy partition", color="white")
    axes[2].grid(True, axis="y", alpha=0.25, color="#30363d")
    axes[2].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")


def main():
    HEIGHT = 201
    WIDTH = 420
    SOURCE_X = 30
    SOURCE_Y = HEIGHT // 2
    STEPS = 220
    LAM = 0.995

    # 对照1：近各向同性（前后侧都不太偏）
    iso_A, iso_S, iso_B = 0.42, 0.30, 0.28
    iso = run_case(HEIGHT, WIDTH, SOURCE_X, SOURCE_Y, STEPS, iso_A, iso_S, iso_B, LAM)
    iso_ratio = directional_partitions(iso, SOURCE_X, SOURCE_Y)

    # 对照2：强方向性（前向强、侧向弱、后向近零）
    dir_A, dir_S, dir_B = 1.00, 0.16, 0.01
    direc = run_case(HEIGHT, WIDTH, SOURCE_X, SOURCE_Y, STEPS, dir_A, dir_S, dir_B, LAM)
    dir_ratio = directional_partitions(direc, SOURCE_X, SOURCE_Y)

    out_png = "directional_emission_comparison.png"
    plot_result(iso, direc, iso_ratio, dir_ratio, out_png)

    print("Directional emission comparison complete.")
    print(f"near-isotropic weights: A={iso_A}, S={iso_S}, B={iso_B}")
    print(f"directional   weights: A={dir_A}, S={dir_S}, B={dir_B}")
    print("energy partitions [forward, side, backward]:")
    print("  near-isotropic =", [round(v, 4) for v in iso_ratio])
    print("  directional    =", [round(v, 4) for v in dir_ratio])
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()

