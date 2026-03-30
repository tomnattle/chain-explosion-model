"""
explore_coherent_double_slit_pure.py
-----------------------------------
纯相干（B 更纯粹）：使用 ce_engine_v3_coherent 的复振幅传播，
只保留严格相位叠加（无相位噪声/无额外 dephasing）。

目标：
  1) 双缝屏上强度分布 I(y) 出现干涉式峰谷结构
  2) 用现有 compute_visibility 统计可见度 V
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")

from ce_engine_v3_coherent import propagate_coherent, compute_intensity
from ce_engine_v2 import compute_visibility


def make_double_slit_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w):
    barrier = np.zeros((height, width), dtype=np.bool_)
    barrier[:, barrier_x] = True
    barrier[slit1_y0 : slit1_y0 + slit_w, barrier_x] = False
    barrier[slit2_y0 : slit2_y0 + slit_w, barrier_x] = False
    return barrier


def main():
    # ---------------- 参数 ----------------
    HEIGHT = 201
    WIDTH = 400
    A = 1.0
    S = 0.28

    # 统一衰减：不引入相位噪声，仍是纯相干机制的演化
    LAM = 0.97

    # k 控制条纹密度（相位步进）
    k = 2.0

    SOURCE_X = 5
    SOURCE_Y = HEIGHT // 2

    BAR_X = 150
    SLIT_W = 8
    SLIT1_Y0 = HEIGHT // 2 - 30
    SLIT2_Y0 = HEIGHT // 2 + 30

    SCREEN_X = WIDTH - 10
    STEPS = 500

    out_png = "coherent_double_slit_pure.png"

    # ---------------- 初始化 ----------------
    barrier = make_double_slit_barrier(
        HEIGHT, WIDTH, BAR_X, SLIT1_Y0, SLIT2_Y0, SLIT_W
    )

    # 复振幅：强度由 |U|^2 给出
    U = np.zeros((HEIGHT, WIDTH), dtype=np.complex128)
    U[SOURCE_Y, SOURCE_X] = 1.0 + 0.0j  # 初始振幅（对应初始强度 1）

    # ---------------- 传播 ----------------
    for _ in range(STEPS):
        U = propagate_coherent(U, barrier, A, S, LAM, k)

    I = compute_intensity(U)
    screen = I[:, SCREEN_X]
    V = compute_visibility(screen)

    print("coherent double slit (pure) done.")
    print(f"k={k}  LAM={LAM}  STEPS={STEPS}")
    print(f"visibility V={V:.4f}")

    # ---------------- 可视化 ----------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    # 左：强度场（log 显示）
    im0 = axes[0].imshow(
        np.log10(I + 1e-12),
        cmap="inferno",
        aspect="auto",
        origin="upper",
    )
    axes[0].axvline(x=BAR_X, color="cyan", linestyle="--", linewidth=1, alpha=0.8)
    axes[0].set_title("Coherent |U|^2 (log)", color="white", fontsize=11)
    axes[0].set_xlabel("x", color="#8b949e")
    axes[0].set_ylabel("y", color="#8b949e")
    fig.colorbar(im0, ax=axes[0]).ax.tick_params(colors="#8b949e")

    # 右：屏上强度与强度归一化
    smax = float(screen.max()) if float(screen.max()) > 0 else 1.0
    axes[1].plot(screen / smax, "b-", linewidth=2)
    axes[1].set_title(f"Screen intensity (x={SCREEN_X})\\nV={V:.3f}", color="white", fontsize=11)
    axes[1].set_xlabel("y", color="#8b949e")
    axes[1].set_ylabel("I(y)/max", color="#8b949e")
    axes[1].grid(True, alpha=0.2, color="#30363d")

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()

