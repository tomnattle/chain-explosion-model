"""
explore_fringe_spacing_vs_slit_gap.py
--------------------------------------
用当前 ce_engine_v2 双缝传播，扫描缝中心间距 d，测量屏上条纹平均间隔 Δy，
检验是否与 Δy ∝ 1/d（固定 L、λ_eff 近似下）同量级。

运行: python explore_fringe_spacing_vs_slit_gap.py
输出: explore_fringe_spacing.png + 终端拟合斜率
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

HEIGHT = 301
WIDTH = 550
A, S, B, LAM = 1.0, 0.28, 0.05, 0.96
SOURCE_X = 8
SOURCE_Y = HEIGHT // 2
BAR_X = 150
SCREEN_X = WIDTH - 30
SLIT_W = 5
STEPS = 620
CENTER = SOURCE_Y

# 缝中心间距 d（像素）系列
D_LIST = [36, 44, 52, 60, 68, 76]


def slit_rows_from_gap(d: int):
    half = d // 2
    y1c = CENTER - half
    y2c = CENTER + half
    o1 = y1c - SLIT_W // 2
    o2 = y2c - SLIT_W // 2
    return o1, o2, d


def dominant_peak_spacing(screen: np.ndarray) -> float:
    """条纹间隔：优先峰间距中位数，失败则用 Hann + rFFT 估计主周期。"""
    sm = np.asarray(screen, dtype=np.float64)
    mx = float(sm.max())
    if mx < 1e-18:
        return float("nan")
    thr = 0.05 * mx
    idx = []
    for i in range(2, len(sm) - 2):
        if sm[i] > sm[i - 1] and sm[i] > sm[i + 1] and sm[i] >= thr:
            idx.append(i)
    if len(idx) >= 3:
        idx = np.array(idx, dtype=np.float64)
        gaps = np.diff(np.sort(idx))
        gaps = gaps[gaps > 2.0]
        if gaps.size >= 2:
            return float(np.median(gaps))

    # FFT 主频 -> 周期（格点）
    s = sm - np.mean(sm)
    if np.sum(s ** 2) < 1e-20:
        return float("nan")
    w = np.hanning(len(s))
    spec = np.abs(np.fft.rfft(s * w))
    spec[0] = 0.0
    freqs = np.fft.rfftfreq(len(s), d=1.0)
    half = max(3, len(spec) // 2)
    best_k, best_m = -1, -1.0
    lo, hi = 4.0, 0.42 * len(s)
    for k in range(1, half):
        f = float(freqs[k])
        if f <= 1e-12:
            continue
        per = 1.0 / f
        if not (lo <= per <= hi):
            continue
        if spec[k] > best_m:
            best_m = spec[k]
            best_k = k
    if best_k < 0 or best_m <= 0:
        return float("nan")
    return 1.0 / float(freqs[best_k])


def run_one(d: int):
    o1, o2, _ = slit_rows_from_gap(d)
    barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    barrier[:, BAR_X] = True
    barrier[o1 : o1 + SLIT_W, BAR_X] = False
    barrier[o2 : o2 + SLIT_W, BAR_X] = False

    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0
    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)
    screen = grid[:, SCREEN_X]
    spacing = dominant_peak_spacing(screen)
    vis = compute_visibility(screen)
    return spacing, vis, screen


def main():
    spacings = []
    ds = []
    vis_list = []
    for d in D_LIST:
        sp, vis, _ = run_one(d)
        spacings.append(sp)
        ds.append(float(d))
        vis_list.append(vis)
        print(f"d={d:3d} px | median fringe spacing Δy ≈ {sp:.3f} | V={vis:.4f}")

    ds = np.array(ds)
    sp = np.array(spacings)
    valid = np.isfinite(sp) & (sp > 0) & (ds > 0)
    if valid.sum() >= 3:
        import warnings

        logd = np.log(ds[valid])
        logs = np.log(sp[valid])
        coef = np.polyfit(logd, logs, 1)
        power = coef[0]
        print(
            f"\n幂律拟合 log(Δy) = {power:.3f} * log(d) + const "
            f"(理想双缝远场近似 Δy∝1/d → 斜率期望约 -1)"
        )
        print(f"拟合斜率 = {power:.4f}")
    else:
        power = float("nan")

    L = SCREEN_X - BAR_X
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(ds, sp, "bo-", lw=2)
    plt.xlabel("slit center distance d (px)")
    plt.ylabel("median fringe spacing Δy (px)")
    plt.title("Fringe spacing vs slit gap (CE grid)")
    plt.grid(alpha=0.3)

    plt.subplot(1, 2, 2)
    if valid.sum() >= 3:
        plt.plot(np.log(ds[valid]), np.log(sp[valid]), "rs-", ms=8)
        xf = np.linspace(np.log(ds[valid]).min(), np.log(ds[valid]).max(), 50)
        plt.plot(xf, np.polyval(coef, xf), "k--", lw=1)
        plt.xlabel("log d")
        plt.ylabel("log Δy")
        plt.title(f"log-log slope ≈ {power:.3f}")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "explore_fringe_spacing.png")
    plt.savefig(out, dpi=140)
    print(f"\nSaved: {out}")
    print(f"几何: L = screen - barrier = {L} px（用于与理论对照时请自洽 λ_eff）")


if __name__ == "__main__":
    main()
