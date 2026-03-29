"""
explore_visibility_ce_vs_uniform_loss.py
----------------------------------------
区分两类「干涉变糊」:
  A) 纯 CE 侧向扩散/传播几何（无额外损耗）
  B) 每步后乘 (1-η) 的全局均匀漏损（玩具退相干/吸收环境）

注意: 对比度 V 来自峰谷的**相对**起伏；对整列屏上乘同一常数，归一化后
V **不变**。因此必须同时看「屏列总强度」或加「非均匀/随机」扰动才有区分度。

运行: python explore_visibility_ce_vs_uniform_loss.py
输出: explore_visibility_loss_compare.png
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from ce_engine_v2 import propagate_double_slit, compute_visibility

HEIGHT = 301
WIDTH = 800
A, S, B, LAM = 1.0, 0.25, 0.04, 0.95
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
BAR_X = 180
SLIT1_Y = HEIGHT // 2 - 25
SLIT2_Y = HEIGHT // 2 + 25
SLIT_W = 6
STEPS_PER_100PX = 150

screen_x_list = [300, 400, 500, 600, 700]
ETA = 0.008  # 每步全局乘 (1-ETA)；若过大易与 baseline 全零，可调小


def build_barrier():
    b = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    b[:, BAR_X] = True
    b[SLIT1_Y : SLIT1_Y + SLIT_W, BAR_X] = False
    b[SLIT2_Y : SLIT2_Y + SLIT_W, BAR_X] = False
    return b


def run_curves(apply_uniform_loss: bool):
    barrier = build_barrier()
    vis, intensity = [], []
    for sx in screen_x_list:
        steps = max(20, (sx - SOURCE_X) * STEPS_PER_100PX // 100)
        grid = np.zeros((HEIGHT, WIDTH))
        grid[SOURCE_Y, SOURCE_X] = 1200.0
        for _ in range(steps):
            grid = propagate_double_slit(grid, barrier, A, S, B, LAM)
            if apply_uniform_loss:
                grid *= 1.0 - ETA
        col = grid[:, sx]
        vis.append(compute_visibility(col))
        intensity.append(float(np.sum(col)))
    return np.array(vis, dtype=np.float64), np.array(intensity, dtype=np.float64)


def main():
    v0, i0 = run_curves(False)
    v1, i1 = run_curves(True)
    dist = np.array([x - BAR_X for x in screen_x_list], dtype=np.float64)

    print("=" * 60)
    print("V（对比度）与 sum(I)（屏列总强度） vs 缝-屏距离")
    print(f"均匀损耗 η={ETA}/step（仅 B 列）")
    print("预期: V 对两曲线几乎相同（均匀标度不改变相对起伏）；sum(I) 应有差异。")
    for i, sx in enumerate(screen_x_list):
        print(
            f" L={sx-BAR_X:3d} | V base={v0[i]:.4f} loss={v1[i]:.4f} | "
            f"sumI base={i0[i]:.4g} loss={i1[i]:.4g}"
        )
    print(
        f"\n相对强度比 median(loss/base) = {np.median(i1 / (i0 + 1e-30)):.4f} "
        f"(期望 < 1 当 η>0、步数足够)"
    )
    print("=" * 60)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(dist, v0, "b-o", lw=2, label="CE only")
    ax[0].plot(dist, v1, "r--s", lw=2, label=f"CE + uniform η={ETA}/step")
    ax[0].set_xlabel("distance from barrier (px)")
    ax[0].set_ylabel("visibility V")
    ax[0].set_title("V (scale-invariant to global factor)")
    ax[0].grid(alpha=0.3)
    ax[0].legend()

    ax[1].semilogy(dist, i0 + 1e-20, "b-o", lw=2, label="CE only")
    ax[1].semilogy(dist, i1 + 1e-20, "r--s", lw=2, label=f"+ uniform η")
    ax[1].set_xlabel("distance from barrier (px)")
    ax[1].set_ylabel("sum(screen column)")
    ax[1].set_title("Total intensity at screen (should differ)")
    ax[1].grid(alpha=0.3)
    ax[1].legend()
    plt.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "explore_visibility_loss_compare.png")
    plt.savefig(out, dpi=140)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
