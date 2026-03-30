"""
explore_coherent_double_slit_fringe_strength_fft_bubbles.py
---------------------------------------------------
在纯相干的 ce_engine_v3_coherent 上做“局部泡泡去相干（bubbles）”：
  - mode=bubbles：只在 bubble mask 内施加相位随机踢（去相干）
  - 可选 mu：泡泡区域振幅抽走（挤兑/抽能）

量化指标：
  - V：compute_visibility（峰谷启发式，可能非单调）
  - FFT_strength：y 方向 FFT 主频功率占比（更抗启发式）

输出：
  - coherent_double_slit_fringe_strength_fft_bubbles.png
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


def make_bubble_mask(height, width, bubble_p, seed=0):
    rng = np.random.default_rng(seed)
    return rng.random(size=(height, width)) < bubble_p


def fringe_strength_fft(screen: np.ndarray) -> float:
    """
    screen: I(y) 1D array
    返回：主频率分量功率占比（DC 去除后，主峰功率/总功率）。
    """
    s = screen.astype(np.float64)
    if not np.isfinite(s).all():
        s = np.nan_to_num(s, nan=0.0, posinf=0.0, neginf=0.0)

    s = s - float(np.mean(s))  # 去 DC
    scale = float(np.max(np.abs(s))) + 1e-18
    s = s / scale

    spec = np.fft.rfft(s)
    power = (np.abs(spec) ** 2).astype(np.float64)
    if power.shape[0] <= 2:
        return 0.0
    power_no_dc = power[1:]
    denom = float(np.sum(power_no_dc)) + 1e-18
    if denom <= 0:
        return 0.0

    # 主频选择：忽略太高频段，让“噪声毛刺”别主导
    k_max = max(1, int(power_no_dc.shape[0] * 0.45))
    idx = int(np.argmax(power_no_dc[:k_max]))
    main_power = float(power_no_dc[idx])
    return main_power / denom


def run_case_bubbles(
    sigma: float,
    seed: int,
    bubble_mask: np.ndarray,
    mu: float,
    HEIGHT: int,
    WIDTH: int,
    barrier: np.ndarray,
    A: float,
    S: float,
    LAM: float,
    k: float,
    SOURCE_X: int,
    SOURCE_Y: int,
    SLIT_W: int,
    SCREEN_X: int,
    STEPS: int,
):
    rng = np.random.default_rng(seed)

    # 复振幅
    U = np.zeros((HEIGHT, WIDTH), dtype=np.complex128)
    U[SOURCE_Y, SOURCE_X] = 1.0 + 0.0j

    for _ in range(STEPS):
        U = propagate_coherent(U, barrier, A, S, LAM, k)

        if sigma <= 0:
            continue

        mask = bubble_mask
        if np.any(mask):
            phi = rng.normal(0.0, sigma, size=(HEIGHT, WIDTH)).astype(np.float64)
            U[mask] *= np.exp(1j * phi[mask])
            if mu > 0:
                U[mask] *= max(0.0, 1.0 - mu)

    I = compute_intensity(U)
    screen = I[:, SCREEN_X]
    V = compute_visibility(screen)
    strength = fringe_strength_fft(screen)
    return V, strength, screen, I


def main():
    # ---------------- 参数 ----------------
    HEIGHT = 201
    WIDTH = 400

    A = 1.0
    S = 0.28
    LAM = 0.97
    k = 2.0

    SOURCE_X = 5
    SOURCE_Y = HEIGHT // 2

    BAR_X = 150
    SLIT_W = 8
    SLIT1_Y0 = HEIGHT // 2 - 30
    SLIT2_Y0 = HEIGHT // 2 + 30
    SCREEN_X = WIDTH - 10

    STEPS = 500

    # bubbles 介质参数
    bubble_p = 0.05
    mu = 0.0  # 只做去相干（更贴“洗掉条纹”的直觉）；想更激进把 mu 调大

    sigma_list = [0.0, 0.1, 0.2, 0.35, 0.5, 0.8, 1.2, 1.8]
    seed = 12345
    bubble_mask_seed = 777

    barrier = make_barrier(HEIGHT, WIDTH, BAR_X, SLIT1_Y0, SLIT2_Y0, SLIT_W)
    bubble_mask = make_bubble_mask(HEIGHT, WIDTH, bubble_p=bubble_p, seed=bubble_mask_seed)

    Vs = []
    strengths = []
    screens = {}

    print("=== bubbles medium toy: FFT fringe strength ===")
    print(f"bubble_p={bubble_p}, mu={mu}, k={k}, LAM={LAM}")
    print(f"sigma_list={sigma_list}")

    for sigma in sigma_list:
        V, strength, screen, _I = run_case_bubbles(
            sigma=sigma,
            seed=seed,
            bubble_mask=bubble_mask,
            mu=mu,
            HEIGHT=HEIGHT,
            WIDTH=WIDTH,
            barrier=barrier,
            A=A,
            S=S,
            LAM=LAM,
            k=k,
            SOURCE_X=SOURCE_X,
            SOURCE_Y=SOURCE_Y,
            SLIT_W=SLIT_W,
            SCREEN_X=SCREEN_X,
            STEPS=STEPS,
        )
        Vs.append(float(V))
        strengths.append(float(strength))
        screens[sigma] = screen
        print(f"sigma={sigma:>4} => V={V:.4f}  FFT_strength={strength:.4f}")

    # ---------------- 可视化 ----------------
    out_png = "coherent_double_slit_fringe_strength_fft_bubbles.png"
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    axes[0].plot(sigma_list, Vs, "o-", color="#58a6ff", linewidth=2, label="V (peaks/valleys)")
    axes[0].plot(sigma_list, strengths, "s--", color="#ffa657", linewidth=2, label="FFT main-power ratio")
    axes[0].set_title("Fringe metrics vs local phase dephasing (bubbles)", color="white", fontsize=11)
    axes[0].set_xlabel("phase kick sigma (rad)", color="#8b949e")
    axes[0].set_ylabel("metric", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")
    axes[0].legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    # 右：挑三个 sigma 展示屏曲线
    Vs_arr = np.asarray(Vs, dtype=np.float64)
    strengths_arr = np.asarray(strengths, dtype=np.float64)
    idx_best = int(np.argmax(strengths_arr))
    idx_worst = int(np.argmin(strengths_arr))
    idx_mid = len(sigma_list) // 2
    chosen = sorted({idx_best, idx_worst, idx_mid})
    for idx in chosen:
        sigma = sigma_list[idx]
        screen = screens[sigma]
        smax = float(screen.max()) if float(screen.max()) > 0 else 1.0
        axes[1].plot(
            screen / smax,
            linewidth=2,
            label=f"sigma={sigma} (V={Vs_arr[idx]:.2f})",
        )

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

