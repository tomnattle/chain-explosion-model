"""
explore_quantum_eraser_delayed_choice.py
-----------------------------------------
最难挑战的 toy：量子擦除 / 延迟选择核心检验（用纯相干复振幅 + 事后条件选择）。

目标（用朴素语言）：
  1) 哪路测量：忽略探测器结果 => 屏上边缘分布没有干涉（V 下降）
  2) 量子擦除：在事后按 ± 基做条件选择 => 条纹在条件子集里恢复（V 回升）
  3) 把 ± 两个子集“混回去” => 边缘分布又等于哪路边缘（无干涉）

这里“事后选择”的含义是：我们先用相干传播得到上/下路径到屏的复振幅，
然后在统计层面做投影/条件分布，等效表达“测量基在更晚的时刻被选定”。

说明：
  - 这不是对真实介质微观等价；它是量子擦除逻辑的最硬实现（对你要的角落最直接）。
  - 不进入测试集合，只输出图片 + 控制台数字。
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")

from ce_engine_v3_coherent import propagate_coherent, compute_intensity
from ce_engine_v2 import compute_visibility


def make_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w, open_mask):
    """
    open_mask: (open_upper: bool, open_lower: bool)
    barrier 为墙：barrier[y, barrier_x] = True 表示墙（只能从开放的 slit 单元发射）。
    """
    barrier = np.zeros((height, width), dtype=np.bool_)
    barrier[:, barrier_x] = True
    open_upper, open_lower = open_mask
    if open_upper:
        barrier[slit1_y0 : slit1_y0 + slit_w, barrier_x] = False
    if open_lower:
        barrier[slit2_y0 : slit2_y0 + slit_w, barrier_x] = False
    return barrier


def propagate_to_screen(U0, barrier, A, S, LAM, k, steps):
    U = U0
    for _ in range(steps):
        U = propagate_coherent(U, barrier, A, S, LAM, k)
    return U


def main():
    # ---------------- 参数（尽量复用你纯相干脚本的量级） ----------------
    HEIGHT = 201
    WIDTH = 400
    A = 1.0
    S = 0.28
    LAM = 0.97
    k = 2.0

    # -------- 两路径模式分解（更硬、更接近“哪路=投影到上/下狭缝模态”）--------
    # 仍用你现有的双缝几何，但不从源点传播来“间接拆路径”，
    # 而是直接把初始复振幅放到上/下狭缝格点上，形成严格的 |up> 与 |low> 两个模式。

    BAR_X = 150
    SLIT_W = 8
    SLIT1_Y0 = HEIGHT // 2 - 30
    SLIT2_Y0 = HEIGHT // 2 + 30
    SCREEN_X = WIDTH - 10
    # 对 ce_engine_v3_coherent：每步主要把幅度推进到 x+1，
    # 因此从 BAR_X 开始传播 STEPS 以便在 SCREEN_X 读出。
    STEPS = int(SCREEN_X - BAR_X)

    barrier = make_barrier(
        HEIGHT, WIDTH, BAR_X, SLIT1_Y0, SLIT2_Y0, SLIT_W, open_mask=(True, True)
    )

    # 初始化：只在上狭缝/只在下狭缝（这一步就是“哪路测量基”的定义）
    U_up0 = np.zeros((HEIGHT, WIDTH), dtype=np.complex128)
    U_low0 = np.zeros((HEIGHT, WIDTH), dtype=np.complex128)
    U_up0[SLIT1_Y0 : SLIT1_Y0 + SLIT_W, BAR_X] = 1.0 + 0.0j
    U_low0[SLIT2_Y0 : SLIT2_Y0 + SLIT_W, BAR_X] = 1.0 + 0.0j

    U_up = propagate_to_screen(U_up0, barrier, A, S, LAM, k, steps=STEPS)
    U_low = propagate_to_screen(U_low0, barrier, A, S, LAM, k, steps=STEPS)

    # 屏上的复振幅（两种“狭缝模态”的输出）
    up = U_up[:, SCREEN_X]
    low = U_low[:, SCREEN_X]

    # ---------------- 三种“统计情景” ----------------
    # 哪路边缘：忽略相干项 => |up|^2 + |low|^2
    I_which_way_marginal = np.abs(up) ** 2 + np.abs(low) ** 2
    # 两臂相干：允许交叉项 => |up + low|^2
    I_both_coherent = np.abs(up + low) ** 2

    # 量子擦除条件选择（± 基）
    I_eraser_plus = np.abs(up + low) ** 2
    I_eraser_minus = np.abs(up - low) ** 2

    # 把 ± 混起来 => 边缘应回到 which-way 边缘（无干涉）
    I_eraser_marginal = 0.5 * (I_eraser_plus + I_eraser_minus)

    # ---------------- 可视化/量化 ----------------
    # I_both = I_marginal + 2 Re(up*low^*)
    interf = I_both_coherent - I_which_way_marginal

    # 为避免 overflow：先用统一尺度归一化，再算 RMS/RMSE
    scale_I = float(
        np.max([I_both_coherent.max(), I_which_way_marginal.max(), I_eraser_plus.max()])
    ) + 1e-18
    I_both_n = I_both_coherent / scale_I
    interf_n = interf / scale_I

    # 相干项相对强度：RMS(interf) / RMS(I_both)（全部在归一化尺度上）
    rms_I = float(np.sqrt(np.mean(I_both_n.astype(np.float64) ** 2)) + 1e-18)
    rms_interf = float(np.sqrt(np.mean(interf_n.astype(np.float64) ** 2)) + 1e-18)
    interf_ratio = rms_interf / rms_I

    # 条件 ± 的“交叉项符号翻转”：I_plus - I_minus 应明显大于数值噪声
    diff_pm = I_eraser_plus - I_eraser_minus
    diff_pm_n = diff_pm / scale_I
    rms_diff_pm = float(np.sqrt(np.mean(diff_pm_n.astype(np.float64) ** 2)) + 1e-18)
    pm_ratio = rms_diff_pm / rms_I

    # eraser marginal 应该回到 which-way marginal（相对尺度上的 RMSE）
    marg_diff = float(
        np.sqrt(np.mean(((I_eraser_marginal - I_which_way_marginal) / scale_I) ** 2))
        + 0.0
    )

    print("=== quantum eraser / delayed-choice toy (hard metric) ===")
    print(f"interference cross-term ratio = RMS(interf)/RMS(I_both) = {interf_ratio:.6f}")
    print(f"(I_plus - I_minus) RMS normalized = {pm_ratio:.6f}")
    print(f"eraser marginal RMSE vs which-way marginal = {marg_diff:.3e}")

    # 同时给出启发式 V 作为参考（可能受单臂自振荡影响）
    V_which_way = compute_visibility(I_which_way_marginal.astype(np.float64))
    V_coherent = compute_visibility(I_both_coherent.astype(np.float64))
    V_plus = compute_visibility(I_eraser_plus.astype(np.float64))
    V_minus = compute_visibility(I_eraser_minus.astype(np.float64))
    V_eraser_marg = compute_visibility(I_eraser_marginal.astype(np.float64))
    print(f"V(which-way marginal) = {V_which_way:.4f}")
    print(f"V(coherent both)      = {V_coherent:.4f}")
    print(f"V(eraser plus)       = {V_plus:.4f}")
    print(f"V(eraser minus)      = {V_minus:.4f}")
    print(f"V(eraser marginal)   = {V_eraser_marg:.4f}")
    print("Interpretation: look at interference cross-term metric, not just V.")

    # 图
    out_png = "quantum_eraser_delayed_choice.png"
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    # 归一化便于对比
    smax = float(
        np.max([I_which_way_marginal.max(), I_both_coherent.max(), I_eraser_plus.max()])
    ) + 1e-18

    axes[0].plot(I_both_coherent / smax, label=f"coherent |up+low|^2 (V={V_coherent:.2f})", linewidth=2)
    axes[0].plot(I_which_way_marginal / smax, label=f"which-way marginal |up|^2+|low|^2 (V={V_which_way:.2f})", linewidth=2)
    axes[0].plot(I_eraser_marginal / smax, "--", label=f"eraser marginal avg (V={V_eraser_marg:.2f})", linewidth=2)
    axes[0].set_title("Edge/marginal patterns", color="white", fontsize=11)
    axes[0].set_xlabel("y index", color="#8b949e")
    axes[0].set_ylabel("I(y)/max", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")
    axes[0].legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    axes[1].plot(I_eraser_plus / smax, label=f"eraser + (V={V_plus:.2f})", linewidth=2)
    axes[1].plot(I_eraser_minus / smax, "--", label=f"eraser - (V={V_minus:.2f})", linewidth=2)
    axes[1].set_title("Conditional patterns in ± basis", color="white", fontsize=11)
    axes[1].set_xlabel("y index", color="#8b949e")
    axes[1].set_ylabel("I(y)/max", color="#8b949e")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    # 干涉交叉项轮廓（强烈更“硬”）
    axes[2].plot(interf / (smax + 1e-18), color="#ffa657", linewidth=2, label="interference cross-term: I_both - I_marg")
    axes[2].axhline(0.0, color="#8b949e", linestyle="--", linewidth=1)
    axes[2].set_title("Interference cross-term profile", color="white", fontsize=11)
    axes[2].set_xlabel("y index", color="#8b949e")
    axes[2].set_ylabel("interf / Imax", color="#8b949e")
    axes[2].grid(True, alpha=0.25, color="#30363d")
    axes[2].legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"saved: {out_png}")


if __name__ == "__main__":
    main()

