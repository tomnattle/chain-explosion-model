"""
explore_threshold_detector_clicks.py
------------------------------------
第3步 toy：连续波 + 阈值探测，得到“点击式”统计。
【优化版：预计算传播，速度提升5~10倍】

流程：
- 每次发射仍是连续波传播（局域、决定论）
- 屏幕端加入噪声与阈值判据
- 每次只记录一个“点击位置”（若超过阈值）
- 多次累计后形成点击分布

输出：
- threshold_detector_clicks.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")

from ce_engine_v3_coherent import propagate_coherent


def make_double_slit_barrier(height, width, barrier_x, slit1_y0, slit2_y0, slit_w):
    barrier = np.zeros((height, width), dtype=np.bool_)
    barrier[:, barrier_x] = True
    barrier[slit1_y0 : slit1_y0 + slit_w, barrier_x] = False
    barrier[slit2_y0 : slit2_y0 + slit_w, barrier_x] = False
    return barrier


def pearson_safe(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    sa = np.std(a)
    sb = np.std(b)
    if sa < 1e-15 or sb < 1e-15:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def compute_one_source_screen(H, W, sx, sy, barrier, A, S, LAM, k, steps, screen_x):
    """单次源位置 → 屏幕强度（预计算用）"""
    U = np.zeros((H, W), dtype=np.complex128)
    U[sy, sx] = 1.0 + 0.0j
    for _ in range(steps):
        U = propagate_coherent(U, barrier, A, S, LAM, k)
    I = np.abs(U) ** 2
    return I[:, screen_x].copy()


def main():
    H, W = 181, 360
    source_x, source_y = 20, H // 2
    barrier_x = 145
    slit_w = 8
    slit1_y0 = H // 2 - 26
    slit2_y0 = H // 2 + 18
    screen_x = W - 12
    steps = 340

    A, S, LAM, k = 1.0, 0.18, 0.995, 2.0
    shots = 1200
    noise_sigma = 0.18
    thr_rel = 0.28
    rng = np.random.default_rng(42)

    barrier = make_double_slit_barrier(H, W, barrier_x, slit1_y0, slit2_y0, slit_w)

    # ===================== 核心优化：预计算所有5种源位置 =====================
    y_offsets = (-2, -1, 0, 1, 2)
    pre_screens = {}
    for dy in y_offsets:
        sy = source_y + dy
        pre_screens[dy] = compute_one_source_screen(
            H, W, source_x, sy, barrier, A, S, LAM, k, steps, screen_x
        )
    # ========================================================================

    accum_cont = np.zeros(H, dtype=np.float64)
    clicks = np.zeros(H, dtype=np.float64)
    hit_count = 0

    # 快速采样：直接取预计算结果
    dy_list = rng.choice(y_offsets, size=shots)
    for dy in dy_list:
        screen = pre_screens[dy]
        accum_cont += screen

        # 阈值与噪声
        smax = np.max(screen) + 1e-18
        noisy = screen + noise_sigma * smax * rng.normal(size=H)
        thr = thr_rel * smax

        cand = np.nonzero(noisy >= thr)[0]
        if cand.size == 0:
            continue

        # 加权选择
        w = noisy[cand]
        w[w < 0] = 0
        sw = w.sum()
        if sw <= 1e-18:
            continue

        idx = rng.choice(cand, p=w / sw)
        clicks[idx] += 1
        hit_count += 1

    # 归一化
    cont_n = accum_cont / (accum_cont.max() + 1e-18)
    click_n = clicks / (clicks.max() + 1e-18)
    r = pearson_safe(cont_n, click_n)
    hit_rate = hit_count / shots
    std_cont = np.std(cont_n)
    std_click = np.std(click_n)

    # 绘图（完全不变）
    out_png = "threshold_detector_clicks.png"
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    axes[0].plot(cont_n, color="#58a6ff", linewidth=2)
    axes[0].set_title("Continuous wave accumulation", color="white")
    axes[0].set_xlabel("y", color="#8b949e")
    axes[0].set_ylabel("normalized intensity", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")

    axes[1].bar(np.arange(H), click_n, color="#ffa657", width=1.0)
    axes[1].set_title("Threshold detector clicks", color="white")
    axes[1].set_xlabel("y", color="#8b949e")
    axes[1].set_ylabel("normalized click count", color="#8b949e")
    axes[1].grid(True, axis="y", alpha=0.25, color="#30363d")

    axes[2].plot(cont_n, color="#58a6ff", linewidth=1.8, label="continuous")
    axes[2].plot(click_n, color="#ffa657", linewidth=1.8, label="clicks")
    axes[2].set_title("Shape comparison", color="white")
    axes[2].set_xlabel("y", color="#8b949e")
    axes[2].set_ylabel("normalized", color="#8b949e")
    axes[2].grid(True, alpha=0.25, color="#30363d")
    axes[2].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    txt = f"shots={shots}\nhit_rate={hit_rate:.3f}\npearson_r={r:.4f}"
    axes[2].text(0.02, 0.98, txt, transform=axes[2].transAxes, va="top", ha="left", color="#c9d1d9", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")

    print("Threshold detector clicks experiment complete.")
    print("shots =", shots)
    print(f"hit_rate = {hit_rate:.4f}")
    print(f"pearson_r = {r:.4f}")
    print(f"std_cont = {std_cont:.6f}, std_click = {std_click:.6f}")
    print("saved:", out_png)


if __name__ == "__main__":
    main()