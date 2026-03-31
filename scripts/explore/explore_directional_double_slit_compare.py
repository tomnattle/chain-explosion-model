"""
explore_directional_double_slit_compare.py
-----------------------------------------
对照：双缝模型在“近各向同性传播” vs “强前向传播”下的屏幕图样与可见度 V。
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


def run_case(height, width, source_x, source_y, barrier, steps, A, S, B, lam):
    grid = np.zeros((height, width), dtype=np.float64)
    grid[source_y, source_x] = 100.0
    out = propagate_double_slit_n_steps(grid, barrier, A, S, B, lam, steps)
    return out


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

    # 近各向同性
    iso_A, iso_S, iso_B = 0.42, 0.30, 0.28
    grid_iso = run_case(HEIGHT, WIDTH, SOURCE_X, SOURCE_Y, barrier, STEPS, iso_A, iso_S, iso_B, LAM)
    screen_iso = grid_iso[:, SCREEN_X]
    v_iso = float(compute_visibility(screen_iso))

    # 强前向
    dir_A, dir_S, dir_B = 1.00, 0.16, 0.01
    grid_dir = run_case(HEIGHT, WIDTH, SOURCE_X, SOURCE_Y, barrier, STEPS, dir_A, dir_S, dir_B, LAM)
    screen_dir = grid_dir[:, SCREEN_X]
    v_dir = float(compute_visibility(screen_dir))

    # 归一化屏幕曲线
    s_iso = float(np.max(screen_iso)) + 1e-18
    s_dir = float(np.max(screen_dir)) + 1e-18
    n_iso = screen_iso / s_iso
    n_dir = screen_dir / s_dir

    out_png = "directional_double_slit_compare.png"
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    eps = 1e-12
    im0 = axes[0, 0].imshow(np.log10(grid_iso + eps), cmap="inferno", aspect="auto", origin="upper")
    axes[0, 0].axvline(BARRIER_X, color="cyan", linestyle="--", linewidth=1)
    axes[0, 0].axvline(SCREEN_X, color="#58a6ff", linestyle="--", linewidth=1)
    axes[0, 0].set_title("Near-isotropic field (log10 E)", color="white")
    fig.colorbar(im0, ax=axes[0, 0]).ax.tick_params(colors="#8b949e")

    im1 = axes[0, 1].imshow(np.log10(grid_dir + eps), cmap="inferno", aspect="auto", origin="upper")
    axes[0, 1].axvline(BARRIER_X, color="cyan", linestyle="--", linewidth=1)
    axes[0, 1].axvline(SCREEN_X, color="#58a6ff", linestyle="--", linewidth=1)
    axes[0, 1].set_title("Directional field (log10 E)", color="white")
    fig.colorbar(im1, ax=axes[0, 1]).ax.tick_params(colors="#8b949e")

    axes[1, 0].plot(n_iso, color="#58a6ff", linewidth=1.8)
    axes[1, 0].set_title(f"Screen profile near-isotropic (V={v_iso:.3f})", color="white")
    axes[1, 0].set_xlabel("y", color="#8b949e")
    axes[1, 0].set_ylabel("I(y)/max", color="#8b949e")
    axes[1, 0].grid(True, alpha=0.25, color="#30363d")

    axes[1, 1].plot(n_dir, color="#ffa657", linewidth=1.8)
    axes[1, 1].set_title(f"Screen profile directional (V={v_dir:.3f})", color="white")
    axes[1, 1].set_xlabel("y", color="#8b949e")
    axes[1, 1].set_ylabel("I(y)/max", color="#8b949e")
    axes[1, 1].grid(True, alpha=0.25, color="#30363d")

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")

    print("Directional double-slit comparison complete.")
    print(f"near-isotropic weights: A={iso_A}, S={iso_S}, B={iso_B}, V={v_iso:.4f}")
    print(f"directional   weights: A={dir_A}, S={dir_S}, B={dir_B}, V={v_dir:.4f}")
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()

