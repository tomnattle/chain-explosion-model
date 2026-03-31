"""
explore_coherent_double_slit_fringe_strength_fft.py
---------------------------------------------------
比原先 compute_visibility(V) 更“抗启发式”的条纹量化：
  - 用屏上强度 I(y) 做去均值
  - 对 y 方向做 FFT
  - 取主频率分量的功率占比作为 fringe strength（更接近“条纹被洗掉”的直觉）

支持两种介质 toy：
  - global：每步对全局相位施加随机踢
  - bubbles：仅在 bubble mask 区域施加相位踢（+可选局部抽走）

注意：这是 toy 指标，不进入测试集合。
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
    screen: I(y) 一维数组（非负）
    返回：主频率分量功率占比（DC 去除后）。
    """
    n = int(screen.shape[0])
    s = screen.astype(np.float64)
    # 清理非有限值（避免 FFT 功率 nan/inf）
    if not np.isfinite(s).all():
        s = np.nan_to_num(s, nan=0.0, posinf=0.0, neginf=0.0)

    s = s - float(np.mean(s))  # 去 DC
    # 归一化，防止大数导致 FFT 功率溢出
    scale = float(np.max(np.abs(s))) + 1e-18
    s = s / scale

    # rfft：频率从 0 到 Nyquist
    spec = np.fft.rfft(s)
    power = (np.abs(spec).astype(np.float64)) ** 2
    if power.shape[0] <= 2:
        return 0.0

    # 丢掉 k=0（DC）
    power_no_dc = power[1:]
    denom = float(np.sum(power_no_dc)) + 1e-18
    if denom <= 0:
        return 0.0

    # 选主频：忽略最高一段（减少高频噪声主导）
    k_max = max(1, int(power_no_dc.shape[0] * 0.45))
    idx = int(np.argmax(power_no_dc[:k_max]))
    main_power = float(power_no_dc[idx])
    return main_power / denom


def run_case(
    mode: str,
    sigma: float,
    seed: int,
    bubble_p: float,
    mu: float,
    HEIGHT: int,
    WIDTH: int,
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
    bubble_mask: np.ndarray,
):
    rng = np.random.default_rng(seed)
    U = np.zeros((HEIGHT, WIDTH), dtype=np.complex128)
    U[SOURCE_Y, SOURCE_X] = 1.0 + 0.0j

    for _ in range(STEPS):
        U = propagate_coherent(U, barrier, A, S, LAM, k)
        if sigma <= 0:
            continue

        if mode == "global":
            phi = rng.normal(0.0, sigma, size=(HEIGHT, WIDTH)).astype(np.float64)
            U *= np.exp(1j * phi)
        elif mode == "bubbles":
            mask = bubble_mask
            if np.any(mask):
                phi = rng.normal(0.0, sigma, size=(HEIGHT, WIDTH)).astype(np.float64)
                U[mask] *= np.exp(1j * phi[mask])
                if mu > 0:
                    U[mask] *= max(0.0, 1.0 - mu)
        else:
            raise ValueError("unknown mode")

    I = compute_intensity(U)
    screen = I[:, SCREEN_X]
    V = compute_visibility(screen)
    strength = fringe_strength_fft(screen)
    return V, strength, screen, I


def main():
    # ---------------- 基础参数（复用你纯相干的量级） ----------------
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

    mode = "global"  # 先做更单调对照：global 去相干
    bubble_p = 0.05
    mu = 0.0

    # 扫描：用少量 sigma 让你更快看到趋势
    sigma_list = [0.0, 0.15, 0.3, 0.5, 0.8, 1.2, 1.8]
    seed = 12345
    bubble_mask_seed = 777

    barrier = make_barrier(HEIGHT, WIDTH, BAR_X, SLIT1_Y0, SLIT2_Y0, SLIT_W)
    bubble_mask = make_bubble_mask(HEIGHT, WIDTH, bubble_p, seed=bubble_mask_seed)

    Vs = []
    strengths = []
    screens = {}

    print("=== coherent double slit: FFT fringe strength ===")
    print(f"mode={mode}, bubble_p={bubble_p}, mu={mu}, k={k}, LAM={LAM}")
    print(f"sigma_list={sigma_list}")

    for sigma in sigma_list:
        V, strength, screen, _I = run_case(
            mode=mode,
            sigma=sigma,
            seed=seed,
            bubble_p=bubble_p,
            mu=mu,
            HEIGHT=HEIGHT,
            WIDTH=WIDTH,
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
            bubble_mask=bubble_mask,
        )
        Vs.append(float(V))
        strengths.append(float(strength))
        screens[sigma] = screen
        print(f"sigma={sigma:>4} => V={V:.4f}  FFT_strength={strength:.4f}")

    # ---------------- 可视化 ----------------
    out_png = "coherent_double_slit_fringe_strength_fft.png"
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    # 左：曲线对比
    axes[0].plot(sigma_list, Vs, "o-", color="#58a6ff", linewidth=2, label="V (peaks/valleys)")
    axes[0].plot(
        sigma_list, strengths, "s--", color="#ffa657", linewidth=2, label="FFT main-power ratio"
    )
    axes[0].set_title("Fringe metrics vs phase dephasing (toy)", color="white", fontsize=11)
    axes[0].set_xlabel("phase kick sigma (rad)", color="#8b949e")
    axes[0].set_ylabel("metric", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")
    axes[0].legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    # 右：选 3 个 sigma 展示屏曲线（归一化）
    sig_a = sigma_list[0]
    sig_b = sigma_list[len(sigma_list) // 2]
    sig_c = sigma_list[-1]
    for sig, color in [(sig_a, "#87ceeb"), (sig_b, "#ffa07a"), (sig_c, "#98fb98")]:
        screen = screens[sig]
        smax = float(screen.max()) if float(screen.max()) > 0 else 1.0
        axes[1].plot(screen / smax, label=f"sigma={sig} (V={Vs[sigma_list.index(sig)]:.2f})", linewidth=2, color=color)

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

