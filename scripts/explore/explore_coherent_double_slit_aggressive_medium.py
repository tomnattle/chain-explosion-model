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
    # 更激进：更密的泡泡区域 + 更强的局部强衰减
    bubble_p = 0.05  # 每格每步约 5% 的泡泡区域（更挤兑）
    mu = 0.70  # 泡泡区域局部强抽走（更激进）

    # 更激进的 sigma 扫描：从“几乎无噪声”到“极端去相干”
    sigma_list = [0.0, 0.08, 0.15, 0.25, 0.4, 0.7, 1.1, 1.6, 2.2]
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
    Vs_arr = np.asarray(Vs, dtype=np.float64)
    idx_max = int(np.argmax(Vs_arr))
    idx_min = int(np.argmin(Vs_arr))
    idx_mid = len(sigma_list) // 2
    chosen = sorted({idx_max, idx_min, idx_mid})
    for idx in chosen:
        sigma = sigma_list[idx]
        screen = screens[sigma]
        smax = float(screen.max()) if float(screen.max()) > 0 else 1.0
        axes[1].plot(
            screen / smax,
            label=f"sigma={sigma} (V={Vs_arr[idx]:.2f})",
            linewidth=2,
        )
    axes[1].set_title(f"Screen intensity at x={SCREEN_X}", color="white", fontsize=11)
    axes[1].set_xlabel("y index", color="#8b949e")
    axes[1].set_ylabel("I(y)/max", color="#8b949e")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"saved: {out_png}")

    # ============================================================
    # 第二轮：mu=0 纯相位去相干（更接近“挤兑洗掉条纹”的直觉）
    # ============================================================
    sigma_list_dephase_only = [0.0, 0.15, 0.4, 0.7, 1.1, 1.6, 2.2]
    mu_dephase_only = 0.0

    Vs2 = []
    screens2 = {}
    print("\n=== dephase only (mu=0) ===")
    print(f"bubble_p={bubble_p}, mu={mu_dephase_only}, k={k}, LAM={LAM}")
    print(f"sigma_list_dephase_only={sigma_list_dephase_only}")

    for sigma in sigma_list_dephase_only:
        V, screen, I = run_case(
            mode=mode,
            sigma=sigma,
            seed=seed,
            bubble_p=bubble_p,
            mu=mu_dephase_only,
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
        Vs2.append(V)
        screens2[sigma] = screen
        print(f"(dephase only) sigma={sigma:>4} => V={V:.4f}")

    out_png2 = "coherent_double_slit_dephase_only.png"
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    # 左：V vs sigma
    axes[0].plot(sigma_list_dephase_only, Vs2, "o-", color="#58a6ff", linewidth=2)
    axes[0].set_title("Visibility V vs phase dephasing (mu=0)", color="white", fontsize=11)
    axes[0].set_xlabel("phase kick sigma (rad)", color="#8b949e")
    axes[0].set_ylabel("V", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")

    # 右：挑几个 sigma 的屏曲线（归一化）
    Vs2_arr = np.asarray(Vs2, dtype=np.float64)
    idx_max2 = int(np.argmax(Vs2_arr))
    idx_min2 = int(np.argmin(Vs2_arr))
    idx_mid2 = len(sigma_list_dephase_only) // 2
    chosen2 = sorted({idx_max2, idx_min2, idx_mid2})
    for idx in chosen2:
        sigma = sigma_list_dephase_only[idx]
        screen = screens2[sigma]
        smax = float(screen.max()) if float(screen.max()) > 0 else 1.0
        axes[1].plot(
            screen / smax,
            label=f"sigma={sigma} (V={Vs2_arr[idx]:.2f})",
            linewidth=2,
        )

    axes[1].set_title(f"Screen intensity at x={SCREEN_X}", color="white", fontsize=11)
    axes[1].set_xlabel("y index", color="#8b949e")
    axes[1].set_ylabel("I(y)/max", color="#8b949e")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(
        loc="upper right",
        facecolor="#161b22",
        edgecolor="#30363d",
        framealpha=0.9,
        fontsize=9,
    )

    plt.tight_layout()
    plt.savefig(out_png2, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"saved: {out_png2}")

    # ============================================================
    # 第三轮：global 全局去相干（更激进，通常更容易把条纹洗掉）
    # ============================================================
    sigma_list_global = [0.0, 0.2, 0.5, 1.0, 1.5]
    mu_global = 0.0

    Vs3 = []
    screens3 = {}
    print("\n=== global dephase only (mode=global, mu=0) ===")
    print(f"k={k}, LAM={LAM}, sigma_list_global={sigma_list_global}")

    for sigma in sigma_list_global:
        V, screen, I = run_case(
            mode="global",
            sigma=sigma,
            seed=seed,
            bubble_p=bubble_p,  # unused for global
            mu=mu_global,
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
        Vs3.append(V)
        screens3[sigma] = screen
        print(f"(global) sigma={sigma:>4} => V={V:.4f}")

    out_png3 = "coherent_double_slit_global_dephase_only.png"
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    axes[0].plot(sigma_list_global, Vs3, "o-", color="#58a6ff", linewidth=2)
    axes[0].set_title("Visibility V vs global phase dephasing (mu=0)", color="white", fontsize=11)
    axes[0].set_xlabel("phase kick sigma (rad)", color="#8b949e")
    axes[0].set_ylabel("V", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")

    Vs3_arr = np.asarray(Vs3, dtype=np.float64)
    idx_max3 = int(np.argmax(Vs3_arr))
    idx_min3 = int(np.argmin(Vs3_arr))
    idx_mid3 = len(sigma_list_global) // 2
    chosen3 = sorted({idx_max3, idx_min3, idx_mid3})
    for idx in chosen3:
        sigma = sigma_list_global[idx]
        screen = screens3[sigma]
        smax = float(screen.max()) if float(screen.max()) > 0 else 1.0
        axes[1].plot(
            screen / smax,
            label=f"sigma={sigma} (V={Vs3_arr[idx]:.2f})",
            linewidth=2,
        )

    axes[1].set_title(f"Screen intensity at x={SCREEN_X}", color="white", fontsize=11)
    axes[1].set_xlabel("y index", color="#8b949e")
    axes[1].set_ylabel("I(y)/max", color="#8b949e")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(
        loc="upper right",
        facecolor="#161b22",
        edgecolor="#30363d",
        framealpha=0.9,
        fontsize=9,
    )

    plt.tight_layout()
    plt.savefig(out_png3, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"saved: {out_png3}")


if __name__ == "__main__":
    main()

