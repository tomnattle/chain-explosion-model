"""
explore_directionality_phase_diagram.py
--------------------------------------
目标：把“方向性传播会改变双缝可见度”从现象图升级为定量关系。

定义方向性指标：
    D = A / (S + B + eps)

在固定双缝几何下扫描一组 (A,S,B)，输出：
- directionality_phase_diagram.png
- 关键数值：corr(V, log10(D))
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")

from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility


def make_double_slit_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w):
    barrier = np.zeros((height, width), dtype=np.bool_)
    barrier[:, barrier_x] = True
    barrier[slit1_y0 : slit1_y0 + slit_w, barrier_x] = False
    barrier[slit2_y0 : slit2_y0 + slit_w, barrier_x] = False
    return barrier


def run_case(height, width, source_x, source_y, barrier, steps, A, S, B, lam, screen_x):
    grid = np.zeros((height, width), dtype=np.float64)
    grid[source_y, source_x] = 100.0
    out = propagate_double_slit_n_steps(grid, barrier, A, S, B, lam, steps)
    screen = out[:, screen_x]
    v = float(compute_visibility(screen))
    hit_energy = float(np.sum(screen))
    return v, hit_energy


def safe_corr(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.size < 3 or y.size < 3:
        return 0.0
    xs = float(np.std(x))
    ys = float(np.std(y))
    if xs < 1e-15 or ys < 1e-15:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def main():
    HEIGHT = 201
    WIDTH = 420
    SOURCE_X = 20
    SOURCE_Y = HEIGHT // 2
    BARRIER_X = 170
    SLIT_W = 8
    SLIT1_Y0 = HEIGHT // 2 - 28
    SLIT2_Y0 = HEIGHT // 2 + 20
    SCREEN_X = WIDTH - 10
    STEPS = 500
    LAM = 0.995

    barrier = make_double_slit_barrier(HEIGHT, WIDTH, BARRIER_X, SLIT1_Y0, SLIT2_Y0, SLIT_W)

    # 扫描网格：A固定，只扫 S,B 看方向性 D 对 V 的影响
    A = 1.0
    s_list = np.array([0.08, 0.12, 0.16, 0.20, 0.26, 0.32], dtype=np.float64)
    b_list = np.array([0.00, 0.01, 0.04, 0.08, 0.14, 0.22], dtype=np.float64)

    V_map = np.zeros((s_list.size, b_list.size), dtype=np.float64)
    D_map = np.zeros((s_list.size, b_list.size), dtype=np.float64)
    H_map = np.zeros((s_list.size, b_list.size), dtype=np.float64)

    d_vals = []
    v_vals = []
    for i in range(s_list.size):
        S = float(s_list[i])
        for j in range(b_list.size):
            B = float(b_list[j])
            v, hit = run_case(
                HEIGHT, WIDTH, SOURCE_X, SOURCE_Y, barrier, STEPS, A, S, B, LAM, SCREEN_X
            )
            D = A / (S + B + 1e-12)
            V_map[i, j] = v
            D_map[i, j] = D
            H_map[i, j] = hit
            d_vals.append(np.log10(D))
            v_vals.append(v)

    corr_v_logd = safe_corr(d_vals, v_vals)

    # 线性拟合：V ~ m*log10(D)+c（只做现象拟合，不作理论证明）
    x = np.asarray(d_vals, dtype=np.float64)
    y = np.asarray(v_vals, dtype=np.float64)
    m, c = np.polyfit(x, y, deg=1)
    y_hat = m * x + c
    rmse = float(np.sqrt(np.mean((y_hat - y) ** 2)))

    # 可视化
    out_png = "directionality_phase_diagram.png"
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    im0 = axes[0].imshow(
        V_map,
        origin="lower",
        aspect="auto",
        cmap="magma",
        vmin=float(np.min(V_map)),
        vmax=float(np.max(V_map)),
    )
    axes[0].set_title("V heatmap over (S,B)", color="white")
    axes[0].set_xlabel("B index", color="#8b949e")
    axes[0].set_ylabel("S index", color="#8b949e")
    axes[0].set_xticks(np.arange(b_list.size))
    axes[0].set_xticklabels(["%.2f" % x for x in b_list], rotation=30)
    axes[0].set_yticks(np.arange(s_list.size))
    axes[0].set_yticklabels(["%.2f" % x for x in s_list])
    fig.colorbar(im0, ax=axes[0]).ax.tick_params(colors="#8b949e")

    axes[1].scatter(x, y, s=30, color="#58a6ff", alpha=0.9, label="samples")
    order = np.argsort(x)
    axes[1].plot(x[order], y_hat[order], color="#ffa657", linewidth=2, label="linear fit")
    axes[1].set_title(
        "V vs log10(D)\nD=A/(S+B), corr=%.3f" % corr_v_logd,
        color="white",
    )
    axes[1].set_xlabel("log10(D)", color="#8b949e")
    axes[1].set_ylabel("V", color="#8b949e")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    im2 = axes[2].imshow(
        np.log10(H_map + 1e-18),
        origin="lower",
        aspect="auto",
        cmap="viridis",
    )
    axes[2].set_title("log10(screen energy sum)", color="white")
    axes[2].set_xlabel("B index", color="#8b949e")
    axes[2].set_ylabel("S index", color="#8b949e")
    axes[2].set_xticks(np.arange(b_list.size))
    axes[2].set_xticklabels(["%.2f" % x for x in b_list], rotation=30)
    axes[2].set_yticks(np.arange(s_list.size))
    axes[2].set_yticklabels(["%.2f" % x for x in s_list])
    fig.colorbar(im2, ax=axes[2]).ax.tick_params(colors="#8b949e")

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")

    print("Directionality phase diagram complete.")
    print("A fixed =", A)
    print("corr(V, log10(D)) = %.4f" % corr_v_logd)
    print("fit: V ~= %.4f * log10(D) + %.4f, rmse=%.4f" % (m, c, rmse))
    print("saved:", out_png)


if __name__ == "__main__":
    main()

