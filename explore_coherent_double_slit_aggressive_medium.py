"""
explore_coherent_double_slit_aggressive_medium.py
---------------------------------------------------
在纯相干（ce_engine_v3_coherent.propagate_coherent）的基础上，加入“介质挤兑/泡泡”玩具效应：
  1) 每一步对相位施加强随机踢：U *= exp(i * N(0, sigma^2))
  2) 可选：在泡泡区域对振幅做局部强衰减：U[mask] *= (1 - mu)

目标：
  - 展示在“很强的介质噪声/挤兑”下，条纹可见度 V 如何退化
  - 仍然走严格相位叠加的框架（传播内核使用复振幅）

注意：这是 toy，不等价于真实介质微观物理；但能测试“介质有效作用”对条纹统计的影响。
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")

from ce_engine_v3_coherent import propagate_coherent, compute_intensity
from ce_engine_v2 import compute_visibility


def make_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w):
    barrier = np.zeros((height, width), dtype=np.bool_)
    barrier[:, barrier_x] = True
    barrier[slit1_y0 : slit1_y0 + slit_w, barrier_x] = False
    barrier[slit2_y0 : slit2_y0 + slit_w, barrier_x] = False
    return barrier


def run_case(
    mode: str,
    sigma: float,
    seed: int,
    bubble_p: float,
    mu: float,
    height: int,
    width: int,
    A: float,
    S: float,
    LAM: float,
    k: float,
    SOURCE_X: int,
    SOURCE_Y: int,
    barrier: np.ndarray,
    SLIT_W: int,
    SCREEN_X: int,
    STEPS: int,
):
    """
    mode:
      - "global": 每格每步都施加相位噪声
      - "bubbles": 仅在泡泡 mask 区域施加相位噪声 + 局部衰减
    """
    rng = np.random.default_rng(seed)
    U = np.zeros((height, width), dtype=np.complex128)
    U[SOURCE_Y, SOURCE_X] = 1.0 + 0.0j

    dist_noise_min = 1e-12
    for _ in range(STEPS):
        U = propagate_coherent(U, barrier, A, S, LAM, k)

        if sigma <= 0:
            continue

        if mode == "global":
            phi = rng.normal(0.0, sigma, size=(height, width)).astype(np.float64)
            # 只需要相位踢，不改变幅度的总体衰减形状
            U *= np.exp(1j * phi)

        elif mode == "bubbles":
            mask = rng.random(size=(height, width)) < bubble_p
            if np.any(mask):
                # 泡泡相位踢：只对 mask 区域生效
                phi = rng.normal(0.0, sigma, size=(height, width)).astype(np.float64)
                U[mask] *= np.exp(1j * phi[mask])
                # 挤兑：额外把泡泡区域做局部能量抽走
                if mu > 0:
                    U[mask] *= max(0.0, 1.0 - mu)

        else:
            raise ValueError("unknown mode")

    I = compute_intensity(U)
    screen = I[:, SCREEN_X]
    V = compute_visibility(screen)
    return V, screen, I


def main():
    # ---------------- 基础参数（尽量沿用纯相干脚本） ----------------
    HEIGHT = 201
    WIDTH = 400

    A = 1.0
    S = 0.28
    LAM = 0.97

    SOURCE_X = 5
    SOURCE_Y = HEIGHT // 2

    BAR_X = 150
    SLIT_W = 8
    SLIT1_Y0 = HEIGHT // 2 - 30
    SLIT2_Y0 = HEIGHT // 2 + 30

    SCREEN_X = WIDTH - 10
    STEPS = 500

    # 相位步进：k 控制条纹密度（玩具）
    k = 2.0

    # ---------------- 介质“泡泡/挤兑”参数（激进） ----------------
    mode = "bubbles"
    bubble_p = 0.01  # 每格每步大约 1% 的泡泡区域
    mu = 0.45  # 泡泡区域局部强抽走（很激进）

    sigma_list = [0.0, 0.15, 0.35, 0.6, 1.0, 1.5]
    seed = 12345

    barrier = make_barrier(HEIGHT, WIDTH, BAR_X, SLIT1_Y0, SLIT2_Y0, SLIT_W)

    Vs = []
    screens = {}

    print("=== aggressive medium toy ===")
    print(f"mode={mode}, bubble_p={bubble_p}, mu={mu}, k={k}, LAM={LAM}")
    print(f"sigma_list={sigma_list}")

    for sigma in sigma_list:
        V, screen, I = run_case(
            mode=mode,
            sigma=sigma,
            seed=seed,
            bubble_p=bubble_p,
            mu=mu,
            height=HEIGHT,
            width=WIDTH,
            A=A,
            S=S,
            LAM=LAM,
            k=k,
            SOURCE_X=SOURCE_X,
            SOURCE_Y=SOURCE_Y,
            barrier=barrier,
            SLIT_W=SLIT_W,
            SCREEN_X=SCREEN_X,
            STEPS=STEPS,
        )
        Vs.append(V)
        screens[sigma] = screen
        print(f"sigma={sigma:>4} => V={V:.4f}")

    # ---------------- 可视化 ----------------
    out_png = "coherent_double_slit_aggressive_medium.png"

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    # 左：V vs sigma
    axes[0].plot(sigma_list, Vs, "o-", color="#58a6ff", linewidth=2)
    axes[0].set_title("Visibility V vs medium dephasing (toy)", color="white", fontsize=11)
    axes[0].set_xlabel("phase kick sigma (rad)", color="#8b949e")
    axes[0].set_ylabel("V", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")

    # 右：挑几个 sigma 的屏曲线（归一化）
    for sigma in [sigma_list[0], sigma_list[len(sigma_list) // 2], sigma_list[-1]]:
        screen = screens[sigma]
        smax = float(screen.max()) if float(screen.max()) > 0 else 1.0
        axes[1].plot(screen / smax, label=f"sigma={sigma} (V={Vs[sigma_list.index(sigma)]:.2f})", linewidth=2)
    axes[1].set_title(f"Screen intensity at x={SCREEN_X}", color="white", fontsize=11)
    axes[1].set_xlabel("y index", color="#8b949e")
    axes[1].set_ylabel("I(y)/max", color="#8b949e")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()

